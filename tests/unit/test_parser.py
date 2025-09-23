#!/usr/bin/env python3
"""
Quick test of MTF parser functionality
"""

import sys
import os
from pathlib import Path

# Add the seeds directory to the path
sys.path.insert(0, os.path.join(os.getcwd(), 'db', 'seeds'))

from mtf_seeder import MTFParser

def main():
    parser = MTFParser()
    
    # Test with our test file
    test_file = Path('data/test_mech.mtf')
    if test_file.exists():
        print(f"Parsing test file: {test_file}")
        mech_data = parser.parse_mtf_file(test_file)
        
        if mech_data:
            print(f"✓ Successfully parsed: {mech_data.chassis} {mech_data.model}")
            print(f"  Tonnage: {mech_data.tonnage}")
            print(f"  Tech Base: {mech_data.tech_base.value}")
            print(f"  Era: {mech_data.era.value}")
            print(f"  Walk MP: {mech_data.walk_mp}")
            print(f"  Run MP: {mech_data.run_mp}")
            print(f"  Jump MP: {mech_data.jump_mp}")
            print(f"  Weapons: {len(mech_data.weapons)}")
            print(f"  Armor locations: {len(mech_data.armor)}")
            print(f"  Equipment: {len(mech_data.equipment)}")
            print(f"  Crit slots: {len(mech_data.crit_slots)}")
            
            if mech_data.weapons:
                print("  Weapons found:")
                for weapon in mech_data.weapons:
                    print(f"    - {weapon.name} in {weapon.location}")
            
            if mech_data.armor:
                print("  Armor found:")
                for armor in mech_data.armor:
                    rear_text = f", {armor.armor_rear} rear" if armor.armor_rear else ""
                    print(f"    - {armor.location}: {armor.armor_front} front{rear_text}, {armor.internal} internal")
            
            if mech_data.equipment:
                print("  Equipment found:")
                for equip in mech_data.equipment:
                    print(f"    - {equip.name} in {equip.location}")
        else:
            print("✗ Failed to parse test file")
    else:
        print(f"Test file not found: {test_file}")

if __name__ == "__main__":
    main()
