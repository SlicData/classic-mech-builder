# Classic Mech Builder

A web application for building and managing BattleTech collections, with automated data import from MegaMek MTF files.

## 🏗️ Project Architecture

### Design Philosophy

This project follows a **modular, maintainable architecture** designed to solve real-world development challenges:

#### Problem: Monolithic Code Issues
- **File size limits**: Large parsing files became unmanageable
- **Testing difficulties**: Hard to test individual components
- **Merge conflicts**: Multiple developers working on same large files
- **Code organization**: Related functionality scattered across large files

#### Solution: Modular Architecture
- **Separation of concerns**: Each module has a single responsibility
- **Independent testing**: Components can be tested in isolation
- **Scalable development**: Easy to add new features without touching existing code
- **Clean interfaces**: Well-defined APIs between modules

### Directory Structure

```
classic-mech-builder/
├── src/                    # 🎯 Main application source code
│   ├── mtf_parser/        # MTF file parsing (modular design)
│   └── database/          # Database operations
├── db/                     # 🗄️ Database structure
│   ├── migrations/        # Schema migrations
│   └── seeds/             # Data seeding scripts
├── tests/                  # 🧪 Organized test suite
│   ├── unit/              # Unit tests for individual components
│   ├── integration/       # Integration tests for system components
│   ├── database/          # Database-specific performance and validation tests
│   ├── test_modular_structure.py    # Core module import tests
│   ├── test_complete_integration.py # Comprehensive integration tests
│   └── test_steps_1_2.py           # Core parsing functionality tests
├── scripts/                # 🔧 Utility and maintenance scripts
│   ├── database/          # Database maintenance and status checks
│   ├── deployment/        # Deployment and release scripts
│   ├── diagnostics/       # Debugging tools and system health checks
│   └── seeding/           # Data import and seeding utilities
├── docs/                   # 📚 Documentation
└── data/                   # 📦 External data (MegaMek files)
    └── megamek/           # MegaMek submodule with MTF files
```

#### Why This Structure?

**`src/` - Application Code**
- **Rationale**: Clear separation between source code and everything else
- **Benefit**: IDEs can focus on this directory for code intelligence
- **Scalability**: Easy to add new modules (web UI, API, etc.)

**`tests/` - Organized Test Suite**
- **Problem Solved**: Test files were scattered and hard to manage
- **Solution**: Organized by test type for easy navigation
- **Subdirectories**:
  - `unit/` - Test individual components in isolation
  - `integration/` - Test system integration and workflows
  - `database/` - Performance tests, query validation, and DB health checks
- **Benefit**: Easy to find and run specific types of tests
- **Convention**: Follows industry standard testing practices

**`scripts/` - Organized Utilities**
- **Purpose**: All utility scripts organized by function
- **Subdirectories**:
  - `database/` - Database maintenance, status checks, utilities
  - `deployment/` - Build, deploy, and release automation
  - `diagnostics/` - Debugging tools, performance analysis, health checks
  - `seeding/` - Data import and seeding utilities
- **Benefit**: Easy to find the right tool for the job

**Modular `src/mtf_parser/`**
- **Problem Solved**: Original parser was a 500+ line monolithic file
- **Solution**: Broken into focused modules:
  - `movement_parser.py` - Handles movement values (Walk/Run/Jump MP)
  - `weapon_parser.py` - Handles weapon parsing and normalization
  - `base_parser.py` - Orchestrates all parsing operations
  - `utils.py` - Shared utilities and data structures

### Architecture Overview

The application follows a **data pipeline architecture**:
1. **Data Ingestion**: MTF files → Structured data objects
2. **Data Processing**: Validation, normalization, classification  
3. **Data Storage**: Relational database with proper relationships
4. **Data Access**: Clean APIs for web application consumption

## 🛠️ Development Workflow

### Running the MTF Seeder
```bash
# Test parsing without database changes
python3 db/seeds/mtf_seeder.py --megamek-path ./data/megamek --dry-run --limit 5

# Full database import with verbose logging
python3 db/seeds/mtf_seeder.py --megamek-path ./data/megamek --verbose

# Import to specific database
python3 db/seeds/mtf_seeder.py --megamek-path ./data/megamek --db-name cmb_production
```

### Common Scripts

#### Database Management
```bash
# Check database status
python3 scripts/database/check_database_status.py

# Run diagnostics
python3 scripts/diagnostics/cmb20_diagnostic.py

# Verify system setup
python3 scripts/diagnostics/cmb20_verification.py
```

#### Development Tools
```bash
# Create configuration from template
cp config_template.py config.py

# Deploy changes
bash scripts/deployment/push_cmb20.sh
```

### Testing

The organized test suite makes it easy to run specific types of tests:

#### Unit Tests
```bash
# Test individual components
python3 tests/unit/test_movement_parsing.py
python3 tests/unit/test_parser.py
```

#### Integration Tests
```bash
# Test system integration
python3 tests/integration/test_cmb20_integration.py
python3 tests/integration/test_complete_seeder.py
python3 tests/integration/test_seeder.py
```

#### Database Tests
```bash
# Run database performance and validation tests
python3 tests/database/test_runner.py

# Run SQL validation queries
psql -d cmb_dev -f tests/database/test_queries.sql
```

#### Core Tests
```bash
# Test modular structure
python3 tests/test_modular_structure.py

# Test core parsing functionality
python3 tests/test_steps_1_2.py

# Comprehensive integration test
python3 tests/test_complete_integration.py

# Test movement parsing specifically
python3 -c "
import sys; sys.path.insert(0, 'src')
from mtf_parser.movement_parser import MovementParser
print('✅ Movement parser working')
"
```

