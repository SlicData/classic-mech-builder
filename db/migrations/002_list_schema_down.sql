-- CMB-8: Rollback list schema

-- Drop triggers first
DROP TRIGGER IF EXISTS list_set_updated_at ON list;

-- Drop indexes
DROP INDEX IF EXISTS idx_list_mech_mech_id;
DROP INDEX IF EXISTS idx_list_mech_list_id;
DROP INDEX IF EXISTS idx_list_created_at;
DROP INDEX IF EXISTS idx_list_owner;

-- Drop tables (foreign key constraints will prevent dropping in wrong order)
DROP TABLE IF EXISTS list_mech;
DROP TABLE IF EXISTS list;
