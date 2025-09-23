#!/usr/bin/env python3
"""
CMB-20 Step 1: Fix Movement Parsing
Simple, focused fix for movement parsing in MTF files
"""

import re

def test_movement_fix():
    """Test the movement parsing fix with a real MTF snippet"""
    
    # Sample from actual Locust MTF file
    sample_content = """chassis:Locust
model:LCT-1V

Mass:20
Engine:160 Fusion Engine
Structure:Standard
Myomer:Standard

Heat Sinks:10 Single
Walk MP:8
Jump MP:0

Armor:Standard(Inner Sphere)"""

    print("=== Movement Parsing Fix Test ===")
    print("Sample content:")
    for line in sample_content.split('\n'):
        if 'walk mp' in line.lower() or 'jump mp' in line.lower():
            print(f"  {line}")
    
    # Current method (potentially broken)
    def parse_walk_mp_old(content):
        match = re.search(r'walk\s+mp:\s*(\d+)', content, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    
    # Fixed method with better patterns
    def parse_walk_mp_fixed(content):
        patterns = [
            r'^Walk\s*MP:\s*(\d+)',     # "Walk MP: 8"
            r'walk\s*mp:\s*(\d+)',      # fallback
        ]
        for pattern in patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                return int(match.group(1))
        return 0
    
    def parse_jump_mp_fixed(content):
        patterns = [
            r'^Jump\s*MP:\s*(\d+)',     # "Jump MP: 0"
            r'jump\s*mp:\s*(\d+)',      # fallback
        ]
        for pattern in patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                return int(match.group(1))
        return 0
    
    # Test both
    old_walk = parse_walk_mp_old(sample_content)
    new_walk = parse_walk_mp_fixed(sample_content)
    new_jump = parse_jump_mp_fixed(sample_content)
    new_run = int(new_walk * 1.5) if new_walk > 0 else 0
    
    print(f"\nResults:")
    print(f"Old walk parsing: {old_walk}")
    print(f"Fixed parsing: Walk={new_walk}, Run={new_run}, Jump={new_jump}")
    
    if new_walk > 0:
        print("✅ Fixed parsing works!")
    else:
        print("❌ Still having issues")

if __name__ == "__main__":
    test_movement_fix()
