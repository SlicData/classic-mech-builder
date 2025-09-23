#!/usr/bin/env python3
"""
MTF Seeder - Clean modular version
Parses MegaMek MTF files and populates the database
"""

import argparse
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from mtf_parser import MTFParser
from database import DatabaseSeeder

def find_mtf_files(megamek_path: Path) -> list[Path]:
    """Find all MTF files in MegaMek directory"""
    mtf_files = []
    search_paths = [
        megamek_path / "megamek" / "data" / "mechfiles", 
        megamek_path / "data" / "mechfiles",
        megamek_path
    ]
    
    for search_path in search_paths:
        if search_path.exists():
            found_files = list(search_path.rglob("*.mtf"))
            mtf_files.extend(found_files)
            if found_files:
                print(f"Found {len(found_files)} MTF files in {search_path}")
    
    return list(set(mtf_files))  # Remove duplicates

def main():
    """Main seeder function"""
    parser = argparse.ArgumentParser(description='Seed database from MegaMek MTF files')
    parser.add_argument('--megamek-path', type=Path, required=True, 
                       help='Path to MegaMek installation')
    parser.add_argument('--db-name', default='cmb_dev',
                       help='Database name to connect to')
    parser.add_argument('--dry-run', action='store_true',
                       help='Parse files but do not insert into database')
    parser.add_argument('--limit', type=int,
                       help='Limit number of files to process')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Find MTF files
    mtf_files = find_mtf_files(args.megamek_path)
    if not mtf_files:
        logger.error(f"No MTF files found in {args.megamek_path}")
        return False
    
    if args.limit:
        mtf_files = mtf_files[:args.limit]
    
    logger.info(f"Found {len(mtf_files)} MTF files to process")
    
    # Initialize parser and database
    mtf_parser = MTFParser()
    db = None
    
    if not args.dry_run:
        db = DatabaseSeeder(args.db_name)
        try:
            db.connect()
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    # Process files
    successful = 0
    failed = 0
    
    try:
        for mtf_file in mtf_files:
            logger.info(f"Processing {mtf_file.name}...")
            
            mech_data = mtf_parser.parse_mtf_file(mtf_file)
            if mech_data:
                if args.dry_run:
                    logger.info(f"  ✓ Parsed {mech_data.chassis} {mech_data.model} ({mech_data.tonnage}t)")
                    logger.info(f"    Movement: Walk={mech_data.walk_mp}, Run={mech_data.run_mp}, Jump={mech_data.jump_mp}")
                    logger.info(f"    Weapons: {len(mech_data.weapons)}")
                    if args.verbose and mech_data.weapons:
                        for weapon in mech_data.weapons[:3]:  # Show first 3
                            logger.info(f"      {weapon.name} x{weapon.count} in {weapon.location}")
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
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
