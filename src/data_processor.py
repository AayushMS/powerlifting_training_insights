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
import re

# Excel file path
DATA_FILE = Path(__file__).parent.parent / "Aayush man .xlsx"

# Current PRs (updated based on latest data)
CURRENT_PRS = {
    'Squat': 220,
    'Bench Press': 135,
    'Deadlift': 262.5
}

# Goal PRs for progress tracking
GOAL_PRS = {
    'Squat': 240,
    'Bench Press': 160,
    'Deadlift': 290
}

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


def parse_weight(val, prescribed=None) -> Optional[float]:
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

        # Outlier detection: if actual is >40% higher than prescribed, likely a typo
        if prescribed is not None and prescribed > 0:
            if weight > prescribed * 1.4:
                # Likely a typo - use prescribed instead
                return prescribed

        return weight
    except ValueError:
        return None


def parse_rpe(val) -> Optional[float]:
    """Parse RPE value, handling Excel date conversion bugs."""
    if pd.isna(val):
        return None

    val_str = str(val).strip()

    # Handle Excel date format (e.g., "2025-06-07 00:00:00" should be 6.7 RPE)
    if '2025' in val_str or '2024' in val_str:
        match = re.search(r'-(\d+)-(\d+)', val_str)
        if match:
            month = int(match.group(1))
            day = int(match.group(2))
            # Interpret as RPE like 6/7 -> 6.5 or 7/8 -> 7.5
            return (month + day) / 2 if day <= 10 else month

    # Handle range like "7.5-8" or "8-9"
    if '-' in val_str:
        parts = val_str.split('-')
        try:
            return (float(parts[0]) + float(parts[1])) / 2
        except (ValueError, IndexError):
            pass

    try:
        rpe = float(val_str)
        if 1 <= rpe <= 10:
            return rpe
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

    total_sheets = len(xl.sheet_names)

    for sheet_idx, sheet_name in enumerate(xl.sheet_names):
        df = pd.read_excel(xl, sheet_name=sheet_name, header=None)

        # Week order: newest first in Excel, so reverse
        week_order = total_sheets - sheet_idx

        # Get block classification
        block_name, block_type = classify_block(sheet_name)

        current_day = None
        session_order = 0

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
                actual = parse_weight(row.iloc[3], prescribed=prescribed) if len(row) > 3 else None
                rpe = parse_rpe(row.iloc[4]) if len(row) > 4 else None
                sets = parse_sets(row.iloc[5]) if len(row) > 5 else None
                reps = parse_reps(row.iloc[6]) if len(row) > 6 else None
            except (IndexError, ValueError):
                continue

            # Use actual weight if available, else prescribed
            weight = actual if actual is not None else prescribed

            if weight is not None and weight > 0:
                all_data.append({
                    'week': sheet_name.strip(),
                    'week_order': week_order,
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
                    'reps': reps or 1
                })

    df = pd.DataFrame(all_data)

    # Calculate tonnage
    df['tonnage'] = df['actual_weight'] * df['sets'] * df['reps']

    return df


def get_main_lift_data() -> pd.DataFrame:
    """Get main lift progression data."""
    df = load_training_data()
    main_lifts = df[df['is_main_lift'] == True].copy()

    # Aggregate by week and exercise
    progression = main_lifts.groupby(['week_order', 'week', 'canonical_name']).agg({
        'actual_weight': 'max',
        'rpe': 'mean',
        'tonnage': 'sum',
        'sets': 'sum'
    }).reset_index()

    progression.columns = ['week_order', 'week', 'exercise', 'top_weight', 'avg_rpe', 'tonnage', 'total_sets']

    return progression.sort_values('week_order')


def get_weekly_volume() -> pd.DataFrame:
    """Get weekly volume summary by category."""
    df = load_training_data()

    volume = df.groupby(['week_order', 'week', 'category']).agg({
        'tonnage': 'sum',
        'sets': 'sum',
        'session_order': 'nunique'
    }).reset_index()

    volume.columns = ['week_order', 'week', 'category', 'tonnage', 'total_sets', 'sessions']

    return volume.sort_values('week_order')


def get_rpe_distribution() -> pd.DataFrame:
    """Get RPE distribution data."""
    df = load_training_data()
    return df[['canonical_name', 'category', 'is_main_lift', 'rpe']].dropna(subset=['rpe'])


def get_accessory_frequency() -> pd.DataFrame:
    """Get accessory exercise frequency."""
    df = load_training_data()
    accessories = df[df['is_main_lift'] == False]

    freq = accessories.groupby(['canonical_name', 'category']).agg({
        'week_order': 'nunique',
        'sets': 'sum'
    }).reset_index()

    freq.columns = ['canonical_name', 'category', 'frequency', 'total_sets']

    return freq.sort_values('frequency', ascending=False)


def get_block_comparison() -> pd.DataFrame:
    """Get block-by-block comparison data."""
    df = load_training_data()
    main_lifts = df[df['is_main_lift'] == True]

    blocks = main_lifts.groupby(['block_name', 'block_type', 'canonical_name']).agg({
        'actual_weight': ['max', 'mean'],
        'tonnage': 'sum',
        'sets': 'sum',
        'week_order': 'min'  # For ordering
    }).reset_index()

    blocks.columns = ['block_name', 'block_type', 'exercise', 'max_weight', 'avg_weight', 'tonnage', 'total_sets', 'block_order']

    return blocks.sort_values('block_order')


