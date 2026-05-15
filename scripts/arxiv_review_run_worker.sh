#!/usr/bin/env bash
# scripts/arxiv_review_run_worker.sh — Phase-2 worker for arxiv conjecture reviews.
#
# Each line of data/arxiv_review_buckets/bucket-NN.txt is a `<safe_id>`.
# For each line we shell out to:
#     python scraper/arxiv_review.py --safe-id <safe_id>
# which composes the prompt, calls `claude -p`, and writes
# data/arxiv_reviews/<safe_id>.json.
#
# Usage (one per terminal OR background):
#   WORKER=01 PER_REVIEW_TIMEOUT=900 bash scripts/arxiv_review_run_worker.sh
#
# Env knobs:
#   WORKER             two-digit bucket number (default 01)
#   PER_REVIEW_TIMEOUT seconds per conjecture (default 900, bump to 1800 for stragglers)
#   MODEL              passed to arxiv_review.py (default claude-sonnet-4-6)
#
# Idempotent: arxiv_review.py skips safe_ids whose JSON already exists.
# Persistent failures: add `<safe_id>` to data/arxiv_review_failed.txt to skip.

set -u

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKER="${WORKER:-01}"
PER_REVIEW_TIMEOUT="${PER_REVIEW_TIMEOUT:-900}"
MODEL="${MODEL:-claude-sonnet-4-6}"

BUCKET="$PROJECT_DIR/data/arxiv_review_buckets/bucket-${WORKER}.txt"
FAILED_LIST="$PROJECT_DIR/data/arxiv_review_failed.txt"
REVIEWS_DIR="$PROJECT_DIR/data/arxiv_reviews"
LOG="$PROJECT_DIR/logs/arxiv-review-worker-${WORKER}.log"

PYTHON="$PROJECT_DIR/.venv/bin/python"
[[ -x "$PYTHON" ]] || PYTHON="$(command -v python3 || command -v python)"

mkdir -p "$(dirname "$LOG")" "$REVIEWS_DIR"
exec > >(tee -a "$LOG") 2>&1

if [[ ! -f "$BUCKET" ]]; then
  echo "[$WORKER] no bucket file at $BUCKET — run: python scripts/arxiv_review_partition.py --workers N"
  exit 2
fi

TOTAL=$(grep -c . "$BUCKET" || echo 0)
echo "[$WORKER] $(date '+%H:%M:%S') start  bucket=$BUCKET  items=$TOTAL  timeout=${PER_REVIEW_TIMEOUT}s  log=$LOG"

I=0
while IFS= read -r review_id || [[ -n "$review_id" ]]; do
  review_id="${review_id%$'\r'}"
  [[ -z "$review_id" ]] && continue
  I=$((I + 1))

  out_json="$REVIEWS_DIR/$review_id.json"
  if [[ -f "$out_json" ]]; then
    echo "[$WORKER] [$I/$TOTAL] $(date '+%H:%M:%S') $review_id — cached, skip"
    continue
  fi
  if [[ -f "$FAILED_LIST" ]] && grep -qxF "$review_id" "$FAILED_LIST"; then
    echo "[$WORKER] [$I/$TOTAL] $(date '+%H:%M:%S') $review_id — in failed list, skip"
    continue
  fi

  echo "[$WORKER] [$I/$TOTAL] $(date '+%H:%M:%S') $review_id — reviewing"
  START=$(date +%s)
  PER_REVIEW_TIMEOUT="$PER_REVIEW_TIMEOUT" \
    "$PYTHON" "$PROJECT_DIR/scraper/arxiv_review.py" \
      --review-id "$review_id" \
      --model "$MODEL" 2>&1 | tail -6 | sed "s/^/[$WORKER]   /"
  STATUS=$?
  ELAPSED=$(($(date +%s) - START))

  if [[ -f "$out_json" ]]; then
    echo "[$WORKER] [$I/$TOTAL]   saved $review_id.json (${ELAPSED}s, exit=$STATUS)"
  else
    echo "[$WORKER] [$I/$TOTAL]   FAILED $review_id (exit=$STATUS, ${ELAPSED}s, no JSON written)"
  fi
done < "$BUCKET"

echo "[$WORKER] $(date '+%H:%M:%S') done"
