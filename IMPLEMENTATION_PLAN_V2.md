# Dashboard Enhancement Implementation Plan v2

**Date:** December 28, 2025
**Goal:** Make the dashboard intuitive for anyone, even non-powerlifters

---

## Overview of Changes

### Problems to Fix
1. **177.5kg bench anomaly** - Should be 117.5kg (typo in data)
2. **Week numbers are confusing** - Use dates/months instead
3. **Too much data on charts** - Hard to understand at a glance
4. **Missing context** - Numbers without interpretation
5. **Skipped exercises not tracked** - Need to show training consistency
6. **Everything lumped together** - Need per-lift breakdowns

### Design Principles
1. **Glanceable** - Understand in 3 seconds
2. **Contextual** - Every number has an interpretation
3. **Actionable** - Clear recommendations
4. **Accessible** - No powerlifting jargon without explanation

---

## Phase 1: Data Quality Fixes

### Tasks
- [ ] Fix 177.5kg bench anomaly (hardcode correction for that specific entry)
- [ ] Track skipped exercises properly (distinguish "not yet done" vs "skipped")
- [ ] Latest week handling (incomplete data = "in progress")

### Acceptance Criteria
- [ ] Bench PR shows 135kg (not 177.5kg)
- [ ] Skipped exercises are clearly identified
- [ ] Current week marked as "in progress"

### Test Cases
```python
def test_bench_pr():
    assert get_current_prs()['Bench Press'] == 135.0

def test_no_anomalies():
    df = load_training_data()
    bench = df[df['canonical_name'] == 'Bench Press']
    assert bench['actual_weight'].max() <= 140  # Reasonable max
```

---

## Phase 2: Date-Based Timeline

### Current Problem
- "Week 45" means nothing to anyone
- Can't relate training to life events

### Solution
- Map 81 weeks to actual dates (estimate start date)
- Display as "Jan 2024", "Feb 2024", etc.
- Group by training blocks with date ranges

### Date Mapping Logic
```
Week 1 = ~April 2024 (81 weeks ago from Dec 2025)
Week 81 = December 2025 (current)
```

### Tasks
- [ ] Calculate start date based on 81 weeks of data
- [ ] Add `training_date` column to all data
- [ ] Update all charts to use date axis
- [ ] Format dates as "Mon YYYY" for readability

### Acceptance Criteria
- [ ] X-axis shows months/years instead of week numbers
- [ ] Hover shows exact date range for each data point
- [ ] Training blocks labeled with date ranges

### Test Cases
```python
def test_date_mapping():
    df = load_training_data()
    assert 'training_date' in df.columns
    assert df['training_date'].min().year >= 2024
```

---

## Phase 3: Per-Lift Breakdown

### Current Problem
- All lifts combined = hard to analyze individual progress
- Can't see which lift needs attention

### Solution
Create separate sections for each lift:

#### 3.1 Squat Section
- Progress chart (just squat)
- Current PR with goal progress
- Volume trend
- RPE distribution
- Interpretation: "Your squat is progressing well at +X kg/month"

#### 3.2 Bench Press Section
- Progress chart (just bench)
- Current PR with goal progress
- Volume trend
- RPE distribution
- Interpretation: "Bench is your weakest lift relative to others"

#### 3.3 Deadlift Section
- Progress chart (just deadlift)
- Current PR with goal progress
- Volume trend
- RPE distribution
- Interpretation: "Deadlift is your strongest lift"

#### 3.4 Accessories Section
- Top accessories by category
- Volume distribution
- Missing movement patterns

### Tasks
- [ ] Create `LiftAnalysis` component for each main lift
- [ ] Add per-lift RPE distributions
- [ ] Add per-lift volume trends
- [ ] Create accessory breakdown by muscle group
- [ ] Add interpretation text for each section

### Acceptance Criteria
- [ ] Each lift has its own dedicated section
- [ ] Interpretations explain what the numbers mean
- [ ] Accessories grouped by purpose (back, arms, core, etc.)

---

## Phase 4: Plain-English Interpretations

### Current Problem
- "Mean RPE: 6.26" - What does that mean?
- "Bench/Squat ratio: 61%" - Good or bad?

### Solution
Add contextual explanations everywhere:

#### RPE Interpretations
| RPE Range | Interpretation |
|-----------|----------------|
| < 6 | "Very easy - you could do many more reps" |
| 6-7 | "Moderate - building technique and volume" |
| 7-8 | "Challenging - good for strength gains" |
| 8-9 | "Hard - close to your limit" |
| 9-10 | "Maximum effort - competition intensity" |

#### Ratio Interpretations
| Ratio | Status | Interpretation |
|-------|--------|----------------|
| Bench/Squat < 65% | Needs work | "Your bench is lagging - this is your biggest opportunity for total improvement" |
| Bench/Squat 65-80% | Good | "Well balanced upper/lower body strength" |
| Deadlift/Squat 110-125% | Ideal | "Good posterior chain development" |

