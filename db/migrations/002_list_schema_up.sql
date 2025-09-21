-- CMB-8: List schema for user-created mech lists

-- Lists table for user-created collections
CREATE TABLE IF NOT EXISTS list (
  id            BIGSERIAL PRIMARY KEY,
  name          TEXT NOT NULL,
  owner         TEXT NOT NULL,
  faction       TEXT,
  notes         TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  
  -- Ensure list names are unique per owner
  UNIQUE (owner, name)
);

-- Junction table for list-mech relationships
CREATE TABLE IF NOT EXISTS list_mech (
  list_id   BIGINT NOT NULL REFERENCES list(id) ON DELETE CASCADE,
  mech_id   BIGINT NOT NULL REFERENCES mech(id) ON DELETE CASCADE,
  quantity  INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
  
  PRIMARY KEY (list_id, mech_id)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_list_owner ON list (owner);
CREATE INDEX IF NOT EXISTS idx_list_created_at ON list (created_at);
CREATE INDEX IF NOT EXISTS idx_list_mech_list_id ON list_mech (list_id);
CREATE INDEX IF NOT EXISTS idx_list_mech_mech_id ON list_mech (mech_id);

-- Updated at trigger for lists
DROP TRIGGER IF EXISTS list_set_updated_at ON list;
CREATE TRIGGER list_set_updated_at
BEFORE UPDATE ON list
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
