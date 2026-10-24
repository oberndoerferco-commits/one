#!/usr/bin/env bash
# Cross-tenant isolation tests for site/supabase/schema.sql.
# Starts a throwaway PostgreSQL cluster, loads a minimal Supabase shim,
# loads schema.sql unchanged, runs isolation.sql, stops and removes the cluster.
# Exit code 0 = all checks passed. Needs PostgreSQL 15+ server binaries
# (initdb, pg_ctl) and psql; not part of `npm run build` or CI.
#
# Env:
#   PG_BIN        directory with initdb/pg_ctl (default: pg_config --bindir,
#                 else the newest /usr/lib/postgresql/*/bin)
#   PGTEST_DIR    working directory for the cluster (default: mktemp -d);
#                 removed afterwards unless PGTEST_KEEP=1
#   PGTEST_PORT   port number used for the Unix socket (default 54329; no TCP)
#   SCHEMA_FILE   schema to test (default ../schema.sql)
#   PGTEST_OS_USER  when run as root, the unprivileged OS user that runs
#                 postgres (default: nobody)
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCHEMA="${SCHEMA_FILE:-$HERE/../schema.sql}"   # SCHEMA_FILE: override for mutation checks

if [[ -z "${PG_BIN:-}" ]]; then
  if command -v pg_config >/dev/null 2>&1 && [[ -x "$(pg_config --bindir)/initdb" ]]; then
    PG_BIN="$(pg_config --bindir)"
  else
    PG_BIN="$(ls -d /usr/lib/postgresql/*/bin 2>/dev/null | sort -V | tail -n1 || true)"
  fi
fi
[[ -x "$PG_BIN/initdb" && -x "$PG_BIN/pg_ctl" ]] || { echo "initdb/pg_ctl not found (set PG_BIN)" >&2; exit 2; }
PSQL="$(command -v psql || echo "$PG_BIN/psql")"
[[ -x "$PSQL" ]] || { echo "psql not found" >&2; exit 2; }

CREATED_DIR=0
if [[ -z "${PGTEST_DIR:-}" ]]; then PGTEST_DIR="$(mktemp -d)"; CREATED_DIR=1; fi
mkdir -p "$PGTEST_DIR"
PORT="${PGTEST_PORT:-54329}"
DATA="$PGTEST_DIR/data"
LOG="$PGTEST_DIR/postgres.log"
OUT="$PGTEST_DIR/results.txt"

RUNAS=()
if [[ "$(id -u)" == 0 ]]; then
  OSUSER="${PGTEST_OS_USER:-nobody}"
  chown "$OSUSER" "$PGTEST_DIR"
  RUNAS=(runuser -u "$OSUSER" --)
  if ! "${RUNAS[@]}" test -w "$PGTEST_DIR"; then
    echo "$OSUSER cannot reach $PGTEST_DIR (a parent directory is not traversable); pick another PGTEST_DIR" >&2
    exit 2
  fi
fi

cleanup() {
  "${RUNAS[@]}" "$PG_BIN/pg_ctl" -D "$DATA" -m fast -w stop >/dev/null 2>&1 || true
  if [[ "${PGTEST_KEEP:-0}" != 1 ]]; then
    if [[ "$CREATED_DIR" == 1 ]]; then rm -rf "$PGTEST_DIR"; else rm -rf "$DATA" "$LOG"; fi
  fi
}
trap cleanup EXIT

"${RUNAS[@]}" "$PG_BIN/initdb" -D "$DATA" -U postgres -A trust -E UTF8 --no-sync >/dev/null
"${RUNAS[@]}" "$PG_BIN/pg_ctl" -D "$DATA" -l "$LOG" -w \
  -o "-c listen_addresses='' -k $PGTEST_DIR -p $PORT -c fsync=off" start >/dev/null

run_psql() { "$PSQL" -X -q -h "$PGTEST_DIR" -p "$PORT" -U postgres -d postgres -v ON_ERROR_STOP=1 "$@"; }

echo "== shim"
run_psql -f "$HERE/supabase_shim.sql"
echo "== schema.sql"
if ! run_psql -f "$SCHEMA"; then echo "schema.sql failed to load" >&2; exit 1; fi
echo "== isolation.sql"
set +e
run_psql -o /dev/null -f "$HERE/isolation.sql" 2>&1 | tee "$OUT"
STATUS=${PIPESTATUS[0]}
set -e
PASS=$(grep -c 'NOTICE:  ok - ' "$OUT" || true)
INFO=$(grep -c 'NOTICE:  info - ' "$OUT" || true)
if [[ $STATUS -ne 0 ]] || grep -q 'FAIL - ' "$OUT"; then
  echo "== FAILED after $PASS passing checks" >&2
  exit 1
fi
echo "== all $PASS checks passed ($INFO info notes)"