### Development Best Practices

#### Adding New Parsing Features
1. **Create a new parser module** in `src/mtf_parser/`
2. **Follow the established pattern**: 
   - Take logger in constructor
   - Return structured data
   - Handle errors gracefully
3. **Add to base parser** orchestration
4. **Write tests** in appropriate `tests/` subdirectory
5. **Update database integration** if needed

#### Example: Adding Armor Parsing
```python
# src/mtf_parser/armor_parser.py
class ArmorParser:
    def __init__(self, logger):
        self.logger = logger
    
    def parse_armor(self, content):
        # Implementation here
        pass

# Add to base_parser.py
from .armor_parser import ArmorParser

class MTFParser:
    def __init__(self):
        self.armor_parser = ArmorParser(self.logger)

# Add unit test in tests/unit/test_armor_parsing.py
# Add integration test in tests/integration/ if needed
```

#### Adding New Utility Scripts
1. **Determine the script's purpose** and place in appropriate `scripts/` subdirectory:
   - Database-related → `scripts/database/`
   - Deployment/build → `scripts/deployment/`
   - Debugging/analysis → `scripts/diagnostics/`
   - Data import → `scripts/seeding/`
2. **Use descriptive names** that indicate function
3. **Add documentation** at the top of the file
4. **Update this README** if it's a commonly used script

#### Writing Tests
1. **Unit tests** → `tests/unit/` - Test individual functions/classes
2. **Integration tests** → `tests/integration/` - Test component interactions
3. **Database tests** → `tests/database/` - Test queries, performance, validation
4. **Follow naming conventions** - `test_*.py` for all test files
5. **Keep tests focused** - One test file per component/feature

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL database
- MegaMek MTF files (for data import)

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone [repository-url]
   cd classic-mech-builder
   ```

2. **Set up the database**
   ```bash
   # Create database
   createdb cmb_dev
   
   # Run migrations
   make migrate
   ```

3. **Configure database connection**
   ```bash
   # Copy template and edit with your settings
   cp config_template.py config.py
   ```

4. **Verify setup**
   ```bash
   # Run system verification
   python3 scripts/diagnostics/cmb20_verification.py
   ```

5. **Import MTF data**
   ```bash
   # Test with a few files first
   python3 db/seeds/mtf_seeder.py --megamek-path ./data/megamek --dry-run --limit 5
   
   # Full import
   python3 db/seeds/mtf_seeder.py --megamek-path ./data/megamek
   ```

6. **Validate installation**
   ```bash
   # Check database connectivity
   python3 scripts/database/check_database_status.py
   
   # Run comprehensive tests
   python3 tests/test_complete_integration.py
   
   # Run database validation
   python3 tests/database/test_runner.py
   ```

### Development Workflow

**Working on MTF parsing:**
```bash
# Test your changes
python3 tests/test_modular_structure.py

# Test specific parsing
python3 tests/test_steps_1_2.py

# Run unit tests
python3 tests/unit/test_movement_parsing.py
```

**Working on database integration:**
```bash
# Test integration
python3 tests/integration/test_cmb20_integration.py

# Run database tests
python3 tests/database/test_runner.py
```

**Adding new parsing features:**
1. Create module in `src/mtf_parser/`
2. Add unit tests in `tests/unit/`
3. Add integration tests in `tests/integration/` if needed
4. Integrate with `base_parser.py`
5. Update database schema if needed

**Adding utility scripts:**
1. Place in appropriate `scripts/` subdirectory
2. Follow naming conventions
3. Document usage and purpose

**Project navigation:**
- Start in `src/` for main code
- Check `tests/unit/` for component examples
- See `tests/integration/` for system tests
- Use `scripts/` for utilities and maintenance
- Refer to `docs/` for detailed documentation

## 🤝 Contributing

The modular architecture and organized structure make contributions easier:

1. **Pick a module** to work on
2. **Write tests first** (TDD approach) in appropriate test subdirectory
3. **Implement feature** in focused module
4. **Update integration** in base parser
5. **Run test suite** to verify changes
6. **Document changes** in relevant files

### File Organization Guidelines

- **Keep the root directory clean** - only essential files like README, LICENSE, Makefile
- **Use the organized structure** - place files in their logical subdirectories
- **Follow naming conventions** - descriptive names that indicate purpose
- **Write appropriate tests** - unit tests for components, integration tests for workflows
- **Update documentation** when adding new scripts or modules

### Testing Guidelines

- **Unit tests** should be fast, focused, and test one thing
- **Integration tests** should test realistic workflows
- **Database tests** should validate performance and data integrity
- **All tests** should be runnable independently
- **Test files** should have clear, descriptive names

## 📋 Technical Decisions

### Why Python for MTF Parsing?
- **Excellent regex support** for complex text parsing
- **Strong ecosystem** for data manipulation
- **Easy database integration** with psycopg2
- **Readable code** for maintenance

### Why Modular Design?
- **Prevents file size issues** that were blocking development
- **Enables parallel development** by multiple contributors
- **Makes testing easier** with focused test suites
- **Follows SOLID principles** for maintainable code

### Why This Directory Structure?
- **Industry standard** practices
- **Tool-friendly** (IDEs, linters, CI/CD)
- **Scalable** for future growth
- **Clear separation** of concerns
- **Easy navigation** - find what you need quickly
- **Organized testing** - run specific test types easily

## 📝 License

[License information here]

---

**Built with ❤️ for the BattleTech community**
