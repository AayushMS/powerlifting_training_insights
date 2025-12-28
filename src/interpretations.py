#!/usr/bin/env python3
"""
Plain-English Interpretations for Powerlifting Metrics

Makes training data understandable for anyone, including non-powerlifters.
"""

from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta


# ============================================
# POWERLIFTING TERM DEFINITIONS
# ============================================

TERM_DEFINITIONS = {
    'PR': 'Personal Record - the heaviest weight you\'ve ever lifted for that exercise',
    'RPE': 'Rate of Perceived Exertion - how hard the set felt on a scale of 1-10',
    'Total': 'The sum of your best squat, bench press, and deadlift',
    'Tonnage': 'Total weight lifted (weight × sets × reps)',
    'Volume': 'The amount of work done - more sets and reps = more volume',
    '1RM': 'One Rep Max - the maximum weight you can lift for one repetition',
    'Deload': 'A planned period of reduced training to allow recovery',
    'Block': 'A training phase with specific goals (building muscle, peaking strength, etc.)',
}


# ============================================
# RPE INTERPRETATIONS
# ============================================

def interpret_rpe(rpe: float) -> Dict[str, str]:
    """
    Interpret an RPE value in plain English.

    Returns dict with:
        - level: short descriptor
        - meaning: what it feels like
        - implication: what it means for training
    """
    if rpe < 5:
        return {
            'level': 'Very Light',
            'meaning': 'Felt like a warm-up. Could easily do 5+ more reps.',
            'implication': 'Good for technique practice and recovery days.',
            'color': '#51CF66'  # green
        }
    elif rpe < 6:
        return {
            'level': 'Light',
            'meaning': 'Comfortable effort. Could do 4-5 more reps.',
            'implication': 'Building work capacity without fatigue.',
            'color': '#51CF66'
        }
    elif rpe < 7:
        return {
            'level': 'Moderate',
            'meaning': 'Starting to feel it. Could do 3-4 more reps.',
            'implication': 'Good for accumulating volume and practice.',
            'color': '#94D82D'  # lime
        }
    elif rpe < 8:
        return {
            'level': 'Moderate-Hard',
            'meaning': 'Challenging but controlled. Could do 2-3 more reps.',
            'implication': 'Sweet spot for building strength.',
            'color': '#FCC419'  # yellow
        }
    elif rpe < 8.5:
        return {
            'level': 'Hard',
            'meaning': 'Demanding. Could do 1-2 more reps with good form.',
            'implication': 'Effective for strength gains. Monitor recovery.',
            'color': '#FF922B'  # orange
        }
    elif rpe < 9.5:
        return {
            'level': 'Very Hard',
            'meaning': 'Near maximum. Maybe 1 more rep possible.',
            'implication': 'High stimulus. Use sparingly to avoid burnout.',
            'color': '#FF6B6B'  # red
        }
    else:
        return {
            'level': 'Maximum',
            'meaning': 'All-out effort. No more reps possible.',
            'implication': 'Competition intensity. Reserve for testing/meets.',
            'color': '#E03131'  # dark red
        }


def interpret_rpe_average(avg_rpe: float) -> str:
    """Interpret average training RPE."""
    if avg_rpe < 6:
        return (
            f"Your average training intensity is **{avg_rpe:.1f} RPE** (Light). "
            "This means most of your sets feel comfortable with plenty in reserve. "
            "**You have room to push harder** on main lifts if you want faster strength gains."
        )
    elif avg_rpe < 7:
        return (
            f"Your average training intensity is **{avg_rpe:.1f} RPE** (Moderate). "
            "You're training with good control and leaving reps in reserve. "
            "This is sustainable but **consider pushing to RPE 7-8** on top sets for better results."
        )
    elif avg_rpe < 8:
        return (
            f"Your average training intensity is **{avg_rpe:.1f} RPE** (Moderate-Hard). "
            "This is the **sweet spot for strength development**. "
            "You're working hard enough to stimulate gains while managing fatigue."
        )
    elif avg_rpe < 8.5:
        return (
            f"Your average training intensity is **{avg_rpe:.1f} RPE** (Hard). "
            "You're pushing close to your limits regularly. "
            "**Monitor your recovery** - this intensity works but can lead to burnout if sustained too long."
        )
    else:
        return (
            f"Your average training intensity is **{avg_rpe:.1f} RPE** (Very Hard). "
            "You're training at near-maximum effort frequently. "
            "**Consider backing off** to RPE 7-8 to reduce injury risk and improve long-term progress."
        )


