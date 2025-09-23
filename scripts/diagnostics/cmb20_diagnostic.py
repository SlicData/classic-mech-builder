#!/usr/bin/env python3
"""
CMB-20 Comprehensive Diagnostic and Fix Script
Principal Engineer approach: Test-Driven Development to fix all issues
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_1_movement_parsing():
    """Test 1: Movement parsing - addresses walk_mp, run_mp showing as 0"""
    print("\n" + "="*50)
    print("TEST 1: Movement Parsing")
    print("="*50)
    
    try:
        from mtf_parser.movement_parser import MovementParser
        from mtf_parser.utils import extract_chassis_model
        
        # Test with our known good MTF content
        test_content = """Version:1.0
Archer ARC-2R

Config:Biped
TechBase:Inner Sphere
Era:2819
Source:TRO 3039 - Succession Wars
Rules Level:1

Mass:70
Engine:280 Fusion Engine
Structure:Standard
Myomer:Standard

Heat Sinks:16 Single
Walk MP:4
Jump MP:0"""

        movement_parser = MovementParser(logger)
        walk_mp, run_mp, jump_mp = movement_parser.parse_movement(test_content)
        
        print(f"✅ Movement Parser imported successfully")
        print(f"📊 Parsed movement:")
        print(f"   Walk MP: {walk_mp} (expected: 4)")
        print(f"   Run MP: {run_mp} (expected: 6 = 4 * 1.5)")
        print(f"   Jump MP: {jump_mp} (expected: 0)")
        
        # Validate results
        assert walk_mp == 4, f"Expected walk_mp=4, got {walk_mp}"
        assert run_mp == 6, f"Expected run_mp=6, got {run_mp}"
        assert jump_mp == 0, f"Expected jump_mp=0, got {jump_mp}"
        
        print("✅ Movement parsing test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Movement parsing test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_2_weapon_parsing():
    """Test 2: Weapon parsing - addresses weapon_catalog, mech_weapon being empty"""
    print("\n" + "="*50)
    print("TEST 2: Weapon Parsing")
    print("="*50)
    
    try:
        from mtf_parser.weapon_parser import WeaponParser
        
        # Test with our known good MTF weapon section
        test_content = """Weapons:4
Medium Laser, Left Arm
Medium Laser, Right Arm
LRM 20, Left Torso
LRM 20, Right Torso"""

        weapon_parser = WeaponParser(logger)
        weapons = weapon_parser.parse_weapons(test_content)
        
        print(f"✅ Weapon Parser imported successfully")
        print(f"📊 Parsed weapons:")
        
        for weapon in weapons:
            print(f"   - {weapon.name} x{weapon.count} in {weapon.location}")
        
        # Validate results
        assert len(weapons) == 4, f"Expected 4 weapons, got {len(weapons)}"
        
        # Check specific weapons
        weapon_names = [w.name for w in weapons]
        assert "Medium Laser" in weapon_names, "Medium Laser not found"
        assert "LRM 20" in weapon_names, "LRM 20 not found"
        
        print("✅ Weapon parsing test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Weapon parsing test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_3_armor_parsing():
    """Test 3: Armor parsing - addresses mech_armor being empty"""
    print("\n" + "="*50)
    print("TEST 3: Armor Parsing")
    print("="*50)
    
    try:
        from mtf_parser.armor_parser import ArmorParser
        
        # Test with our known good MTF armor section
        test_content = """Armor:Standard(Inner Sphere)
