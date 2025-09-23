#!/usr/bin/env python3
"""
Simple test to verify movement parsing is working
"""

import re
from pathlib import Path

# Test the actual MTF file content
def test_real_mtf_file():
    mtf_file = Path('/Users/justi/classic-mech-builder/data/megamek/data/mechfiles/3039u/Locust LCT-1V.mtf')
    
    if not mtf_file.exists():
        print(f"File not found: {mtf_file}")
        return
    
    with open(mtf_file, 'r') as f:
        content = f.read()
    
    print("=== Real MTF File Test ===")
    print(f"File: {mtf_file.name}")
    
    # Current parser methods
    def parse_walk_mp(content):
        match = re.search(r'walk\s+mp:\s*(\d+)', content, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    
    def parse_jump_mp(content):
        match = re.search(r'jump\s+mp:\s*(\d+)', content, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    
    def parse_run_mp(content):
        walk_mp = parse_walk_mp(content)
        return int(walk_mp * 1.5) if walk_mp > 0 else 0
    
    # Test parsing
    walk = parse_walk_mp(content)
    run = parse_run_mp(content)
    jump = parse_jump_mp(content)
    
    print(f"Parsed movement: Walk={walk}, Run={run}, Jump={jump}")
    
    # Show the movement lines
    print("\nMovement lines in file:")
    for line_num, line in enumerate(content.split('\n'), 1):
        if any(word in line.lower() for word in ['walk mp', 'jump mp']):
            print(f"  Line {line_num}: '{line.strip()}'")
    
    if walk == 0 and run == 0:
        print("❌ PROBLEM: Movement parsing returned 0s")
        
        # Let's debug further
        print("\nDebugging patterns:")
        
        # Test each line individually
        for line in content.split('\n'):
            if 'walk' in line.lower():
                walk_match = re.search(r'walk\s+mp:\s*(\d+)', line, re.IGNORECASE)
                print(f"Line '{line.strip()}' -> walk match: {walk_match}")
            if 'jump' in line.lower():
                jump_match = re.search(r'jump\s+mp:\s*(\d+)', line, re.IGNORECASE)  
                print(f"Line '{line.strip()}' -> jump match: {jump_match}")
    else:
        print("✅ Movement parsing working correctly!")

if __name__ == "__main__":
    test_real_mtf_file()
