# CMB-20.4: Critical Slot Parsing & Database Integration

## 🎯 Objective
Implement complete critical slot parsing and database integration to populate the `mech_crit_slot` table.

## 📊 Current Status
- **Status**: 🟡 Foundation exists, enum mapping needs fix
- **Current Issue**: `crit_item_type` enum mapping disabled due to conflicts
- **Log Evidence**: `DEBUG - Skipping X crit slots for mech Y (enum issue)`

## 🔧 Technical Requirements

### 1. Fix Enum Mapping
**Valid `crit_item_type` values:**
```sql
'weapon', 'equipment', 'ammo', 'engine', 'gyro', 'life_support', 
'sensors', 'cockpit', 'heatsink', 'jump_jet', 'empty'
```

**Current Parser Issues:**
- Using `'actuator'` instead of `'equipment'` 
- Need mapping for BattleTech components

### 2. Enhanced Crit Slot Parsing
**MTF Format Example:**
```
Left Arm:
Shoulder
Upper Arm Actuator  
Lower Arm Actuator
Hand Actuator
Medium Laser
-Empty-
```

**Required Parsing:**
- Parse location sections (Left Arm, Right Torso, etc.)
- Extract equipment in each slot (1-12 for most locations)
- Classify equipment types correctly
- Handle empty slots properly

### 3. Database Integration
**Tables to populate:**
- `mech_crit_slot` - Main critical slot data
- Link to `weapon_catalog`, `equipment_catalog`, `ammo_catalog` as needed

**Constraints to satisfy:**
- Slot index limits by location (HD: 1-6, others: 1-12)
- Proper foreign key references based on item_type
- Unique constraint: (mech_id, loc, slot_index)

## 📋 Implementation Tasks

### Phase 1: Fix Current Parser
- [ ] Update `CritSlotParser.classify_equipment()` enum mapping
- [ ] Map `'actuator'` → `'equipment'` 
- [ ] Add classifications for gyro, life_support, sensors, etc.
- [ ] Re-enable crit slot insertion in `DatabaseSeeder`

### Phase 2: Enhanced Parsing  
- [ ] Improve location header detection
- [ ] Better equipment name normalization
- [ ] Handle weapons vs equipment classification
- [ ] Proper ammo detection

### Phase 3: Database Links
- [ ] Link weapons to `weapon_catalog`
- [ ] Link equipment to `equipment_catalog` 
- [ ] Link ammo to `ammo_catalog`
- [ ] Validate foreign key constraints

### Phase 4: Testing & Validation
- [ ] Test with sample MTF files
- [ ] Verify slot counts match expected values
- [ ] Check proper classification distribution
- [ ] Validate database constraints

## 🎯 Success Criteria

### Quantitative Goals
- [ ] `mech_crit_slot` table populated (expect thousands of records)
- [ ] 95%+ of crit slots properly classified  
- [ ] All foreign key references valid
- [ ] No constraint violations

### Quality Metrics
- [ ] Proper equipment classification (weapons vs equipment vs ammo)
- [ ] Correct slot indexing (1-based, location-appropriate)
- [ ] Valid location mapping (LA, RA, CT, etc.)
- [ ] Empty slots handled correctly

## 🔍 Testing Strategy

### Test Cases
1. **Simple Mech**: Archer ARC-2R (included test file)
2. **Complex Mech**: Clan OmniMech with equipment variations  
3. **Edge Cases**: Mechs with jump jets, special equipment
4. **Validation**: Check against known BattleTech record sheets

### Verification Queries
```sql
-- Check crit slot counts by location
SELECT loc, COUNT(*) FROM mech_crit_slot GROUP BY loc;

-- Check item type distribution  
SELECT item_type, COUNT(*) FROM mech_crit_slot GROUP BY item_type;

-- Find mechs with expected crit slot counts
SELECT m.chassis, m.model, COUNT(mcs.*)
FROM mech m 
LEFT JOIN mech_crit_slot mcs ON m.id = mcs.mech_id
GROUP BY m.id, m.chassis, m.model
HAVING COUNT(mcs.*) > 0;
```

## 📈 Expected Impact

**Database Population:**
- ~50,000+ critical slot records (12 slots × 8 locations × 4,000+ mechs)
- Complete internal structure representation
- Foundation for equipment parsing (CMB-20.5)

**Success Rate Improvement:**
- Addresses major gap in MTF parsing
- Enables complete mech representation
- Sets up remaining subtasks for success

## 🔗 Dependencies & Follow-ups

**Depends on:**
- CMB-20.3 ✅ (Complete - provides test data)

**Enables:**
- CMB-20.5 (Equipment Parsing) - will use crit slot data
- CMB-20.6 (Ammo Parsing) - will link to crit slots
- Complete MTF representation

---

**Priority**: High
**Estimated Effort**: Medium
**Ready to Start**: Yes ✅
