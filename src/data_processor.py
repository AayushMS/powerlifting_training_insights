#!/usr/bin/env python3
"""
Data Processor for Powerlifting Training Insights

Reads training data directly from Excel file and provides
all analytics without database dependency.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from functools import lru_cache
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import re

# Excel file path
DATA_FILE = Path(__file__).parent.parent / "Aayush man .xlsx"

# Training timeline (dates are approximate — the sheet has no explicit dates):
# - Start: 3rd week of March 2024 (~March 18)
# - ~105 training weeks through mid-2026
# - Training breaks below are added on top of consecutive training weeks so the
#   newest week lands near the present day.
TRAINING_START_DATE = datetime(2024, 3, 18)

# Training breaks (weeks with no training)
# Total: ~13 weeks to account for March 18 start to Dec 28 end with 81 training weeks
TRAINING_BREAKS = [
    {'start': datetime(2024, 6, 1), 'duration_weeks': 4, 'reason': 'June 2024 break'},
    {'start': datetime(2024, 10, 1), 'duration_weeks': 2, 'reason': 'October 2024 break'},
    {'start': datetime(2024, 12, 9), 'duration_weeks': 2, 'reason': 'Post-NYFC Classic break'},
    {'start': datetime(2025, 5, 1), 'duration_weeks': 3, 'reason': 'May 2025 break'},
    {'start': datetime(2025, 8, 1), 'duration_weeks': 2, 'reason': 'Scattered misses'},
]

# =============================================================================
# ATHLETE PROFILE
# =============================================================================
ATHLETE_PROFILE = {
    'name': 'Aayush Man Singh',
    'weight_class': 'U93kg',
    'bodyweight': '90-91kg',
    'federation': 'IPF',  # Assuming based on competition names
}

# =============================================================================
# COMPETITION HISTORY
# =============================================================================
COMPETITIONS = [
    {
        'name': 'NYFC Classic 2024 Invitational',
        'date': datetime(2024, 12, 9),
        'squat': 220.0,
        'bench': 122.5,
        'deadlift': 250.0,
        'total': 592.5,
        'attempts': '8/9',
        'placement': '4th',
        'notes': 'Missed 130kg bench on 3rd attempt'
    },
    {
        'name': 'OX Classic Summerslam',
        'date': datetime(2025, 4, 27),
        'squat': 220.0,
        'bench': 130.0,
        'deadlift': 255.0,
        'total': 605.0,
        'attempts': '9/9',
        'placement': '3rd',
        'notes': 'Perfect meet! Made the bench that was missed at NYFC'
    }
]

# Current PRs (informational only — get_current_prs() derives these from the data)
CURRENT_PRS = {
    'Squat': 220,
    'Bench Press': 135,
    'Deadlift': 275
}

# Goal PRs for 2026 - user-defined targets
GOAL_PRS = {
    'Squat': 240,       # 2026 target
    'Bench Press': 150, # 2026 target
    'Deadlift': 280     # 2026 target
}
# Total goal: 670kg

# Color scheme
COLORS = {
    'Squat': '#FF6B6B',
    'Bench Press': '#4ECDC4',
    'Deadlift': '#45B7D1',
    'Accessory': '#96CEB4',
    'squat': '#FF6B6B',
    'bench': '#4ECDC4',
    'deadlift': '#45B7D1'
}

# Known data anomalies to fix
KNOWN_ANOMALIES = {
    # Sheet name, exercise, wrong value -> correct value
    (' building 45', 'Bench Press', 177.5): 117.5,
}


def week_to_date(week_order: int) -> datetime:
    """
    Convert week order to approximate date, accounting for training breaks.

    The week_order represents consecutive training weeks (1 to 81).
    We need to add break weeks when the date crosses break periods.
    """
    # Start with the base calculation
    base_date = TRAINING_START_DATE + timedelta(weeks=week_order - 1)

    # Add break weeks for any breaks that occurred before this training week
    extra_weeks = 0
    for brk in TRAINING_BREAKS:
        break_start = brk['start']
        break_weeks = brk['duration_weeks']

        # If our calculated date is after the break start, add the break duration
        if base_date >= break_start:
            extra_weeks += break_weeks

    return TRAINING_START_DATE + timedelta(weeks=week_order - 1 + extra_weeks)


def format_date(dt: datetime) -> str:
    """Format date as 'Mon YYYY'."""
    return dt.strftime('%b %Y')


def format_date_short(dt: datetime) -> str:
    """Format date as 'Mon'."""
    return dt.strftime('%b')


def canonicalize_exercise(movement: str) -> Tuple[str, str, bool]:
    """
    Canonicalize exercise name to standard form.

    Returns:
        Tuple of (canonical_name, category, is_main_lift)
    """
    if pd.isna(movement):
        return None, None, False

    m = str(movement).lower().strip()

    # Main lifts
    if 'squat' in m and 'split' not in m and 'bulgarian' not in m:
        return 'Squat', 'squat', True
    elif 'bench press' in m and 'close' not in m and 'incline' not in m and 'db' not in m:
        return 'Bench Press', 'bench', True
    elif ('sumo deadlift' in m or 'deadlift' in m) and 'romanian' not in m and 'rdl' not in m:
        return 'Deadlift', 'deadlift', True

    # Accessories by category
    elif 'row' in m:
        return movement.strip(), 'back', False
    elif 'pull' in m:
        return movement.strip(), 'back', False
    elif 'press' in m:
        return movement.strip(), 'pressing', False
    elif 'curl' in m or 'bicep' in m:
        return movement.strip(), 'arms', False
    elif 'extension' in m or 'tricep' in m:
        return movement.strip(), 'arms', False
    elif 'rdl' in m or 'romanian' in m:
        return 'Romanian Deadlift', 'posterior', False
    elif 'split' in m or 'lunge' in m or 'bulgarian' in m:
        return movement.strip(), 'legs', False
    elif 'plank' in m or 'core' in m or 'ab' in m:
        return movement.strip(), 'core', False
    else:
        return movement.strip(), 'accessory', False


def parse_weight(val, prescribed=None, sheet_name=None, exercise=None) -> Optional[float]:
    """Parse weight value from various formats."""
    if pd.isna(val):
        return None

    val_str = str(val).strip().upper()

    # Handle bodyweight
    if 'BW' in val_str:
        return 80.0  # Assume bodyweight

    # Handle RPE notation (not a weight)
    if 'RPE' in val_str:
        return None

    # Handle ranges like "40-30" or "75-80"
    if '-' in val_str and not val_str.startswith('-'):
        parts = val_str.split('-')
        try:
            # Take the higher value
            return max(float(parts[0]), float(parts[1]))
        except (ValueError, IndexError):
            pass

    # Handle numeric with units
    val_str = val_str.replace('KG', '').replace('LB', '').strip()

    try:
        weight = float(val_str)

        # Check for known anomalies
        if sheet_name and exercise:
            anomaly_key = (sheet_name, exercise, weight)
            if anomaly_key in KNOWN_ANOMALIES:
                return KNOWN_ANOMALIES[anomaly_key]

        # Outlier detection: if actual is >40% higher than prescribed, likely a typo
        if prescribed is not None and prescribed > 0:
            if weight > prescribed * 1.4:
                # Likely a typo - use prescribed instead
                return prescribed

        return weight
    except ValueError:
        return None


def _valid_rpe(rpe: Optional[float]) -> Optional[float]:
    """Return the RPE only if it is within the sane 1-10 range."""
    if rpe is None:
        return None
    return rpe if 1 <= rpe <= 10 else None


def parse_rpe(val) -> Optional[float]:
    """
    Parse RPE value, handling Google Sheets' date-conversion quirk.

    Athletes log RPE ranges like "8/9" which Google Sheets silently
    reinterprets as a date (e.g. Aug 9). We recover the intended RPE from
    the month/day (8/9 -> 8.5). Every path is clamped to the valid 1-10
    range so stray dates/typos can never pollute the average.
    """
    if pd.isna(val):
        return None

    # Datetime cells: "8/9" -> Aug 9 -> RPE 8.5, "9/10" -> Sep 10 -> 9.5
    if isinstance(val, (datetime, pd.Timestamp)):
        return _valid_rpe((val.month + val.day) / 2)

    val_str = str(val).strip()

    # Date-as-string fallback for any year (e.g. "2026-08-09 00:00:00")
    date_match = re.search(r'(?:19|20)\d{2}-(\d{1,2})-(\d{1,2})', val_str)
    if date_match:
        month = int(date_match.group(1))
        day = int(date_match.group(2))
        return _valid_rpe((month + day) / 2)

    # Handle range like "7.5-8" or "8-9"
    if '-' in val_str and not val_str.startswith('-'):
        parts = val_str.split('-')
        try:
            return _valid_rpe((float(parts[0]) + float(parts[1])) / 2)
        except (ValueError, IndexError):
            pass

    try:
        return _valid_rpe(float(val_str))
    except ValueError:
        pass

    return None


def parse_reps(val) -> Optional[int]:
    """Parse reps value from various formats."""
    if pd.isna(val):
        return None

    val_str = str(val).lower().strip()

    # Handle AMRAP
    if 'amrap' in val_str:
        return 1

    # Handle "each side" notation
    val_str = val_str.replace('es', '').replace('ea', '').strip()

    try:
        return int(float(val_str))
    except ValueError:
        return None


def parse_sets(val) -> Optional[int]:
    """Parse sets value."""
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def classify_block(sheet_name: str) -> Tuple[str, str]:
    """
    Classify sheet into training block and block type.

    Returns:
        Tuple of (block_name, block_type)
    """
    name = str(sheet_name).lower().strip()

    if 'b5' in name:
        return 'Block 5', 'build'
    elif 'b4' in name:
        return 'Block 4', 'build'
    elif 'b3' in name:
        return 'Block 3', 'build'
    elif 'b2' in name:
        return 'Block 2', 'build'
    elif 'game' in name or 'show' in name:
        return 'Competition', 'competition'
    elif 'prep' in name:
        return 'Meet Prep', 'prep'
    elif 'meet' in name and 'intro' in name:
        return 'Meet Intro', 'intro'
    elif 'build' in name:
        return 'Building', 'build'
    elif 'start' in name:
        return 'Start', 'intro'
    elif 'week' in name:
        match = re.search(r'week\s*(\d+)', name)
        if match:
            week_num = int(match.group(1))
            return f'Week {week_num}', 'intro'
    elif 'new block' in name:
        return 'New Block', 'build'

    return sheet_name.strip(), 'other'


@lru_cache(maxsize=1)
def load_training_data() -> pd.DataFrame:
    """
    Load and process all training data from Excel.

    Returns:
        DataFrame with all training entries
    """
    xl = pd.ExcelFile(DATA_FILE)
    all_data = []
    skipped_exercises = []

    total_sheets = len(xl.sheet_names)
    is_latest_week = True  # First sheet in Excel is the latest

    for sheet_idx, sheet_name in enumerate(xl.sheet_names):
        df = pd.read_excel(xl, sheet_name=sheet_name, header=None)

        # Week order: newest first in Excel, so reverse
        week_order = total_sheets - sheet_idx

        # Calculate approximate date for this week
        training_date = week_to_date(week_order)

        # Get block classification
        block_name, block_type = classify_block(sheet_name)

        current_day = None
        session_order = 0
        exercises_in_week = set()

        for i, row in df.iterrows():
            cell0 = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''

            # Track day of week
            if cell0.lower() in ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']:
                current_day = cell0.title()
                session_order += 1
                continue

            # Skip header/warmup rows
            if 'warm up' in cell0.lower() or cell0.lower() == 'movement':
                continue
            if 'foam roll' in cell0.lower() or 'cardio' in cell0.lower():
                continue
            if 'banded' in cell0.lower() and 'squat' not in cell0.lower():
                continue
            if 'dynamic' in cell0.lower() or 'pvc' in cell0.lower():
                continue
            if 'band pull' in cell0.lower():
                continue

            # Get canonical exercise info
            canonical, category, is_main = canonicalize_exercise(cell0)

            if canonical is None:
                continue

            # Parse values
            try:
                prescribed = parse_weight(row.iloc[2]) if len(row) > 2 else None
                actual_raw = row.iloc[3] if len(row) > 3 else None
                actual = parse_weight(actual_raw, prescribed=prescribed, sheet_name=sheet_name, exercise=canonical)
                rpe = parse_rpe(row.iloc[4]) if len(row) > 4 else None
                sets = parse_sets(row.iloc[5]) if len(row) > 5 else None
                reps = parse_reps(row.iloc[6]) if len(row) > 6 else None
            except (IndexError, ValueError):
                continue

            # Track if this is a main lift that was skipped (has prescribed but no actual)
            if is_main and prescribed is not None and actual is None:
                # Check if it's truly skipped (not just the latest week in progress)
                if not is_latest_week:
                    skipped_exercises.append({
                        'week': sheet_name.strip(),
                        'week_order': week_order,
                        'training_date': training_date,
                        'exercise': canonical,
                        'prescribed_weight': prescribed
                    })

            # Use actual weight if available, else prescribed
            weight = actual if actual is not None else prescribed

            if weight is not None and weight > 0:
                exercises_in_week.add(canonical)
                all_data.append({
                    'week': sheet_name.strip(),
                    'week_order': week_order,
                    'training_date': training_date,
                    'month_year': format_date(training_date),
                    'block_name': block_name,
                    'block_type': block_type,
                    'day': current_day,
                    'session_order': session_order,
                    'movement': cell0,
                    'canonical_name': canonical,
                    'category': category,
                    'is_main_lift': is_main,
                    'prescribed_weight': prescribed,
                    'actual_weight': weight,
                    'rpe': rpe,
                    'sets': sets or 1,
                    'reps': reps or 1,
                    'is_latest_week': is_latest_week
                })

        is_latest_week = False  # Only first sheet is latest

    df = pd.DataFrame(all_data)

    # Calculate tonnage
    df['tonnage'] = df['actual_weight'] * df['sets'] * df['reps']

    return df


# Global cache for skipped exercises
_skipped_exercises_cache = None


def _get_skipped_exercises_internal() -> pd.DataFrame:
    """Internal function to get skipped exercises, populated during load."""
    global _skipped_exercises_cache

    if _skipped_exercises_cache is None:
        # Need to reparse to get skipped exercises
        xl = pd.ExcelFile(DATA_FILE)
        skipped_exercises = []
        total_sheets = len(xl.sheet_names)
        is_latest_week = True

        for sheet_idx, sheet_name in enumerate(xl.sheet_names):
            df = pd.read_excel(xl, sheet_name=sheet_name, header=None)
            week_order = total_sheets - sheet_idx
            training_date = week_to_date(week_order)

            for i, row in df.iterrows():
                cell0 = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''

                canonical, category, is_main = canonicalize_exercise(cell0)
                if canonical is None or not is_main:
                    continue

                try:
                    prescribed = parse_weight(row.iloc[2]) if len(row) > 2 else None
                    actual = parse_weight(row.iloc[3]) if len(row) > 3 else None
                except:
                    continue

                if prescribed is not None and actual is None and not is_latest_week:
                    skipped_exercises.append({
                        'week': sheet_name.strip(),
                        'week_order': week_order,
                        'training_date': training_date,
                        'exercise': canonical,
                        'prescribed_weight': prescribed
                    })

            is_latest_week = False

        _skipped_exercises_cache = pd.DataFrame(skipped_exercises) if skipped_exercises else pd.DataFrame()

    return _skipped_exercises_cache


def get_skipped_exercises() -> pd.DataFrame:
    """Get exercises that were skipped (prescribed but not done)."""
    return _get_skipped_exercises_internal()


def get_main_lift_data() -> pd.DataFrame:
    """Get main lift progression data."""
    df = load_training_data()
    main_lifts = df[df['is_main_lift'] == True].copy()

    # Aggregate by week and exercise
    progression = main_lifts.groupby(['week_order', 'week', 'training_date', 'month_year', 'canonical_name']).agg({
        'actual_weight': 'max',
        'rpe': 'mean',
        'tonnage': 'sum',
        'sets': 'sum'
    }).reset_index()

    progression.columns = ['week_order', 'week', 'training_date', 'month_year', 'exercise', 'top_weight', 'avg_rpe', 'tonnage', 'total_sets']

    return progression.sort_values('week_order')


def get_lift_specific_data(lift: str) -> Dict:
    """Get detailed data for a specific lift."""
    df = load_training_data()
    lift_data = df[(df['is_main_lift'] == True) & (df['canonical_name'] == lift)].copy()

    if lift_data.empty:
        return {}

    # Weekly progression
    weekly = lift_data.groupby(['week_order', 'training_date', 'month_year']).agg({
        'actual_weight': 'max',
        'rpe': 'mean',
        'tonnage': 'sum',
        'sets': 'sum',
        'reps': 'sum'
    }).reset_index()

    # Calculate monthly averages for smoother chart
    lift_data['month'] = lift_data['training_date'].apply(lambda x: x.strftime('%Y-%m'))
    monthly = lift_data.groupby('month').agg({
        'actual_weight': 'max',
        'rpe': 'mean',
        'tonnage': 'sum',
        'sets': 'sum',
        'week_order': 'mean'
    }).reset_index()

    # RPE distribution
    rpe_data = lift_data['rpe'].dropna()

    # Progress metrics
    first_10_weeks = weekly.head(10)['actual_weight'].mean()
    last_10_weeks = weekly.tail(10)['actual_weight'].mean()
    pr = lift_data['actual_weight'].max()
    total_volume = lift_data['tonnage'].sum()

    return {
        'weekly': weekly,
        'monthly': monthly,
        'rpe_data': rpe_data,
        'pr': pr,
        'first_10_avg': first_10_weeks,
        'last_10_avg': last_10_weeks,
        'total_volume': total_volume,
        'total_sets': lift_data['sets'].sum(),
        'weeks_trained': lift_data['week_order'].nunique(),
        'mean_rpe': rpe_data.mean() if len(rpe_data) > 0 else None,
        'rpe_low_pct': (rpe_data < 7).sum() / len(rpe_data) * 100 if len(rpe_data) > 0 else 0,
        'rpe_mid_pct': ((rpe_data >= 7) & (rpe_data <= 8.5)).sum() / len(rpe_data) * 100 if len(rpe_data) > 0 else 0,
        'rpe_high_pct': (rpe_data > 8.5).sum() / len(rpe_data) * 100 if len(rpe_data) > 0 else 0,
    }


def get_weekly_volume() -> pd.DataFrame:
    """Get weekly volume summary by category."""
    df = load_training_data()

    volume = df.groupby(['week_order', 'week', 'training_date', 'month_year', 'category']).agg({
        'tonnage': 'sum',
        'sets': 'sum',
        'session_order': 'nunique'
    }).reset_index()

    volume.columns = ['week_order', 'week', 'training_date', 'month_year', 'category', 'tonnage', 'total_sets', 'sessions']

    return volume.sort_values('week_order')


def get_rpe_distribution() -> pd.DataFrame:
    """Get RPE distribution data."""
    df = load_training_data()
    return df[['canonical_name', 'category', 'is_main_lift', 'rpe', 'week_order', 'training_date']].dropna(subset=['rpe'])


def get_rpe_by_lift() -> Dict[str, pd.Series]:
    """Get RPE distribution for each main lift."""
    rpe_df = get_rpe_distribution()
    main_lifts = rpe_df[rpe_df['is_main_lift'] == True]

    return {
        lift: main_lifts[main_lifts['canonical_name'] == lift]['rpe']
        for lift in ['Squat', 'Bench Press', 'Deadlift']
    }


def get_accessory_frequency() -> pd.DataFrame:
    """Get accessory exercise frequency."""
    df = load_training_data()
    accessories = df[df['is_main_lift'] == False]

    freq = accessories.groupby(['canonical_name', 'category']).agg({
        'week_order': 'nunique',
        'sets': 'sum',
        'tonnage': 'sum'
    }).reset_index()

    freq.columns = ['canonical_name', 'category', 'frequency', 'total_sets', 'total_tonnage']

    return freq.sort_values('frequency', ascending=False)


def get_accessory_by_category() -> Dict[str, pd.DataFrame]:
    """Get accessories grouped by muscle category."""
    accessories = get_accessory_frequency()

    categories = {
        'Back': accessories[accessories['category'] == 'back'],
        'Arms': accessories[accessories['category'] == 'arms'],
        'Legs': accessories[accessories['category'] == 'legs'],
        'Core': accessories[accessories['category'] == 'core'],
        'Pressing': accessories[accessories['category'] == 'pressing'],
        'Posterior Chain': accessories[accessories['category'] == 'posterior'],
        'Other': accessories[accessories['category'] == 'accessory'],
    }

    return {k: v for k, v in categories.items() if not v.empty}


def get_block_comparison() -> pd.DataFrame:
    """Get block-by-block comparison data."""
    df = load_training_data()
    main_lifts = df[df['is_main_lift'] == True]

    blocks = main_lifts.groupby(['block_name', 'block_type', 'canonical_name']).agg({
        'actual_weight': ['max', 'mean'],
        'tonnage': 'sum',
        'sets': 'sum',
        'week_order': ['min', 'max'],
        'training_date': ['min', 'max']
    }).reset_index()

    blocks.columns = ['block_name', 'block_type', 'exercise', 'max_weight', 'avg_weight',
                      'tonnage', 'total_sets', 'start_week', 'end_week', 'start_date', 'end_date']

    return blocks.sort_values('start_week')


def get_training_frequency() -> pd.DataFrame:
    """Get training frequency data."""
    df = load_training_data()

    # Count unique sessions per week
    freq = df.groupby(['week_order', 'week', 'training_date', 'month_year']).agg({
        'session_order': 'max',
        'day': 'nunique'
    }).reset_index()

    freq.columns = ['week_order', 'week', 'training_date', 'month_year', 'sessions_per_week', 'unique_days']

    # Also get lift-specific frequency
    main_lifts = df[df['is_main_lift'] == True]
    for lift in ['Squat', 'Bench Press', 'Deadlift']:
        lift_sessions = main_lifts[main_lifts['canonical_name'] == lift].groupby('week_order')['session_order'].nunique()
        freq[f'{lift.lower().replace(" ", "_")}_sessions'] = freq['week_order'].map(lift_sessions).fillna(0).astype(int)

    return freq.sort_values('week_order')


def get_current_prs() -> Dict[str, float]:
    """Get current PRs from data."""
    df = load_training_data()
    main_lifts = df[df['is_main_lift'] == True]

    prs = {}
    for lift in ['Squat', 'Bench Press', 'Deadlift']:
        lift_data = main_lifts[main_lifts['canonical_name'] == lift]
        if not lift_data.empty:
            prs[lift] = float(lift_data['actual_weight'].max())

    return prs


def get_pr_history() -> Dict[str, pd.DataFrame]:
    """Get PR progression history for each lift."""
    df = load_training_data()
    main_lifts = df[df['is_main_lift'] == True]

    pr_history = {}
    for lift in ['Squat', 'Bench Press', 'Deadlift']:
        lift_data = main_lifts[main_lifts['canonical_name'] == lift].sort_values('week_order')

        # Track running max
        running_max = 0
        pr_dates = []
        for _, row in lift_data.iterrows():
            if row['actual_weight'] > running_max:
                running_max = row['actual_weight']
                pr_dates.append({
                    'date': row['training_date'],
                    'month_year': row['month_year'],
                    'weight': running_max,
                    'week': row['week']
                })

        pr_history[lift] = pd.DataFrame(pr_dates)

    return pr_history


def get_summary_stats() -> Dict:
    """Get overall summary statistics."""
    df = load_training_data()
    main_lifts = df[df['is_main_lift'] == True]

    # Get RPE stats
    rpe_data = main_lifts['rpe'].dropna()

    # Get volume by lift
    volume_by_lift = main_lifts.groupby('canonical_name')['tonnage'].sum().to_dict()

    # Get training frequency
    freq = get_training_frequency()

    # Get PRs
    prs = get_current_prs()

    # Date range
    min_date = df['training_date'].min()
    max_date = df['training_date'].max()

    return {
        'total_weeks': df['week_order'].nunique(),
        'total_sessions': int(df.groupby('week_order')['session_order'].max().sum()),
        'total_entries': len(df),
        'avg_sessions_per_week': freq['sessions_per_week'].mean(),
        'mean_rpe': rpe_data.mean() if len(rpe_data) > 0 else 0,
        'median_rpe': rpe_data.median() if len(rpe_data) > 0 else 0,
        'rpe_low_pct': (rpe_data < 7).sum() / len(rpe_data) * 100 if len(rpe_data) > 0 else 0,
        'rpe_mid_pct': ((rpe_data >= 7) & (rpe_data <= 8.5)).sum() / len(rpe_data) * 100 if len(rpe_data) > 0 else 0,
        'rpe_high_pct': (rpe_data > 8.5).sum() / len(rpe_data) * 100 if len(rpe_data) > 0 else 0,
        'volume_squat': volume_by_lift.get('Squat', 0),
        'volume_bench': volume_by_lift.get('Bench Press', 0),
        'volume_deadlift': volume_by_lift.get('Deadlift', 0),
        'total_volume': sum(volume_by_lift.values()),
        'current_prs': prs,
        'total_pr': sum(prs.values()),
        'start_date': min_date,
        'end_date': max_date,
        'training_duration_months': (max_date - min_date).days / 30,
    }


def get_monthly_summary() -> pd.DataFrame:
    """Get monthly training summary."""
    df = load_training_data()

    df['month'] = df['training_date'].apply(lambda x: x.strftime('%Y-%m'))

    monthly = df.groupby('month').agg({
        'tonnage': 'sum',
        'sets': 'sum',
        'week_order': 'nunique',
        'session_order': 'sum',
        'training_date': 'first'
    }).reset_index()

    monthly['month_label'] = monthly['training_date'].apply(format_date)

    return monthly.sort_values('month')


def get_insights() -> List[Dict]:
    """Generate training insights based on data analysis."""
    from interpretations import (
        interpret_rpe_average,
        interpret_bench_squat_ratio,
        interpret_deadlift_squat_ratio,
        interpret_progress,
        interpret_consistency,
        interpret_sessions_per_week
    )

    stats = get_summary_stats()
    prs = stats['current_prs']

    insights = []

    # RPE insight
    insights.append({
        'type': 'rpe',
        'priority': 'medium' if stats['mean_rpe'] < 7 else 'low',
        'title': 'Training Intensity',
        'message': interpret_rpe_average(stats['mean_rpe']),
        'icon': '💪'
    })

    # Bench/Squat ratio
    bench_ratio = interpret_bench_squat_ratio(prs.get('Bench Press', 0), prs.get('Squat', 1))
    insights.append({
        'type': 'ratio',
        'priority': 'high' if bench_ratio['status'] == 'needs_attention' else 'low',
        'title': f"{bench_ratio['emoji']} Bench vs Squat Balance",
        'message': bench_ratio['detail'],
        'action': bench_ratio['action'],
        'icon': bench_ratio['emoji']
    })

    # Deadlift/Squat ratio
    dl_ratio = interpret_deadlift_squat_ratio(prs.get('Deadlift', 0), prs.get('Squat', 1))
    insights.append({
        'type': 'ratio',
        'priority': 'low' if dl_ratio['status'] == 'balanced' else 'medium',
        'title': f"{dl_ratio['emoji']} Deadlift vs Squat Balance",
        'message': dl_ratio['detail'],
        'action': dl_ratio['action'],
        'icon': dl_ratio['emoji']
    })

    # Training frequency
    insights.append({
        'type': 'frequency',
        'priority': 'low',
        'title': '📅 Training Frequency',
        'message': interpret_sessions_per_week(stats['avg_sessions_per_week']),
        'icon': '📅'
    })

    # Progress for each lift
    for lift in ['Squat', 'Bench Press', 'Deadlift']:
        lift_data = get_lift_specific_data(lift)
        if lift_data and lift_data['first_10_avg'] and lift_data['last_10_avg']:
            progress_msg = interpret_progress(
                lift_data['first_10_avg'],
                lift_data['last_10_avg'],
                lift_data['weeks_trained'],
                lift
            )
            insights.append({
                'type': 'progress',
                'priority': 'low',
                'title': f'📈 {lift} Progress',
                'message': progress_msg,
                'icon': '📈'
            })

    return sorted(insights, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}[x['priority']])


def get_recent_training(weeks: int = 4) -> pd.DataFrame:
    """Get most recent training data."""
    df = load_training_data()
    max_week = df['week_order'].max()
    return df[df['week_order'] > max_week - weeks]


def get_block_summaries() -> List[Dict]:
    """
    Get detailed summaries for each training block.

    Returns list of block summaries with stats and interpretations.
    """
    df = load_training_data()

    # Group by block
    blocks = df.groupby(['block_name', 'block_type']).agg({
        'week_order': ['min', 'max', 'nunique'],
        'training_date': ['min', 'max'],
        'tonnage': 'sum',
        'sets': 'sum',
        'rpe': 'mean',
        'session_order': 'sum'
    }).reset_index()

    blocks.columns = ['block_name', 'block_type', 'start_week', 'end_week', 'weeks',
                      'start_date', 'end_date', 'tonnage', 'total_sets', 'avg_rpe', 'sessions']

    blocks = blocks.sort_values('start_week')

    summaries = []
    for _, block in blocks.iterrows():
        # Get main lift data for this block
        block_data = df[(df['block_name'] == block['block_name']) & (df['is_main_lift'] == True)]

        lift_peaks = {}
        lift_details = {}

        for lift in ['Squat', 'Bench Press', 'Deadlift']:
            lift_data = block_data[block_data['canonical_name'] == lift].sort_values('week_order')
            if not lift_data.empty:
                lift_peaks[lift] = lift_data['actual_weight'].max()

                # Get start and end weights for this block
                first_week_data = lift_data.head(3)  # First few entries
                last_week_data = lift_data.tail(3)   # Last few entries

                start_weight = first_week_data['actual_weight'].max()
                end_weight = last_week_data['actual_weight'].max()
                change = end_weight - start_weight
                avg_rpe = lift_data['rpe'].mean()
                total_sets = lift_data['sets'].sum()

                lift_details[lift] = {
                    'start_weight': start_weight,
                    'end_weight': end_weight,
                    'change': change,
                    'peak': lift_data['actual_weight'].max(),
                    'avg_rpe': avg_rpe if not pd.isna(avg_rpe) else 0,
                    'total_sets': int(total_sets),
                    'trend': 'up' if change > 0 else ('down' if change < 0 else 'stable')
                }

        # Generate interpretation
        interpretation = _interpret_block(block, lift_peaks, lift_details)

        summaries.append({
            'name': block['block_name'],
            'type': block['block_type'],
            'start_date': block['start_date'],
            'end_date': block['end_date'],
            'weeks': int(block['weeks']),
            'tonnage': block['tonnage'],
            'total_sets': int(block['total_sets']),
            'avg_rpe': block['avg_rpe'],
            'lift_peaks': lift_peaks,
            'lift_details': lift_details,
            'interpretation': interpretation
        })

    return summaries


def _interpret_block(block: pd.Series, lift_peaks: Dict, lift_details: Dict = None) -> str:
    """Generate detailed interpretation text for a training block with per-lift analysis."""
    block_type = block['block_type']
    avg_rpe = block['avg_rpe']

    # Base interpretation
    if block_type == 'build':
        if avg_rpe < 7:
            base = "Volume-focused building phase. Emphasis on technique and accumulating work capacity."
        else:
            base = "Intensity-focused building phase. Pushing weights while building strength."
    elif block_type == 'prep':
        base = "Meet preparation phase. Peaking for competition with reduced volume and higher intensity."
    elif block_type == 'competition':
        base = "Competition phase. Testing maximal strength on the platform."
    elif block_type == 'intro':
        base = "Introduction/transition phase. Establishing baseline and preparing for upcoming training."
    else:
        base = "General training phase with mixed focus."

    # Add per-lift progression details
    if lift_details:
        lift_summaries = []
        for lift in ['Squat', 'Bench Press', 'Deadlift']:
            if lift in lift_details:
                details = lift_details[lift]
                start = details['start_weight']
                end = details['end_weight']
                change = details['change']
                trend = details['trend']
                peak = details['peak']

                lift_name = lift.replace('Bench Press', 'Bench')

                if trend == 'up':
                    direction = f"+{change:.1f}kg"
                    emoji = "📈"
                elif trend == 'down':
                    direction = f"{change:.1f}kg"
                    emoji = "📉"
                else:
                    direction = "maintained"
                    emoji = "➡️"

                lift_summaries.append(f"{emoji} {lift_name}: {start:.1f}→{end:.1f}kg ({direction}), peaked at {peak:.1f}kg")

        if lift_summaries:
            return base + "\n\n" + "\n".join(lift_summaries)

    return base


def get_primary_secondary_day_analysis() -> Dict:
    """
    Analyze primary (Day 1-2) vs secondary (Day 3-4) training days.

    Primary days typically have main competition lifts with heavier weights.
    Secondary days focus on variations, accessories, and volume work.
    """
    df = load_training_data()

    # Classify days: 1-2 = primary, 3-4 = secondary
    df['day_type'] = df['session_order'].apply(
        lambda x: 'primary' if x <= 2 else 'secondary'
    )

    # Overall split
    primary_data = df[df['day_type'] == 'primary']
    secondary_data = df[df['day_type'] == 'secondary']

    # Main lifts analysis by day type
    main_lifts = df[df['is_main_lift'] == True]

    analysis = {
        'primary': {
            'sessions': primary_data['session_order'].nunique() if not primary_data.empty else 0,
            'total_tonnage': primary_data['tonnage'].sum(),
            'avg_rpe': primary_data['rpe'].mean() if not primary_data.empty else 0,
            'main_lift_volume': primary_data[primary_data['is_main_lift'] == True]['tonnage'].sum(),
            'accessory_volume': primary_data[primary_data['is_main_lift'] == False]['tonnage'].sum(),
        },
        'secondary': {
            'sessions': secondary_data['session_order'].nunique() if not secondary_data.empty else 0,
            'total_tonnage': secondary_data['tonnage'].sum(),
            'avg_rpe': secondary_data['rpe'].mean() if not secondary_data.empty else 0,
            'main_lift_volume': secondary_data[secondary_data['is_main_lift'] == True]['tonnage'].sum(),
            'accessory_volume': secondary_data[secondary_data['is_main_lift'] == False]['tonnage'].sum(),
        },
        'by_lift': {}
    }

    # Per-lift analysis
    for lift in ['Squat', 'Bench Press', 'Deadlift']:
        lift_data = main_lifts[main_lifts['canonical_name'] == lift]

        primary_lift = lift_data[lift_data['day_type'] == 'primary']
        secondary_lift = lift_data[lift_data['day_type'] == 'secondary']

        analysis['by_lift'][lift] = {
            'primary_avg_weight': primary_lift['actual_weight'].mean() if not primary_lift.empty else 0,
            'secondary_avg_weight': secondary_lift['actual_weight'].mean() if not secondary_lift.empty else 0,
            'primary_max': primary_lift['actual_weight'].max() if not primary_lift.empty else 0,
            'secondary_max': secondary_lift['actual_weight'].max() if not secondary_lift.empty else 0,
            'primary_rpe': primary_lift['rpe'].mean() if not primary_lift.empty else 0,
            'secondary_rpe': secondary_lift['rpe'].mean() if not secondary_lift.empty else 0,
        }

    return analysis


def get_all_skipped_exercises() -> pd.DataFrame:
    """
    Get all skipped exercises including accessories.

    Returns DataFrame with skipped exercises (both main lifts and accessories).
    """
    xl = pd.ExcelFile(DATA_FILE)
    skipped_exercises = []
    total_sheets = len(xl.sheet_names)
    is_latest_week = True

    for sheet_idx, sheet_name in enumerate(xl.sheet_names):
        df = pd.read_excel(xl, sheet_name=sheet_name, header=None)
        week_order = total_sheets - sheet_idx
        training_date = week_to_date(week_order)

        for i, row in df.iterrows():
            cell0 = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''

            # Skip headers and warmups
            if cell0.lower() in ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']:
                continue
            if 'warm up' in cell0.lower() or cell0.lower() == 'movement':
                continue
            if 'foam roll' in cell0.lower() or 'cardio' in cell0.lower():
                continue

            canonical, category, is_main = canonicalize_exercise(cell0)
            if canonical is None:
                continue

            try:
                prescribed = parse_weight(row.iloc[2]) if len(row) > 2 else None
                actual = parse_weight(row.iloc[3]) if len(row) > 3 else None
            except:
                continue

            # Track if exercise was prescribed but not done
            if prescribed is not None and actual is None and not is_latest_week:
                skipped_exercises.append({
                    'week': sheet_name.strip(),
                    'week_order': week_order,
                    'training_date': training_date,
                    'exercise': canonical,
                    'category': category,
                    'is_main_lift': is_main,
                    'prescribed_weight': prescribed
                })

        is_latest_week = False

    return pd.DataFrame(skipped_exercises) if skipped_exercises else pd.DataFrame()


def get_skip_summary() -> Dict:
    """Get summary of skipped exercises by type."""
    skipped = get_all_skipped_exercises()

    if skipped.empty:
        return {
            'main_lifts': {},
            'accessories': {},
            'total_main_skips': 0,
            'total_accessory_skips': 0
        }

    main_skips = skipped[skipped['is_main_lift'] == True]
    accessory_skips = skipped[skipped['is_main_lift'] == False]

    return {
        'main_lifts': main_skips.groupby('exercise').size().to_dict() if not main_skips.empty else {},
        'accessories': accessory_skips.groupby('exercise').size().to_dict() if not accessory_skips.empty else {},
        'total_main_skips': len(main_skips),
        'total_accessory_skips': len(accessory_skips),
        'by_category': accessory_skips.groupby('category').size().to_dict() if not accessory_skips.empty else {}
    }


def calculate_goal_projections() -> Dict:
    """
    Calculate realistic goal projections based on current progression rate.

    Returns projections for 6 months, 12 months, and long-term.
    """
    stats = get_summary_stats()

    # Calculate progression rate per month for each lift
    projections = {
        '6_month': {},
        '12_month': {},
        'long_term': {},
        'progression_rates': {}
    }

    for lift in ['Squat', 'Bench Press', 'Deadlift']:
        lift_data = get_lift_specific_data(lift)
        if not lift_data:
            continue

        pr = lift_data['pr']
        first_avg = lift_data['first_10_avg']
        last_avg = lift_data['last_10_avg']
        weeks = lift_data['weeks_trained']

        if first_avg and last_avg and weeks > 0:
            # Calculate monthly progression rate
            total_gain = last_avg - first_avg
            months = weeks / 4.33  # Average weeks per month
            monthly_rate = total_gain / months if months > 0 else 0

            projections['progression_rates'][lift] = monthly_rate

            # Project from current PR
            # Conservative: 70% of historical rate (progress slows as you advance)
            # Moderate: 85% of historical rate
            # Aggressive: 100% of historical rate

            conservative_rate = monthly_rate * 0.7
            moderate_rate = monthly_rate * 0.85

            projections['6_month'][lift] = {
                'conservative': pr + (conservative_rate * 6),
                'moderate': pr + (moderate_rate * 6),
                'current_pr': pr
            }

            projections['12_month'][lift] = {
                'conservative': pr + (conservative_rate * 12),
                'moderate': pr + (moderate_rate * 12),
                'current_pr': pr
            }

            # Long-term (2 years) - assume further slowdown
            long_term_rate = monthly_rate * 0.5
            projections['long_term'][lift] = {
                'conservative': pr + (long_term_rate * 24),
                'moderate': pr + (monthly_rate * 0.6 * 24),
                'current_pr': pr
            }

    return projections


def get_competition_context() -> Dict:
    """
    Get context around competition dates for chart markers.

    Returns competition info with week_order for chart plotting.
    """
    competitions_with_context = []

    for comp in COMPETITIONS:
        # Find the closest week_order to the competition date
        comp_date = comp['date']
        days_since_start = (comp_date - TRAINING_START_DATE).days
        week_order = max(1, days_since_start // 7 + 1)

        competitions_with_context.append({
            **comp,
            'week_order': week_order,
            'month_year': format_date(comp_date)
        })

    return {
        'competitions': competitions_with_context,
        'meet_to_meet_progress': _calculate_meet_progress()
    }


def _calculate_meet_progress() -> Dict:
    """Calculate progress between meets."""
    if len(COMPETITIONS) < 2:
        return {}

    first = COMPETITIONS[0]
    last = COMPETITIONS[-1]

    return {
        'squat_gain': last['squat'] - first['squat'],
        'bench_gain': last['bench'] - first['bench'],
        'deadlift_gain': last['deadlift'] - first['deadlift'],
        'total_gain': last['total'] - first['total'],
        'time_between': (last['date'] - first['date']).days,
        'attempts_improvement': f"{first['attempts']} → {last['attempts']}"
    }


if __name__ == '__main__':
    # Test data loading
    print("Loading training data...")
    df = load_training_data()
    print(f"Total entries: {len(df)}")

    stats = get_summary_stats()
    print(f"\nSummary Stats:")
    print(f"  Total weeks: {stats['total_weeks']}")
    print(f"  Date range: {stats['start_date'].strftime('%b %Y')} - {stats['end_date'].strftime('%b %Y')}")
    print(f"  Avg sessions/week: {stats['avg_sessions_per_week']:.1f}")
    print(f"  Mean RPE: {stats['mean_rpe']:.2f}")
    print(f"  Current PRs: {stats['current_prs']}")
    print(f"  Total: {stats['total_pr']:.1f}kg")

    print("\nSkipped exercises:")
    skipped = get_skipped_exercises()
    if not skipped.empty:
        print(skipped.to_string())
    else:
        print("  None found")