def get_training_frequency() -> pd.DataFrame:
    """Get training frequency data."""
    df = load_training_data()

    # Count unique sessions per week
    freq = df.groupby(['week_order', 'week']).agg({
        'session_order': 'max',
        'day': 'nunique'
    }).reset_index()

    freq.columns = ['week_order', 'week', 'sessions_per_week', 'unique_days']

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
            prs[lift] = lift_data['actual_weight'].max()

    return prs


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

    return {
        'total_weeks': df['week_order'].nunique(),
        'total_sessions': df['session_order'].sum(),
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
        'current_prs': prs,
        'total_pr': sum(prs.values())
    }


def get_insights() -> List[Dict]:
    """Generate training insights based on data analysis."""
    df = load_training_data()
    stats = get_summary_stats()
    progression = get_main_lift_data()

    insights = []

    # RPE Analysis
    if stats['mean_rpe'] < 7:
        insights.append({
            'type': 'info',
            'priority': 'medium',
            'title': 'Conservative Training Intensity',
            'message': f"Your average RPE is {stats['mean_rpe']:.1f}. Research suggests RPE 7.5-8.5 is optimal for strength gains. You have room to push harder on main lifts.",
            'action': 'Consider increasing intensity on top sets to RPE 8-8.5'
        })
    elif stats['mean_rpe'] > 8.5:
        insights.append({
            'type': 'warning',
            'priority': 'high',
            'title': 'High Training Intensity',
            'message': f"Your average RPE is {stats['mean_rpe']:.1f}. Sustained high RPE training increases injury risk and can impair recovery.",
            'action': 'Consider adding more submaximal volume work'
        })
    else:
        insights.append({
            'type': 'success',
            'priority': 'low',
            'title': 'Well-Balanced Intensity',
            'message': f"Your average RPE of {stats['mean_rpe']:.1f} is in the optimal range for strength development.",
            'action': 'Maintain current approach'
        })

    # Lift ratio analysis
    prs = stats['current_prs']
    bench_squat_ratio = prs.get('Bench Press', 0) / prs.get('Squat', 1)

    if bench_squat_ratio < 0.65:
        insights.append({
            'type': 'warning',
            'priority': 'high',
            'title': 'Bench Press Lagging',
            'message': f"Your bench ({prs.get('Bench Press', 0)}kg) is {bench_squat_ratio*100:.0f}% of your squat ({prs.get('Squat', 0)}kg). The ideal ratio is 75-80%.",
            'action': 'Prioritize bench volume and frequency. Add a 3rd bench day with technique work.'
        })

    # Volume analysis
    bench_volume_ratio = stats['volume_bench'] / max(stats['volume_squat'], 1)
    if bench_volume_ratio < 0.6:
        insights.append({
            'type': 'info',
            'priority': 'medium',
            'title': 'Low Bench Volume',
            'message': f"Bench tonnage ({stats['volume_bench']:,.0f}kg) is only {bench_volume_ratio*100:.0f}% of squat tonnage ({stats['volume_squat']:,.0f}kg).",
            'action': 'Increase bench press volume with more back-off sets'
        })

    # Progression analysis
    for lift in ['Squat', 'Bench Press', 'Deadlift']:
        lift_data = progression[progression['exercise'] == lift].sort_values('week_order')
        if len(lift_data) >= 20:
            first_10 = lift_data.head(10)['top_weight'].mean()
            last_10 = lift_data.tail(10)['top_weight'].mean()
            progress_pct = ((last_10 - first_10) / first_10 * 100) if first_10 > 0 else 0

            if progress_pct > 10:
                insights.append({
                    'type': 'success',
                    'priority': 'low',
                    'title': f'{lift} Progressing Well',
                    'message': f"Your {lift.lower()} has improved by {progress_pct:.1f}% (avg {first_10:.0f}kg → {last_10:.0f}kg).",
                    'action': 'Continue current approach'
                })
            elif progress_pct < 0:
                insights.append({
                    'type': 'warning',
                    'priority': 'medium',
                    'title': f'{lift} Needs Attention',
                    'message': f"Your recent {lift.lower()} weights are below your earlier average.",
                    'action': 'Review technique, recovery, and programming'
                })

    # Frequency analysis
    if stats['avg_sessions_per_week'] < 3:
        insights.append({
            'type': 'info',
            'priority': 'medium',
            'title': 'Low Training Frequency',
            'message': f"Averaging {stats['avg_sessions_per_week']:.1f} sessions/week. Research supports 3-5 sessions for optimal progress.",
            'action': 'Consider adding training days if schedule allows'
        })

    # Goal projections
    total = stats['total_pr']
    insights.append({
        'type': 'info',
        'priority': 'high',
        'title': 'Goal Projection',
        'message': f"Current total: {total:.1f}kg. With continued progression, a 650kg total appears achievable.",
        'action': f"Focus on bench (current gap: ~{165 - prs.get('Bench Press', 135):.0f}kg to balanced ratio)"
    })

    return sorted(insights, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}[x['priority']])


def get_recent_training(weeks: int = 4) -> pd.DataFrame:
    """Get most recent training data."""
    df = load_training_data()
    max_week = df['week_order'].max()
    return df[df['week_order'] > max_week - weeks]


if __name__ == '__main__':
    # Test data loading
    print("Loading training data...")
    df = load_training_data()
    print(f"Total entries: {len(df)}")

    stats = get_summary_stats()
    print(f"\nSummary Stats:")
    print(f"  Total weeks: {stats['total_weeks']}")
    print(f"  Avg sessions/week: {stats['avg_sessions_per_week']:.1f}")
    print(f"  Mean RPE: {stats['mean_rpe']:.2f}")
    print(f"  Current PRs: {stats['current_prs']}")
    print(f"  Total: {stats['total_pr']:.1f}kg")

    print("\nInsights:")
    for insight in get_insights():
        print(f"  [{insight['priority'].upper()}] {insight['title']}: {insight['message']}")
