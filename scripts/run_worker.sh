#!/usr/bin/env bash
# Process a bucket of OPG slugs sequentially, one `claude -p` per slug.
#
# Usage (in its own terminal):
#   WORKER=01 bash scripts/run_worker.sh
#
# Optional env:
#   WORKER          two-digit bucket number, default 01
#   MODEL           --model passed to claude, default claude-sonnet-4-6
#   PER_SLUG_TIMEOUT  hard ceiling per slug in seconds (0 disables), default 0
#                   (set to 720 to bound stragglers; needs `gtimeout` from coreutils)
#
# The script is idempotent: it skips slugs whose JSON already exists.
# Stop a worker any time with Ctrl-C; rerun to resume.

set -u

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKER="${WORKER:-01}"
MODEL="${MODEL:-claude-sonnet-4-6}"
PER_SLUG_TIMEOUT="${PER_SLUG_TIMEOUT:-0}"

BUCKET="$PROJECT_DIR/data/agent_buckets/bucket-${WORKER}.txt"
PROMPTS_DIR="$PROJECT_DIR/data/agent_prompts"
REVIEWS_DIR="$PROJECT_DIR/data/reviews"
LOG="$PROJECT_DIR/logs/worker-${WORKER}.log"

mkdir -p "$REVIEWS_DIR" "$(dirname "$LOG")"
# Tee everything to the worker's log file (and to stdout).
exec > >(tee -a "$LOG") 2>&1

if [[ ! -f "$BUCKET" ]]; then
  echo "[$WORKER] no bucket file at $BUCKET — run: python scripts/partition.py --workers N"
  exit 2
fi

TOTAL=$(grep -c . "$BUCKET" || echo 0)
echo "[$WORKER] $(date '+%H:%M:%S') start  bucket=$BUCKET  slugs=$TOTAL  model=$MODEL  log=$LOG"

# Pick a timeout wrapper if PER_SLUG_TIMEOUT > 0. Order of preference:
# gtimeout > timeout > Python fallback (scripts/timeout_claude.py, no install needed).
RUNNER=()
if [[ "$PER_SLUG_TIMEOUT" -gt 0 ]]; then
  if command -v gtimeout >/dev/null 2>&1; then
    RUNNER=(gtimeout --kill-after=10 "${PER_SLUG_TIMEOUT}s")
  elif command -v timeout >/dev/null 2>&1; then
    RUNNER=(timeout --kill-after=10 "${PER_SLUG_TIMEOUT}s")
  elif command -v python3 >/dev/null 2>&1; then
    RUNNER=(python3 "$PROJECT_DIR/scripts/timeout_claude.py" "$PER_SLUG_TIMEOUT")
  else
    echo "[$WORKER] PER_SLUG_TIMEOUT set but no gtimeout/timeout/python3 — running without timeout"
  fi
fi

I=0
while IFS= read -r slug || [[ -n "$slug" ]]; do
  slug="${slug%$'\r'}"
  [[ -z "$slug" ]] && continue
  I=$((I + 1))

  if [[ -f "$REVIEWS_DIR/$slug.json" ]]; then
    echo "[$WORKER] [$I/$TOTAL] $(date '+%H:%M:%S') $slug — cached, skip"
    continue
  fi

  if [[ -f "$PROJECT_DIR/data/agent_failed.txt" ]] && grep -qxF "$slug" "$PROJECT_DIR/data/agent_failed.txt"; then
    echo "[$WORKER] [$I/$TOTAL] $(date '+%H:%M:%S') $slug — listed in agent_failed.txt, skip"
    continue
  fi

  PROMPT_FILE="$PROMPTS_DIR/$slug.md"
  if [[ ! -f "$PROMPT_FILE" ]]; then
    echo "[$WORKER] [$I/$TOTAL] $(date '+%H:%M:%S') $slug — MISSING prompt at $PROMPT_FILE, skip"
    continue
  fi

  # Compose the message: the prompt file plus a write instruction with the
  # *absolute* output path (claude -p inherits the worker's cwd).
  USER_MSG="$(cat "$PROMPT_FILE")

After completing the review, use the Write tool to save the JSON object (raw, no <review_json> tags) to this exact path:

$REVIEWS_DIR/$slug.json

Include these extra fields in the JSON object:
- \"slug\": \"$slug\"
- \"reviewed_at\": \"$(date +%Y-%m-%d)\"
- \"model\": \"$MODEL (worker $WORKER)\"
- \"search_enabled\": true

Issue independent WebSearch / WebFetch calls in parallel where possible. Verify every cited URL with WebFetch before writing it. Be decisive — if you cannot verify any post-posting paper after 4 search queries, return status \"unclear\" with confidence \"low\". Then output one line: done: $slug -> <status> (<confidence>, <N> cites)."

  echo "[$WORKER] [$I/$TOTAL] $(date '+%H:%M:%S') $slug — reviewing"
  START=$(date +%s)
  "${RUNNER[@]}" claude -p "$USER_MSG" \
    --allowed-tools "WebSearch WebFetch Read Write" \
    --model "$MODEL" \
    --output-format text \
    --no-session-persistence 2>&1 | tail -3 | sed "s/^/[$WORKER]   /"
  STATUS=$?
  ELAPSED=$(($(date +%s) - START))

  if [[ -f "$REVIEWS_DIR/$slug.json" ]]; then
    echo "[$WORKER] [$I/$TOTAL]   saved $slug.json (${ELAPSED}s)"
  else
    echo "[$WORKER] [$I/$TOTAL]   FAILED $slug (claude exit=$STATUS, ${ELAPSED}s, no JSON written)"
  fi
done < "$BUCKET"

echo "[$WORKER] $(date '+%H:%M:%S') done"
