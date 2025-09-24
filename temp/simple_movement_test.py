#!/usr/bin/env python3
"""
Simple movement parsing test - CMB-20 Step 1
"""

import re

def test_movement_parsing():
    """Test movement parsing patterns"""
    
    # Sample MTF content (from King Crab)
    king_crab_sample = """
chassis:King Crab
model:KGC-0000

Config:Biped
TechBase:Inner Sphere
Era:2815
Source:TRO: 3039

Mass:100
Engine:300 Fusion Engine
Structure:Standard
Myomer:Standard

Heat Sinks:15 Single
Walk MP:3
Jump MP:0

Armor:Standard(Inner Sphere)
LA Armor:33
"""

    # Sample MTF content (from Phoenix Hawk with jump jets)
    phoenix_sample = """
chassis:Phoenix Hawk
model:PXH-1

Mass:45
Engine:270 Fusion Engine

Heat Sinks:10 Single
Walk MP:6
Jump MP:6

Armor:Standard(Inner Sphere)
"""

    print("=== Movement Parsing Test ===")
    
    def test_content(content, name):
        print(f"\n{name}:")
        
        # Show the relevant lines
        for line in content.split('\n'):
            if any(word in line.lower() for word in ['walk mp', 'jump mp']):
                print(f"  Found: {line.strip()}")
        
        # Current broken patterns
        old_walk_match = re.search(r'walk\s+mp:\s*(\d+)', content, re.IGNORECASE)
        old_jump_match = re.search(r'jump\s+mp:\s*(\d+)', content, re.IGNORECASE)
        
        old_walk = int(old_walk_match.group(1)) if old_walk_match else 0
        old_jump = int(old_jump_match.group(1)) if old_jump_match else 0
        old_run = int(old_walk * 1.5) if old_walk > 0 else 0
        
        print(f"  Current (broken): Walk={old_walk}, Run={old_run}, Jump={old_jump}")
        
        # Fixed patterns
        walk = run = jump = 0
        
        # Walk MP pattern - fixed
        walk_patterns = [
            r'^Walk\s*MP:\s*(\d+)',
            r'^Walk:\s*(\d+)', 
            r'walk\s*mp:\s*(\d+)'
        ]
        
        for pattern in walk_patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                walk = int(match.group(1))
                break
        
        # Jump MP pattern - fixed
        jump_patterns = [
            r'^Jump\s*MP:\s*(\d+)',
            r'^Jump:\s*(\d+)',
            r'jump\s*mp:\s*(\d+)'
        ]
        
        for pattern in jump_patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                jump = int(match.group(1))
                break
        
        # Calculate run
        if walk > 0 and run == 0:
            run = int(walk * 1.5)
        
        print(f"  Fixed: Walk={walk}, Run={run}, Jump={jump}")
        
        return walk, run, jump
    
    # Test both samples
    test_content(king_crab_sample, "King Crab (no jump)")
    test_content(phoenix_sample, "Phoenix Hawk (with jump)")
    
    print("\n=== Pattern Analysis ===")
    print("Issue: Current regex 'walk\\s+mp:' requires space between 'walk' and 'mp'")
    print("Reality: MTF files use 'Walk MP:' format")
    print("Fix: Use '^Walk\\s*MP:' pattern to match start of line")

if __name__ == "__main__":
    test_movement_parsing()
