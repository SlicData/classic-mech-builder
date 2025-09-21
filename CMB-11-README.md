# CMB-11: Query Validation

This directory contains comprehensive query validation tests for the classic-mech-builder database schema.

## Files Created

- **`test_queries.sql`** - Comprehensive SQL test suite covering all requirements
- **`test_runner.py`** - Automated Python test runner with performance validation  
- **`config_template.py`** - Database configuration template
- **Updated `Makefile`** - Added `test-queries` and `validate-queries` targets

## Test Coverage

### Requirement 1: Query by name returns correct mech
- Exact chassis matching
- Exact chassis + model matching  
- Fuzzy name search using trigram indexes
- Case-insensitive searches
- Partial model searches (common use case)

### Requirement 2: Query by era/tech level returns only matching mechs
- Era filtering (clan_invasion, dark_age, etc.)
- Tech base filtering (inner_sphere, clan, mixed)
- Combined era + tech base queries
- Rules level filtering
- Multiple era searches

### Requirement 3: Query performance (<200ms for 1,000 records)
- Large result sets with index usage validation
- Battle value range queries
- Complex multi-table joins
- Trigram search performance
- Uses EXPLAIN ANALYZE for query plan inspection

### Requirement 4: Representative queries covering all tables
- **mech** - Core mech data with all attributes
- **mech_armor** - Armor distribution by location
- **mech_weapon** - Weapon loadouts and counts
- **mech_equipment** - Equipment installations
- **mech_crit_slot** - Critical slot layouts
- **mech_quirk** - Mech quirks and special rules
- **weapon_catalog** - Weapon definitions and stats
- **equipment_catalog** - Equipment definitions
- **ammo_catalog** - Ammunition types

### Edge Case Testing
- Mechs with no weapons (should be rare/none)
- Invalid rear armor locations (constraint validation)
- Critical slot overflow validation
- Movement profile edge cases
- Data integrity validation
- Constraint violation detection

### Data Validation
- Enum value verification
- Orphaned record detection
- Constraint compliance checking
- Referential integrity validation

## Usage

### Setup
1. Copy configuration template:
   ```bash
   cp config_template.py config.py
   # Edit config.py with your database settings
   ```

2. Ensure your database is running and has the seeded mech data

### Running Tests

**Manual SQL Testing:**
```bash
make test-queries
```
This runs the raw SQL file against your database for manual inspection.

**Automated Validation:**
```bash
make validate-queries
```
This runs the Python test suite with:
- Automated pass/fail validation
- Performance timing
- Result counting
- Comprehensive test reporting

**Direct Python execution:**
```bash
python3 test_runner.py
```

### Expected Results

With 4,132 mechs seeded from MegaMek data, you should see:
- All name-based queries returning appropriate results
- Era/tech filtering working correctly
- All performance tests under 200ms
- Complete coverage of all schema tables
- Zero constraint violations
- Zero orphaned records

### Performance Benchmarks

Target performance thresholds:
- Simple queries: < 50ms
- Complex multi-table joins: < 200ms
- Aggregation queries: < 100ms
- Text search queries: < 150ms

## Test Categories

### 1. Functional Tests
Validate that queries return correct data:
- Exact matches work
- Filtering works correctly
- Joins return expected relationships
- Data integrity is maintained

### 2. Performance Tests  
Validate query execution speed:
- Large result sets
- Complex joins
- Index utilization
- Query plan efficiency

### 3. Edge Case Tests
Validate system behavior with unusual data:
- Empty result sets
- Constraint boundaries
- Missing relationships
- Data validation rules

### 4. Integration Tests
Validate multi-table operations:
- Complete mech profiles
- Cross-table aggregations
- Complex filtering combinations
- Real-world query patterns

## Files Based on MTF Analysis

The test suite specifically validates data patterns found in your MTF examples:

**From King Crab KGC-009C:**
- Mixed tech base handling
- Era: 3143 (dark_age)
- Complex weapon loadouts
- Rear armor on torsos only

**From Kodiak II variants:**  
- Clan tech base
- Command mech quirks
- Heavy assault mech profiles

**From Prey Seeker PY-SR20:**
- Light mech mobility (12 walk MP)
- Inner Sphere tech
- Minimal armor profiles

**From various mechs:**
- All location types (HD, CT, LT, RT, LA, RA, LL, RL)
- Weapon diversity (ballistic, energy, missile)
- Equipment variety (ECM, targeting computers, etc.)
- Critical slot complexity

## Success Criteria

CMB-11 is complete when:
- [ ] All name-based queries return correct mechs
- [ ] Era/tech filtering works accurately  
- [ ] All queries execute under 200ms for 1,000 records
- [ ] At least 3 representative queries pass validation
- [ ] All edge cases handled properly
- [ ] Performance benchmarks met
- [ ] Zero data integrity violations

Run `make validate-queries` to get a comprehensive PASS/FAIL report!
