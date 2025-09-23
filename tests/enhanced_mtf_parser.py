#!/usr/bin/env python3
"""
CMB-20: Enhanced MTF File Parser for Classic Mech Builder
Parses MegaMek .mtf files and imports complete data into PostgreSQL database
"""

import os
import re
import psycopg2
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import argparse
import logging
from dataclasses import dataclass, field
from enum import Enum

# Import existing enums and classes from original file
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
    # Enhanced fields
    weapons: List[WeaponData] = field(default_factory=list)
    armor: List[ArmorData] = field(default_factory=list)
    equipment: List[EquipmentData] = field(default_factory=list)
    crit_slots: List[CritSlotData] = field(default_factory=list)
    quirks: List[str] = field(default_factory=list)

# Simple test to verify import works
if __name__ == "__main__":
    print("Enhanced MTF parser structure loaded successfully")
    print("Data classes: WeaponData, ArmorData, EquipmentData, CritSlotData, MechData")
