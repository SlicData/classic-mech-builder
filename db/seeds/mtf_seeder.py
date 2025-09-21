#!/usr/bin/env python3
"""
MTF File Parser for Classic Mech Builder
Parses MegaMek .mtf files and imports data into PostgreSQL database
"""

import os
import re
import psycopg2
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Set

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
    weapon_name: Optional[str] = None
    equipment_name: Optional[str] = None

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
    # New fields for detailed data
    weapons: List[WeaponData] = field(default_factory=list)
    armor: List[ArmorData] = field(default_factory=list)
    equipment: List[EquipmentData] = field(default_factory=list)
    crit_slots: List[CritSlotData] = field(default_factory=list)
    quirks: List[str] = field(default_factory=list)

class MTFParser:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_mtf_file(self, file_path: Path) -> Optional[MechData]:
        """Parse a single MTF file into MechData"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract basic info
            chassis_model = self._extract_chassis_model(content)
            if not chassis_model:
                return None
            
            chassis, model = chassis_model
            
            # Parse all fields
            data = MechData(
                chassis=chassis,
                model=model,
                tech_base=self._parse_tech_base(content),
                era=self._parse_era(content),
                rules_level=self._parse_rules_level(content),
                tonnage=self._parse_tonnage(content),
                battle_value=self._calculate_battle_value(content),
                walk_mp=self._parse_walk_mp(content),
                run_mp=self._parse_run_mp(content),
                jump_mp=self._parse_jump_mp(content),
                engine_type=self._parse_engine_type(content),
                engine_rating=self._parse_engine_rating(content),
                heat_sinks=self._parse_heat_sinks(content),
                armor_type=self._parse_armor_type(content),
                role=self._parse_role(content),
                year=self._parse_year(content),
                source=self._parse_source(content),
                cost_cbill=self._parse_cost(content),
                # Parse new detailed data
                weapons=self._parse_weapons(content),
                armor=self._parse_armor_values(content),
                equipment=self._parse_equipment(content),
                crit_slots=self._parse_crit_slots(content),
                quirks=self._parse_quirks(content)
            )
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {e}")
            return None
    
    def _extract_chassis_model(self, content: str) -> Optional[Tuple[str, str]]:
        """Extract chassis and model from MTF content"""
        # Look for chassis: and model: fields (new format)
        chassis_match = re.search(r'^chassis:\s*(.+)$', content, re.MULTILINE | re.IGNORECASE)
        model_match = re.search(r'^model:\s*(.+)$', content, re.MULTILINE | re.IGNORECASE)
        
        if chassis_match and model_match:
            chassis = chassis_match.group(1).strip()
            model = model_match.group(1).strip()
            return chassis, model
        
        # Fallback: look for the old format (second non-comment line)
        lines = [line for line in content.strip().split('\n') if not line.startswith('#') and line.strip()]
        if len(lines) >= 2:
            name_line = lines[1].strip()
            # Try to split chassis and model
            parts = name_line.split()
            if len(parts) >= 2:
                chassis = parts[0]
                model = ' '.join(parts[1:])
                return chassis, model
            return name_line, ""
        
        return None
    
    def _parse_tech_base(self, content: str) -> TechBase:
        """Parse TechBase field"""
        match = re.search(r'techbase:\s*(.+)', content, re.IGNORECASE | re.MULTILINE)
        if match:
            value = match.group(1).strip().lower()
            if "inner sphere" in value:
                return TechBase.INNER_SPHERE
            elif "clan" in value:
                return TechBase.CLAN
            elif "mixed" in value:
                return TechBase.MIXED
        return TechBase.INNER_SPHERE  # Default
    
    def _parse_era(self, content: str) -> Era:
        """Parse Era field or derive from year"""
        # Look for year first
        year = self._parse_year(content)
        if year:
            if year < 2781:
                return Era.STAR_LEAGUE
            elif year < 3049:
                return Era.SUCCESSION
            elif year < 3067:
                return Era.CLAN_INVASION
            elif year < 3080:
                return Era.CIVIL_WAR
            elif year < 3135:
                return Era.JIHAD
            elif year < 3151:
                return Era.DARK_AGE
            else:
                return Era.ILCLAN
        return Era.SUCCESSION  # Default
    
    def _parse_rules_level(self, content: str) -> int:
        """Parse Rules Level field"""
        match = re.search(r'rules level:\s*(\d+)', content, re.IGNORECASE)
        return int(match.group(1)) if match else 1
    
    def _parse_tonnage(self, content: str) -> int:
        """Parse mass field"""
        match = re.search(r'mass:\s*(\d+)', content, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    
    def _calculate_battle_value(self, content: str) -> int:
        """Calculate or extract battle value"""
        # Look for BV in the file first
        match = re.search(r'bv:\s*(\d+)', content, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        # Fallback: rough estimate
        tonnage = self._parse_tonnage(content)
        return tonnage * 20  # Rough estimate for seeding
    
    def _parse_walk_mp(self, content: str) -> int:
        """Parse walk speed"""
        # Fix: Look for 'walk mp:' not just 'walk:'
        match = re.search(r'walk\s+mp:\s*(\d+)', content, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    
    def _parse_run_mp(self, content: str) -> int:
        """Parse run speed or calculate from walk"""
        # Fix: Look for 'run mp:' not just 'run:'
        match = re.search(r'run\s+mp:\s*(\d+)', content, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        # Calculate from walk MP
        walk_mp = self._parse_walk_mp(content)
        return int(walk_mp * 1.5)  # Standard BattleTech rule
    
    def _parse_jump_mp(self, content: str) -> int:
        """Parse jump speed"""
        # Fix: Look for 'jump mp:' not just 'jump:'
        match = re.search(r'jump\s+mp:\s*(\d+)', content, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    
    def _parse_engine_type(self, content: str) -> EngineType:
        """Parse engine type"""
        match = re.search(r'engine:\s*(.+)', content, re.IGNORECASE)
        if match:
            engine_text = match.group(1).lower()
            if "xl" in engine_text:
                return EngineType.XL_FUSION
            elif "light" in engine_text:
                return EngineType.LIGHT_FUSION
            elif "ice" in engine_text:
                return EngineType.ICE
            elif "compact" in engine_text:
                return EngineType.COMPACT_FUSION
            elif "fusion" in engine_text:
                return EngineType.FUSION
        return EngineType.FUSION  # Default
    
    def _parse_engine_rating(self, content: str) -> int:
        """Extract engine rating"""
        match = re.search(r'engine:\s*(\d+)', content, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    
    def _parse_heat_sinks(self, content: str) -> int:
        """Parse heat sinks"""
        match = re.search(r'heat sinks:\s*(\d+)', content, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    
    def _parse_armor_type(self, content: str) -> ArmorType:
        """Parse armor type"""
        if re.search(r'ferro.?fibrous', content, re.IGNORECASE):
            return ArmorType.FERRO_FIBROUS
        elif re.search(r'hardened', content, re.IGNORECASE):
            return ArmorType.HARDENED
        elif re.search(r'stealth', content, re.IGNORECASE):
            return ArmorType.STEALTH
        elif re.search(r'endo.?steel', content, re.IGNORECASE):
            return ArmorType.ENDO_STEEL
        return ArmorType.STANDARD  # Default
    
    def _parse_role(self, content: str) -> Optional[str]:
        """Extract role information"""
        match = re.search(r'role:\s*(.+)', content, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    def _parse_year(self, content: str) -> Optional[int]:
        """Extract year"""
        match = re.search(r'year:\s*(\d+)', content, re.IGNORECASE)
        return int(match.group(1)) if match else None
    
    def _parse_source(self, content: str) -> Optional[str]:
        """Extract source information"""
        match = re.search(r'source:\s*(.+)', content, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    def _parse_cost(self, content: str) -> Optional[int]:
        """Extract cost information if available"""
        match = re.search(r'cost:\s*(\d+)', content, re.IGNORECASE)
        return int(match.group(1)) if match else None
    
    def _parse_weapons(self, content: str) -> List[WeaponData]:
        """Parse weapons section from MTF content"""
        weapons = []
        
        # Look for Weapons: section
        weapons_match = re.search(r'Weapons:\s*(\d+)', content, re.IGNORECASE)
        if not weapons_match:
            return weapons
        
        # Find the weapons list after "Weapons:X"
        lines = content.split('\n')
        in_weapons_section = False
        
        for line in lines:
            line = line.strip()
            
            if re.match(r'Weapons:\s*\d+', line, re.IGNORECASE):
                in_weapons_section = True
                continue
            
            # Stop at next major section or empty line
            if in_weapons_section:
                if not line or re.match(r'^[A-Z][A-Za-z\s]+:', line):
                    break
                
                # Parse weapon line: "HAG/20, Left Arm"
                if ',' in line:
                    parts = line.split(',')
                    if len(parts) >= 2:
                        weapon_name = parts[0].strip()
                        location = parts[1].strip()
                        
                        # Convert location names
                        location = self._normalize_location(location)
                        
                        weapons.append(WeaponData(
                            name=weapon_name,
                            location=location
                        ))
        
        return weapons
    
    def _parse_armor_values(self, content: str) -> List[ArmorData]:
        """Parse armor values by location"""
        armor = []
        
        # Standard armor location patterns
        armor_patterns = {
            'LA': r'LA armor:\s*(\d+)',
            'RA': r'RA armor:\s*(\d+)',
            'LT': r'LT armor:\s*(\d+)',
            'RT': r'RT armor:\s*(\d+)',
            'CT': r'CT armor:\s*(\d+)',
            'HD': r'HD armor:\s*(\d+)',
            'LL': r'LL armor:\s*(\d+)',
            'RL': r'RL armor:\s*(\d+)'
        }
        
        # Rear armor patterns
        rear_patterns = {
            'LT': r'RTL armor:\s*(\d+)',
            'RT': r'RTR armor:\s*(\d+)',
            'CT': r'RTC armor:\s*(\d+)'
        }
        
        for location, pattern in armor_patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                front_armor = int(match.group(1))
                
                # Check for rear armor
                rear_armor = None
                if location in rear_patterns:
                    rear_match = re.search(rear_patterns[location], content, re.IGNORECASE)
                    if rear_match:
                        rear_armor = int(rear_match.group(1))
                
                armor.append(ArmorData(
                    location=location,
                    armor_front=front_armor,
                    armor_rear=rear_armor,
                    internal=self._calculate_internal_structure(location, self._parse_tonnage(content))
                ))
        
        return armor
    
    def _parse_equipment(self, content: str) -> List[EquipmentData]:
        """Parse equipment from critical slot sections"""
        equipment = []
        equipment_seen = set()
        
        # Parse critical slot sections for equipment
        location_sections = self._parse_location_sections(content)
        
        for location, items in location_sections.items():
            for item in items:
                # Skip basic actuators and structure
                if item in ['Shoulder', 'Upper Arm Actuator', 'Lower Arm Actuator', 
                           'Hand Actuator', 'Hip', 'Upper Leg Actuator', 'Lower Leg Actuator',
                           'Foot Actuator', 'Life Support', 'Sensors', 'Cockpit', 
                           'Fusion Engine', 'Gyro', '-Empty-']:
                    continue
                
                # Skip weapons (handled separately)
                if any(weapon_keyword in item.upper() for weapon_keyword in 
                      ['LASER', 'PPC', 'AC', 'LRM', 'SRM', 'GAUSS', 'RIFLE']):
                    continue
                
                # This is equipment
                equipment_key = f"{item}_{location}"
                if equipment_key not in equipment_seen:
                    equipment_seen.add(equipment_key)
                    equipment.append(EquipmentData(
                        name=item,
                        location=self._normalize_location(location)
                    ))
        
        return equipment
    
    def _parse_crit_slots(self, content: str) -> List[CritSlotData]:
        """Parse critical slot layout from location sections"""
        crit_slots = []
        
        location_sections = self._parse_location_sections(content)
        
        for location, items in location_sections.items():
            normalized_location = self._normalize_location(location)
            
            for slot_index, item in enumerate(items, 1):
                # Determine item type
                item_type = self._classify_crit_item(item)
                
                crit_slots.append(CritSlotData(
                    location=normalized_location,
                    slot_index=slot_index,
                    item_type=item_type,
                    display_name=item
                ))
        
        return crit_slots
    
    def _parse_quirks(self, content: str) -> List[str]:
        """Parse quirk lines"""
        quirks = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('quirk:'):
                quirk = line.replace('quirk:', '').strip()
                if quirk:
                    quirks.append(quirk)
        
        return quirks
    
    def _parse_location_sections(self, content: str) -> Dict[str, List[str]]:
        """Parse location sections (Left Arm:, Right Arm:, etc.)"""
        sections = {}
        lines = content.split('\n')
        current_location = None
        
        for line in lines:
            line = line.strip()
            
            # Check if this is a location header
            if line.endswith(':') and len(line.split()) <= 3:
                potential_location = line[:-1].strip()
                if potential_location in ['Left Arm', 'Right Arm', 'Left Torso', 'Right Torso',
                                        'Center Torso', 'Head', 'Left Leg', 'Right Leg']:
                    current_location = potential_location
                    sections[current_location] = []
                    continue
            
            # Add items to current location
            if current_location and line and not line.startswith('overview:'):
                sections[current_location].append(line)
        
        return sections
    
    def _normalize_location(self, location: str) -> str:
        """Convert location names to database enum values"""
        location_map = {
            'Left Arm': 'LA',
            'Right Arm': 'RA', 
            'Left Torso': 'LT',
            'Right Torso': 'RT',
            'Center Torso': 'CT',
            'Head': 'HD',
            'Left Leg': 'LL',
            'Right Leg': 'RL'
        }
        return location_map.get(location, location)
    
    def _classify_crit_item(self, item: str) -> str:
        """Classify critical slot item type"""
        item_upper = item.upper()
        
        if any(weapon_keyword in item_upper for weapon_keyword in 
              ['LASER', 'PPC', 'AC', 'LRM', 'SRM', 'GAUSS', 'RIFLE', 'CANNON']):
            return 'weapon'
        elif 'AMMO' in item_upper:
            return 'ammo'
        elif item in ['Fusion Engine', 'Gyro']:
            return item.lower().replace(' ', '_')
        elif item in ['Life Support', 'Sensors', 'Cockpit']:
            return item.lower().replace(' ', '_')
        elif 'HEATSINK' in item_upper or 'HEAT SINK' in item_upper:
            return 'heatsink'
        elif 'JUMP JET' in item_upper:
            return 'jump_jet'
        elif item == '-Empty-':
            return 'empty'
        else:
            return 'equipment'
    
    def _calculate_internal_structure(self, location: str, tonnage: int) -> int:
        """Calculate internal structure points for a location"""
        # Standard BattleTech internal structure rules
        if location == 'HD':
            return 3
        elif location == 'CT':
            return tonnage // 10
        elif location in ['LT', 'RT']:
            return tonnage // 10
        elif location in ['LA', 'RA']:
            return tonnage // 10
        elif location in ['LL', 'RL']:
            return tonnage // 10
        return 0

class DatabaseSeeder:
    def __init__(self, db_name: str = "cmb_dev"):
        self.db_name = db_name
        self.conn = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            # Use the same detection logic as our test runner
            from db_config import detect_db_config
            config = detect_db_config()
            if config:
                self.conn = psycopg2.connect(**config)
                self.conn.autocommit = True
                self.logger.info(f"Connected to database as user: {config['user']}")
            else:
                raise Exception("Could not detect database configuration")
            
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            self.logger.error("Try running: psql cmb_dev -c 'SELECT current_user;' to check your database user")
            raise
    
    def insert_mech(self, mech: MechData) -> bool:
        """Insert complete mech data into database"""
        try:
            cursor = self.conn.cursor()
            
            # Insert main mech record first
            mech_id = self._insert_mech_main(cursor, mech)
            if not mech_id:
                return False
    
    def _insert_mech_main(self, cursor, mech: MechData) -> Optional[int]:
        """Insert main mech record and return mech_id"""
        # Use UPSERT to handle duplicates
        sql = """
            INSERT INTO mech (
                chassis, model, tech_base, era, rules_level,
                tonnage, battle_value, walk_mp, run_mp, jump_mp,
                engine_type, engine_rating, heat_sinks, armor_type,
                role, year, source, cost_cbill
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (chassis, model) DO UPDATE SET
                tech_base = EXCLUDED.tech_base,
                era = EXCLUDED.era,
                rules_level = EXCLUDED.rules_level,
                tonnage = EXCLUDED.tonnage,
                battle_value = EXCLUDED.battle_value,
                walk_mp = EXCLUDED.walk_mp,
                run_mp = EXCLUDED.run_mp,
                jump_mp = EXCLUDED.jump_mp,
                engine_type = EXCLUDED.engine_type,
                engine_rating = EXCLUDED.engine_rating,
                heat_sinks = EXCLUDED.heat_sinks,
                armor_type = EXCLUDED.armor_type,
                role = EXCLUDED.role,
                year = EXCLUDED.year,
                source = EXCLUDED.source,
                cost_cbill = EXCLUDED.cost_cbill,
                updated_at = NOW()
            RETURNING id
        """
        
        cursor.execute(sql, (
            mech.chassis, mech.model, mech.tech_base.value, mech.era.value,
            mech.rules_level, mech.tonnage, mech.battle_value,
            mech.walk_mp, mech.run_mp, mech.jump_mp,
            mech.engine_type.value, mech.engine_rating, mech.heat_sinks,
            mech.armor_type.value, mech.role, mech.year, mech.source,
            mech.cost_cbill
        ))
        
        result = cursor.fetchone()
        return result[0] if result else None
    
    def _insert_armor_data(self, cursor, mech_id: int, armor_data: List[ArmorData]):
        """Insert armor data for all locations"""
        # Delete existing armor data
        cursor.execute("DELETE FROM mech_armor WHERE mech_id = %s", (mech_id,))
        
        for armor in armor_data:
            sql = """
                INSERT INTO mech_armor (mech_id, loc, armor_front, armor_rear, internal)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                mech_id, armor.location, armor.armor_front, 
                armor.armor_rear, armor.internal
            ))
    
    def _insert_weapon_data(self, cursor, mech_id: int, weapons: List[WeaponData]):
        """Insert weapon data with catalog entries"""
        # Delete existing weapon data
        cursor.execute("DELETE FROM mech_weapon WHERE mech_id = %s", (mech_id,))
        
        for weapon in weapons:
            # Insert/get weapon catalog entry
            weapon_id = self._get_or_create_weapon(cursor, weapon.name)
            
            if weapon_id:
                # Insert mech weapon assignment
                sql = """
                    INSERT INTO mech_weapon (mech_id, weapon_id, count)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (mech_id, weapon_id) DO UPDATE SET
                        count = mech_weapon.count + EXCLUDED.count
                """
                cursor.execute(sql, (mech_id, weapon_id, weapon.count))
    
    def _insert_equipment_data(self, cursor, mech_id: int, equipment: List[EquipmentData]):
        """Insert equipment data with catalog entries"""
        # Delete existing equipment data
        cursor.execute("DELETE FROM mech_equipment WHERE mech_id = %s", (mech_id,))
        
        for equip in equipment:
            # Insert/get equipment catalog entry
            equipment_id = self._get_or_create_equipment(cursor, equip.name)
            
            if equipment_id:
                # Insert mech equipment assignment
                sql = """
                    INSERT INTO mech_equipment (mech_id, equipment_id, count)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (mech_id, equipment_id) DO UPDATE SET
                        count = mech_equipment.count + EXCLUDED.count
                """
                cursor.execute(sql, (mech_id, equipment_id, equip.count))
    
    def _insert_crit_slot_data(self, cursor, mech_id: int, crit_slots: List[CritSlotData]):
        """Insert critical slot layout"""
        # Delete existing crit slot data
        cursor.execute("DELETE FROM mech_crit_slot WHERE mech_id = %s", (mech_id,))
        
        for slot in crit_slots:
            sql = """
                INSERT INTO mech_crit_slot (
                    mech_id, loc, slot_index, item_type, display_name
                ) VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                mech_id, slot.location, slot.slot_index, 
                slot.item_type, slot.display_name
            ))
    
    def _insert_quirk_data(self, cursor, mech_id: int, quirks: List[str]):
        """Insert quirk data"""
        # Delete existing quirk data
        cursor.execute("DELETE FROM mech_quirk WHERE mech_id = %s", (mech_id,))
        
        for quirk in quirks:
            sql = """
                INSERT INTO mech_quirk (mech_id, quirk)
                VALUES (%s, %s)
            """
            cursor.execute(sql, (mech_id, quirk))
    
    def _get_or_create_weapon(self, cursor, weapon_name: str) -> Optional[int]:
        """Get or create weapon catalog entry"""
        # Check if weapon exists
        cursor.execute(
            "SELECT id FROM weapon_catalog WHERE name = %s", 
            (weapon_name,)
        )
        result = cursor.fetchone()
        if result:
            return result[0]
        
        # Create new weapon entry with basic data
        sql = """
            INSERT INTO weapon_catalog (name, class, tech_base)
            VALUES (%s, %s, %s)
            RETURNING id
        """
        
        # Basic classification (can be enhanced later)
        weapon_class = self._classify_weapon(weapon_name)
        tech_base = self._guess_weapon_tech_base(weapon_name)
        
        cursor.execute(sql, (weapon_name, weapon_class, tech_base))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def _get_or_create_equipment(self, cursor, equipment_name: str) -> Optional[int]:
        """Get or create equipment catalog entry"""
        # Check if equipment exists
        cursor.execute(
            "SELECT id FROM equipment_catalog WHERE name = %s", 
            (equipment_name,)
        )
        result = cursor.fetchone()
        if result:
            return result[0]
        
        # Create new equipment entry
        sql = """
            INSERT INTO equipment_catalog (name, category, tech_base)
            VALUES (%s, %s, %s)
            RETURNING id
        """
        
        category = self._classify_equipment(equipment_name)
        tech_base = self._guess_equipment_tech_base(equipment_name)
        
        cursor.execute(sql, (equipment_name, category, tech_base))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def _classify_weapon(self, weapon_name: str) -> str:
        """Classify weapon by name"""
        name_upper = weapon_name.upper()
        
        if any(keyword in name_upper for keyword in ['LASER', 'PPC']):
            return 'energy'
        elif any(keyword in name_upper for keyword in ['AC', 'GAUSS', 'RIFLE']):
            return 'ballistic'
        elif any(keyword in name_upper for keyword in ['LRM', 'SRM', 'MRM', 'ROCKET']):
            return 'missile'
        elif any(keyword in name_upper for keyword in ['TAG', 'NARC', 'ECM']):
            return 'support'
        else:
            return 'ballistic'  # Default
    
    def _classify_equipment(self, equipment_name: str) -> str:
        """Classify equipment by name"""
        name_upper = equipment_name.upper()
        
        if any(keyword in name_upper for keyword in ['HEAT', 'SINK']):
            return 'heat'
        elif any(keyword in name_upper for keyword in ['ECM', 'GUARDIAN', 'PROBE']):
            return 'electronics'
        elif any(keyword in name_upper for keyword in ['JUMP', 'JET']):
            return 'movement'
        elif any(keyword in name_upper for keyword in ['ENDO', 'STEEL']):
            return 'structure'
        elif any(keyword in name_upper for keyword in ['GYRO']):
            return 'gyro'
        elif any(keyword in name_upper for keyword in ['COCKPIT']):
            return 'cockpit'
        else:
            return 'other'
    
    def _guess_weapon_tech_base(self, weapon_name: str) -> str:
        """Guess weapon tech base from name"""
        name_upper = weapon_name.upper()
        
        if name_upper.startswith('CL') or name_upper.startswith('CLAN'):
            return 'clan'
        elif name_upper.startswith('IS') or 'INNER SPHERE' in name_upper:
            return 'inner_sphere'
        else:
            return 'inner_sphere'  # Default
    
    def _guess_equipment_tech_base(self, equipment_name: str) -> str:
        """Guess equipment tech base from name"""
        name_upper = equipment_name.upper()
        
        if name_upper.startswith('CL') or name_upper.startswith('CLAN'):
            return 'clan'
        elif name_upper.startswith('IS') or 'INNER SPHERE' in name_upper:
            return 'inner_sphere'
        else:
            return 'inner_sphere'  # Default
            
            # Insert related data
            self._insert_armor_data(cursor, mech_id, mech.armor)
            self._insert_weapon_data(cursor, mech_id, mech.weapons)
            self._insert_equipment_data(cursor, mech_id, mech.equipment)
            self._insert_crit_slot_data(cursor, mech_id, mech.crit_slots)
            self._insert_quirk_data(cursor, mech_id, mech.quirks)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to insert mech {mech.chassis} {mech.model}: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def find_mtf_files(megamek_path: Path) -> List[Path]:
    """Find all .mtf files in MegaMek directory"""
    mtf_files = []
    
    # Look in multiple possible locations
    search_paths = [
        megamek_path / "megamek" / "data" / "mechfiles",  # Expected location
        megamek_path / "megamek" / "testresources",       # Actual location in this repo
        megamek_path  # Fallback: search entire directory
    ]
    
    for search_path in search_paths:
        if search_path.exists():
            found_files = list(search_path.rglob("*.mtf"))
            mtf_files.extend(found_files)
            if found_files:
                print(f"Found {len(found_files)} MTF files in {search_path}")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_files = []
    for f in mtf_files:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)
    
    return unique_files

def main():
    parser = argparse.ArgumentParser(description='Seed database from MegaMek MTF files')
    parser.add_argument('--megamek-path', type=Path, required=True,
                       help='Path to MegaMek repository')
    parser.add_argument('--db-name', default='cmb_dev',
                       help='Database name')
    parser.add_argument('--dry-run', action='store_true',
                       help='Parse files but don\'t insert into database')
    parser.add_argument('--limit', type=int,
                       help='Limit number of files to process (for testing)')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Find MTF files
    mtf_files = find_mtf_files(args.megamek_path)
    if not mtf_files:
        logger.error(f"No MTF files found in {args.megamek_path}")
        return
    
    if args.limit:
        mtf_files = mtf_files[:args.limit]
    
    logger.info(f"Found {len(mtf_files)} MTF files to process")
    
    # Initialize parser and database
    parser_obj = MTFParser()
    db = None
    
    if not args.dry_run:
        db = DatabaseSeeder(args.db_name)
        try:
            db.connect()
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return
    
    # Process files
    successful = 0
    failed = 0
    
    try:
        for mtf_file in mtf_files:
            logger.info(f"Processing {mtf_file.name}...")
            
            mech_data = parser_obj.parse_mtf_file(mtf_file)
            if mech_data:
                if args.dry_run:
                    logger.info(f"  ✓ {mech_data.chassis} {mech_data.model} ({mech_data.tonnage}t)")
                    successful += 1
                else:
                    if db.insert_mech(mech_data):
                        logger.info(f"  ✓ Inserted {mech_data.chassis} {mech_data.model}")
                        successful += 1
                    else:
                        logger.error(f"  ✗ Failed to insert {mech_data.chassis} {mech_data.model}")
                        failed += 1
            else:
                logger.warning(f"  ✗ Failed to parse {mtf_file.name}")
                failed += 1
    
    finally:
        if db:
            db.close()
    
    logger.info(f"Completed: {successful} successful, {failed} failed")

if __name__ == "__main__":
    main()
