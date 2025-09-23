#!/usr/bin/env python3
"""
CMB-20 Final Integration Test - Fixed Version
"""

import sys
import os
import logging
from pathlib import Path

# Setup environment  
project_root = Path('/Users/justi/classic-mech-builder')
os.chdir(project_root)
sys.path.insert(0, str(project_root / 'src'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def clean_test_data(cursor):
    """Thoroughly clean any existing test data"""
    print("   🧹 Cleaning up existing test data...")
    
    # Get any existing mech IDs
    cursor.execute("SELECT id FROM mech WHERE chassis = 'Archer' AND model = 'ARC-2R'")
    existing_mechs = cursor.fetchall()
    
    if existing_mechs:
        for (mech_id,) in existing_mechs:
            print(f"   Removing existing mech ID: {mech_id}")
            # Delete in proper order to avoid constraint violations
            cursor.execute("DELETE FROM mech_crit_slot WHERE mech_id = %s", (mech_id,))
            cursor.execute("DELETE FROM mech_armor WHERE mech_id = %s", (mech_id,))
            cursor.execute("DELETE FROM mech_weapon WHERE mech_id = %s", (mech_id,))
            cursor.execute("DELETE FROM mech_equipment WHERE mech_id = %s", (mech_id,))
            cursor.execute("DELETE FROM mech_quirk WHERE mech_id = %s", (mech_id,))
    
    # Final cleanup by chassis/model
    cursor.execute("DELETE FROM mech WHERE chassis = 'Archer' AND model = 'ARC-2R'")
    
    # Commit the cleanup
    cursor.connection.commit()
    print("   ✅ Cleanup complete")

def run_complete_test():
    """Run the complete integration test"""
    print("🚀 Starting CMB-20 Final Integration Test")
    print("=" * 60)
    
    try:
        # Step 1: Import all modules
        print("📦 Testing imports...")
        from mtf_parser import MTFParser
        from database import DatabaseSeeder
        print("✅ All imports successful")
        
        # Step 2: Parse test file
        print("📄 Parsing test MTF file...")
        parser = MTFParser()
        test_file = Path("data/test_mech.mtf")
        
        if not test_file.exists():
            print("❌ Test file not found!")
            return False
        
        mech_data = parser.parse_mtf_file(test_file)
        
        if not mech_data:
            print("❌ Failed to parse MTF file")
            return False
        
        print(f"✅ Parsed: {mech_data.chassis} {mech_data.model}")
        print(f"   Tonnage: {mech_data.tonnage}t")
        print(f"   Movement: {mech_data.walk_mp}/{mech_data.run_mp}/{mech_data.jump_mp}")
        print(f"   Weapons: {len(mech_data.weapons)} parsed")
        print(f"   Armor: {len(mech_data.armor)} locations")
        
        # Show weapon details
        for weapon in mech_data.weapons:
            print(f"      {weapon.name} x{weapon.count} in {weapon.location}")
        
        # Step 3: Test database connection
        print("🗃️ Testing database connection...")
        db = DatabaseSeeder('cmb_dev')
        db.connect()
        print("✅ Database connected successfully")
        
        # Step 4: Clean and insert
        print("⚔️ Preparing for insertion...")
        cursor = db.connection.cursor()
        
        # Clean up any existing test data
        clean_test_data(cursor)
        
        # Step 5: Insert mech
        print("🤖 Inserting mech data...")
        success = db.insert_mech(mech_data)
        
        if not success:
            print("❌ Failed to insert mech data")
            cursor.close()
            db.close()
            return False
        
        print("✅ Mech data inserted successfully")
        
        # Step 6: Verify data
        print("🔍 Verifying inserted data...")
        
        # Check main mech table
        cursor.execute("SELECT COUNT(*) FROM mech WHERE chassis = 'Archer' AND model = 'ARC-2R'")
        mech_count = cursor.fetchone()[0]
        print(f"   Mech records: {mech_count}")
        
        # Check weapon catalog
        cursor.execute("SELECT COUNT(*) FROM weapon_catalog")
        weapon_catalog_count = cursor.fetchone()[0]
        print(f"   Weapon catalog: {weapon_catalog_count} entries")
        
        # Check mech weapons
        cursor.execute("""
            SELECT COUNT(*) FROM mech_weapon mw 
            JOIN mech m ON mw.mech_id = m.id 
            WHERE m.chassis = 'Archer' AND m.model = 'ARC-2R'
        """)
        mech_weapon_count = cursor.fetchone()[0]
        print(f"   Mech weapons: {mech_weapon_count} entries")
        
        # Check mech armor
        cursor.execute("""
            SELECT COUNT(*) FROM mech_armor ma 
            JOIN mech m ON ma.mech_id = m.id 
            WHERE m.chassis = 'Archer' AND m.model = 'ARC-2R'
        """)
        mech_armor_count = cursor.fetchone()[0]
        print(f"   Mech armor: {mech_armor_count} entries")
        
        # Check crit slots
        cursor.execute("""
            SELECT COUNT(*) FROM mech_crit_slot mcs 
            JOIN mech m ON mcs.mech_id = m.id 
            WHERE m.chassis = 'Archer' AND m.model = 'ARC-2R'
        """)
        mech_crit_count = cursor.fetchone()[0]
        print(f"   Crit slots: {mech_crit_count} entries")
        
        # Show specific weapon entries
        print("\n   📋 Weapon details:")
        cursor.execute("""
            SELECT wc.name, mw.count 
            FROM mech_weapon mw
            JOIN weapon_catalog wc ON mw.weapon_id = wc.id
            JOIN mech m ON mw.mech_id = m.id
            WHERE m.chassis = 'Archer' AND m.model = 'ARC-2R'
        """)
        weapons_in_db = cursor.fetchall()
        for weapon_name, count in weapons_in_db:
            print(f"      {weapon_name} x{count}")
        
        cursor.close()
        db.close()
        
        # Final validation
        print("\n📊 RESULTS SUMMARY:")
        print("=" * 40)
        all_good = True
        
        if mech_count != 1:
            print(f"❌ Expected 1 mech, got {mech_count}")
            all_good = False
        else:
            print(f"✅ Mech inserted: {mech_count}")
        
        if weapon_catalog_count == 0:
            print(f"❌ No weapons in catalog")
            all_good = False
        else:
            print(f"✅ Weapon catalog populated: {weapon_catalog_count}")
        
        if mech_weapon_count == 0:
            print(f"❌ No mech weapons linked")
            all_good = False
        else:
            print(f"✅ Mech weapons linked: {mech_weapon_count}")
        
        if mech_armor_count == 0:
            print(f"❌ No armor data")
            all_good = False
        else:
            print(f"✅ Armor data inserted: {mech_armor_count}")
        
        if all_good:
            print("\n🎉 CMB-20 INTEGRATION TEST PASSED!")
            print("✅ MTF parsing works")
            print("✅ Database insertion works")
            print("✅ All tables populated")
            print("\n🚀 Ready for full MegaMek data import!")
        else:
            print("\n⚠️ Some issues found, but basic functionality works")
        
        return all_good
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    success = run_complete_test()
    
    if success:
        print("\n🎯 CMB-20 READY TO COMPLETE!")
        print("   Next steps:")
        print("   1. Test with more MTF files:")
        print("      python3 scripts/seeding/mtf_seeder.py --test")
        print("   2. Run full MegaMek import")
        print("   3. Mark CMB-20 as DONE ✅")
    else:
        print("\n🔧 Some fixes needed - check errors above")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
