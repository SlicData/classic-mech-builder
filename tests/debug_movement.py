#!/usr/bin/env python3
"""
Debug Movement Parsing - CMB-20 Step 1
Test the current MTF parser directly to see what's happening with movement parsing
"""

import sys
import os
sys.path.append('/Users/justi/classic-mech-builder/db/seeds')

from mtf_seeder import MTFParser
from pathlib import Path

def debug_movement_parsing():
    """Debug the current movement parsing on real MTF files"""
    
    print("=== Debug Movement Parsing ===")
    
    # Test files
    test_files = [
        '/Users/justi/classic-mech-builder/data/megamek/data/mechfiles/3039u/Locust LCT-1V.mtf',
        '/Users/justi/classic-mech-builder/data/megamek/data/mechfiles/3039u/Phoenix Hawk PXH-1.mtf',
        '/Users/justi/classic-mech-builder/data/megamek/data/mechfiles/3039u/King Crab KGC-0000.mtf'
    ]
    
    parser = MTFParser()
    
    for file_path in test_files:
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            continue
            
        print(f"\n=== {file_path.name} ===")
        
        try:
            # Parse the file
            mech_data = parser.parse_mtf_file(file_path)
            
            if mech_data:
                print(f"✅ Parsed: {mech_data.chassis} {mech_data.model}")
                print(f"   Movement: Walk={mech_data.walk_mp}, Run={mech_data.run_mp}, Jump={mech_data.jump_mp}")
                
                # Also test individual methods to see where the issue is
                with open(file_path, 'r') as f:
                    content = f.read()
                
                walk_mp = parser._parse_walk_mp(content)
                run_mp = parser._parse_run_mp(content)
                jump_mp = parser._parse_jump_mp(content)
                
                print(f"   Individual: Walk={walk_mp}, Run={run_mp}, Jump={jump_mp}")
                
                # Show the relevant lines from the file
                print("   Movement lines in file:")
                for line_num, line in enumerate(content.split('\n'), 1):
                    if any(word in line.lower() for word in ['walk', 'jump', 'movement']):
                        print(f"     Line {line_num}: {line.strip()}")
                
                # Test the patterns manually
                import re
                
                walk_match = re.search(r'walk\s+mp:\s*(\d+)', content, re.IGNORECASE)
                jump_match = re.search(r'jump\s+mp:\s*(\d+)', content, re.IGNORECASE)
                
                print(f"   Pattern test: walk_match={walk_match}, jump_match={jump_match}")
                
                if walk_match:
                    print(f"   Walk pattern matched: {walk_match.group(1)}")
                else:
                    print("   ❌ Walk pattern did NOT match")
                
                if jump_match:
                    print(f"   Jump pattern matched: {jump_match.group(1)}")
                else:
                    print("   ❌ Jump pattern did NOT match")
                    
            else:
                print(f"❌ Failed to parse file")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_movement_parsing()
