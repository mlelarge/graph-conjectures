#!/usr/bin/env bash
# Snapshot of every worker: done count, fail count, current in-flight slug,
# and how long it's been on that slug. A "⚠" marker flags >10 min on one slug.

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR" || exit 1
NOW=$(date +%s)

DONE=$(find data/reviews -maxdepth 1 -name '*.json' ! -name '*.raw.json' 2>/dev/null | wc -l | tr -d ' ')
LATEST_FILE_MTIME=$(find data/reviews -maxdepth 1 -name '*.json' ! -name '*.raw.json' -print0 2>/dev/null | xargs -0 stat -f '%m %N' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f1)
if [[ -n "$LATEST_FILE_MTIME" ]]; then
  GLOBAL_AGE=$((NOW - LATEST_FILE_MTIME))
  printf 'global: %s / 227 reviews on disk · last file written %ds ago\n\n' "$DONE" "$GLOBAL_AGE"
else
  printf 'global: %s / 227 reviews on disk\n\n' "$DONE"
fi

shopt -s nullglob
LOGS=( logs/worker-*.log )
if [[ ${#LOGS[@]} -eq 0 ]]; then
  echo "no worker logs at logs/worker-*.log — start a worker with: WORKER=01 bash scripts/run_worker.sh"
  exit 0
fi

printf '%-8s %-5s %-5s %-7s  %s\n' worker done fail age slug
printf '%-8s %-5s %-5s %-7s  %s\n' "-------" "----" "----" "------" "-----------------------"

for log in "${LOGS[@]}"; do
  w=$(basename "$log" .log | sed 's/^worker-//')
  # Count UNIQUE slugs — `tee -a` appends across restarts, so a slug can appear
  # FAILED on run 1 and `saved` on run 2; uniquing avoids double-count.
  ndone=$(grep -oE '  saved [^ ]+\.json' "$log" | sort -u | wc -l | tr -d ' ')
  nfail=$(grep -oE '  FAILED [^ ]+' "$log" | awk '{print $2}' | sort -u | wc -l | tr -d ' ')
  last_review_line=$(grep '— reviewing' "$log" | tail -1)
  if [[ -z "$last_review_line" ]]; then
    printf '%-8s %-5s %-5s %-7s  %s\n' "$w" "$ndone" "$nfail" "—" "(no reviews started yet)"
    continue
  fi
  slug=$(echo "$last_review_line" | sed -E 's/.* ([^ ]+) — reviewing$/\1/')

  if grep -q "saved ${slug}.json\|FAILED ${slug}" "$log"; then
    last_done_line=$(grep -E "(saved [^ ]+.json|FAILED )" "$log" | tail -1)
    last_done_mtime=$(stat -f %m "$log")
    age=$((NOW - last_done_mtime))
    printf '%-8s %-5s %-5s %-7s  %s\n' "$w" "$ndone" "$nfail" "${age}s" "(idle, between slugs)"
  else
    log_mtime=$(stat -f %m "$log")
    age=$((NOW - log_mtime))
    marker=""
    if [[ $age -gt 600 ]]; then marker="⚠"
    elif [[ $age -gt 300 ]]; then marker="·"
    fi
    printf '%-8s %-5s %-5s %-7s  %s %s\n' "$w" "$ndone" "$nfail" "${age}s" "$marker" "$slug"
  fi
done
