# Powerlifting Training Insights - Implementation Plan

## Executive Summary

This document outlines the plan to ingest 77 weeks of powerlifting training data from an Excel file into a PostgreSQL database and create meaningful visualizations for training insights.

---

## 1. Data Analysis Summary

### 1.1 Excel File Structure

- **Total Sheets**: 77 (each representing a training week)
- **Sheet Naming Conventions**:
  - `week N` - Initial training weeks (10 sheets)
  - `BN week N` - Block training cycles, e.g., B4 week 55 (15 sheets)
  - `build*` / `buildup*` - Building phase weeks (23 sheets)
  - `Start*` / `start*` - Starting phase weeks (6 sheets)
  - `Prep*` - Meet preparation weeks (6 sheets)
  - `new block*` - New training blocks (9 sheets)
  - `meet*` - Meet prep intro weeks (4 sheets)
  - `Game Time`, `Show time`, `Game day` - Competition days (3 sheets)

### 1.2 Sheet Layout (Per Week)

Each sheet follows this general structure:

| Rows | Content |
|------|---------|
| 0-10 | Warm-up/Activation section + Current Maxes (outdated in sheets - actual current: Squat: 220kg, Bench: 135kg, Deadlift: 260kg) |
| 11+ | Training days (Sunday, Monday, Wednesday, Thursday, Friday) with exercises |

**Note**: The "Current Maxes" values in the Excel sheets (200/120/250) were not kept updated. The actual current PRs are **Squat: 220kg, Bench: 135kg, Deadlift: 260kg**. These will be used as the reference maxes in the database.

### 1.3 Training Day Structure

Each training day contains:
- **Header Row**: Day name (Sunday, Monday, etc.)
- **Column Headers**: Movement, Intensity(KG), Weight used, Actual RPE, Sets, Reps, Tempo, Rest, Coach's Notes
- **Exercise Rows**: Main lifts and accessories with data

### 1.4 Main Lifts Identified

| Category | Canonical Name | Variations (all map to same exercise) |
|----------|----------------|---------------------------------------|
| **Squat** | Squat | Back Squat, Squat, Competition Squat, Comp Squat |
| **Bench** | Bench Press | Bench Press, Bench, Comp Bench Press, Competition Bench Press |
| **Deadlift** | Sumo Deadlift | Sumo Deadlift, Deadlift |

**Bench Variations (separate exercises)**:
- TnG Bench (Touch and Go - different movement pattern)
- Close Grip Bench Press (accessory)
- Wide Grip Spoto Bench (accessory)
- Incline Spoto Bench (accessory)
- Incline DB Bench (accessory)

**Deadlift Variations (separate exercises)**:
- Romanian Deadlift (accessory)
- Dumbbell RDL (accessory)

### 1.5 Accessory Movements

- Bulgarian split squat, Leg Press, Leg curl, Nordic, Nordic Curl Negative
- Pull Ups, Weighted Pull ups, Chin up, Chest supported row, DB Row
- Weighted Dips, Rolling Skull Crusher, over head extension
- Face Pull, Bicep 21's, Cable Upright Row
- Bird dog, Side plank, Hollow body hold, Three way plank

### 1.6 Data Inconsistencies Found

1. **RPE as Dates**: Some RPE values like `5/6` or `7/8` got interpreted as Excel dates (e.g., `2024-05-06 00:00:00`)
2. **Rep Schemes as Dates**: Values like `10/8` became dates
3. **Varying Column Counts**: Sheets have 12-14 columns depending on extra notes
4. **Movement Naming**: Inconsistent capitalization and spacing (e.g., "bulgarian split squat" vs "Bulgarian split sq")
5. **Same Exercise, Different Names**: Competition lifts have multiple names that mean the same thing:
   - Squat = Back Squat = Competition Squat = Comp Squat
   - Bench Press = Bench = Comp Bench Press = Competition Bench Press
   - Sumo Deadlift = Deadlift
6. **Missing Data**: Some accessory exercises have RPE targets instead of actual weights
7. **Row Offset Variations**: Some sheets have extra blank rows before day headers
8. **Outdated Current Maxes**: Sheet maxes show 200/120/250 but actual current PRs are 220/135/260

---

## 2. Database Design

### 2.1 PostgreSQL Schema

