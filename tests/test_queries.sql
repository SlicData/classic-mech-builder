-- CMB-11: Query Validation Test Suite
-- Comprehensive tests for mech schema queries covering all tables and edge cases

-- =========================
-- REQUIREMENT 1: Query by name returns correct mech
-- =========================

-- Test 1.1: Exact chassis match
SELECT chassis, model, tonnage, era, tech_base 
FROM mech 
WHERE chassis = 'King Crab'
ORDER BY model;

-- Test 1.2: Exact chassis + model match  
SELECT chassis, model, tonnage, battle_value, era
FROM mech 
WHERE chassis = 'King Crab' AND model = 'KGC-009C';

-- Test 1.3: Fuzzy name search using trigram index
SELECT chassis, model, tonnage, era,
       similarity(chassis || ' ' || model, 'King Crab') as sim_score
FROM mech 
WHERE (chassis || ' ' || model) % 'King Crab'
ORDER BY sim_score DESC
LIMIT 10;

-- Test 1.4: Case-insensitive search
SELECT chassis, model, tonnage
FROM mech 
WHERE UPPER(chassis) = UPPER('kodiak ii')
ORDER BY model;

-- Test 1.5: Partial model search (common use case)
SELECT chassis, model, tonnage, era
FROM mech 
WHERE model LIKE 'ARC-%'
ORDER BY chassis, model;

-- =========================
-- REQUIREMENT 2: Query by era/tech level returns only matching mechs
-- =========================

-- Test 2.1: Era filtering
SELECT era, COUNT(*) as mech_count
FROM mech 
WHERE era = 'clan_invasion'
GROUP BY era;

-- Test 2.2: Tech base filtering  
SELECT tech_base, COUNT(*) as mech_count
FROM mech 
WHERE tech_base = 'clan'
GROUP BY tech_base;

-- Test 2.3: Combined era + tech base
SELECT chassis, model, era, tech_base, tonnage
FROM mech 
WHERE era = 'dark_age' AND tech_base = 'inner_sphere'
ORDER BY tonnage DESC
LIMIT 10;

-- Test 2.4: Rules level filtering
SELECT rules_level, COUNT(*) as mech_count
FROM mech 
WHERE rules_level <= 2
GROUP BY rules_level
ORDER BY rules_level;

-- Test 2.5: Multiple era search
SELECT chassis, model, era, "year"
FROM mech 
WHERE era IN ('clan_invasion', 'civil_war', 'jihad')
ORDER BY era, "year" NULLS LAST;

-- =========================
-- REQUIREMENT 3: Performance tests (<200ms for 1,000 records)
-- =========================

-- Test 3.1: Large result set with index usage (tonnage)
EXPLAIN ANALYZE
SELECT chassis, model, tonnage, battle_value
FROM mech 
WHERE tonnage BETWEEN 20 AND 100
ORDER BY tonnage, battle_value DESC;

-- Test 3.2: Battle value range query (should use index)
EXPLAIN ANALYZE  
SELECT chassis, model, battle_value, tonnage
FROM mech 
WHERE battle_value BETWEEN 1000 AND 3000
ORDER BY battle_value DESC;

-- Test 3.3: Complex multi-table join (performance critical)
EXPLAIN ANALYZE
SELECT m.chassis, m.model, m.tonnage, 
       COUNT(mw.weapon_id) as weapon_count,
       COUNT(me.equipment_id) as equipment_count
FROM mech m
LEFT JOIN mech_weapon mw ON m.id = mw.mech_id
LEFT JOIN mech_equipment me ON m.id = me.mech_id
WHERE m.tonnage >= 50
GROUP BY m.id, m.chassis, m.model, m.tonnage
ORDER BY m.tonnage DESC
LIMIT 1000;

-- Test 3.4: Trigram search performance
EXPLAIN ANALYZE
SELECT chassis, model, tonnage
FROM mech 
WHERE (chassis || ' ' || model) % 'Archer'
ORDER BY similarity(chassis || ' ' || model, 'Archer') DESC
LIMIT 20;

