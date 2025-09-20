#!/usr/bin/env bash
set -euo pipefail
name="${1:-}"
if [[ -z "$name" ]]; then
  echo "Usage: $0 <snake_case_name>"
  exit 1
fi
last=$(ls -1 db/migrations/*_up.sql 2>/dev/null | awk -F/ '{print $3}' | awk -F_ '{print $1}' | sort -n | tail -1)
next=$(printf "%03d" $(( ${last:-0} + 1 )))
up="db/migrations/${next}_${name}_up.sql"
down="db/migrations/${next}_${name}_down.sql"
cat > "$up" <<SQL
-- ${next}_${name} (UP)
BEGIN;
-- SQL goes here
COMMIT;
SQL
cat > "$down" <<SQL
-- ${next}_${name} (DOWN)
BEGIN;
-- SQL goes here
COMMIT;
SQL
echo "Created:"
echo "  $up"
echo "  $down"
