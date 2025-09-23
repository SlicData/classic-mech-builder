-- CMB-20: Rollback engine type additions
-- This removes the added engine types (BE CAREFUL - will fail if data exists)

-- Remove the added engine types
-- WARNING: This will fail if any mech records use these engine types
ALTER TYPE engine_type DROP VALUE IF EXISTS 'xxl_fusion';
ALTER TYPE engine_type DROP VALUE IF EXISTS 'fuel_cell';