```sql
-- Training blocks/cycles
CREATE TABLE training_blocks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    block_type VARCHAR(50), -- 'intro', 'build', 'prep', 'meet', 'competition'
    sequence_order INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Individual training weeks
CREATE TABLE training_weeks (
    id SERIAL PRIMARY KEY,
    block_id INT REFERENCES training_blocks(id),
    sheet_name VARCHAR(100) NOT NULL,
    week_number INT,
    current_squat_max DECIMAL(6,2),
    current_bench_max DECIMAL(6,2),
    current_deadlift_max DECIMAL(6,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Training sessions (days)
CREATE TABLE training_sessions (
    id SERIAL PRIMARY KEY,
    week_id INT REFERENCES training_weeks(id),
    day_of_week VARCHAR(20) NOT NULL, -- Sunday, Monday, etc.
    session_order INT, -- Order within the week
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exercise catalog (normalized)
CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    canonical_name VARCHAR(100), -- Standardized name
    category VARCHAR(50), -- 'squat', 'bench', 'deadlift', 'accessory'
    is_main_lift BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name)
);

-- Individual sets performed
CREATE TABLE training_sets (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES training_sessions(id),
    exercise_id INT REFERENCES exercises(id),
    set_order INT,
    prescribed_weight DECIMAL(6,2),
    actual_weight DECIMAL(6,2),
    prescribed_rpe DECIMAL(3,1),
    actual_rpe DECIMAL(3,1),
    sets INT,
    reps VARCHAR(20), -- Can be "8", "AMRAP", "10 es", etc.
    tempo VARCHAR(20),
    rest VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Personal records tracking
CREATE TABLE personal_records (
    id SERIAL PRIMARY KEY,
    exercise_id INT REFERENCES exercises(id),
    weight DECIMAL(6,2) NOT NULL,
    reps INT DEFAULT 1,
    estimated_1rm DECIMAL(6,2),
    achieved_date DATE,
    week_id INT REFERENCES training_weeks(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX idx_training_sets_session ON training_sets(session_id);
CREATE INDEX idx_training_sets_exercise ON training_sets(exercise_id);
CREATE INDEX idx_training_sessions_week ON training_sessions(week_id);
CREATE INDEX idx_training_weeks_block ON training_weeks(block_id);
```

### 2.2 Docker Setup

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:16
    container_name: powerlifting_db
    environment:
      POSTGRES_USER: powerlifter
      POSTGRES_PASSWORD: stronglifts
      POSTGRES_DB: training_insights
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

volumes:
  pgdata:
