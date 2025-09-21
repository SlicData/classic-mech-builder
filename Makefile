DB_NAME ?= cmb_dev
.PHONY: migrate rollback newdb reset seed seed-megamek seed-test
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