# ============================================
# LIFT RATIO INTERPRETATIONS
# ============================================

def interpret_bench_squat_ratio(bench: float, squat: float) -> Dict[str, str]:
    """Interpret bench to squat ratio."""
    ratio = (bench / squat) * 100 if squat > 0 else 0

    if ratio < 60:
        return {
            'status': 'needs_attention',
            'emoji': '⚠️',
            'summary': 'Bench is significantly behind',
            'detail': (
                f"Your bench press ({bench:.0f}kg) is **{ratio:.0f}%** of your squat ({squat:.0f}kg). "
                f"The typical range is 65-80%. "
                f"**This is your biggest opportunity for improvement.** "
                f"A balanced bench would be around {squat * 0.75:.0f}kg."
            ),
            'action': 'Increase bench press volume and frequency. Consider adding a 3rd bench day.'
        }
    elif ratio < 70:
        return {
            'status': 'developing',
            'emoji': '📈',
            'summary': 'Bench catching up',
            'detail': (
                f"Your bench press ({bench:.0f}kg) is **{ratio:.0f}%** of your squat ({squat:.0f}kg). "
                f"You're in the lower end of normal (65-80%). "
                f"Keep prioritizing bench to reach a balanced **{squat * 0.75:.0f}kg**."
            ),
            'action': 'Continue bench focus. You\'re on the right track.'
        }
    elif ratio <= 80:
        return {
            'status': 'balanced',
            'emoji': '✅',
            'summary': 'Well balanced',
            'detail': (
                f"Your bench press ({bench:.0f}kg) is **{ratio:.0f}%** of your squat ({squat:.0f}kg). "
                f"This is in the ideal range (65-80%). "
                f"Your upper and lower body strength are well proportioned."
            ),
            'action': 'Maintain current approach. All lifts progressing well together.'
        }
    else:
        return {
            'status': 'bench_dominant',
            'emoji': '💪',
            'summary': 'Strong bencher',
            'detail': (
                f"Your bench press ({bench:.0f}kg) is **{ratio:.0f}%** of your squat ({squat:.0f}kg). "
                f"This is above typical (65-80%). You have excellent pressing strength! "
                f"Your squat may have more room for improvement."
            ),
            'action': 'Consider focusing more on squat to maximize your total.'
        }


def interpret_deadlift_squat_ratio(deadlift: float, squat: float) -> Dict[str, str]:
    """Interpret deadlift to squat ratio."""
    ratio = (deadlift / squat) * 100 if squat > 0 else 0

    if ratio < 105:
        return {
            'status': 'squat_dominant',
            'emoji': '🦵',
            'summary': 'Strong squatter',
            'detail': (
                f"Your deadlift ({deadlift:.0f}kg) is **{ratio:.0f}%** of your squat ({squat:.0f}kg). "
                f"Typically deadlift is 110-125% of squat. "
                f"Your squat is relatively strong - your deadlift has room to grow."
            ),
            'action': 'Focus on deadlift technique and volume to bring it up.'
        }
    elif ratio <= 125:
        return {
            'status': 'balanced',
            'emoji': '✅',
            'summary': 'Well balanced',
            'detail': (
                f"Your deadlift ({deadlift:.0f}kg) is **{ratio:.0f}%** of your squat ({squat:.0f}kg). "
                f"This is in the ideal range (110-125%). "
                f"Your hip and back strength are well developed relative to your legs."
            ),
            'action': 'Maintain current balance. Both lifts progressing well.'
        }
    else:
        return {
            'status': 'deadlift_dominant',
            'emoji': '🔥',
            'summary': 'Strong puller',
            'detail': (
                f"Your deadlift ({deadlift:.0f}kg) is **{ratio:.0f}%** of your squat ({squat:.0f}kg). "
                f"This is above typical (110-125%). You're an excellent puller! "
                f"Your squat may be holding back your total."
            ),
            'action': 'Prioritize squat development for bigger total gains.'
        }


# ============================================
# PROGRESS INTERPRETATIONS
# ============================================

