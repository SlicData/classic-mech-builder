-- CMB-7: Initial schema for classicMechBuilder (normalized, MTF-ready)

-- Optional extension for fuzzy name search (safe to keep, skip if perms error)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Enums
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tech_base') THEN
    CREATE TYPE tech_base AS ENUM ('inner_sphere','clan','mixed','primitive');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'era') THEN
    CREATE TYPE era AS ENUM ('star_league','succession','clan_invasion','civil_war','jihad','dark_age','ilclan');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'engine_type') THEN
    CREATE TYPE engine_type AS ENUM ('fusion','xl_fusion','light_fusion','ice','compact_fusion','other');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'armor_type') THEN
    CREATE TYPE armor_type AS ENUM ('standard','ferro_fibrous','hardened','stealth','endo_steel','other');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'location') THEN
    CREATE TYPE location AS ENUM ('HD','CT','LT','RT','LA','RA','LL','RL');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'weapon_class') THEN
    CREATE TYPE weapon_class AS ENUM ('ballistic','energy','missile','support','artillery');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'equipment_category') THEN
    CREATE TYPE equipment_category AS ENUM ('movement','defense','electronics','heat','structure','gyro','cockpit','other');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'crit_item_type') THEN
    CREATE TYPE crit_item_type AS ENUM ('weapon','equipment','ammo','engine','gyro','life_support','sensors','cockpit','heatsink','jump_jet','empty');
  END IF;
END $$;

-- Core mech table
CREATE TABLE IF NOT EXISTS mech (
  id            BIGSERIAL PRIMARY KEY,
  chassis       TEXT NOT NULL,
  model         TEXT NOT NULL,
  tech_base     tech_base NOT NULL,
  era           era NOT NULL,
  rules_level   SMALLINT NOT NULL CHECK (rules_level BETWEEN 1 AND 4),

  tonnage       INTEGER NOT NULL CHECK (tonnage > 0),
  battle_value  INTEGER NOT NULL CHECK (battle_value >= 0),

  walk_mp       INTEGER NOT NULL CHECK (walk_mp >= 0),
  run_mp        INTEGER NOT NULL CHECK (run_mp  >= 0),
  jump_mp       INTEGER NOT NULL CHECK (jump_mp >= 0),
  engine_type   engine_type NOT NULL,
  engine_rating INTEGER NOT NULL CHECK (engine_rating >= 0),
  heat_sinks    INTEGER NOT NULL CHECK (heat_sinks >= 0),

  armor_type    armor_type NOT NULL,

  role          TEXT,
  "year"        INTEGER,
  source        TEXT,
  cost_cbill    BIGINT,

  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  UNIQUE (chassis, model)
);

