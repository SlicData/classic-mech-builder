#!/usr/bin/env python3
"""
Test script for movement parsing fix - CMB-20 Step 1
"""

import re
from pathlib import Path

def test_movement_parsing():
    """Test movement parsing against sample MTF files"""
    
    # Sample MTF files for testing
    test_files = [
        "/Users/justi/classic-mech-builder/data/megamek/data/mechfiles/3039u/King Crab KGC-0000.mtf",
        "/Users/justi/classic-mech-builder/data/megamek/data/mechfiles/3039u/Locust LCT-1V.mtf",
        "/Users/justi/classic-mech-builder/data/megamek/data/mechfiles/3039u/Phoenix Hawk PXH-1.mtf"
    ]
    
    print("=== Testing Current (Broken) Movement Parsing ===")
    for file_path in test_files:
        if Path(file_path).exists():
            with open(file_path, 'r') as f:
                content = f.read()
            
            chassis = extract_chassis(content)
            
            # Current broken patterns
            old_walk = parse_walk_mp_old(content)
            old_run = parse_run_mp_old(content, old_walk)
            old_jump = parse_jump_mp_old(content)
            
            print(f"\n{chassis}:")
            print(f"  Current: Walk={old_walk}, Run={old_run}, Jump={old_jump}")
            
            # New fixed patterns
            new_walk, new_run, new_jump = parse_movement_fixed(content)
            print(f"  Fixed:   Walk={new_walk}, Run={new_run}, Jump={new_jump}")
            
            # Show raw lines for debugging
            print(f"  Raw movement lines:")
            for line in content.split('\n'):
                if any(word in line.lower() for word in ['walk', 'jump', 'movement']):
                    print(f"    {line.strip()}")

def extract_chassis(content: str) -> str:
    """Extract chassis name for display"""
    match = re.search(r'^chassis:\s*(.+)$', content, re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else "Unknown"

def parse_walk_mp_old(content: str) -> int:
    """Current broken walk MP parsing"""
    match = re.search(r'walk\s+mp:\s*(\d+)', content, re.IGNORECASE)
    return int(match.group(1)) if match else 0

def parse_run_mp_old(content: str, walk_mp: int) -> int:
    """Current broken run MP parsing"""
    return int(walk_mp * 1.5) if walk_mp > 0 else 0

def parse_jump_mp_old(content: str) -> int:
    """Current broken jump MP parsing"""
    match = re.search(r'jump\s+mp:\s*(\d+)', content, re.IGNORECASE)
    return int(match.group(1)) if match else 0

def parse_movement_fixed(content: str) -> tuple[int, int, int]:
    """Fixed movement parsing with multiple pattern support"""
    walk_mp = run_mp = jump_mp = 0
    
    # Pattern 1: Individual lines (most common in MTF files)
    walk_patterns = [
        r'^Walk\s*MP:\s*(\d+)',           # "Walk MP: 3"
        r'^Walk:\s*(\d+)',                # "Walk: 3" 
        r'walk\s*mp:\s*(\d+)',            # Original pattern (case insensitive)
    ]
    
    for pattern in walk_patterns:
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        if match:
            walk_mp = int(match.group(1))
            break
    
    jump_patterns = [
        r'^Jump\s*MP:\s*(\d+)',           # "Jump MP: 6"
        r'^Jump:\s*(\d+)',                # "Jump: 6"
        r'jump\s*mp:\s*(\d+)',            # Original pattern
    ]
    
    for pattern in jump_patterns:
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        if match:
            jump_mp = int(match.group(1))
            break
    
    # Pattern 2: Combined movement line (less common but should support)
    movement_patterns = [
        r'Movement:\s*Walk(?:\s*MP)?:\s*(\d+),\s*Run(?:\s*MP)?:\s*(\d+)(?:,\s*Jump(?:\s*MP)?:\s*(\d+))?',
        r'Walk\s*MP:\s*(\d+).*?Run\s*MP:\s*(\d+).*?(?:Jump\s*MP:\s*(\d+))?',
    ]
    
    for pattern in movement_patterns:
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE | re.DOTALL)
        if match:
            walk_mp = int(match.group(1)) if match.group(1) else walk_mp
            run_mp = int(match.group(2)) if match.group(2) else run_mp
            if match.group(3):
                jump_mp = int(match.group(3))
            break
    
    # Calculate run_mp if not found but walk_mp exists
    if walk_mp > 0 and run_mp == 0:
        run_mp = int(walk_mp * 1.5)
    
    return walk_mp, run_mp, jump_mp

if __name__ == "__main__":
    test_movement_parsing()
