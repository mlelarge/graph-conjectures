#!/usr/bin/env bash
# Long-run wrapper for SMS solver invocations.
#
# Captures stdout, stderr, pid, exit_status, plus a meta block with host,
# SMS commit / describe / dirty status, command, timeout, and start/end UTC.
# Detaches via nohup + disown so the run survives shell exit and harness
# timeouts, suitable for overnight or multi-day budgets.
#
# Usage:
#   run_smsg.sh <label> <timeout_seconds> <cmd> [args...]
#
# Layout:
#   problems/earth_moon_problem/data/<label>/<UTC-timestamp>/
#       meta.txt        host, SMS provenance, command, timestamps, exit_status
#       stdout.log      solver stdout
#       stderr.log      solver stderr
#       pid             gtimeout PID, written after launch
#       worker_pid      wrapper bash PID, for diagnostics only
#       exit_status     gtimeout exit code, written after exec
#
# Example:
#   ./run_smsg.sh candidate1_calibration 43200 \
#       python encodings/planarity.py -v 19 --directed --earthmoon_candidate1

set -euo pipefail

if [ $# -lt 3 ]; then
    cat <<EOF >&2
Usage: $0 <label> <timeout_seconds> <cmd> [args...]

Example:
  $0 candidate1_calibration 43200 \\
      python encodings/planarity.py -v 19 --directed --earthmoon_candidate1
EOF
    exit 2
fi

LABEL="$1"
TIMEOUT_SECS="$2"
shift 2

command -v gtimeout >/dev/null \
    || { echo "Error: gtimeout not on PATH (brew install coreutils)" >&2; exit 3; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SMS_DIR="$PROJECT_DIR/external/sat-modulo-symmetries"
VENV="$PROJECT_DIR/.venv"

[ -d "$SMS_DIR" ] || { echo "Error: SMS clone not found at $SMS_DIR" >&2; exit 4; }

if [ -f "$VENV/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$VENV/bin/activate"
else
    echo "Warning: venv not found at $VENV; using system python" >&2
fi

TS="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$PROJECT_DIR/data/$LABEL/$TS"
mkdir -p "$RUN_DIR"

META="$RUN_DIR/meta.txt"
STDOUT="$RUN_DIR/stdout.log"
STDERR="$RUN_DIR/stderr.log"
PIDFILE="$RUN_DIR/pid"
WORKER_PIDFILE="$RUN_DIR/worker_pid"
EXITFILE="$RUN_DIR/exit_status"

{
    echo "label: $LABEL"
    echo "timestamp_utc: $TS"
    echo "host: $(uname -a)"
    echo "start_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "timeout_seconds: $TIMEOUT_SECS"
    echo "venv: $VENV"
    echo "sms_dir: $SMS_DIR"
    echo "sms_head: $(cd "$SMS_DIR" && git rev-parse HEAD)"
    echo "sms_describe: $(cd "$SMS_DIR" && git describe --always --tags --dirty)"
    echo "sms_status: $(cd "$SMS_DIR" && git status --short | tr '\n' ';')"
    echo "cmd: $*"
} > "$META"

# Detached worker: cd into SMS_DIR (so relative encoding paths resolve), run
# under gtimeout, capture stdout/stderr separately, record the gtimeout pid
# plus exit_status, append end_utc to meta. nohup + disown lets the worker
# outlive this shell.
nohup bash -c '
    set -u
    sms_dir="$1"; pidfile="$2"; worker_pidfile="$3"; tout="$4"; out="$5"; err="$6"; exitfile="$7"; meta="$8"
    shift 8
    cd "$sms_dir"
    echo $$ > "$worker_pidfile"
    gtimeout "$tout" "$@" >"$out" 2>"$err" &
    timeout_pid=$!
    echo "$timeout_pid" > "$pidfile"
    wait "$timeout_pid"
    rc=$?
    echo "$rc" > "$exitfile"
    {
        echo "end_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo "exit_status: $rc"
    } >> "$meta"
' _ "$SMS_DIR" "$PIDFILE" "$WORKER_PIDFILE" "$TIMEOUT_SECS" "$STDOUT" "$STDERR" "$EXITFILE" "$META" "$@" \
    </dev/null >/dev/null 2>&1 &
disown

# Wait briefly for the worker to record its pid.
for _ in 1 2 3 4 5 6 7 8 9 10; do
    [ -s "$PIDFILE" ] && break
    sleep 0.1
done

cat <<EOF
run_dir:    $RUN_DIR
pid:        $(cat "$PIDFILE" 2>/dev/null || echo unknown)
timeout:    ${TIMEOUT_SECS}s
tail:       tail -F "$STDOUT"
status:     cat "$EXITFILE" 2>/dev/null || echo running
kill:       kill \$(cat "$PIDFILE")
EOF
