#!/usr/bin/env python3
"""
Test the CMB-20 Step 1 movement parsing fix
"""

import sys
import logging
sys.path.append('/Users/justi/classic-mech-builder/db/seeds')

from mtf_seeder import MTFParser
from pathlib import Path

def test_movement_fix():
    """Test the movement parsing fix on sample MTF files"""
    
    # Set up logging to see debug output
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
    
    print("=== CMB-20 Step 1: Movement Parsing Fix Test ===")
    
    # Test files
    test_files = [
        'Locust LCT-1V.mtf',
        'Phoenix Hawk PXH-1.mtf', 
        'King Crab KGC-0000.mtf'
    ]
    
    parser = MTFParser()
    
    for filename in test_files:
        file_path = Path(f'/Users/justi/classic-mech-builder/data/megamek/data/mechfiles/3039u/{filename}')
        
        if not file_path.exists():
            print(f"❌ File not found: {filename}")
            continue
            
        print(f"\n=== Testing {filename} ===")
        
        try:
            mech_data = parser.parse_mtf_file(file_path)
            
            if mech_data:
                print(f"✅ Parsed: {mech_data.chassis} {mech_data.model}")
                print(f"   Movement: Walk={mech_data.walk_mp}, Run={mech_data.run_mp}, Jump={mech_data.jump_mp}")
                
                if mech_data.walk_mp > 0:
                    print(f"   ✅ Movement parsing SUCCESS!")
                else:
                    print(f"   ❌ Movement parsing FAILED - walk_mp = 0")
                    
            else:
                print(f"❌ Failed to parse {filename}")
                
        except Exception as e:
            print(f"❌ Error parsing {filename}: {e}")

    print(f"\n=== Summary ===")
    print(f"Step 1 Fix Applied:")
    print(f"✅ Enhanced regex patterns for MTF format")
    print(f"✅ Added validation for walk_mp > 0")
    print(f"✅ Better error logging and debugging")
    print(f"✅ Proper run_mp calculation from walk_mp")

if __name__ == "__main__":
    test_movement_fix()
