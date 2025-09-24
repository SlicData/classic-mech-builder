#!/usr/bin/env python3
"""
Integration test for MTF parser and database seeder
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from mtf_parser import MTFParser
from database import DatabaseSeeder

def test_parsing():
    """Test parsing the sample MTF file"""
    print("=== Testing MTF Parser ===")
    
    # Initialize parser
    parser = MTFParser()
    
    # Parse test file
    test_file = Path(__file__).parent.parent / "data" / "test_mech.mtf"
    if not test_file.exists():
        print(f"ERROR: Test file {test_file} not found")
        return False
    
    print(f"Parsing {test_file}...")
    mech_data = parser.parse_mtf_file(test_file)
    
    if not mech_data:
        print("ERROR: Failed to parse MTF file")
        return False
    
    # Print parsed data
    print(f"✓ Parsed: {mech_data.chassis} {mech_data.model}")
    print(f"  Tonnage: {mech_data.tonnage}")
    print(f"  Movement: Walk={mech_data.walk_mp}, Run={mech_data.run_mp}, Jump={mech_data.jump_mp}")
    print(f"  Weapons: {len(mech_data.weapons)}")
    
    for weapon in mech_data.weapons:
        print(f"    {weapon.name} x{weapon.count} in {weapon.location}")
    
    print(f"  Armor: Total={mech_data.armor.total_armor}")
    print(f"  Crit slots: {len(mech_data.crit_slots)}")
    
    return True

def test_database():
    """Test database connection and seeding"""
    print("\n=== Testing Database Seeder ===")
    
    try:
        # Initialize database
        db = DatabaseSeeder('cmb_dev')
        db.connect()
        print("✓ Connected to database")
        
        # Parse test mech
        parser = MTFParser()
        test_file = Path(__file__).parent.parent / "data" / "test_mech.mtf"
        mech_data = parser.parse_mtf_file(test_file)
        
        if not mech_data:
            print("ERROR: Failed to parse test mech")
            return False
        
        # Try to insert
        print(f"Inserting {mech_data.chassis} {mech_data.model}...")
        success = db.insert_mech(mech_data)
        
        if success:
            print("✓ Successfully inserted mech data")
        else:
            print("ERROR: Failed to insert mech data")
            return False
        
        # Check table counts
        print("\nTable counts:")
        cursor = db.connection.cursor()
        
        tables = ['mech', 'weapon_catalog', 'mech_weapon', 'mech_armor', 'mech_equipment', 'mech_crit_slot']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count}")
        
        cursor.close()
        db.close()
        
        return True
        
    except Exception as e:
        print(f"ERROR: Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run integration tests"""
    print("Starting MTF Seeder Integration Test")
    print("=" * 40)
    
    # Test parsing
    if not test_parsing():
        print("FAILED: Parsing test failed")
        return False
    
    # Test database
    if not test_database():
        print("FAILED: Database test failed")
        return False
    
    print("\n" + "=" * 40)
    print("SUCCESS: All integration tests passed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
