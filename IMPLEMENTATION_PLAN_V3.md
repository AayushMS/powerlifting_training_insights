# Dashboard Enhancement Implementation Plan v3

**Date:** December 28, 2025
**Athlete:** Aayush Man Singh | U93kg | ~90-91kg bodyweight

---

## Overview of New Features

### User Requirements
1. **Competition History** - Show NYFC Classic 2024 and OX Classic 2025 results
2. **Competition Markers on Charts** - Visual indicators on progress charts
3. **Athlete Profile Section** - Name, weight class, bodyweight
4. **Block Summaries** - Performance analysis for each training block
5. **Accessory Skip Tracking** - Track skipped accessories (not just main lifts)
6. **Primary/Secondary Day Metrics** - Day 1-2 vs Day 3-4 analysis
7. **Goal Projections** - 6-month, 12-month, and long-term goals
8. **Latest Week Handling** - Mark as incomplete (not yet done)
9. **Comprehensive Review** - Validate all numbers and analysis

---

## Competition Data

### NYFC Classic 2024 Invitational (December 9, 2024)
- **Squat:** 220 kg
- **Bench:** 122.5 kg (missed 130kg 3rd attempt)
- **Deadlift:** 250 kg
- **Total:** 592.5 kg
- **Attempts:** 8/9
- **Placement:** 4th

### OX Classic Summerslam (April 27, 2025)
- **Squat:** 220 kg
- **Bench:** 130 kg
- **Deadlift:** 255 kg
- **Total:** 605 kg
- **Attempts:** 9/9
- **Placement:** TBD

### Progress Between Meets
- Squat: 220 → 220 (+0 kg)
- Bench: 122.5 → 130 (+7.5 kg) ✓ Made the weight that was missed!
- Deadlift: 250 → 255 (+5 kg)
- Total: 592.5 → 605 (+12.5 kg)

---

## Phase 1: Add Competition Data & Athlete Profile

### Tasks
- [ ] Create athlete profile constants (name, weight class, bodyweight)
- [ ] Create competition history data structure
- [ ] Add "Athlete Profile" section at top of dashboard
- [ ] Add "Competition History" section with results comparison

### Files to Modify
- `src/data_processor.py` - Add competition data constants
- `src/app.py` - Add profile and competition sections

---

## Phase 2: Competition Markers on Charts

### Tasks
- [ ] Add vertical lines/markers on progress charts at competition dates
- [ ] Show competition totals as special points on the chart
- [ ] Add tooltips showing competition details

### Implementation
```python
COMPETITIONS = [
    {
        'name': 'NYFC Classic 2024',
        'date': datetime(2024, 12, 9),
        'squat': 220, 'bench': 122.5, 'deadlift': 250,
        'total': 592.5, 'attempts': '8/9', 'place': '4th'
    },
    {
        'name': 'OX Classic Summerslam',
        'date': datetime(2025, 4, 27),
        'squat': 220, 'bench': 130, 'deadlift': 255,
        'total': 605, 'attempts': '9/9', 'place': 'TBD'
    }
]
```

---

## Phase 3: Block Summaries with Interpretations

### Tasks
- [ ] Identify all training blocks from sheet names
- [ ] Calculate per-block statistics (volume, intensity, PRs)
- [ ] Generate interpretations for each block
- [ ] Create "Block Review" section showing progression

### Block Analysis Template
```
Block X (Month Year - Month Year)
├── Duration: X weeks
├── Main Lift Peaks: Squat Xkg, Bench Xkg, Deadlift Xkg
├── Average RPE: X.X
├── Total Volume: X tons
├── Interpretation: "Building phase focused on volume..."
└── Key Insight: "Bench showed most improvement..."
```

---

## Phase 4: Accessory Skip Tracking & Primary/Secondary Days

### Tasks
- [ ] Update skip tracking to include accessories
- [ ] Classify days as primary (Day 1-2) vs secondary (Day 3-4)
- [ ] Calculate metrics for each day type
- [ ] Add "Training Distribution" section

### Day Classification
- **Primary Days (Day 1-2):** Main competition lifts, heavier weights
- **Secondary Days (Day 3-4):** Variations, accessories, volume work

### Metrics to Track
- Volume distribution (primary vs secondary)
- RPE distribution by day type
- Skip rate by day type
- Progress correlation

---

## Phase 5: Goal Projections

### Tasks
- [ ] Calculate current progression rate (kg/month)
- [ ] Project 6-month goals based on trend
- [ ] Project 12-month goals
- [ ] Set long-term goals (2+ years)
- [ ] Add "Goal Roadmap" section

### Projection Logic
```
Current PR + (monthly_gain × months) = Projected PR

Conservative: 80% of trend rate
Moderate: 100% of trend rate
Aggressive: 120% of trend rate
```

---

## Phase 6: Complete Analysis & Validation

### Tasks
- [ ] Validate all PR numbers against raw data
- [ ] Cross-check competition data
- [ ] Review all interpretations for accuracy
- [ ] Identify any data anomalies
- [ ] Add "Data Quality Report" section

### Validation Checklist
- [ ] Squat PR matches max in data
- [ ] Bench PR matches max (with anomaly fix)
- [ ] Deadlift PR matches max in data
- [ ] Date range is accurate
- [ ] Week count is correct
- [ ] Competition dates align with data

---

## Phase 7: Data Collection Suggestions (Terminal Only)

**NOT to be included in dashboard - output to terminal only**

Potential additional data points:
1. Weekly training reflections
2. Sleep quality/hours
3. Nutrition tracking (calories, protein)
4. Bodyweight trends
5. Fatigue/readiness scores
6. Video links for PRs
7. Injury/pain notes
8. Life stress indicators

---

## Implementation Order

### Session 1: Phases 1-2
1. Add athlete profile and competition data
2. Update charts with competition markers
3. Test visualization

### Session 2: Phases 3-4
1. Create block analysis functions
2. Implement primary/secondary day classification
3. Update accessory skip tracking

### Session 3: Phases 5-6
1. Add goal projections
2. Complete validation review
3. Final testing

### Session 4: Phase 7
1. Output data collection suggestions to terminal

---

*Plan created: December 28, 2025*