-- =========================
-- REQUIREMENT 4: Representative queries covering all tables
-- =========================

-- Test 4.1: Complete mech profile with all related data
SELECT 
    m.chassis,
    m.model, 
    m.tonnage,
    m.era,
    m.tech_base,
    m.walk_mp,
    m.run_mp,
    m.jump_mp,
    m.engine_type,
    m.armor_type,
    m.battle_value,
    COUNT(DISTINCT mw.weapon_id) as unique_weapons,
    COUNT(DISTINCT me.equipment_id) as unique_equipment,
    COUNT(DISTINCT ma.loc) as armored_locations,
    COUNT(DISTINCT mq.quirk) as quirk_count
FROM mech m
LEFT JOIN mech_weapon mw ON m.id = mw.mech_id
LEFT JOIN mech_equipment me ON m.id = me.mech_id  
LEFT JOIN mech_armor ma ON m.id = ma.mech_id
LEFT JOIN mech_quirk mq ON m.id = mq.mech_id
WHERE m.chassis = 'Archer' AND m.model = 'ARC-2K'
GROUP BY m.id, m.chassis, m.model, m.tonnage, m.era, m.tech_base, 
         m.walk_mp, m.run_mp, m.jump_mp, m.engine_type, m.armor_type, m.battle_value;

-- Test 4.2: Armor distribution analysis
SELECT 
    m.chassis,
    m.model,
    ma.loc,
    ma.armor_front,
    ma.armor_rear,
    ma.internal
FROM mech m
JOIN mech_armor ma ON m.id = ma.mech_id
WHERE m.chassis = 'Banshee' AND m.model = 'BNC-3MC'
ORDER BY ma.loc;

-- Test 4.3: Weapon loadout analysis
SELECT 
    m.chassis,
    m.model,
    wc.name as weapon_name,
    wc.class as weapon_class,
    mw.count as weapon_count,
    wc.heat,
    wc.dmg_short
FROM mech m
JOIN mech_weapon mw ON m.id = mw.mech_id
JOIN weapon_catalog wc ON mw.weapon_id = wc.id
WHERE m.tonnage = 100  -- Assault mechs
ORDER BY m.chassis, m.model, wc.class, wc.name;

-- Test 4.4: Critical slot layout
SELECT 
    m.chassis,
    m.model,
    mcs.loc,
    mcs.slot_index,
    mcs.item_type,
    mcs.display_name,
    wc.name as weapon_name,
    ec.name as equipment_name
FROM mech m
JOIN mech_crit_slot mcs ON m.id = mcs.mech_id
LEFT JOIN weapon_catalog wc ON mcs.weapon_id = wc.id
LEFT JOIN equipment_catalog ec ON mcs.equipment_id = ec.id
WHERE m.chassis = 'Prey Seeker' AND m.model = 'PY-SR20'
ORDER BY mcs.loc, mcs.slot_index;

-- Test 4.5: Tech base and era distribution
SELECT 
    tech_base,
    era,
    COUNT(*) as mech_count,
    AVG(tonnage) as avg_tonnage,
    AVG(battle_value) as avg_bv
FROM mech
GROUP BY tech_base, era
ORDER BY tech_base, era;

-- =========================
-- EDGE CASE TESTS
-- =========================

-- Test 5.1: Mechs with no weapons (possible edge case)
SELECT m.chassis, m.model, m.tonnage
FROM mech m
LEFT JOIN mech_weapon mw ON m.id = mw.mech_id
WHERE mw.mech_id IS NULL;

-- Test 5.2: Mechs with rear armor (only torsos should have this)
SELECT m.chassis, m.model, ma.loc, ma.armor_rear
FROM mech m
JOIN mech_armor ma ON m.id = ma.mech_id
WHERE ma.armor_rear IS NOT NULL
ORDER BY m.chassis, m.model, ma.loc;

