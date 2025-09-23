#!/usr/bin/env python3
"""
Check database enum values
"""

import sys
import os
from pathlib import Path

os.chdir('/Users/justi/classic-mech-builder')
sys.path.insert(0, 'src')

try:
    from database import DatabaseSeeder
    
    print("🔍 Checking database enum values...")
    db = DatabaseSeeder('cmb_dev')
    db.connect()
    
    cursor = db.connection.cursor()
    
    # Check crit_item_type enum values
    cursor.execute("""
        SELECT enumlabel 
        FROM pg_enum 
        WHERE enumtypid = (
            SELECT oid FROM pg_type WHERE typname = 'crit_item_type'
        )
        ORDER BY enumsortorder
    """)
    
    enum_values = cursor.fetchall()
    print("Valid crit_item_type enum values:")
    for (value,) in enum_values:
        print(f"  - '{value}'")
    
    # Check what tables exist
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE 'mech%'
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    print("\nMech-related tables:")
    for (table,) in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  - {table}: {count} records")
    
    cursor.close()
    db.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
