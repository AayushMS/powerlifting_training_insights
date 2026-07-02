# Technical Architecture

## Tech Stack
- **Frontend:** Streamlit
- **Visualization:** Plotly
- **Data Processing:** Pandas, NumPy
- **Data Source:** Excel file (no database)

## File Structure
```
training_insights/
├── src/
│   ├── app.py              # Main Streamlit dashboard
│   ├── data_processor.py   # Data loading and analytics
│   └── interpretations.py  # Plain-English interpretations
├── knowledge_base/         # Documentation and context
├── docs/archive/           # Historical planning docs
├── Aayush man .xlsx        # Training data (105 sheets, 1 per week)
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container configuration (runs src/app.py)
└── docker-compose.yml      # Docker orchestration
```

## Refreshing the Data
The dashboard reads a static Excel export of the training-log Google Sheet. To update:
1. Export the Google Sheet as `.xlsx` (File → Download → Microsoft Excel, or the Drive API).
2. Drop the empty scratch tabs (`Sheet7`-`Sheet10`) so they aren't counted as weeks.
3. Replace `Aayush man .xlsx` at the repo root.
4. `load_training_data()` treats the first sheet as the newest week; ordering must stay
   newest-first (top) to oldest-bottom.

## Key Components

### data_processor.py
Main data processing module with these key functions:

| Function | Purpose |
|----------|---------|
| `load_training_data()` | Load and parse all Excel sheets |
| `get_lift_specific_data(lift)` | Get detailed data for one lift |
| `get_summary_stats()` | Overall training statistics |
| `get_block_summaries()` | Block-by-block analysis |
| `get_primary_secondary_day_analysis()` | Day 1-2 vs 3-4 comparison |
| `get_skip_summary()` | Skipped exercises (main + accessories) |
| `calculate_goal_projections()` | 6mo, 12mo, long-term projections |
| `get_competition_context()` | Competition data with chart markers |

### Key Constants (in data_processor.py)
```python
TRAINING_START_DATE = datetime(2024, 3, 18)  # Week 1 start (approximate)
ATHLETE_PROFILE = {...}  # Name, weight class, etc.
COMPETITIONS = [...]     # Meet results
GOAL_PRS = {...}         # Target PRs
```

### interpretations.py
Plain-English interpretation functions:
- `interpret_rpe()` - RPE levels explained
- `interpret_bench_squat_ratio()` - Ratio analysis
- `interpret_tonnage()` - Volume in relatable terms
- `interpret_goal_progress()` - Progress to goals
- `TERM_DEFINITIONS` - Glossary of powerlifting terms

### app.py
Streamlit dashboard sections:
1. Header with athlete profile
2. Hero section (PRs with trends)
3. Competition history
4. Per-lift progress charts (with competition markers)
5. Lift ratio analysis
6. Goal projections (6mo/12mo/long-term)
7. Block summaries
8. Primary/Secondary day analysis
9. Training consistency
10. Skip analysis
11. Accessory analysis
12. Insights & recommendations
13. Glossary

## Data Flow
```
Excel File → load_training_data() → DataFrame
    ↓
Canonicalize exercises, parse weights/RPE
    ↓
Apply anomaly fixes (177.5kg → 117.5kg)
    ↓
Add training_date column (week_to_date)
    ↓
Calculate tonnage, aggregate by week/month/block
    ↓
Generate interpretations → Display in Streamlit
```

## Deployment
- **Platform:** Streamlit Cloud
- **Branch:** release
- **URL:** Configured by user
