#!/usr/bin/env python3
"""
Test the new modular MTF parser structure
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_imports():
    """Test that all modules import correctly"""
    try:
        from mtf_parser import MTFParser, MovementParser, WeaponParser
        from database import DatabaseSeeder
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_parser():
    """Test basic parser functionality"""
    try:
        from mtf_parser import MTFParser
        parser = MTFParser()
        print("✅ MTF Parser created successfully")
        return True
    except Exception as e:
        print(f"❌ Parser creation failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing Modular Structure ===")
    
    success = True
    success &= test_imports()
    success &= test_parser()
    
    if success:
        print("\n✅ Modular structure working correctly!")
        print("Ready for CMB-20 Step 3!")
    else:
        print("\n❌ Issues with modular structure")
