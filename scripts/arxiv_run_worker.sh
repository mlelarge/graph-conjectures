#!/usr/bin/env bash
# scripts/arxiv_run_worker.sh — process one bucket of arxiv extraction work.
#
# Each line of data/arxiv_buckets/bucket-NN.txt is a `<safe_id>` (unique paper).
# For each line we shell out to:
#     python scraper/arxiv_extract.py --paper <safe_id>
# which auto-detects which author's cache contains the paper, then writes
# data/arxiv_extracted/<safe_id>.json. Wrapped in a per-paper timeout.
#
# Usage (in its own terminal, one worker per bucket):
#   WORKER=01 bash scripts/arxiv_run_worker.sh
#
# Env knobs:
#   WORKER             two-digit bucket number, default 01
#   PER_PAPER_TIMEOUT  hard ceiling per paper in seconds, default 900 (15 min)
#                      stragglers pass: bump to 1800 (30 min)
#   MODEL              passed to claude inside arxiv_extract.py via env; default unset
#
# Idempotent: arxiv_extract.py skips papers whose output JSON already exists.
# Persistent failures: add `<author_slug>/<safe_id>` to data/arxiv_failed.txt
# to make the worker skip them on future runs.

set -u

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKER="${WORKER:-01}"
PER_PAPER_TIMEOUT="${PER_PAPER_TIMEOUT:-900}"

BUCKET="$PROJECT_DIR/data/arxiv_buckets/bucket-${WORKER}.txt"
FAILED_LIST="$PROJECT_DIR/data/arxiv_failed.txt"
LOG="$PROJECT_DIR/logs/arxiv-worker-${WORKER}.log"
EXTRACTED_DIR="$PROJECT_DIR/data/arxiv_extracted"

PYTHON="$PROJECT_DIR/.venv/bin/python"
[[ -x "$PYTHON" ]] || PYTHON="$(command -v python3 || command -v python)"

mkdir -p "$(dirname "$LOG")" "$EXTRACTED_DIR"
exec > >(tee -a "$LOG") 2>&1

if [[ ! -f "$BUCKET" ]]; then
  echo "[$WORKER] no bucket file at $BUCKET — run: python scripts/arxiv_partition.py --workers N"
  exit 2
fi

TOTAL=$(grep -c . "$BUCKET" || echo 0)
echo "[$WORKER] $(date '+%H:%M:%S') start  bucket=$BUCKET  items=$TOTAL  timeout=${PER_PAPER_TIMEOUT}s  log=$LOG"

I=0
while IFS= read -r safe_id || [[ -n "$safe_id" ]]; do
  safe_id="${safe_id%$'\r'}"
  [[ -z "$safe_id" ]] && continue
  I=$((I + 1))

  out_json="$EXTRACTED_DIR/$safe_id.json"
  if [[ -f "$out_json" ]]; then
    echo "[$WORKER] [$I/$TOTAL] $(date '+%H:%M:%S') $safe_id — cached, skip"
    continue
  fi
  if [[ -f "$FAILED_LIST" ]] && grep -qxF "$safe_id" "$FAILED_LIST"; then
    echo "[$WORKER] [$I/$TOTAL] $(date '+%H:%M:%S') $safe_id — in failed list, skip"
    continue
  fi

  # Reconstruct the arxiv_id from safe_id (old-style ids: 'cs_0703001' → 'cs/0703001')
  if [[ "$safe_id" =~ ^[a-z\-]+_[0-9]+$ ]]; then
    arxiv_id="${safe_id/_//}"
  else
    arxiv_id="$safe_id"
  fi

  echo "[$WORKER] [$I/$TOTAL] $(date '+%H:%M:%S') $safe_id — extracting"
  START=$(date +%s)
  OUTER_TIMEOUT=$((PER_PAPER_TIMEOUT + 60))
  PER_PAPER_TIMEOUT="$PER_PAPER_TIMEOUT" \
    "$PYTHON" "$PROJECT_DIR/scripts/timeout_claude.py" "$OUTER_TIMEOUT" \
      "$PYTHON" "$PROJECT_DIR/scraper/arxiv_extract.py" \
        --paper "$arxiv_id" 2>&1 | tail -8 | sed "s/^/[$WORKER]   /"
  STATUS=$?
  ELAPSED=$(($(date +%s) - START))

  if [[ -f "$out_json" ]]; then
    echo "[$WORKER] [$I/$TOTAL]   saved $safe_id.json (${ELAPSED}s, exit=$STATUS)"
  else
    echo "[$WORKER] [$I/$TOTAL]   FAILED $safe_id (exit=$STATUS, ${ELAPSED}s, no JSON written)"
  fi
done < "$BUCKET"

echo "[$WORKER] $(date '+%H:%M:%S') done"
