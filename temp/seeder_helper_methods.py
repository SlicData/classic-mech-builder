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

