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
                    logger.info(f"    Weapons: {len(mech_data.weapons)}, Armor: {len(mech_data.armor)}, Equipment: {len(mech_data.equipment)}")
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
