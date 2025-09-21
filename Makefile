DB_NAME ?= cmb_dev
.PHONY: migrate rollback newdb reset seed seed-megamek seed-test test-queries validate-queries
migrate:
	DB_NAME=$(DB_NAME) ./db/migrate.sh
rollback:
	DB_NAME=$(DB_NAME) ./db/rollback_last.sh
newdb:
	createdb $(DB_NAME) || true
reset:
	DB_NAME=$(DB_NAME) ./db/rollback_last.sh || true
seed-megamek:
	python3 db/seeds/mtf_seeder.py --megamek-path ./data/megamek --db-name $(DB_NAME)
seed-test:
	python3 db/seeds/mtf_seeder.py --megamek-path ./data/megamek --db-name $(DB_NAME) --limit 10 --dry-run
seed:
	@echo "Use 'make seed-megamek' to seed from MegaMek MTF files"
	@echo "Use 'make seed-test' to test parsing without database changes"

# CMB-11: Query validation tests
test-queries:
	@echo "Running manual SQL query tests..."
	psql -d $(DB_NAME) -f test_queries.sql

validate-queries:
	@echo "Running automated query validation suite..."
	python3 test_runner.py
	@echo "Query validation complete!"
