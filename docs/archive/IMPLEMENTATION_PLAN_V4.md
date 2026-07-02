# Implementation Plan V4: Chart Labels, Date Corrections, and 2026 Goals

## Summary of Changes
1. **Show data labels on all charts** - Display values directly on charts without needing to hover
2. **Correct training dates** - Account for training breaks and adjust TRAINING_START_DATE
3. **Update 2026 goals** - Squat 240, Bench 150, Deadlift 280

## Training Break Schedule
- June 2024: 4 weeks break
- October 2024: 2 weeks break
- May 2025: 3 weeks break
- Latest week: Dec 28, 2025

## Date Calculation
- Total breaks: 4 + 2 + 3 = 9 weeks
- 81 sheets = 81 weeks of actual training
- If latest week is Dec 28, 2025, counting back 81 training weeks + 9 break weeks = 90 weeks total
- 90 weeks before Dec 28, 2025 = ~March 2024
- TRAINING_START_DATE should be approximately **March 4, 2024**

---

## Phase 1: Update Goals to 2026 Targets
**Files:** `src/data_processor.py`

### Changes:
1. Update `GOAL_PRS` to new 2026 targets:
   - Squat: 240kg
   - Bench Press: 150kg
   - Deadlift: 280kg
   - Total: 670kg

---

## Phase 2: Correct Training Date Calculation
**Files:** `src/data_processor.py`

### Changes:
1. Update `TRAINING_START_DATE` to March 4, 2024
2. Add `TRAINING_BREAKS` constant to track break periods
3. Modify `week_to_date()` function to account for training breaks

### Training Breaks Data:
```python
TRAINING_BREAKS = [
    {'start': datetime(2024, 6, 1), 'weeks': 4},   # June 2024
    {'start': datetime(2024, 10, 1), 'weeks': 2},  # October 2024
    {'start': datetime(2025, 5, 1), 'weeks': 3},   # May 2025
]
```

---

## Phase 3: Add Data Labels to Charts
**Files:** `src/app.py`

### Changes:
1. Modify `create_lift_section()` to show text labels on data points
2. Increase chart height for better readability
3. Add `textposition` and `text` parameters to scatter traces
4. Ensure labels don't overlap with markers

### Implementation Details:
- Use `mode='lines+markers+text'` instead of `mode='lines+markers'`
- Add `text` parameter with formatted weight values
- Use `textposition='top center'` for label positioning
- Increase chart height from 300 to 400 pixels
- Adjust font size for readability

---

## Phase 4: Test and Validate
1. Verify date calculations are correct
2. Confirm charts display labels properly
3. Check goal progress percentages update correctly
4. Ensure no visual overlap or clutter

---

## Execution Order
1. Phase 1: Update GOAL_PRS (quick change)
2. Phase 2: Fix date calculations (requires logic changes)
3. Phase 3: Add chart labels (UI changes)
4. Phase 4: Test all changes together
