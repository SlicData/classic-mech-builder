#!/usr/bin/env bash
set -euo pipefail
DB_NAME="${DB_NAME:-cmb_dev}"
PSQL_ARGS=${DATABASE_URL:+-d "$DATABASE_URL"}
last=$(psql ${PSQL_ARGS:-} "$DB_NAME" -A -t -v ON_ERROR_STOP=1 -c "SELECT version FROM schema_migrations ORDER BY applied_at DESC LIMIT 1;")
if [[ -z "$last" ]]; then
  echo "No applied migrations."
  exit 0
fi
down="db/migrations/${last}_down.sql"
if [[ ! -f "$down" ]]; then
  echo "Missing down file: $down"
  exit 1
fi
echo "Rolling back: $last"
psql ${PSQL_ARGS:-} "$DB_NAME" -v ON_ERROR_STOP=1 <<SQL
BEGIN;
\i $down
DELETE FROM schema_migrations WHERE version='$last';
COMMIT;
SQL
echo "✅ Rolled back: $last"
