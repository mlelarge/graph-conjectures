#!/usr/bin/env bash
# scripts/arxiv_name_run_worker.sh — name one bucket of arxiv conjectures.
#
# Each line of data/arxiv_name_buckets/bucket-NN.txt is a `<review_id>`.
# Shells out to scraper/arxiv_name.py per review_id; writes
# data/arxiv_names/<review_id>.json. No web tools, fast.
#
# Usage:
#   WORKER=01 PER_NAME_TIMEOUT=120 bash scripts/arxiv_name_run_worker.sh

set -u
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKER="${WORKER:-01}"
PER_NAME_TIMEOUT="${PER_NAME_TIMEOUT:-120}"
MODEL="${MODEL:-claude-sonnet-4-6}"

BUCKET="$PROJECT_DIR/data/arxiv_name_buckets/bucket-${WORKER}.txt"
NAMES_DIR="$PROJECT_DIR/data/arxiv_names"
LOG="$PROJECT_DIR/logs/arxiv-name-worker-${WORKER}.log"

PYTHON="$PROJECT_DIR/.venv/bin/python"
[[ -x "$PYTHON" ]] || PYTHON="$(command -v python3 || command -v python)"

mkdir -p "$(dirname "$LOG")" "$NAMES_DIR"
exec > >(tee -a "$LOG") 2>&1

if [[ ! -f "$BUCKET" ]]; then
  echo "[$WORKER] no bucket file at $BUCKET — run: python scripts/arxiv_name_partition.py --workers N"
  exit 2
fi

TOTAL=$(grep -c . "$BUCKET" || echo 0)
echo "[$WORKER] $(date '+%H:%M:%S') start  bucket=$BUCKET  items=$TOTAL  timeout=${PER_NAME_TIMEOUT}s  log=$LOG"

I=0
while IFS= read -r review_id || [[ -n "$review_id" ]]; do
  review_id="${review_id%$'\r'}"
  [[ -z "$review_id" ]] && continue
  I=$((I + 1))

  out_json="$NAMES_DIR/$review_id.json"
  if [[ -f "$out_json" ]]; then
    continue   # silent skip — most cached on resume
  fi

  echo "[$WORKER] [$I/$TOTAL] $(date '+%H:%M:%S') $review_id"
  START=$(date +%s)
  PER_NAME_TIMEOUT="$PER_NAME_TIMEOUT" \
    "$PYTHON" "$PROJECT_DIR/scraper/arxiv_name.py" \
      --review-id "$review_id" \
      --model "$MODEL" 2>&1 | tail -3 | sed "s/^/[$WORKER]   /"
  STATUS=$?
  ELAPSED=$(($(date +%s) - START))

  if [[ -f "$out_json" ]]; then
    name=$($PYTHON -c "import json; print(json.load(open('$out_json'))['nice_name'])" 2>/dev/null)
    echo "[$WORKER] [$I/$TOTAL]   saved (${ELAPSED}s): $name"
  else
    echo "[$WORKER] [$I/$TOTAL]   FAILED $review_id (exit=$STATUS, ${ELAPSED}s)"
  fi
done < "$BUCKET"

echo "[$WORKER] $(date '+%H:%M:%S') done"
