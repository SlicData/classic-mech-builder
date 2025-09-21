#!/usr/bin/env python3
"""
Test script to validate MTF parsing improvements
"""

import sys
sys.path.append('/Users/justi/classic-mech-builder/db/seeds')

from mtf_seeder import MTFParser
from pathlib import Path

def test_movement_parsing():
    """Test the movement parsing fixes"""
    
    # Sample MTF content with correct format
    test_content = """
chassis:King Crab
model:KGC-009C
techbase:Mixed (IS Chassis)
era:3143
rules level:2

mass:100
engine:300 Fusion Engine(IS)

heat sinks:14 IS Double
walk mp:3
jump mp:0

armor:Standard(Clan)
LA armor:34
RA armor:34
"""
    
    parser = MTFParser()
    
    # Test the individual parsing methods
    walk_mp = parser._parse_walk_mp(test_content)
    run_mp = parser._parse_run_mp(test_content)
    jump_mp = parser._parse_jump_mp(test_content)
    
    print("Movement Parsing Test Results:")
    print(f"Walk MP: {walk_mp} (expected: 3)")
    print(f"Run MP: {run_mp} (expected: 4-5 calculated from walk)")
    print(f"Jump MP: {jump_mp} (expected: 0)")
    
    # Test with an actual MTF file
    mtf_file = Path('/Users/justi/classic-mech-builder/data/test_mech.mtf')
    if mtf_file.exists():
        print(f"\nTesting with actual file: {mtf_file}")
        mech_data = parser.parse_mtf_file(mtf_file)
        if mech_data:
            print(f"Chassis: {mech_data.chassis}")
            print(f"Model: {mech_data.model}")
            print(f"Walk MP: {mech_data.walk_mp}")
            print(f"Run MP: {mech_data.run_mp}")
            print(f"Jump MP: {mech_data.jump_mp}")
            print(f"Tonnage: {mech_data.tonnage}")
        else:
            print("Failed to parse test mech file")
    else:
        print(f"Test file not found: {mtf_file}")

if __name__ == "__main__":
    test_movement_parsing()
