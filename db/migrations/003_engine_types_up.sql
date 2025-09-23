-- CMB-20: Update engine_type enum to support all MegaMek engine types
-- Run this after 001_init_up.sql if needed

-- Add missing engine types to the enum
DO $$ 
BEGIN
    -- Add xxl_fusion if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum e 
        JOIN pg_type t ON e.enumtypid = t.oid 
        WHERE t.typname = 'engine_type' AND e.enumlabel = 'xxl_fusion'
    ) THEN
        ALTER TYPE engine_type ADD VALUE 'xxl_fusion';
    END IF;
    
    -- Add fuel_cell if it doesn't exist  
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum e 
        JOIN pg_type t ON e.enumtypid = t.oid 
        WHERE t.typname = 'engine_type' AND e.enumlabel = 'fuel_cell'
    ) THEN
        ALTER TYPE engine_type ADD VALUE 'fuel_cell';
    END IF;
END $$;