def interpret_progress(start_weight: float, current_weight: float, weeks: int, lift_name: str) -> str:
    """Interpret progress over time."""
    gain = current_weight - start_weight
    gain_pct = (gain / start_weight * 100) if start_weight > 0 else 0
    monthly_rate = (gain / weeks * 4.33) if weeks > 0 else 0  # 4.33 weeks per month

    if gain < 0:
        return (
            f"Your {lift_name} has **decreased** by {abs(gain):.1f}kg ({abs(gain_pct):.0f}%) "
            f"over {weeks} weeks. This might be due to technique changes, fatigue, or a reset. "
            f"**Review what changed** in your training."
        )
    elif gain_pct < 5:
        return (
            f"Your {lift_name} has improved by **{gain:.1f}kg** ({gain_pct:.0f}%) over {weeks} weeks. "
            f"That's about **{monthly_rate:.1f}kg per month**. "
            f"Progress is slow but steady. Consider increasing volume or intensity."
        )
    elif gain_pct < 15:
        return (
            f"Your {lift_name} has improved by **{gain:.1f}kg** ({gain_pct:.0f}%) over {weeks} weeks. "
            f"That's about **{monthly_rate:.1f}kg per month**. "
            f"This is solid, sustainable progress. Keep doing what you're doing!"
        )
    else:
        return (
            f"Your {lift_name} has improved by **{gain:.1f}kg** ({gain_pct:.0f}%) over {weeks} weeks. "
            f"That's about **{monthly_rate:.1f}kg per month**. "
            f"**Excellent progress!** You're making great gains."
        )


# ============================================
# VOLUME INTERPRETATIONS
# ============================================

def interpret_tonnage(tonnage_kg: float) -> str:
    """Make tonnage relatable."""
    # Fun comparisons
    cars = tonnage_kg / 1500  # Average car weight
    elephants = tonnage_kg / 5000  # Average elephant

    if tonnage_kg < 10000:
        return f"**{tonnage_kg:,.0f} kg** lifted - that's about {cars:.0f} cars!"
    elif tonnage_kg < 50000:
        return f"**{tonnage_kg/1000:,.0f} tons** lifted - equivalent to {cars:.0f} cars!"
    else:
        return f"**{tonnage_kg/1000:,.0f} tons** lifted - that's {elephants:.0f} elephants worth of weight!"


def interpret_volume_change(current: float, previous: float) -> Dict[str, str]:
    """Interpret change in training volume."""
    if previous == 0:
        return {'status': 'new', 'message': 'Starting fresh!'}

    change_pct = ((current - previous) / previous) * 100

    if change_pct < -20:
        return {
            'status': 'decrease',
            'emoji': '📉',
            'message': f"Volume **down {abs(change_pct):.0f}%**. This could be a planned deload or life getting in the way."
        }
    elif change_pct < -5:
        return {
            'status': 'slight_decrease',
            'emoji': '➡️',
            'message': f"Volume **slightly down {abs(change_pct):.0f}%**. Normal fluctuation."
        }
    elif change_pct <= 10:
        return {
            'status': 'stable',
            'emoji': '✅',
            'message': f"Volume **stable** ({change_pct:+.0f}%). Consistent training!"
        }
    elif change_pct <= 20:
        return {
            'status': 'increase',
            'emoji': '📈',
            'message': f"Volume **up {change_pct:.0f}%**. Progressive overload in action!"
        }
    else:
        return {
            'status': 'big_increase',
            'emoji': '🚀',
            'message': f"Volume **up {change_pct:.0f}%**. Big jump! Make sure you can recover."
        }


# ============================================
# CONSISTENCY INTERPRETATIONS
# ============================================

def interpret_consistency(weeks_trained: int, total_weeks: int) -> str:
    """Interpret training consistency."""
    pct = (weeks_trained / total_weeks * 100) if total_weeks > 0 else 0
    missed = total_weeks - weeks_trained

    if pct >= 95:
        return (
            f"**{pct:.0f}% consistency** - You trained {weeks_trained} out of {total_weeks} weeks. "
            f"Only {missed} week(s) missed. **Incredible dedication!** "
            "Consistency is the #1 factor in long-term progress."
        )
    elif pct >= 85:
        return (
            f"**{pct:.0f}% consistency** - You trained {weeks_trained} out of {total_weeks} weeks. "
            f"Missed {missed} weeks. **Great consistency!** "
            "Life happens, but you keep showing up."
        )
    elif pct >= 70:
        return (
            f"**{pct:.0f}% consistency** - You trained {weeks_trained} out of {total_weeks} weeks. "
            f"Missed {missed} weeks. **Good consistency**, but there's room for improvement. "
            "Try to minimize gaps between training weeks."
        )
    else:
        return (
            f"**{pct:.0f}% consistency** - You trained {weeks_trained} out of {total_weeks} weeks. "
            f"**Inconsistent training** limits progress. "
            "Even 2-3 sessions per week consistently beats sporadic intense training."
        )


