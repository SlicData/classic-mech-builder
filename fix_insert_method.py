    def insert_mech(self, mech: MechData) -> bool:
        """Insert complete mech data into database"""
        try:
            cursor = self.conn.cursor()
            
            # Insert main mech record first
            mech_id = self._insert_mech_main(cursor, mech)
            if not mech_id:
                return False
            
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