-- Test 5.3: Quirk analysis
SELECT 
    quirk,
    COUNT(*) as mech_count,
    STRING_AGG(DISTINCT m.chassis || ' ' || m.model, ', ') as examples
FROM mech_quirk mq
JOIN mech m ON mq.mech_id = m.id
GROUP BY quirk
ORDER BY mech_count DESC;

-- Test 5.4: Movement profile edge cases
SELECT chassis, model, walk_mp, run_mp, jump_mp,
       CASE 
           WHEN jump_mp > 0 THEN 'Jump Capable'
           WHEN run_mp > walk_mp * 2 THEN 'Fast'
           WHEN walk_mp <= 3 THEN 'Slow'
           ELSE 'Standard'
       END as mobility_class
FROM mech
WHERE tonnage >= 80  -- Assault mechs with unusual mobility
ORDER BY walk_mp DESC, jump_mp DESC;

-- Test 5.5: Critical slot validation
SELECT 
    m.chassis,
    m.model,
    mcs.loc,
    COUNT(*) as slots_used,
    CASE 
        WHEN mcs.loc = 'HD' THEN 6
        WHEN mcs.loc IN ('CT','LT','RT','LA','RA') THEN 12
        WHEN mcs.loc IN ('LL','RL') THEN 6
    END as max_slots
FROM mech m
JOIN mech_crit_slot mcs ON m.id = mcs.mech_id
GROUP BY m.id, m.chassis, m.model, mcs.loc
HAVING COUNT(*) > CASE 
    WHEN mcs.loc = 'HD' THEN 6
    WHEN mcs.loc IN ('CT','LT','RT','LA','RA') THEN 12
    WHEN mcs.loc IN ('LL','RL') THEN 6
END;

-- =========================
-- DATA VALIDATION QUERIES
-- =========================

-- Test 6.1: Check for constraint violations
SELECT 'walk_mp > run_mp violation' as issue, chassis, model, walk_mp, run_mp
FROM mech WHERE walk_mp > run_mp
UNION ALL
SELECT 'negative tonnage' as issue, chassis, model, tonnage::text, ''
FROM mech WHERE tonnage <= 0
UNION ALL  
SELECT 'negative battle_value' as issue, chassis, model, battle_value::text, ''
FROM mech WHERE battle_value < 0;

-- Test 6.2: Verify enum values are valid
SELECT DISTINCT tech_base FROM mech ORDER BY tech_base;
SELECT DISTINCT era FROM mech ORDER BY era;
SELECT DISTINCT engine_type FROM mech ORDER BY engine_type;
SELECT DISTINCT armor_type FROM mech ORDER BY armor_type;

-- Test 6.3: Check for orphaned records
SELECT 'orphaned mech_weapon' as issue, COUNT(*)
FROM mech_weapon mw
LEFT JOIN mech m ON mw.mech_id = m.id
WHERE m.id IS NULL
UNION ALL
SELECT 'orphaned mech_armor' as issue, COUNT(*)
FROM mech_armor ma  
LEFT JOIN mech m ON ma.mech_id = m.id
WHERE m.id IS NULL;

-- =========================
-- PERFORMANCE BENCHMARKS
-- =========================

-- Benchmark 1: Name search performance
\timing on
SELECT chassis, model, tonnage FROM mech WHERE chassis ILIKE '%king%';
\timing off

-- Benchmark 2: Complex aggregation
\timing on
SELECT 
    era,
    tech_base,
    COUNT(*) as mechs,
    AVG(tonnage) as avg_tonnage,
    MAX(battle_value) as max_bv
FROM mech 
GROUP BY era, tech_base
ORDER BY era, tech_base;
\timing off

-- Benchmark 3: Join performance  
\timing on
SELECT m.chassis, m.model, COUNT(mw.weapon_id) as weapons
FROM mech m
LEFT JOIN mech_weapon mw ON m.id = mw.mech_id
GROUP BY m.id, m.chassis, m.model
ORDER BY weapons DESC
LIMIT 100;
\timing off
