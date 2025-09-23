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
├── tests/                  # 🧪 All test files
├── scripts/                # 🔧 Utility scripts
├── docs/                   # 📚 Documentation
├── data/                   # 📦 External data (MegaMek files)
└── temp/                   # 🗂️ Development files
```

#### Why This Structure?

**`src/` - Application Code**
- **Rationale**: Clear separation between source code and everything else
- **Benefit**: IDEs can focus on this directory for code intelligence
- **Scalability**: Easy to add new modules (web UI, API, etc.)

**`tests/` - Isolated Testing**
- **Problem Solved**: Test files were cluttering the root directory
- **Benefit**: Clear separation makes testing easier to manage
- **Convention**: Follows industry standard practices

**`scripts/` - Utilities**
- **Purpose**: One-off scripts, maintenance tools, deployment helpers
- **Benefit**: Keeps utility code separate from main application logic

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

### Testing
```bash
# Test modular structure
python3 tests/test_modular_structure.py

# Test specific components
python3 tests/test_steps_1_2.py

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
4. **Write tests** in `tests/`
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
```

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

4. **Import MTF data**
   ```bash
   # Test with a few files first
   python3 db/seeds/mtf_seeder.py --megamek-path /path/to/megamek --dry-run --limit 5
   
   # Full import
   python3 db/seeds/mtf_seeder.py --megamek-path /path/to/megamek
   ```

### Development Workflow

**Working on MTF parsing:**
```bash
# Test your changes
python3 tests/test_modular_structure.py

# Test specific parsing
python3 tests/test_steps_1_2.py
```

**Adding new parsing features:**
1. Create module in `src/mtf_parser/`
2. Add tests in `tests/`
3. Integrate with `base_parser.py`
4. Update database schema if needed

**Project structure:**
- Start in `src/` for main code
- Check `tests/` for examples
- See `docs/` for detailed documentation

## 🤝 Contributing

The modular architecture makes contributions easier:

1. **Pick a module** to work on
2. **Write tests first** (TDD approach)
3. **Implement feature** in focused module
4. **Update integration** in base parser
5. **Document changes** in relevant files

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

---

**Built with ❤️ for the BattleTech community**
