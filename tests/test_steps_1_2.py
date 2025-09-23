#!/usr/bin/env python3
"""
Simple test for CMB-20 Steps 1 & 2
"""

import sys
sys.path.append('/Users/justi/classic-mech-builder/db/seeds')

from mtf_seeder import MTFParser
from pathlib import Path

def test_parsing():
    parser = MTFParser()
    
    # Test King Crab
    file_path = Path('/Users/justi/classic-mech-builder/data/megamek/data/mechfiles/3039u/King Crab KGC-0000.mtf')
    
    if file_path.exists():
        print("=== Testing King Crab KGC-0000 ===")
        mech = parser.parse_mtf_file(file_path)
        
        if mech:
            print(f"✅ {mech.chassis} {mech.model}")
            print(f"Movement: Walk={mech.walk_mp}, Run={mech.run_mp}, Jump={mech.jump_mp}")
            print(f"Weapons: {len(mech.weapons)} total")
            
            for weapon in mech.weapons:
                print(f"  {weapon.name} x{weapon.count} in {weapon.location}")
        else:
            print("❌ Failed to parse")
    else:
        print("❌ File not found")

if __name__ == "__main__":
    test_parsing()
