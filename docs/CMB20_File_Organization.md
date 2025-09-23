# CMB-20 File Organization

This document explains the cleaned up file structure after CMB-20 completion.

## Production Files

### Scripts
- `scripts/seeding/mtf_seeder.py` - Production MTF seeder for importing MegaMek data

### Core Implementation  
- `src/mtf_parser/` - Complete MTF parsing system
- `src/database/` - Database seeder implementation
- `db/seeds/` - Database seeding utilities and configuration

## Test Files

### Integration Tests
- `tests/integration/test_mtf_seeder.py` - Complete integration test for MTF seeder
- `tests/test_cmb20_verification.py` - Verification script for CMB-20 setup

### Test Data
- `data/test_mech.mtf` - Test MTF file (Archer ARC-2R)

## Documentation
- `docs/CMB20_Implementation.md` - Complete CMB-20 implementation documentation

## Usage

### Run Integration Test
```bash
cd /Users/justi/classic-mech-builder
python3 tests/integration/test_mtf_seeder.py
```

### Run Verification
```bash
python3 tests/test_cmb20_verification.py  
```

### Run Production Seeder
```bash
# Test mode
python3 scripts/seeding/mtf_seeder.py --test

# Single file
python3 scripts/seeding/mtf_seeder.py --single-file data/test_mech.mtf

# Full MegaMek import
python3 scripts/seeding/mtf_seeder.py --megamek-path /path/to/megamek
```

## Temporary Files

Temporary test files have been moved to `temp/` directory and can be deleted:
- `temp/test_imports.py`
- `temp/test_minimal.py` 
- `temp/test_step_by_step.py`
- `temp/cmb20_final_test.py`
- `temp/check_enums.py`

## Clean Directory Structure

The root directory is now clean with only essential files:
- Configuration files (Makefile, .gitignore, etc.)
- Documentation (README.md, LICENSE)
- Organized subdirectories (src/, tests/, scripts/, docs/, data/, db/)