```

---

## 3. Data Ingestion Pipeline

### 3.1 Python Script Structure

```
/training_insights/
├── docker-compose.yml
├── init.sql                    # Database schema
├── training_log.xlsx          # Source data
├── src/
│   ├── __init__.py
│   ├── config.py              # Database configuration
│   ├── models.py              # SQLAlchemy models
│   ├── parser.py              # Excel parsing logic
│   ├── normalizer.py          # Data cleaning/normalization
│   ├── ingest.py              # Main ingestion script
│   └── utils.py               # Helper functions
├── visualizations/
│   ├── dashboard.py           # Streamlit dashboard
│   └── charts.py              # Chart generation functions
└── requirements.txt
```

### 3.2 Data Normalization Rules

| Issue | Solution |
|-------|----------|
| Date-formatted RPE (2024-05-06) | Extract month/day as RPE (5/6 → 5.5 or range) |
| Date-formatted reps (1900-01-10) | Extract day as reps (10) |
| Movement name variations | Map to canonical names (see mapping table) |
| "RPE 8" in weight column | Parse as target RPE, set weight as NULL |
| "BW" weight | Store as 0 with flag for bodyweight |
| "20es" or "10 ea" reps | Store as-is, parse for calculations |
| Empty/NaN values | Store as NULL |

### 3.2.1 Critical Data Validation Rules

**IMPORTANT: These must be implemented during ingestion to catch data entry errors**

1. **Weight Deviation Check**
   - Flag any `actual_weight` that differs from `prescribed_weight` by more than 20%
   - Example caught: "building 45" sheet had bench logged as 177.5kg when prescribed was 117.5kg (typo)
   - Action: Log warning, use prescribed weight if deviation > 20%

2. **Weight Range Parsing**
   - Values like "40-30", "75-80" are weight ranges, NOT single numbers
   - Current bug: "40-30" parses as 4030, "75-80" parses as 7580
   - Solution: Detect hyphen in string, take the higher value (or average)
   - Affected sheets: "Prep 48" (40-30), "week 7" (75-80), "week 5" (75-80)

3. **Week Ordering/Sequencing**
   - Sheets are NOT in chronological order in the Excel file
   - Must establish sequence based on naming patterns:
     - `week 1` → `week 10` (initial weeks, oldest)
     - `start` → `Start 55`
     - `building 15` → `building 55`
     - Continue through blocks until `B4 week 55` (most recent)
   - Use sheet order in file (reversed) as proxy for chronological order

4. **Reasonable Weight Bounds**
   - Squat: Flag anything > 250kg or < 60kg for main lift
   - Bench: Flag anything > 160kg or < 40kg for main lift
   - Deadlift: Flag anything > 300kg or < 80kg for main lift
   - These bounds catch obvious typos while allowing for progression

### 3.3 Exercise Canonicalization Map

```python
EXERCISE_MAP = {
    # Squat - ALL these variations are the SAME main lift (just worded differently)
    'back squat': ('Squat', 'squat', True),
    'squat': ('Squat', 'squat', True),
    'squat ': ('Squat', 'squat', True),
    'competition squat': ('Squat', 'squat', True),
    'comp squat': ('Squat', 'squat', True),

    # Bench Press - ALL these variations are the SAME main lift (just worded differently)
    'bench press': ('Bench Press', 'bench', True),
    'bench': ('Bench Press', 'bench', True),
    'comp bench press': ('Bench Press', 'bench', True),
    'competition bench press': ('Bench Press', 'bench', True),
    'long pause bench': ('Bench Press', 'bench', True),  # Still competition-style

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
    'chest supported row': ('Chest Supported Row', 'accessory', False),
    'chest supported rows': ('Chest Supported Row', 'accessory', False),
    'seated chest supported rows': ('Chest Supported Row', 'accessory', False),
    'three way plank': ('Three Way Plank', 'accessory', False),
    '3 way plank': ('Three Way Plank', 'accessory', False),
    'face pull': ('Face Pull', 'accessory', False),
    'face pulls': ('Face Pull', 'accessory', False),
    # ... etc
}
```

---

## 4. Visualization Dashboard

### 4.1 Key Metrics for Powerlifters

1. **Main Lift Progression**
   - Line chart showing Squat/Bench/Deadlift top weights over time
   - Estimated 1RM progression using Epley formula

2. **Training Volume Analysis**
   - Weekly tonnage (sets × reps × weight) per lift category
   - Volume distribution across muscle groups

3. **Intensity Distribution**
   - RPE distribution histograms
   - Percentage of max progression over training blocks

4. **Competition Performance**
   - Best lifts on "Game day" / "Show time" sheets
   - Total (S+B+D) progression

5. **Accessory Work Balance**
   - Frequency of accessory movements
   - Push/Pull ratio analysis

6. **Training Frequency**
   - Days trained per week
   - Lift frequency (how often each main lift is trained)

### 4.2 Streamlit Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                    POWERLIFTING TRAINING INSIGHTS               │
├─────────────────────────────────────────────────────────────────┤
│  Current PRs:  Squat: 220 kg | Bench: 135 kg | Deadlift: 260 kg │
│  Estimated Total: 615 kg                                        │
├─────────────┬───────────────────────────────────────────────────┤
│   Filters   │                                                   │
│  ─────────  │         MAIN LIFT PROGRESSION CHART               │
│  Block: [▼] │              (Line chart - SBD)                   │
│  Date: [▼]  │                                                   │
│  Lift: [▼]  │                                                   │
├─────────────┼───────────────────────────────────────────────────┤
│   WEEKLY    │              INTENSITY DISTRIBUTION               │
│   VOLUME    │                (Histogram by RPE)                 │
│  (Bar chart)│                                                   │
├─────────────┴───────────────────────────────────────────────────┤
│                    BLOCK-BY-BLOCK COMPARISON                    │
│                (Grouped bar chart - volume by block)            │
├─────────────────────────────────────────────────────────────────┤
│  ACCESSORY FREQUENCY  │  TRAINING SPLIT DISTRIBUTION            │
│  (Horizontal bar)     │  (Pie chart by muscle group)            │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 Charts Implementation

Using **Plotly** for interactive charts:

1. **Main Lift Progression**: `px.line()` with multiple traces
2. **Volume Analysis**: `px.bar()` with grouping
3. **RPE Distribution**: `px.histogram()`
4. **Accessory Frequency**: `px.bar(orientation='h')`
5. **E1RM Trend**: `px.scatter()` with trendline

---

## 5. Implementation Steps

### Phase 1: Infrastructure Setup
1. Create `docker-compose.yml` for PostgreSQL
2. Write `init.sql` with schema
3. Create Python virtual environment
4. Install dependencies (pandas, openpyxl, sqlalchemy, psycopg2, streamlit, plotly)

### Phase 2: Data Ingestion
1. Implement Excel parser with day detection logic
2. Create normalization functions for RPE/date issues
3. Build exercise canonicalization mapping
4. Write ingestion script with progress tracking
5. Add validation and error handling

### Phase 3: Data Validation
1. Verify row counts match source
2. Check for orphaned records
3. Validate weight/RPE ranges
4. Generate data quality report

### Phase 4: Visualization
1. Create Streamlit app structure
2. Implement database queries for metrics
3. Build individual chart components
4. Assemble dashboard layout
5. Add interactivity (filters, date ranges)

### Phase 5: Enhancement
1. Add estimated 1RM calculations
2. Implement PR tracking and alerts
3. Add export functionality
4. Create training recommendations based on data

---

## 6. Dependencies

```txt
# requirements.txt
pandas>=2.0.0
openpyxl>=3.1.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
streamlit>=1.28.0
plotly>=5.18.0
python-dotenv>=1.0.0
```

---

## 7. Expected Outputs

1. **PostgreSQL Database** with normalized training data
2. **Interactive Dashboard** with:
   - Main lift progression charts
   - Volume and intensity analysis
   - Block-by-block comparisons
   - Accessory work tracking
   - PR timeline
3. **Data Export** capability for further analysis

---

## 8. Estimated Data Volume

| Table | Estimated Rows |
|-------|----------------|
| training_blocks | ~15 |
| training_weeks | 77 |
| training_sessions | ~350 (5 days × 70 weeks avg) |
| exercises | ~50 unique |
| training_sets | ~3,000-5,000 |
| personal_records | ~100+ |

---

## 9. Training Data Analysis & Insights

### 9.1 Current Status Summary

| Metric | Value |
|--------|-------|
| **Training Duration** | 77 weeks |
| **Current PRs** | Squat: 220kg, Bench: 135kg, Deadlift: 260kg |
| **Competition Total** | 615 kg |
| **Total Training Entries** | 930 sets tracked |

---

### 9.2 Main Lift Progression

#### Top Set Progression Over 77 Weeks

| Lift | Starting (First 10 wks) | Current (Last 10 wks) | All-Time Max | Trend |
|------|-------------------------|----------------------|--------------|-------|
| **Squat** | 178.0 kg | 208.5 kg | 220.0 kg | +0.83 kg/week |
| **Bench Press** | 109.8 kg | 127.2 kg | 135.0 kg | +0.27 kg/week |
| **Sumo Deadlift** | 208.5 kg | 237.2 kg | 260.0 kg | +0.98 kg/week |

#### Estimated 1RM Improvements (Epley Formula)

| Lift | Starting E1RM | Current E1RM | Improvement |
|------|--------------|--------------|-------------|
| Squat | 178.1 kg | 208.5 kg | **+30.4 kg (+17.1%)** |
| Bench | 109.8 kg | 129.3 kg | **+19.6 kg (+17.9%)** |
| Deadlift | 208.5 kg | 237.8 kg | **+29.2 kg (+14.0%)** |

---

### 9.3 Volume Analysis

#### Weekly Tonnage (Sets × Reps × Weight)

| Lift | Avg Weekly | Peak Weekly | Recent 10 Weeks |
|------|------------|-------------|-----------------|
| Squat | 685 kg | 1,205 kg | 698 kg |
| Bench Press | 398 kg | 550 kg | 433 kg |
| Sumo Deadlift | 768 kg | 912 kg | 861 kg |
| **TOTAL** | **1,850 kg** | **2,305 kg** | **1,992 kg** |

---

### 9.4 Intensity Analysis

#### Average Top Set Intensity (% of Current Max)

| Lift | Average | Recent 10 Weeks | Highest Reached |
|------|---------|-----------------|-----------------|
| Squat (220kg max) | 86.5% | 94.8% | 100.0% |
| Bench (135kg max) | 88.2% | 94.3% | 100.0% |
| Deadlift (260kg max) | 82.3% | 91.2% | 100.0% |

#### Intensity Zone Distribution (Squat)
- <70%: 6% of weeks
- 70-80%: 12% of weeks
- 80-90%: 42% of weeks (most common)
- 90-95%: 29% of weeks
- 95%+: 12% of weeks

---

### 9.5 RPE Analysis

| Lift | Avg RPE (All Sets) | Avg RPE (Top Sets) | Recent 10 Weeks |
|------|-------------------|-------------------|-----------------|
| Squat | 5.9 | 6.6 | 6.4 |
| Bench Press | 7.0 | 7.2 | 7.2 |
| Sumo Deadlift | 5.7 | 6.0 | 6.6 |

---

### 9.6 Lift Ratios (Relative Strength)

| Ratio | Your Value | Typical Elite Range | Assessment |
|-------|------------|---------------------|------------|
| Bench/Squat | 61.4% | 60-70% | ✅ Normal |
| Deadlift/Squat | 118.2% | 110-125% | ✅ Normal |
| Bench/Deadlift | 51.9% | 50-60% | ✅ Normal |

**Lift Distribution**: Squat 35.8% | Bench 22.0% | Deadlift 42.3%

---

### 9.7 Recent Performance (Last 10 vs Previous 10 Weeks)

| Lift | Previous Top | Recent Top | Change | Volume Change |
|------|-------------|------------|--------|---------------|
| Squat | 212.5 kg | 220.0 kg | **+7.5 kg** | +3% |
| Bench | 132.5 kg | 135.0 kg | **+2.5 kg** | -4% |
| Deadlift | 245.0 kg | 260.0 kg | **+15.0 kg** | +3% |

---

### 9.8 Training Frequency

| Lift | Sessions/Week | Most Common |
|------|--------------|-------------|
| Squat | 2.0 | 2 sessions/week |
| Bench Press | 2.0 | 2 sessions/week |
| Sumo Deadlift | 1.9 | 2 sessions/week |

---

### 9.9 Accessory Work Summary

| Exercise | Total Sets | Weeks Present |
|----------|-----------|---------------|
| Bench Variations (Spoto, CG, etc.) | 156 | 75 weeks |
| Rows | 155 | 57 weeks |
| RDL | 49 | 49 weeks |
| Pull Ups | 44 | 43 weeks |
| Bulgarian Split Squat | 34 | 34 weeks |
| Dips | 34 | 34 weeks |

---

## 10. Coaching Insights & Recommendations

### 10.1 What's Going Well ✅

1. **Consistent Progress**: All three lifts showing positive weekly trends
   - Deadlift growing fastest (+0.98 kg/week)
   - Squat solid progression (+0.83 kg/week)
   - Bench slower but still moving (+0.27 kg/week)

2. **Balanced Lift Ratios**: Your S/B/D ratios are within normal elite ranges - no major imbalances

3. **Good Training Frequency**: 2x/week per lift is optimal for intermediate-advanced lifters

4. **Conservative RPE Management**: Average RPE 5.9-7.0 leaves room for progression without burnout

5. **Strong Recent Block**: Last 10 weeks show acceleration in all lifts

### 10.2 Areas of Concern ⚠️

1. **Bench Press Is Your Weakest Link**
   - Slowest progression rate (+0.27 kg/week vs ~1 kg/week for others)
   - Volume actually DECREASED (-4%) in last 10 weeks while others increased
   - This is the lift with most room for improvement

2. **Bench Volume Declining**: Your bench volume dropped from 452 kg/wk to 433 kg/wk recently while squat/deadlift volume increased

3. **Deadlift Has Room to Grow**: At 82.3% average intensity, you're leaving some room on the table compared to squat (86.5%)

### 10.3 Actionable Recommendations

#### For Bench Press (Priority #1)
1. **Increase Volume**: Add 1-2 more working sets per session (you're at lowest volume of the three)
2. **Add Frequency**: Consider a 3rd bench day (even if light technique work)
3. **More Bench Variations**: You already do these consistently - keep them up

#### For Squat
1. **Current Approach Working**: Maintain 2x/week frequency
2. **Push Intensity**: You're ready for more 95%+ work (only 12% of weeks currently)
3. **Recent trend is strong**: +7.5kg in last block is excellent

#### For Deadlift
1. **Best Momentum**: Keep doing what you're doing
2. **Consider Higher Intensity**: You can handle more 90%+ work
3. **15kg PR in last 10 weeks is excellent** - program is working well

#### General
1. **Keep Bulgarian Split Squats**: Great for squat carryover, you're consistent with them
2. **Maintain Row Work**: Good pull-push balance
3. **Consider Adding**: Direct hamstring work (leg curls, GHR) to support deadlift

### 10.4 Key Metrics to Track in Dashboard

Based on this analysis, the dashboard should prominently display:

1. **Main Lift Progression Chart** (most important)
2. **Weekly Tonnage by Lift** (identify volume imbalances)
3. **Intensity Distribution** (% of max zones)
4. **RPE Trends** (fatigue management)
5. **Bench-specific metrics** (given it's the weak link)
6. **Block-over-Block Comparison** (see periodization effects)
7. **PR Timeline** (motivation)

---

## Next Steps

Once you approve this plan, I will:
1. Set up the Docker PostgreSQL container
2. Create the database schema
3. Write and execute the ingestion scripts
4. Build the Streamlit visualization dashboard
5. Present the training insights with interactive charts