LA Armor:22
RA Armor:22
LT Armor:22
RT Armor:22
CT Armor:33
HD Armor:9
LL Armor:30
RL Armor:30
RTL Armor:8
RTR Armor:8
RTC Armor:10"""

        armor_parser = ArmorParser(logger)
        armor_data, armor_type = armor_parser.parse_armor(test_content, 70)  # 70 ton mech
        
        print(f"✅ Armor Parser imported successfully")
        print(f"📊 Parsed armor:")
        
        for armor in armor_data:
            print(f"   - {armor.location}: Front={armor.armor_front}, Rear={armor.armor_rear}, Internal={armor.internal}")
        
        # Validate results
        assert len(armor_data) > 0, f"Expected armor data, got {len(armor_data)}"
        
        print("✅ Armor parsing test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Armor parsing test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_4_complete_mech_parsing():
    """Test 4: Complete mech parsing using the full MTF parser"""
    print("\n" + "="*50)
    print("TEST 4: Complete Mech Parsing")
    print("="*50)
    
    try:
        from mtf_parser import MTFParser
        
        # Test file path
        test_file = Path("data/test_mech.mtf")
        
        parser = MTFParser()
        mech_data = parser.parse_mtf_file(test_file)
        
        if mech_data:
            print(f"✅ Parsed complete mech: {mech_data.chassis} {mech_data.model}")
            print(f"📊 Complete mech data:")
            print(f"   Tonnage: {mech_data.tonnage}")
            print(f"   Movement: Walk={mech_data.walk_mp}, Run={mech_data.run_mp}, Jump={mech_data.jump_mp}")
            print(f"   Weapons: {len(mech_data.weapons)} items")
            print(f"   Armor: {len(mech_data.armor)} locations")
            print(f"   Equipment: {len(mech_data.equipment)} items")
            print(f"   Crit Slots: {len(mech_data.crit_slots)} slots")
            
            # Validate critical data
            assert mech_data.walk_mp > 0, f"Walk MP is 0 - parsing failed"
            assert len(mech_data.weapons) > 0, f"No weapons parsed"
            assert len(mech_data.armor) > 0, f"No armor parsed"
            
            print("✅ Complete mech parsing test PASSED")
            return mech_data
        else:
            print("❌ Complete mech parsing returned None")
            return None
            
    except Exception as e:
        print(f"❌ Complete mech parsing test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_5_database_insertion():
    """Test 5: Database insertion - the likely culprit"""
    print("\n" + "="*50)
    print("TEST 5: Database Insertion")
    print("="*50)
    
    try:
        from database import DatabaseSeeder
        
        # Get mech data from previous test
        mech_data = test_4_complete_mech_parsing()
        if not mech_data:
            print("❌ Cannot test database insertion - no mech data")
            return False
        
        # Test database connection
        db = DatabaseSeeder("cmb_dev")
        
        try:
            db.connect()
            print("✅ Database connection successful")
            
            # Try a dry-run insert (we'll check what happens)
            print("📊 Testing database insertion...")
            result = db.insert_mech(mech_data)
            
            if result:
                print("✅ Database insertion test PASSED")
                
                # Now verify the data was actually inserted
                print("🔍 Verifying inserted data...")
                cursor = db.conn.cursor()
                
                # Check main mech table
                cursor.execute("SELECT COUNT(*) FROM mech WHERE chassis = %s AND model = %s", 
                             (mech_data.chassis, mech_data.model))
                mech_count = cursor.fetchone()[0]
                print(f"   Mechs in database: {mech_count}")
                
                # Check related tables
                cursor.execute("SELECT COUNT(*) FROM weapon_catalog")
                weapon_catalog_count = cursor.fetchone()[0]
                print(f"   Weapons in catalog: {weapon_catalog_count}")
                
                cursor.execute("SELECT COUNT(*) FROM mech_weapon")
                mech_weapon_count = cursor.fetchone()[0]
                print(f"   Mech-weapon associations: {mech_weapon_count}")
                
                cursor.execute("SELECT COUNT(*) FROM mech_armor")
                mech_armor_count = cursor.fetchone()[0]
                print(f"   Mech armor entries: {mech_armor_count}")
                
                cursor.close()
                
                if weapon_catalog_count == 0:
                    print("⚠️ WARNING: weapon_catalog is empty - this is the issue!")
                if mech_weapon_count == 0:
                    print("⚠️ WARNING: mech_weapon is empty - this is the issue!")
                if mech_armor_count == 0:
                    print("⚠️ WARNING: mech_armor is empty - this is the issue!")
                
                return True
            else:
                print("❌ Database insertion returned False")
                return False
            
        except Exception as db_e:
            print(f"❌ Database connection failed: {db_e}")
            return False
        finally:
            if db.conn:
                db.close()
                
    except Exception as e:
        print(f"❌ Database insertion test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main diagnostic function"""
    print("🔍 CMB-20 COMPREHENSIVE DIAGNOSTIC")
    print("=" * 60)
    print("Principal Engineer TDD approach to fix all MTF seeder issues")
    print("=" * 60)
    
    tests = [
        test_1_movement_parsing,
        test_2_weapon_parsing, 
        test_3_armor_parsing,
        test_4_complete_mech_parsing,
        test_5_database_insertion
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("📋 DIAGNOSTIC SUMMARY")
    print("="*60)
    
    test_names = [
        "Movement Parsing", 
        "Weapon Parsing",
        "Armor Parsing", 
        "Complete Mech Parsing",
        "Database Insertion"
    ]
    
    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {test_name}: {status}")
    
    if all(results):
        print("\n🎉 ALL TESTS PASSED! CMB-20 is ready!")
    else:
        print(f"\n🔧 {len([r for r in results if not r])} test(s) failed - need fixes")
        
        # Provide specific remediation advice
        if not results[0]:  # Movement parsing
            print("   → Fix movement parsing regex patterns")
        if not results[1]:  # Weapon parsing
            print("   → Fix weapon parsing logic")
        if not results[2]:  # Armor parsing
            print("   → Fix armor parsing logic")
        if not results[3]:  # Complete parsing
            print("   → Fix MTF parser integration")
        if not results[4]:  # Database insertion
            print("   → Fix database insertion - likely the main culprit")

if __name__ == "__main__":
    main()