def interpret_sessions_per_week(avg_sessions: float) -> str:
    """Interpret training frequency."""
    if avg_sessions < 2:
        return (
            f"**{avg_sessions:.1f} sessions/week** - This is quite low for powerlifting. "
            "Aim for at least 3 sessions to see consistent progress."
        )
    elif avg_sessions < 3:
        return (
            f"**{avg_sessions:.1f} sessions/week** - Minimum effective dose. "
            "You're maintaining, but 3-4 sessions would accelerate progress."
        )
    elif avg_sessions <= 4:
        return (
            f"**{avg_sessions:.1f} sessions/week** - **Ideal frequency** for most people. "
            "Enough stimulus for progress with adequate recovery time."
        )
    elif avg_sessions <= 5:
        return (
            f"**{avg_sessions:.1f} sessions/week** - High frequency training. "
            "Great for advanced lifters. Make sure you're recovering well."
        )
    else:
        return (
            f"**{avg_sessions:.1f} sessions/week** - Very high frequency. "
            "This works for some, but watch for burnout and overuse injuries."
        )


# ============================================
# SKIPPED EXERCISE INTERPRETATIONS
# ============================================

def interpret_skipped_lift(lift_name: str, weeks_skipped: int, total_weeks: int) -> str:
    """Interpret skipped main lift sessions."""
    skip_pct = (weeks_skipped / total_weeks * 100) if total_weeks > 0 else 0

    if weeks_skipped == 0:
        return f"**Never skipped {lift_name}** - Perfect consistency on this lift!"
    elif skip_pct < 5:
        return (
            f"Skipped {lift_name} **{weeks_skipped} times** ({skip_pct:.0f}% of weeks). "
            "Very minor - probably planned deloads or life events."
        )
    elif skip_pct < 15:
        return (
            f"Skipped {lift_name} **{weeks_skipped} times** ({skip_pct:.0f}% of weeks). "
            "Some inconsistency. Try to prioritize this lift when scheduling is tight."
        )
    else:
        return (
            f"Skipped {lift_name} **{weeks_skipped} times** ({skip_pct:.0f}% of weeks). "
            "**Frequent skips may limit progress** on this lift. Consider why this happens."
        )


# ============================================
# GOAL INTERPRETATIONS
# ============================================

def interpret_goal_progress(current: float, goal: float, lift_name: str) -> Dict[str, str]:
    """Interpret progress toward a goal."""
    if goal <= 0:
        return {'status': 'no_goal', 'message': 'No goal set'}

    pct = (current / goal) * 100
    remaining = goal - current

    if pct >= 100:
        return {
            'status': 'achieved',
            'emoji': '🎉',
            'message': f"**GOAL ACHIEVED!** You hit {current:.1f}kg, surpassing your {goal:.0f}kg goal for {lift_name}!",
            'color': '#51CF66'
        }
    elif pct >= 90:
        return {
            'status': 'close',
            'emoji': '🔥',
            'message': f"**Almost there!** Only {remaining:.1f}kg to go for your {lift_name} goal.",
            'color': '#94D82D'
        }
    elif pct >= 75:
        return {
            'status': 'good_progress',
            'emoji': '💪',
            'message': f"**{pct:.0f}% there** - {remaining:.1f}kg left to your {lift_name} goal. Keep pushing!",
            'color': '#FCC419'
        }
    elif pct >= 50:
        return {
            'status': 'halfway',
            'emoji': '📈',
            'message': f"**Halfway there** ({pct:.0f}%) - {remaining:.1f}kg to go for {lift_name}. Steady progress!",
            'color': '#FF922B'
        }
    else:
        return {
            'status': 'early',
            'emoji': '🎯',
            'message': f"**{pct:.0f}% progress** toward {lift_name} goal. {remaining:.1f}kg to go. You've got this!",
            'color': '#74C0FC'
        }
