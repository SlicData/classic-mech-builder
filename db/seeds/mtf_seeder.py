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
from dataclasses import dataclass
from enum import Enum

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
                cost_cbill=self._parse_cost(content)
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
        match = re.search(r'walk:\s*(\d+)', content, re.IGNORECASE)
        return int(match.group(1)) if match else 0
    
    def _parse_run_mp(self, content: str) -> int:
        """Parse run speed or calculate from walk"""
        match = re.search(r'run:\s*(\d+)', content, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        # Calculate from walk MP
        walk_mp = self._parse_walk_mp(content)
        return int(walk_mp * 1.5)  # Standard BattleTech rule
    
    def _parse_jump_mp(self, content: str) -> int:
        """Parse jump speed"""
        match = re.search(r'jump:\s*(\d+)', content, re.IGNORECASE)
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

class DatabaseSeeder:
    def __init__(self, db_name: str = "cmb_dev"):
        self.db_name = db_name
        self.conn = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            # Try different connection methods
            connection_params = {
                'host': 'localhost',
                'database': self.db_name
            }
            
            # First try with system user (most common on macOS)
            import getpass
            system_user = getpass.getuser()
            
            try:
                connection_params['user'] = system_user
                self.conn = psycopg2.connect(**connection_params)
                self.conn.autocommit = True
                self.logger.info(f"Connected to database as user: {system_user}")
                return
            except psycopg2.OperationalError:
                pass
            
            # Fallback: try postgres user
            try:
                connection_params['user'] = 'postgres'
                self.conn = psycopg2.connect(**connection_params)
                self.conn.autocommit = True
                self.logger.info("Connected to database as user: postgres")
                return
            except psycopg2.OperationalError:
                pass
            
            # Final fallback: no explicit user (use peer authentication)
            del connection_params['user']
            self.conn = psycopg2.connect(**connection_params)
            self.conn.autocommit = True
            self.logger.info("Connected to database using default authentication")
            
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            self.logger.error("Try running: psql cmb_dev -c 'SELECT current_user;' to check your database user")
            raise
    
    def insert_mech(self, mech: MechData) -> bool:
        """Insert mech data into database"""
        try:
            cursor = self.conn.cursor()
            
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
            """
            
            cursor.execute(sql, (
                mech.chassis, mech.model, mech.tech_base.value, mech.era.value,
                mech.rules_level, mech.tonnage, mech.battle_value,
                mech.walk_mp, mech.run_mp, mech.jump_mp,
                mech.engine_type.value, mech.engine_rating, mech.heat_sinks,
                mech.armor_type.value, mech.role, mech.year, mech.source,
                mech.cost_cbill
            ))
            
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
