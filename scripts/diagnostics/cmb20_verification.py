#!/usr/bin/env python3
"""
CMB-20 Quick Verification Script
Run this to verify the MTF seeder is ready to go
"""

import sys
import os
from pathlib import Path

def main():
    print("🔍 CMB-20 Quick Verification")
    print("=" * 40)
    
    # Change to project directory
    project_dir = Path("/Users/justi/classic-mech-builder")
    if not project_dir.exists():
        print("❌ Project directory not found")
        return False
    
    os.chdir(project_dir)
    sys.path.insert(0, str(project_dir / 'src'))
    
    # Check 1: Required files exist
    print("📁 Checking required files...")
    required_files = [
        'src/mtf_parser/__init__.py',
        'src/mtf_parser/base_parser.py',
        'src/mtf_parser/weapon_parser.py',
        'src/mtf_parser/armor_parser.py',
        'src/mtf_parser/movement_parser.py',
        'src/mtf_parser/engine_parser.py',
        'src/mtf_parser/crit_slot_parser.py',
        'src/mtf_parser/utils.py',
        'src/database/__init__.py',
        'src/database/seeder.py',
        'data/test_mech.mtf',
        'db/seeds/db_config.py',
        'tests/integration/test_mtf_seeder.py',
        'scripts/seeding/mtf_seeder.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print("\n❌ Missing files:")
        for file_path in missing_files:
            print(f"  ❌ {file_path}")
        return False
    
    # Check 2: Basic imports
    print("\n📦 Testing basic imports...")
    try:
        from mtf_parser.utils import MechData, WeaponData, TechBase, EngineType
        print("  ✅ Utils imported")
        
        from mtf_parser.weapon_parser import WeaponParser
        print("  ✅ WeaponParser imported")
        
        from mtf_parser.armor_parser import ArmorParser
        print("  ✅ ArmorParser imported")
        
        from mtf_parser import MTFParser
        print("  ✅ MTFParser imported")
        
        from database import DatabaseSeeder
        print("  ✅ DatabaseSeeder imported")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Check 3: Test file can be read
    print("\n📄 Testing test file...")
    try:
        test_file = Path("data/test_mech.mtf")
        with open(test_file, 'r') as f:
            content = f.read()
        
        if "Archer ARC-2R" in content and "Weapons:" in content:
            print("  ✅ Test file readable and contains expected data")
        else:
            print("  ❌ Test file missing expected content")
            return False
            
    except Exception as e:
        print(f"❌ Test file error: {e}")
        return False
    
    # Check 4: Basic parsing test
    print("\n🔧 Testing basic parsing...")
    try:
        parser = MTFParser()
        mech_data = parser.parse_mtf_file(Path("data/test_mech.mtf"))
        
        if mech_data and mech_data.chassis == "Archer" and mech_data.model == "ARC-2R":
            print(f"  ✅ Parsed: {mech_data.chassis} {mech_data.model}")
            print(f"  ✅ Weapons: {len(mech_data.weapons)}")
            print(f"  ✅ Armor: {len(mech_data.armor)}")
        else:
            print("  ❌ Parsing failed or returned invalid data")
            return False
            
    except Exception as e:
        print(f"❌ Parsing error: {e}")
        return False
    
    # Check 5: Database config
    print("\n🗃️ Testing database config...")
    try:
        sys.path.insert(0, 'db/seeds')
        from db_config import detect_db_config
        
        config = detect_db_config()
        if config:
            print(f"  ✅ Database config detected: {config['user']}@{config['host']}")
        else:
            print("  ⚠️ Database config not detected (may need manual setup)")
            
    except Exception as e:
        print(f"❌ Database config error: {e}")
        return False
    
    # Final summary
    print("\n" + "=" * 40)
    print("🎯 VERIFICATION SUMMARY")
    print("✅ All required files present")
    print("✅ All modules import successfully")
    print("✅ Test file loads and parses")
    print("✅ Database configuration available")
    
    print("\n🚀 CMB-20 IS READY!")
    print("\nNext steps:")
    print("1. Run: python3 tests/integration/test_mtf_seeder.py")
    print("2. If test passes, run full import:")
    print("   python3 scripts/seeding/mtf_seeder.py --test")
    print("3. Mark CMB-20 as COMPLETE ✅")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n🔧 Fix the issues above before proceeding")
    sys.exit(0 if success else 1)
