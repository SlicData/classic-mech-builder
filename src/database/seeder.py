#!/usr/bin/env python3
"""
Database Seeder - Handles database operations for MTF data
"""

import psycopg2
import logging
from typing import List, Optional

from mtf_parser.utils import MechData, WeaponData, ArmorData

class DatabaseSeeder:
    """Handles database insertion and management for MTF data"""
    
    def __init__(self, db_name: str = "cmb_dev"):
        self.db_name = db_name
        self.conn = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        """Connect to the database"""
        try:
            from db_config import detect_db_config
            config = detect_db_config()
            if config:
                self.conn = psycopg2.connect(**config)
                self.conn.autocommit = True
                self.logger.info(f"Connected as user: {config['user']}")
            else:
                raise Exception("Could not detect database configuration")
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            raise
    
    def insert_mech(self, mech: MechData) -> bool:
        """Insert a complete mech with all related data"""
        try:
            cursor = self.conn.cursor()
            mech_id = self._insert_mech_main(cursor, mech)
            if not mech_id: 
                return False
            
            # Insert related data
            self._insert_armor_data(cursor, mech_id, mech.armor)
            self._insert_weapon_data(cursor, mech_id, mech.weapons)
            cursor.close()
            return True
        except Exception as e:
            self.logger.error(f"Failed to insert mech {mech.chassis} {mech.model}: {e}")
            return False
    
    def _insert_mech_main(self, cursor, mech: MechData) -> Optional[int]:
        """Insert main mech record"""
        sql = """INSERT INTO mech (chassis, model, tech_base, era, rules_level, tonnage, battle_value, 
                 walk_mp, run_mp, jump_mp, engine_type, engine_rating, heat_sinks, armor_type) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                 ON CONFLICT (chassis, model) DO UPDATE SET tonnage = EXCLUDED.tonnage, updated_at = NOW()
                 RETURNING id"""
        
        cursor.execute(sql, (mech.chassis, mech.model, mech.tech_base.value, mech.era.value,
                           mech.rules_level, mech.tonnage, mech.battle_value, mech.walk_mp, mech.run_mp,
                           mech.jump_mp, mech.engine_type.value, mech.engine_rating, mech.heat_sinks,
                           mech.armor_type.value))
        
        result = cursor.fetchone()
        return result[0] if result else None
    
    def _insert_armor_data(self, cursor, mech_id: int, armor_data: List[ArmorData]):
        """Insert armor data for a mech"""
        cursor.execute("DELETE FROM mech_armor WHERE mech_id = %s", (mech_id,))
        for armor in armor_data:
            cursor.execute("INSERT INTO mech_armor (mech_id, loc, armor_front, armor_rear, internal) VALUES (%s, %s, %s, %s, %s)",
                          (mech_id, armor.location, armor.armor_front, armor.armor_rear, armor.internal))
    
    def _insert_weapon_data(self, cursor, mech_id: int, weapons: List[WeaponData]):
        """Insert weapon data for a mech"""
        cursor.execute("DELETE FROM mech_weapon WHERE mech_id = %s", (mech_id,))
        for weapon in weapons:
            weapon_id = self._get_or_create_weapon(cursor, weapon.name)
            if weapon_id:
                cursor.execute("INSERT INTO mech_weapon (mech_id, weapon_id, location, count) VALUES (%s, %s, %s, %s)",
                              (mech_id, weapon_id, weapon.location, weapon.count))
    
    def _get_or_create_weapon(self, cursor, weapon_name: str) -> Optional[int]:
        """Get or create weapon in catalog"""
        cursor.execute("SELECT id FROM weapon_catalog WHERE name = %s", (weapon_name,))
        result = cursor.fetchone()
        if result: 
            return result[0]
        
        # Import weapon parser for classification
        from mtf_parser.weapon_parser import WeaponParser
        weapon_parser = WeaponParser(self.logger)
        
        weapon_class = weapon_parser.classify_weapon_type(weapon_name)
        tech_base = weapon_parser.determine_tech_base(weapon_name)
        
        cursor.execute("INSERT INTO weapon_catalog (name, class, tech_base) VALUES (%s, %s, %s) RETURNING id",
                      (weapon_name, weapon_class, tech_base))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def close(self):
        """Close database connection"""
        if self.conn: 
            self.conn.close()
