#!/usr/bin/env python3
"""
Test CMB-20 Step 5: Critical Slot Parsing - TDD Approach
🔴 RED PHASE: Write failing tests first to define requirements
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_crit_slot_parser_exists():
    """Test that critical slot parser module can be imported"""
    try:
        from mtf_parser.crit_slot_parser import CritSlotParser
        print("✅ CritSlotParser class imported successfully")
        return True
    except ImportError:
        print("❌ CritSlotParser class not found - need to create it")
        return False

def test_crit_slot_parsing():
    """Test critical slot parsing functionality - should fail initially"""
    
    # Sample MTF content with critical slot data
    atlas_crit_slots = """
chassis:Atlas
model:AS7-D

Left Arm:
Shoulder
Upper Arm Actuator
Lower Arm Actuator
Hand Actuator
Heat Sink
Heat Sink
Autocannon/20
Autocannon/20
Autocannon/20
Autocannon/20
Autocannon/20 Ammo
LRM 20 Ammo

Right Arm:
Shoulder
Upper Arm Actuator
Lower Arm Actuator
Hand Actuator
Heat Sink
Heat Sink
LRM 20
LRM 20
LRM 20
LRM 20
LRM 20
SRM 6
"""
    
    try:
        from mtf_parser.crit_slot_parser import CritSlotParser
        import logging
        
        logger = logging.getLogger(__name__)
        crit_parser = CritSlotParser(logger)
        
        # Test critical slot parsing
        crit_slots = crit_parser.parse_critical_slots(atlas_crit_slots)
        
        if crit_slots and len(crit_slots) > 0:
            print(f"✅ Critical slots parsed: {len(crit_slots)} total")
            
            # Check for expected locations
            locations_found = set(slot.location for slot in crit_slots)
            expected_locations = {'LA', 'RA'}  # Left Arm, Right Arm
            
            if expected_locations.issubset(locations_found):
                print(f"✅ Expected locations found: {locations_found}")
            else:
                print(f"❌ Missing expected locations: expected {expected_locations}, found {locations_found}")
                return False
            
            # Check for expected equipment
            equipment_found = [slot.equipment_name for slot in crit_slots if slot.equipment_name != "Empty"]
            if "Autocannon/20" in equipment_found and "LRM 20" in equipment_found:
                print(f"✅ Expected equipment found: AC/20, LRM 20")
            else:
                print(f"❌ Expected equipment not found in: {equipment_found}")
                return False
                
            return True
        else:
            print("❌ No critical slot data returned")
            return False
            
    except Exception as e:
        print(f"❌ Critical slot parsing test failed: {e}")
        return False

def test_crit_slot_validation():
    """Test critical slot validation - should fail initially"""
    
    try:
        from mtf_parser.crit_slot_parser import CritSlotParser
        import logging
        
        logger = logging.getLogger(__name__)
        crit_parser = CritSlotParser(logger)
        
        # Test validation logic
        # Atlas LA should have 12 slots
        test_slots = [
            {"location": "LA", "slot": 1, "equipment": "Shoulder"},
            {"location": "LA", "slot": 2, "equipment": "Upper Arm Actuator"},
            # ... more slots
        ]
        
        is_valid = crit_parser.validate_critical_slots("LA", test_slots)
        
        if isinstance(is_valid, bool):
            print(f"✅ Critical slot validation working: {is_valid}")
            return True
        else:
            print("❌ Critical slot validation not returning boolean")
            return False
            
    except Exception as e:
        print(f"❌ Critical slot validation test failed: {e}")
        return False

def test_equipment_classification():
    """Test equipment classification functionality"""
    
    try:
        from mtf_parser.crit_slot_parser import CritSlotParser
        import logging
        
        logger = logging.getLogger(__name__)
        crit_parser = CritSlotParser(logger)
        
        # Test equipment classification
        test_cases = [
            ("Autocannon/20", "weapon"),
            ("Heat Sink", "heat_sink"),
            ("Shoulder", "actuator"),
            ("CASE", "equipment"),
            ("Empty", "empty"),
        ]
        
        for equipment, expected_type in test_cases:
            equipment_type = crit_parser.classify_equipment(equipment)
            if equipment_type == expected_type:
                print(f"✅ {equipment} classified as {equipment_type}")
            else:
                print(f"❌ {equipment} classified as {equipment_type}, expected {expected_type}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Equipment classification test failed: {e}")
        return False

def test_slot_count_validation():
    """Test that we can validate slot counts for different locations"""
    
    try:
        from mtf_parser.crit_slot_parser import CritSlotParser
        import logging
        
        logger = logging.getLogger(__name__)
        crit_parser = CritSlotParser(logger)
        
        # Test slot count validation for different locations
        test_cases = [
            ("HD", 6),   # Head has 6 slots
            ("CT", 12),  # Center Torso has 12 slots  
            ("LA", 12),  # Left Arm has 12 slots
            ("LL", 6),   # Left Leg has 6 slots
        ]
        
        for location, expected_count in test_cases:
            max_slots = crit_parser.get_max_slots_for_location(location)
            if max_slots == expected_count:
                print(f"✅ {location} max slots: {max_slots}")
            else:
                print(f"❌ {location} max slots: {max_slots}, expected {expected_count}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Slot count validation test failed: {e}")
        return False

def test_integration_with_main_parser():
    """Test that crit slot parser integrates with main MTF parser"""
    
    try:
        from mtf_parser import MTFParser
        
        parser = MTFParser()
        
        if hasattr(parser, 'crit_slot_parser'):
            print("✅ Critical slot parser integrated with main MTF parser")
            return True
        else:
            print("❌ Critical slot parser not integrated with main parser")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== TDD Step 5: Critical Slot Parsing ===")
    print("🔴 RED PHASE: Running tests that should fail\n")
    
    test_results = []
    
    print("1. Testing CritSlotParser import...")
    test_results.append(test_crit_slot_parser_exists())
    
    print("\n2. Testing critical slot parsing...")
    test_results.append(test_crit_slot_parsing())
    
    print("\n3. Testing critical slot validation...")
    test_results.append(test_crit_slot_validation())
    
    print("\n4. Testing equipment classification...")
    test_results.append(test_equipment_classification())
    
    print("\n5. Testing slot count validation...")
    test_results.append(test_slot_count_validation())
    
    print("\n6. Testing integration...")
    test_results.append(test_integration_with_main_parser())
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"\n=== TDD RED PHASE RESULTS ===")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == 0:
        print("🔴 PERFECT! All tests failing as expected in RED phase")
        print("✅ Ready to write minimum code to make tests pass (GREEN phase)")
    elif passed < total:
        print("🟡 Some tests passing, some failing - good for TDD")
        print("✅ Ready to implement missing functionality")
    else:
        print("🟢 All tests passing - either we already have the code or tests are wrong")
    
    print("\n🎯 REQUIREMENTS DEFINED BY TESTS:")
    print("📋 Parse critical slot sections from MTF files")
    print("📋 Extract equipment placement in each location") 
    print("📋 Classify equipment types (weapons, heat sinks, actuators)")
    print("📋 Validate slot counts against BattleTech limits")
    print("📋 Integrate with existing modular parser")
    
    print("\nNext: Implement CritSlotParser to make these tests pass! 🚀")
