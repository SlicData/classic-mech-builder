#!/usr/bin/env python3
"""
MTF Parser Utilities - Shared components
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Enums
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
    XXL_FUSION = "xxl_fusion"
    FUEL_CELL = "fuel_cell"
    OTHER = "other"

class ArmorType(Enum):
    STANDARD = "standard"
    FERRO_FIBROUS = "ferro_fibrous"
    HARDENED = "hardened"
    STEALTH = "stealth"
    ENDO_STEEL = "endo_steel"
    OTHER = "other"

# Data Classes
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
class EquipmentData:
    name: str
    location: str
    count: int = 1

@dataclass
class CritSlotData:
    location: str
    slot_index: int
    item_type: str
    display_name: str

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
    equipment: List[EquipmentData] = field(default_factory=list)
    crit_slots: List[CritSlotData] = field(default_factory=list)
    quirks: List[str] = field(default_factory=list)

# Utility Functions
def normalize_location(location: str) -> str:
    """Normalize location names to standard abbreviations"""
    location_map = {
        'left arm': 'LA', 'right arm': 'RA', 'center torso': 'CT', 'head': 'HD',
        'left torso': 'LT', 'right torso': 'RT', 'left leg': 'LL', 'right leg': 'RL'
    }
    return location_map.get(location.lower(), location.upper())

def extract_chassis_model(content: str) -> Optional[Tuple[str, str]]:
    """Extract chassis and model from MTF content"""
    lines = [line for line in content.strip().split('\n') if not line.startswith('#') and line.strip()]
    if len(lines) >= 2:
        parts = lines[1].strip().split()
        return (parts[0], ' '.join(parts[1:])) if len(parts) >= 2 else (lines[1].strip(), "")
    return None

def calc_internal_structure(location: str) -> int:
    """Calculate internal structure for location (simplified)"""
    return 3 if location == 'HD' else 7
