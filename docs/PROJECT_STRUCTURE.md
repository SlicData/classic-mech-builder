# Classic Mech Builder - Project Structure

## Directory Organization

```
classic-mech-builder/
├── src/                           # Main application source code
│   ├── mtf_parser/               # Modular MTF file parser
│   │   ├── __init__.py
│   │   ├── base_parser.py        # Main MTF parser orchestrator  
│   │   ├── movement_parser.py    # Movement parsing (CMB-20 Step 1)
│   │   ├── weapon_parser.py      # Weapon parsing (CMB-20 Step 2)
│   │   └── utils.py             # Shared utilities and data classes
│   └── database/                 # Database operations
│       ├── __init__.py
│       └── seeder.py            # Database insertion logic
├── db/                           # Database structure
│   ├── migrations/              # Database migrations
│   └── seeds/                   # Database seeding scripts
│       └── mtf_seeder.py       # Main MTF seeder (clean version)
├── tests/                        # All test files
│   ├── test_*.py               # Various test scripts
│   └── test_queries.sql        # Test SQL queries
├── scripts/                      # Utility scripts
│   └── cleanup.py              # Directory cleanup script
├── docs/                         # Documentation
│   └── PROJECT_STRUCTURE.md   # This file
├── data/                         # External data
│   └── megamek/                # MegaMek MTF files
└── temp/                         # Temporary development files
```

## Key Improvements Made

### Modular Design
- **Separated concerns**: Movement parsing, weapon parsing, database operations are now in separate modules
- **Easier testing**: Each component can be tested independently
- **Better maintainability**: No more monolithic files
- **Scalable**: Easy to add new parsing modules (armor, engine, etc.)

### Clean Structure
- **No more root clutter**: All test files moved to `tests/`
- **Logical organization**: Source code in `src/`, utilities in `scripts/`
- **Clear separation**: Database operations separate from parsing logic

### Enhanced Features

#### Step 1: Movement Parsing ✅
- Fixed regex patterns for MTF format
- Added validation (walk_mp > 0)
- Enhanced error logging and debugging

#### Step 2: Weapon Parsing ✅
- Support for multiple weapon formats
- Weapon name normalization and aliases
- Location standardization
- Enhanced weapon classification

## Usage

### Running the Seeder
```bash
# Dry run to test parsing
python3 db/seeds/mtf_seeder.py --megamek-path ./data/megamek --dry-run --limit 5

# Full database seeding
python3 db/seeds/mtf_seeder.py --megamek-path ./data/megamek --verbose

# With custom database
python3 db/seeds/mtf_seeder.py --megamek-path ./data/megamek --db-name cmb_prod
```

### Running Tests
```bash
# Test specific components
python3 tests/test_steps_1_2.py

# Test movement parsing
python3 -c "from src.mtf_parser.movement_parser import MovementParser; print('Movement parser ready')"
```

## Next Steps

Ready for **CMB-20 Step 3** options:
- **Armor System Enhancement**: Improve armor parsing and validation
- **Engine and Heat Sink Parsing**: Parse engine types and heat sink data
- **Critical Slot Parsing**: Parse equipment placement in critical slots
- **Database Schema Improvements**: Enhance database structure

The modular design makes adding new features much easier!
