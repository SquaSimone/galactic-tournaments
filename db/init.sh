#!/bin/bash
set -e

echo "=== Galactic Tournaments Database Init ==="

for f in /migrations/*.sql; do
    echo "Applying migration: $(basename $f)"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f "$f"
done

echo "=== All migrations applied ==="