#### Volume Interpretations
- "You lifted X tons this month - that's equivalent to Y cars!"
- "Your training volume increased X% compared to last month"

### Tasks
- [ ] Add interpretation helpers for all metrics
- [ ] Create "What this means" sections
- [ ] Add relatable comparisons (e.g., "weight of a small car")
- [ ] Explain powerlifting terms on first use

### Acceptance Criteria
- [ ] Every metric has plain-English explanation
- [ ] Non-powerlifters can understand the dashboard
- [ ] Jargon is defined when first used

---

## Phase 5: Simplified Charts

### Current Problem
- Too many lines on one chart
- Information overload
- Hard to see trends

### Solution
Apply these principles to all charts:

#### 5.1 One Message Per Chart
- Bad: "All lifts progression with trends, averages, and PRs"
- Good: "Your squat is going up"

#### 5.2 Reduce Data Points
- Show monthly averages instead of every session
- Use sparklines for quick trends
- Reserve detailed views for expandable sections

#### 5.3 Color Coding
- 🟢 Green = Good/Improving
- 🟡 Yellow = Needs attention
- 🔴 Red = Problem area

#### 5.4 Progress Indicators
- Use gauges for ratios
- Use progress bars for goals
- Use trend arrows for direction

### New Chart Types

#### Hero Stats (Top of Page)
```
┌─────────────────────────────────────────────────────────┐
│  SQUAT          BENCH           DEADLIFT       TOTAL   │
│  220 kg         135 kg          262.5 kg       617.5kg │
│  ████████░░     ████░░░░░░      █████████░     ███████░│
│  92% of goal    84% of goal     91% of goal    89%     │
│  ↑ +15kg        ↑ +5kg          ↑ +12.5kg      ↑ +32.5 │
│  vs 6mo ago     vs 6mo ago      vs 6mo ago     vs 6mo  │
└─────────────────────────────────────────────────────────┘
```

#### Monthly Progress (Simple Line)
```
        Squat Progress
280 ┤
260 ┤                              ●
240 ┤                    ●    ●
220 ┤              ● ●
200 ┤        ● ●
180 ┤   ● ●
    └──────────────────────────────
      Apr  Jun  Aug  Oct  Dec
      2024           2025
```

#### Training Consistency Calendar
```
    Apr 2024                Dec 2025
    ■ ■ ■ ■ □ ■ ■ ■ ■ ■ ... ■ ■ ■ □

    ■ = Trained  □ = Skipped

    "You trained 78 out of 81 weeks (96% consistency)"
```

### Tasks
- [ ] Redesign hero section with trend indicators
- [ ] Create monthly aggregated charts
- [ ] Add training consistency calendar
- [ ] Implement color-coded status indicators
- [ ] Add sparklines for quick trends
- [ ] Create expandable detailed views

### Acceptance Criteria
- [ ] Each chart conveys one clear message
- [ ] Can understand dashboard in under 30 seconds
- [ ] Color coding is consistent throughout
- [ ] Mobile-friendly layout

---

## Phase 6: New Sections to Add

### 6.1 Training Summary Card
"In the last 81 weeks, you've:
- Lifted 120 tons total (weight of 80 cars!)
- Trained 324 sessions (4x per week average)
- Increased your total by 67.5 kg (+12%)
- Never missed more than 1 week in a row"

### 6.2 This Month vs Last Month
Simple comparison table with arrows

### 6.3 Strength Milestones
- "First 200kg squat: March 2024"
- "First 250kg deadlift: June 2024"
- "Current goal: 650kg total"

### 6.4 Recovery Indicators
Based on RPE trends:
- "Your recent training intensity is sustainable"
- "Consider a deload if fatigue accumulates"

### 6.5 What to Focus On Next
Prioritized recommendations:
1. "Increase bench press volume (+20%)"
2. "Push RPE to 7-8 on main lifts"
3. "Add more tricep work for bench support"

---

## Implementation Order

### Day 1: Phases 1-2
1. Fix data anomalies
2. Add date mapping
3. Test data integrity

### Day 2: Phases 3-4
1. Create per-lift sections
2. Add interpretations
3. Write explanation text

### Day 3: Phases 5-6
1. Simplify charts
2. Add new sections
3. Final testing

---

## Success Metrics

After implementation, the dashboard should:

1. **Be understandable by anyone** - Show to a non-lifter, they get it
2. **Load in < 3 seconds** - No performance regression
3. **Answer key questions immediately:**
   - "How am I progressing?" → Hero stats with trends
   - "What should I focus on?" → Prioritized recommendations
   - "Am I training consistently?" → Calendar view
   - "Is my training balanced?" → Ratio gauges

---

## Files to Modify

| File | Changes |
|------|---------|
| `src/data_processor.py` | Add date mapping, fix anomalies, skipped exercise tracking |
| `src/app.py` | Complete redesign with new sections |
| `src/interpretations.py` | NEW: All interpretation logic |

---

*Plan created: December 28, 2025*
