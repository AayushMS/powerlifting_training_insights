# Known Issues and Fixes

## Data Anomalies

### 177.5kg Bench Press Anomaly
- **Issue:** One entry showed 177.5kg bench press (impossible given progression)
- **Cause:** Typo - should be 117.5kg
- **Fix:** Added to `KNOWN_ANOMALIES` dict in data_processor.py
- **Also:** Added outlier detection (>40% higher than prescribed = likely typo)

```python
KNOWN_ANOMALIES = {
    (' building 45', 'Bench Press', 177.5): 117.5,
}
```

## Technical Issues

### Excel Date Format in RPE Column
- **Issue:** Excel sometimes converts RPE values like "6/7" to dates
- **Example:** "6/7" becomes "2025-06-07 00:00:00"
- **Fix:** `parse_rpe()` function detects and converts date strings back to RPE

### Skipped Exercises vs In-Progress
- **Issue:** Latest week may have null values because it's not complete yet
- **Fix:** Track `is_latest_week` flag and exclude from skip calculations

## Plotly Chart Issues

### Competition Marker vline Error
- **Issue:** `fig.add_vline()` fails with string x-axis (month format)
- **Cause:** Plotly's vline annotation can't handle categorical/string axes
- **Fix:** Use scatter markers with vertical line shapes instead

## Data Structure Notes

### Week Ordering
- Excel sheets are ordered newest-first
- `week_order` is calculated as `total_sheets - sheet_idx`
- Week 1 = April 2024, Week 81 = October 2025

### Exercise Canonicalization
Main lift detection:
- Squat: Contains "squat" but not "split" or "bulgarian"
- Bench Press: Contains "bench press" but not "close", "incline", or "db"
- Deadlift: Contains "deadlift" or "sumo deadlift" but not "romanian" or "rdl"

### Training Date Calculation
```python
TRAINING_START_DATE = datetime(2024, 4, 1)
training_date = TRAINING_START_DATE + timedelta(weeks=week_order - 1)
```
