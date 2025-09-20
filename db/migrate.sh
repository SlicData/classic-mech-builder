#!/usr/bin/env bash
set -euo pipefail

DB_NAME="${DB_NAME:-cmb_dev}"
PSQL_ARGS=${DATABASE_URL:+-d "$DATABASE_URL"}

psql ${PSQL_ARGS:-} "$DB_NAME" -v ON_ERROR_STOP=1 <<'SQL'
CREATE TABLE IF NOT EXISTS schema_migrations (
  version TEXT PRIMARY KEY,
  applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
SQL

for f in $(ls -1 db/migrations/*_up.sql 2>/dev/null | sort); do
  base="$(basename "$f")"
  version="${base%_up.sql}"
  has=$(psql ${PSQL_ARGS:-} "$DB_NAME" -A -t -v ON_ERROR_STOP=1 \
        -c "SELECT 1 FROM schema_migrations WHERE version='$version' LIMIT 1;")
  if [[ "$has" == "1" ]]; then
    echo "Already applied: $version"
    continue
  fi

  echo "Applying: $version"
  psql ${PSQL_ARGS:-} "$DB_NAME" -v ON_ERROR_STOP=1 <<SQL
BEGIN;
\i $f
INSERT INTO schema_migrations(version) VALUES ('$version');
COMMIT;
SQL
done

echo "✅ Migrations up to date."
