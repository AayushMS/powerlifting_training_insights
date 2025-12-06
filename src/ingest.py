#!/usr/bin/env python3
"""
Powerlifting Training Data Ingestion Script

Parses the training_log.xlsx file and ingests data into PostgreSQL database.
Implements all data validation rules from the implementation plan.
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import re
import os
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
import warnings
from dotenv import load_dotenv

warnings.filterwarnings('ignore')

# Load environment variables from .env file
load_dotenv()

# Database connection settings - supports both local and Docker environments
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 5432)),
    'database': os.environ.get('DB_NAME', 'training_insights'),
    'user': os.environ.get('DB_USER', 'powerlifter'),
    'password': os.environ.get('DB_PASSWORD', 'stronglifts')
}

# Current actual maxes (not the outdated ones in the sheets)
CURRENT_MAXES = {
    'squat': 220,
    'bench': 135,
    'deadlift': 260
}

# Exercise canonicalization map
EXERCISE_MAP = {
    # Squat - ALL these variations are the SAME main lift
    'back squat': ('Squat', 'squat', True),
    'squat': ('Squat', 'squat', True),
    'squat ': ('Squat', 'squat', True),
    'competition squat': ('Squat', 'squat', True),
    'comp squat': ('Squat', 'squat', True),

    # Bench Press - ALL these variations are the SAME main lift
    'bench press': ('Bench Press', 'bench', True),
    'bench': ('Bench Press', 'bench', True),
    'comp bench press': ('Bench Press', 'bench', True),
    'competition bench press': ('Bench Press', 'bench', True),
    'long pause bench': ('Bench Press', 'bench', True),

    # Bench variations (DIFFERENT exercises - accessories)
    'tng bench': ('Touch and Go Bench', 'bench', False),
    'close grip bench press': ('Close Grip Bench Press', 'bench', False),
    'wide grip spoto bench': ('Wide Grip Spoto Bench', 'bench', False),
    'incline spoto bench': ('Incline Spoto Bench', 'bench', False),
    'incline db bench': ('Incline DB Bench', 'bench', False),

    # Deadlift - ALL these variations are the SAME main lift
    'sumo deadlift': ('Sumo Deadlift', 'deadlift', True),
    'deadlift': ('Sumo Deadlift', 'deadlift', True),

    # Deadlift variations (DIFFERENT exercises - accessories)
    'romanian deadlift': ('Romanian Deadlift', 'deadlift', False),
    'dumbbell rdl': ('Dumbbell RDL', 'deadlift', False),

    # Accessories - normalize naming variations
    'bulgarian split squat': ('Bulgarian Split Squat', 'accessory', False),
    'bulgarian split sq': ('Bulgarian Split Squat', 'accessory', False),
    'pull ups': ('Pull Ups', 'accessory', False),
    'weighted pull ups': ('Weighted Pull Ups', 'accessory', False),
    'chin up': ('Chin Ups', 'accessory', False),
    'chest supported row': ('Chest Supported Row', 'accessory', False),
    'chest supported rows': ('Chest Supported Row', 'accessory', False),
    'seated chest supported rows': ('Chest Supported Row', 'accessory', False),
    'single arm landmine row': ('Landmine Row', 'accessory', False),
    'single arm cable row': ('Cable Row', 'accessory', False),
    'db row': ('DB Row', 'accessory', False),
    'three way plank': ('Three Way Plank', 'accessory', False),
    '3 way plank': ('Three Way Plank', 'accessory', False),
    'face pull': ('Face Pull', 'accessory', False),
    'face pulls': ('Face Pull', 'accessory', False),
    'weighted dips': ('Weighted Dips', 'accessory', False),
    'rolling skull crusher': ('Skull Crusher', 'accessory', False),
    'over head extension': ('Overhead Extension', 'accessory', False),
    'overhead extension': ('Overhead Extension', 'accessory', False),
    'bicep 21\'s': ('Bicep 21s', 'accessory', False),
    'biceps option': ('Biceps', 'accessory', False),
    'bicep option': ('Biceps', 'accessory', False),
    'nordic': ('Nordic Curl', 'accessory', False),
    'nordic curl negative': ('Nordic Curl', 'accessory', False),
    'leg press': ('Leg Press', 'accessory', False),
    'leg press calf raise': ('Calf Raise', 'accessory', False),
    'leg curl': ('Leg Curl', 'accessory', False),
    'single arm lat pull down': ('Lat Pulldown', 'accessory', False),
    'cable upright row': ('Upright Row', 'accessory', False),
    'knees to elbow': ('Knees to Elbow', 'accessory', False),
    'off bench obliques': ('Obliques', 'accessory', False),
    'bird dog': ('Bird Dog', 'accessory', False),
    'side plank': ('Side Plank', 'accessory', False),
    'hollow body hold': ('Hollow Body Hold', 'accessory', False),
    'prone trap raise': ('Trap Raise', 'accessory', False),
    'thumbs down lateral raise': ('Lateral Raise', 'accessory', False),
    'tread mill run': ('Cardio', 'accessory', False),
    'fat dumbell press': ('DB Press', 'accessory', False),
    'dumbells fly': ('DB Fly', 'accessory', False),
    'overhead press': ('Overhead Press', 'accessory', False),
}

# Weight bounds for validation (catches obvious typos)
WEIGHT_BOUNDS = {
    'squat': (60, 250),
    'bench': (40, 160),
    'deadlift': (80, 300),
    'accessory': (0, 200)
}


def get_connection():
    """Get database connection."""
    return psycopg2.connect(**DB_CONFIG)


def canonicalize_exercise(name: str) -> Optional[Tuple[str, str, bool]]:
    """
    Convert exercise name to canonical form.
    Returns (canonical_name, category, is_main_lift) or None if not recognized.
    """
    if pd.isna(name):
        return None

    name_lower = str(name).strip().lower()

    # Skip headers and warmup items
    skip_items = ['movement', 'warm up/ activation', 'focus', 'optional',
                  'sunday', 'monday', 'tuesday', 'wednesday', 'thursday',
                  'friday', 'saturday', 'atempts', '']
    if name_lower in skip_items or 'warm up' in name_lower or 'focus' in name_lower:
        return None

    # Check direct mapping
    if name_lower in EXERCISE_MAP:
        return EXERCISE_MAP[name_lower]

    # Try partial matches for unmapped exercises
    for key, value in EXERCISE_MAP.items():
        if key in name_lower or name_lower in key:
            return value

    # Return as generic accessory if not found
    clean_name = name.strip().title()
    if len(clean_name) > 2:
        return (clean_name, 'accessory', False)

    return None


def parse_weight(val, prescribed_val=None, sheet_name='', row_num=0, category='accessory') -> Tuple[Optional[float], str]:
    """
    Parse weight value, handling various formats.
    Returns (weight, quality_flag).

    Implements validation rules:
    - Weight range parsing (40-30 -> 40, not 4030)
    - Weight deviation check (>20% from prescribed)
    - Reasonable bounds check
    """
    if pd.isna(val):
        return None, 'valid'

    val_str = str(val).strip().lower()

    # Skip non-weight values
    if val_str in ['bw', 'bodyweight', '', 'nan']:
        return None, 'bodyweight'
    if 'rpe' in val_str:
        return None, 'rpe_in_weight'

    quality_flag = 'valid'

    try:
        # Handle weight ranges like "40-30", "75-80"
        # These are NOT dates, they're weight ranges
        if '-' in val_str and not val_str.startswith('-'):
            parts = val_str.replace('kg', '').split('-')
            if len(parts) == 2:
                try:
                    w1, w2 = float(parts[0].strip()), float(parts[1].strip())
                    # Both parts should be reasonable weights
                    if w1 < 500 and w2 < 500:
                        weight = max(w1, w2)
                        quality_flag = 'weight_range'
                        return weight, quality_flag
                except:
                    pass

        # Handle "20es" format (each side)
        match = re.search(r'(\d+\.?\d*)\s*es', val_str)
        if match:
            weight = float(match.group(1))
            if weight < 500:  # Reasonable
                return weight, 'each_side'

        # Standard numeric parsing
        weight = float(re.sub(r'[^\d.]', '', val_str))

        # CRITICAL: Reject obviously wrong values (likely date conversions or typos)
        # Any weight over 500kg is definitely wrong
        if weight > 500:
            # Try to extract a reasonable weight
            # Sometimes dates like 2024-08-09 get parsed as 20240809
            # Look for patterns in the string
            if prescribed_val is not None:
                try:
                    prescribed = float(re.sub(r'[^\d.]', '', str(prescribed_val)))
                    if 0 < prescribed < 500:
                        return prescribed, 'extreme_value_corrected'
                except:
                    pass
            return None, 'extreme_value'

        # Check absolute bounds based on category
        bounds = WEIGHT_BOUNDS.get(category, (0, 300))
        if weight > bounds[1] * 1.5:  # Allow some buffer above max
            if prescribed_val is not None:
                try:
                    prescribed = float(re.sub(r'[^\d.]', '', str(prescribed_val)))
                    if bounds[0] <= prescribed <= bounds[1]:
                        return prescribed, 'out_of_bounds_corrected'
                except:
                    pass
            return None, 'out_of_bounds'

        # Validation: Check deviation from prescribed weight (only for main lifts with reasonable values)
        if prescribed_val is not None and weight > 20:  # Only check if weight is substantial
            try:
                prescribed = float(re.sub(r'[^\d.]', '', str(prescribed_val)))
                # Only compare if prescribed is reasonable
                if 20 < prescribed < 400 and 20 < weight < 400:
                    deviation = abs(weight - prescribed) / prescribed
                    if deviation > 0.50:  # More than 50% deviation for main lifts
                        # This is likely a typo - use prescribed instead
                        quality_flag = 'weight_deviation'
                        # Return prescribed weight instead of typo
                        return prescribed, quality_flag
            except:
                pass

        return weight, quality_flag

    except:
        return None, 'parse_error'


def parse_rpe(val) -> Optional[float]:
    """
    Parse RPE value, handling date conversions.
    Excel converts "5/6" to dates like 2024-05-06.
    """
    if pd.isna(val):
        return None

    val_str = str(val).strip()

    # Handle datetime objects (Excel date conversion issue)
    if 'datetime' in str(type(val)).lower() or '00:00:00' in val_str:
        try:
            if hasattr(val, 'month') and hasattr(val, 'day'):
                # Convert date back to RPE: month/day -> average
                return (val.month + val.day) / 2
            # Parse from string format
            match = re.search(r'(\d{4})-(\d{2})-(\d{2})', val_str)
            if match:
                month, day = int(match.group(2)), int(match.group(3))
                if month <= 10 and day <= 10:  # Valid RPE range
                    return (month + day) / 2
        except:
            pass
        return None

    # Handle RPE ranges like "7-8" or "8-9"
    if '-' in val_str:
        try:
            parts = val_str.replace('rpe', '').strip().split('-')
            r1, r2 = float(parts[0].strip()), float(parts[1].strip())
            if 1 <= r1 <= 10 and 1 <= r2 <= 10:
                return (r1 + r2) / 2
        except:
            pass

    # Standard numeric parsing
    try:
        rpe = float(re.sub(r'[^\d.]', '', val_str))
        if 1 <= rpe <= 10:
            return rpe
    except:
        pass

    return None


def parse_reps(val) -> Tuple[str, Optional[int]]:
    """
    Parse reps value.
    Returns (reps_string, reps_numeric).
    """
    if pd.isna(val):
        return '', None

    val_str = str(val).strip().lower()

    # Handle datetime (Excel date conversion)
    if '1900-01' in val_str or 'datetime' in str(type(val)).lower():
        try:
            if hasattr(val, 'day'):
                return str(val.day), val.day
            match = re.search(r'1900-01-(\d{2})', val_str)
            if match:
                day = int(match.group(1))
                return str(day), day
        except:
            pass
        return val_str, None

    # Handle "AMRAP"
    if 'amrap' in val_str:
        return 'AMRAP', 8  # Estimate for calculations

    # Handle "10 es" or "10 ea" (each side)
    match = re.search(r'(\d+)\s*(es|ea|each)', val_str)
    if match:
        reps = int(match.group(1))
        return f"{reps} each", reps * 2  # Double for total volume

    # Handle time-based (30 sec, etc)
    if 'sec' in val_str or 'min' in val_str:
        return val_str, None

    # Standard numeric
    try:
        reps = int(float(re.sub(r'[^\d.]', '', val_str)))
        return str(reps), reps
    except:
        return val_str, None


def classify_block(sheet_name: str) -> Tuple[str, str]:
    """Classify sheet into block type and extract block name."""
    name = sheet_name.lower().strip()

    if 'game' in name or 'show' in name:
        return 'Competition', 'competition'
    elif re.match(r'b4\s*week', name):
        return 'Block 4', 'block'
    elif re.match(r'b3\s*week', name):
        return 'Block 3', 'block'
    elif re.match(r'b2\s*week', name):
        return 'Block 2', 'block'
    elif 'prep' in name:
        return 'Prep', 'prep'
    elif 'meet' in name:
        return 'Meet Prep', 'meet'
    elif 'build' in name:
        return 'Build', 'build'
    elif 'new block' in name:
        return 'New Block', 'build'
    elif 'start' in name:
        return 'Start', 'intro'
    elif re.match(r'week\s*\d+', name):
        return 'Initial', 'intro'
    else:
        return 'Other', 'other'


def ingest_data(excel_path: str):
    """Main ingestion function."""
    print("=" * 60)
    print("POWERLIFTING TRAINING DATA INGESTION")
    print("=" * 60)

    # Load Excel file
    print(f"\nLoading {excel_path}...")
    xlsx = pd.ExcelFile(excel_path)
    print(f"Found {len(xlsx.sheet_names)} sheets")

    # Reverse sheet order for chronological sequence
    # (oldest weeks are at the end of the Excel file)
    sheet_order = list(reversed(xlsx.sheet_names))

    conn = get_connection()
    cur = conn.cursor()

    # Track statistics
    stats = {
        'sheets_processed': 0,
        'sessions_created': 0,
        'sets_created': 0,
        'exercises_created': 0,
        'data_quality_issues': 0
    }

    # Cache for exercises
    exercise_cache = {}

    try:
        # Create blocks
        print("\nCreating training blocks...")
        blocks_created = set()

        for seq, sheet_name in enumerate(sheet_order):
            block_name, block_type = classify_block(sheet_name)
            if block_name not in blocks_created:
                cur.execute("""
                    INSERT INTO training_blocks (name, block_type, sequence_order)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING
                    RETURNING id
                """, (block_name, block_type, len(blocks_created) + 1))
                blocks_created.add(block_name)

        conn.commit()
        print(f"Created {len(blocks_created)} blocks")

        # Process each sheet
        print("\nProcessing training weeks...")

        for seq, sheet_name in enumerate(sheet_order):
            df = pd.read_excel(xlsx, sheet_name=sheet_name, header=None)

            block_name, block_type = classify_block(sheet_name)

            # Get block ID
            cur.execute("SELECT id FROM training_blocks WHERE name = %s", (block_name,))
            block_id = cur.fetchone()[0]

            # Create training week
            cur.execute("""
                INSERT INTO training_weeks
                (block_id, sheet_name, sequence_order, current_squat_max, current_bench_max, current_deadlift_max)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (block_id, sheet_name.strip(), seq,
                  CURRENT_MAXES['squat'], CURRENT_MAXES['bench'], CURRENT_MAXES['deadlift']))
            week_id = cur.fetchone()[0]

            # Find training days in sheet
            days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            current_day = None
            current_session_id = None
            session_order = 0
            set_order = 0

            for row_idx, row in df.iterrows():
                cell_val = str(row[0]).strip() if pd.notna(row[0]) else ''

                # Check for day header
                if cell_val in days:
                    current_day = cell_val
                    session_order += 1
                    set_order = 0

                    # Create session
                    cur.execute("""
                        INSERT INTO training_sessions (week_id, day_of_week, session_order)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """, (week_id, current_day, session_order))
                    current_session_id = cur.fetchone()[0]
                    stats['sessions_created'] += 1
                    continue

                # Skip if no active session
                if current_session_id is None:
                    continue

                # Skip header rows
                if cell_val.lower() in ['movement', '']:
                    continue

                # Try to parse as exercise
                exercise_info = canonicalize_exercise(cell_val)
                if exercise_info is None:
                    continue

                canonical_name, category, is_main_lift = exercise_info

                # Get or create exercise
                if canonical_name not in exercise_cache:
                    cur.execute("""
                        INSERT INTO exercises (name, canonical_name, category, is_main_lift)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                        RETURNING id
                    """, (canonical_name, canonical_name, category, is_main_lift))
                    exercise_cache[canonical_name] = cur.fetchone()[0]
                    stats['exercises_created'] += 1

                exercise_id = exercise_cache[canonical_name]

                # Parse set data
                prescribed_weight = row[2] if len(row) > 2 else None
                actual_weight_raw = row[3] if len(row) > 3 else None
                rpe_raw = row[4] if len(row) > 4 else None
                sets_raw = row[5] if len(row) > 5 else None
                reps_raw = row[6] if len(row) > 6 else None
                tempo = str(row[7]).strip() if len(row) > 7 and pd.notna(row[7]) else None
                rest = str(row[8]).strip() if len(row) > 8 and pd.notna(row[8]) else None
                notes = str(row[9]).strip() if len(row) > 9 and pd.notna(row[9]) else None

                # Parse with validation
                prescribed, _ = parse_weight(prescribed_weight, category=category)
                actual, quality_flag = parse_weight(
                    actual_weight_raw,
                    prescribed_weight,
                    sheet_name,
                    row_idx,
                    category
                )

                # Use actual if available, otherwise prescribed
                final_weight = actual if actual else prescribed

                # Validate against bounds
                if final_weight and is_main_lift:
                    bounds = WEIGHT_BOUNDS.get(category, (0, 500))
                    if not (bounds[0] <= final_weight <= bounds[1]):
                        print(f"  WARNING: Weight out of bounds in '{sheet_name}' row {row_idx}: "
                              f"{canonical_name} = {final_weight}kg")
                        quality_flag = 'out_of_bounds'
                        stats['data_quality_issues'] += 1

                # Parse other fields
                rpe = parse_rpe(rpe_raw)
                reps_str, reps_numeric = parse_reps(reps_raw)

                # Parse sets (default to 1)
                try:
                    sets_count = int(float(str(sets_raw))) if pd.notna(sets_raw) else 1
                except:
                    sets_count = 1

                set_order += 1

                # Check for bodyweight
                is_bodyweight = quality_flag == 'bodyweight' or (
                    actual_weight_raw and str(actual_weight_raw).strip().lower() in ['bw', 'bodyweight']
                )

                # Log data quality issues
                if quality_flag not in ['valid', 'bodyweight']:
                    cur.execute("""
                        INSERT INTO data_quality_log
                        (sheet_name, row_number, column_name, original_value, corrected_value, issue_type)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (sheet_name, row_idx, 'weight', str(actual_weight_raw),
                          str(final_weight), quality_flag))
                    stats['data_quality_issues'] += 1

                # Insert training set
                cur.execute("""
                    INSERT INTO training_sets
                    (session_id, exercise_id, set_order, prescribed_weight, actual_weight,
                     actual_rpe, sets, reps, reps_numeric, tempo, rest, notes,
                     is_bodyweight, data_quality_flag)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (current_session_id, exercise_id, set_order, prescribed, final_weight,
                      rpe, sets_count, reps_str, reps_numeric, tempo, rest, notes,
                      is_bodyweight, quality_flag))
                stats['sets_created'] += 1

            stats['sheets_processed'] += 1

            if stats['sheets_processed'] % 10 == 0:
                print(f"  Processed {stats['sheets_processed']}/{len(sheet_order)} sheets...")
                conn.commit()

        conn.commit()

        # Generate personal records
        print("\nGenerating personal records...")
        cur.execute("""
            INSERT INTO personal_records (exercise_id, weight, reps, estimated_1rm, week_id)
            SELECT DISTINCT ON (e.id)
                e.id,
                ts.actual_weight,
                ts.reps_numeric,
                ts.actual_weight * (1 + ts.reps_numeric::float / 30) as estimated_1rm,
                tw.id
            FROM training_sets ts
            JOIN training_sessions tsess ON ts.session_id = tsess.id
            JOIN training_weeks tw ON tsess.week_id = tw.id
            JOIN exercises e ON ts.exercise_id = e.id
            WHERE e.is_main_lift = TRUE
              AND ts.actual_weight IS NOT NULL
              AND ts.reps_numeric IS NOT NULL
              AND ts.data_quality_flag = 'valid'
            ORDER BY e.id, ts.actual_weight DESC
        """)
        conn.commit()

        print("\n" + "=" * 60)
        print("INGESTION COMPLETE")
        print("=" * 60)
        print(f"Sheets processed:     {stats['sheets_processed']}")
        print(f"Sessions created:     {stats['sessions_created']}")
        print(f"Training sets:        {stats['sets_created']}")
        print(f"Exercises cataloged:  {stats['exercises_created']}")
        print(f"Data quality issues:  {stats['data_quality_issues']}")

        # Verify data
        print("\n--- Data Verification ---")
        cur.execute("SELECT COUNT(*) FROM training_weeks")
        print(f"Training weeks: {cur.fetchone()[0]}")

        cur.execute("SELECT COUNT(*) FROM training_sessions")
        print(f"Training sessions: {cur.fetchone()[0]}")

        cur.execute("SELECT COUNT(*) FROM training_sets")
        print(f"Training sets: {cur.fetchone()[0]}")

        cur.execute("""
            SELECT e.canonical_name, MAX(ts.actual_weight) as max_weight
            FROM training_sets ts
            JOIN exercises e ON ts.exercise_id = e.id
            WHERE e.is_main_lift = TRUE AND ts.data_quality_flag = 'valid'
            GROUP BY e.canonical_name
            ORDER BY e.canonical_name
        """)
        print("\nMax weights per main lift (validated):")
        for row in cur.fetchall():
            print(f"  {row[0]}: {row[1]} kg")

    except Exception as e:
        conn.rollback()
        print(f"\nERROR: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    ingest_data('training_log.xlsx')
