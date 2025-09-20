-- CMB-7: Rollback initial schema

DROP TABLE IF EXISTS mech_manufacturer;
DROP TABLE IF EXISTS mech_quirk;
DROP TABLE IF EXISTS mech_crit_slot;
DROP TABLE IF EXISTS mech_ammo_bin;
DROP TABLE IF EXISTS mech_equipment;
DROP TABLE IF EXISTS mech_weapon;
DROP TABLE IF EXISTS mech_armor;
DROP TABLE IF EXISTS ammo_catalog;
DROP TABLE IF EXISTS equipment_catalog;
DROP TABLE IF EXISTS weapon_catalog;
DROP TRIGGER IF EXISTS mech_set_updated_at ON mech;
DROP FUNCTION IF EXISTS set_updated_at;
DROP TABLE IF EXISTS mech;

DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'crit_item_type') THEN DROP TYPE crit_item_type; END IF;
  IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'equipment_category') THEN DROP TYPE equipment_category; END IF;
  IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'weapon_class') THEN DROP TYPE weapon_class; END IF;
  IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'location') THEN DROP TYPE location; END IF;
  IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'armor_type') THEN DROP TYPE armor_type; END IF;
  IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'engine_type') THEN DROP TYPE engine_type; END IF;
  IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'era') THEN DROP TYPE era; END IF;
  IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tech_base') THEN DROP TYPE tech_base; END IF;
END $$;
