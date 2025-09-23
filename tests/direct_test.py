#!/usr/bin/env python3
"""
Direct test of MTF parsing without external dependencies
"""

import re
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

# Copy the necessary enums and classes
class TechBase(Enum):
    INNER_SPHERE = "inner_sphere"
    CLAN = "clan"
    MIXED = "mixed"
    PRIMITIVE = "primitive"

class Era(Enum):
    STAR_LEAGUE = "star_league"
    SUCCESSION = "succession"
    CLAN_INVASION = "clan_invasion"
    CIVIL_WAR = "civil_war"
    JIHAD = "jihad"
    DARK_AGE = "dark_age"
    ILCLAN = "ilclan"

class EngineType(Enum):
    FUSION = "fusion"
    XL_FUSION = "xl_fusion"
    LIGHT_FUSION = "light_fusion"
    ICE = "ice"
    COMPACT_FUSION = "compact_fusion"
    OTHER = "other"

class ArmorType(Enum):
    STANDARD = "standard"
    FERRO_FIBROUS = "ferro_fibrous"
    HARDENED = "hardened"
    STEALTH = "stealth"
    ENDO_STEEL = "endo_steel"
    OTHER = "other"

@dataclass
class WeaponData:
    name: str
    location: str
    count: int = 1

@dataclass 
class ArmorData:
    location: str
    armor_front: int
    armor_rear: Optional[int] = None
    internal: int = 0

@dataclass
class MechData:
    chassis: str
    model: str
    tech_base: TechBase
    era: Era
    rules_level: int
    tonnage: int
    battle_value: int
    walk_mp: int
    run_mp: int
    jump_mp: int
    engine_type: EngineType
    engine_rating: int
    heat_sinks: int
    armor_type: ArmorType
    role: Optional[str] = None
    year: Optional[int] = None
    source: Optional[str] = None
    cost_cbill: Optional[int] = None
    weapons: List[WeaponData] = field(default_factory=list)
    armor: List[ArmorData] = field(default_factory=list)

def test_parsing():
    """Test parsing our test file"""
    test_file = Path('/Users/justi/classic-mech-builder/data/test_mech.mtf')
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print(f"📁 Reading file: {test_file}")
    
    try:
        with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        print("📄 File content preview:")
        print(content[:500] + "..." if len(content) > 500 else content)
        print()
        
        # Test basic parsing
        print("🔍 Testing basic field extraction:")
        
        # Test chassis/model extraction
        lines = [line for line in content.strip().split('\n') if not line.startswith('#') and line.strip()]
        if len(lines) >= 2:
            chassis_model = lines[1].strip()
            parts = chassis_model.split()
            chassis = parts[0]
            model = ' '.join(parts[1:])
            print(f"  Chassis: {chassis}")
            print(f"  Model: {model}")
        
        # Test tonnage
        match = re.search(r'mass:\\s*(\\d+)', content, re.IGNORECASE)
        if match:
            tonnage = int(match.group(1))
            print(f"  Tonnage: {tonnage}")
        
        # Test movement
        walk_match = re.search(r'walk\\s+mp:\\s*(\\d+)', content, re.IGNORECASE)
        if walk_match:
            walk_mp = int(walk_match.group(1))
            print(f"  Walk MP: {walk_mp}")
        
        # Test weapons
        print("\\n🔫 Testing weapon parsing:")
        weapons_match = re.search(r'Weapons:\\s*(\\d+)', content, re.IGNORECASE)
        if weapons_match:
            weapon_count = int(weapons_match.group(1))
            print(f"  Weapon count declared: {weapon_count}")
            
            # Find weapon lines
            lines = content.split('\\n')
            in_weapons_section = False
            weapons_found = []
            
            for line in lines:
                line = line.strip()
                
                if re.match(r'Weapons:\\s*\\d+', line, re.IGNORECASE):
                    in_weapons_section = True
                    continue
                
                if in_weapons_section:
                    if not line or re.match(r'^[A-Z][A-Za-z\\s]+:$', line):
                        break
                    
                    if ',' in line:
                        parts = line.split(',')
                        if len(parts) >= 2:
                            weapon_name = parts[0].strip()
                            location = parts[1].strip()
                            weapons_found.append((weapon_name, location))
                            print(f"    - {weapon_name} in {location}")
            
            print(f"  Weapons parsed: {len(weapons_found)}")
        
        # Test armor
        print("\\n🛡️  Testing armor parsing:")
        armor_patterns = {
            'LA': r'LA armor:\\s*(\\d+)',
            'RA': r'RA armor:\\s*(\\d+)',
            'CT': r'CT armor:\\s*(\\d+)',
            'HD': r'HD armor:\\s*(\\d+)',
        }
        
        armor_found = 0
        for location, pattern in armor_patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                armor_value = int(match.group(1))
                print(f"    - {location}: {armor_value} armor")
                armor_found += 1
        
        print(f"  Armor locations found: {armor_found}")
        
        print("\\n✅ Basic parsing tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during parsing: {e}")
        return False

if __name__ == "__main__":
    test_parsing()
