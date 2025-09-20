DB_NAME ?= cmb_dev
.PHONY: migrate rollback newdb reset seed
migrate:
	DB_NAME=$(DB_NAME) ./db/migrate.sh
rollback:
	DB_NAME=$(DB_NAME) ./db/rollback_last.sh
newdb:
	createdb $(DB_NAME) || true
reset:
	DB_NAME=$(DB_NAME) ./db/rollback_last.sh || true
seed:
	psql $(DB_NAME) -v ON_ERROR_STOP=1 -f db/seeds/um_r27.sql