-- Search indexes
CREATE INDEX IF NOT EXISTS idx_mech_display_trgm
  ON mech USING gin ((chassis || ' ' || model) gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_mech_era      ON mech (era);
CREATE INDEX IF NOT EXISTS idx_mech_techbase ON mech (tech_base);
CREATE INDEX IF NOT EXISTS idx_mech_bv       ON mech (battle_value);
CREATE INDEX IF NOT EXISTS idx_mech_tonnage  ON mech (tonnage);

-- updated_at trigger
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS mech_set_updated_at ON mech;
CREATE TRIGGER mech_set_updated_at
BEFORE UPDATE ON mech
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Catalogs
CREATE TABLE IF NOT EXISTS weapon_catalog (
  id              BIGSERIAL PRIMARY KEY,
  name            TEXT NOT NULL,
  class           weapon_class NOT NULL,
  tech_base       tech_base,
  heat            INTEGER NOT NULL DEFAULT 0,
  min_range       INTEGER NOT NULL DEFAULT 0,
  short_range     INTEGER NOT NULL DEFAULT 0,
  med_range       INTEGER NOT NULL DEFAULT 0,
  long_range      INTEGER NOT NULL DEFAULT 0,
  dmg_short       NUMERIC(6,2),
  dmg_med         NUMERIC(6,2),
  dmg_long        NUMERIC(6,2),
  cluster         BOOLEAN DEFAULT FALSE,
  tonnage         NUMERIC(6,2),
  critical_slots  INTEGER,
  ammo_type       TEXT,
  artemis_capable BOOLEAN DEFAULT FALSE,
  UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS equipment_catalog (
  id              BIGSERIAL PRIMARY KEY,
  name            TEXT NOT NULL,
  category        equipment_category NOT NULL,
  tech_base       tech_base,
  tonnage         NUMERIC(6,2),
  critical_slots  INTEGER,
  UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS ammo_catalog (
  id             BIGSERIAL PRIMARY KEY,
  ammo_type      TEXT NOT NULL,
  per_ton_rounds INTEGER NOT NULL,
  tech_base      tech_base,
  UNIQUE (ammo_type, tech_base)
);

-- Per-mech detail
CREATE TABLE IF NOT EXISTS mech_armor (
  mech_id      BIGINT NOT NULL REFERENCES mech(id) ON DELETE CASCADE,
  loc          location NOT NULL,
  armor_front  INTEGER NOT NULL DEFAULT 0 CHECK (armor_front >= 0),
  armor_rear   INTEGER,
  internal     INTEGER NOT NULL DEFAULT 0 CHECK (internal >= 0),
  PRIMARY KEY (mech_id, loc)
);

CREATE TABLE IF NOT EXISTS mech_weapon (
  mech_id    BIGINT NOT NULL REFERENCES mech(id) ON DELETE CASCADE,
  weapon_id  BIGINT NOT NULL REFERENCES weapon_catalog(id),
  "count"    INTEGER NOT NULL CHECK ("count" >= 1),
  PRIMARY KEY (mech_id, weapon_id)
);

CREATE TABLE IF NOT EXISTS mech_equipment (
  mech_id       BIGINT NOT NULL REFERENCES mech(id) ON DELETE CASCADE,
  equipment_id  BIGINT NOT NULL REFERENCES equipment_catalog(id),
  "count"       INTEGER NOT NULL CHECK ("count" >= 1),
  PRIMARY KEY (mech_id, equipment_id)
);

CREATE TABLE IF NOT EXISTS mech_ammo_bin (
  mech_id   BIGINT NOT NULL REFERENCES mech(id) ON DELETE CASCADE,
  ammo_id   BIGINT NOT NULL REFERENCES ammo_catalog(id),
  loc       location NOT NULL,
  tons      NUMERIC(4,1) NOT NULL CHECK (tons > 0),
  PRIMARY KEY (mech_id, ammo_id, loc)
);

CREATE TABLE IF NOT EXISTS mech_crit_slot (
  mech_id       BIGINT NOT NULL REFERENCES mech(id) ON DELETE CASCADE,
  loc           location NOT NULL,
  slot_index    INTEGER NOT NULL CHECK (slot_index >= 1),
  item_type     crit_item_type NOT NULL,
  weapon_id     BIGINT REFERENCES weapon_catalog(id),
  equipment_id  BIGINT REFERENCES equipment_catalog(id),
  ammo_id       BIGINT REFERENCES ammo_catalog(id),
  display_name  TEXT,
  PRIMARY KEY (mech_id, loc, slot_index)
);

CREATE TABLE IF NOT EXISTS mech_quirk (
  mech_id  BIGINT NOT NULL REFERENCES mech(id) ON DELETE CASCADE,
  quirk    TEXT NOT NULL,
  PRIMARY KEY (mech_id, quirk)
);

CREATE TABLE IF NOT EXISTS mech_manufacturer (
  mech_id  BIGINT NOT NULL REFERENCES mech(id) ON DELETE CASCADE,
  system   TEXT NOT NULL,
  name     TEXT NOT NULL,
  PRIMARY KEY (mech_id, system)
);
