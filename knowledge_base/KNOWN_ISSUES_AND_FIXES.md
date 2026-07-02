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

### Excel/Google-Sheets Date Format in RPE Column
- **Issue:** Google Sheets converts RPE values like "8/9" into dates (e.g. Aug 9).
- **Example:** "8/9" becomes a datetime `2026-08-09`; "6/7" becomes `2025-06-07`.
- **2026 regression:** The old parser only checked for "2024"/"2025" strings, so 2026
  dates fell through to the range-splitter and produced `(2026+8)/2 ≈ 1017` RPE, which
  blew up the average to ~26.
- **Fix:** `parse_rpe()` now handles `datetime`/`Timestamp` cells directly (month/day →
  RPE, e.g. 8/9 → 8.5), matches dates of any year as a string fallback, and **clamps
  every path to the valid 1-10 range** (`_valid_rpe`) so stray dates/typos are dropped.

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
- Week 1 ≈ March 2024, Week 105 ≈ mid 2026
- Empty scratch tabs (`Sheet7`-`Sheet10`) must be dropped from the export or they
  inflate `total_sheets` and shift every week's computed date.

### Missing Weeks (source-sheet gaps)
- Some block weeks were never duplicated in the Google Sheet: **build up 2/5,
  build week 4/5, build 4/5** (holes between existing weeks).
- These predate the earliest repo snapshot (Dec 2025); **not recoverable** from the
  snapshot files or the Drive API (native Sheets can't be exported at a past revision,
  and the API's revision window starts Mar 2026). Only Google Sheets Version History
  could help, if within retention.

### Exercise Canonicalization
Main lift detection:
- Squat: Contains "squat" but not "split" or "bulgarian"
- Bench Press: Contains "bench press" but not "close", "incline", or "db"
- Deadlift: Contains "deadlift" or "sumo deadlift" but not "romanian" or "rdl"

### Training Date Calculation
Dates are approximate (the sheet has no explicit dates). Consecutive training weeks are
laid out from the start date, with hardcoded `TRAINING_BREAKS` inserted so the newest
week lands near the present.
```python
TRAINING_START_DATE = datetime(2024, 3, 18)
# see week_to_date() — adds break weeks that fall before a given week
```
