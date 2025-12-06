-- Powerlifting Training Insights Database Schema

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
    sequence_order INT, -- Global ordering across all weeks
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
    reps_numeric INT, -- Parsed numeric value for calculations
    tempo VARCHAR(20),
    rest VARCHAR(20),
    notes TEXT,
    is_bodyweight BOOLEAN DEFAULT FALSE,
    data_quality_flag VARCHAR(50), -- 'valid', 'weight_deviation', 'out_of_bounds', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Personal records tracking
CREATE TABLE personal_records (
    id SERIAL PRIMARY KEY,
    exercise_id INT REFERENCES exercises(id),
    weight DECIMAL(6,2) NOT NULL,
    reps INT DEFAULT 1,
    estimated_1rm DECIMAL(6,2),
    week_id INT REFERENCES training_weeks(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data quality log for tracking issues found during ingestion
CREATE TABLE data_quality_log (
    id SERIAL PRIMARY KEY,
    sheet_name VARCHAR(100),
    row_number INT,
    column_name VARCHAR(50),
    original_value TEXT,
    corrected_value TEXT,
    issue_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX idx_training_sets_session ON training_sets(session_id);
CREATE INDEX idx_training_sets_exercise ON training_sets(exercise_id);
CREATE INDEX idx_training_sessions_week ON training_sessions(week_id);
CREATE INDEX idx_training_weeks_block ON training_weeks(block_id);
CREATE INDEX idx_training_weeks_sequence ON training_weeks(sequence_order);
CREATE INDEX idx_exercises_canonical ON exercises(canonical_name);
CREATE INDEX idx_exercises_category ON exercises(category);

-- Insert current max values as reference
INSERT INTO training_blocks (name, block_type, sequence_order) VALUES
    ('Current', 'reference', 0);

-- View for easy access to main lift progression
CREATE VIEW main_lift_progression AS
SELECT
    tw.sequence_order,
    tw.sheet_name,
    e.canonical_name as exercise,
    MAX(ts.actual_weight) as top_weight,
    MAX(ts.actual_rpe) as top_set_rpe,
    SUM(ts.sets * ts.reps_numeric * ts.actual_weight) as tonnage
FROM training_sets ts
JOIN training_sessions tsess ON ts.session_id = tsess.id
JOIN training_weeks tw ON tsess.week_id = tw.id
JOIN exercises e ON ts.exercise_id = e.id
WHERE e.is_main_lift = TRUE
GROUP BY tw.sequence_order, tw.sheet_name, e.canonical_name
ORDER BY tw.sequence_order, e.canonical_name;

-- View for weekly volume summary
CREATE VIEW weekly_volume_summary AS
SELECT
    tw.sequence_order,
    tw.sheet_name,
    e.category,
    COUNT(DISTINCT tsess.id) as sessions,
    SUM(ts.sets) as total_sets,
    SUM(ts.sets * ts.reps_numeric * ts.actual_weight) as tonnage
FROM training_sets ts
JOIN training_sessions tsess ON ts.session_id = tsess.id
JOIN training_weeks tw ON tsess.week_id = tw.id
JOIN exercises e ON ts.exercise_id = e.id
WHERE ts.actual_weight IS NOT NULL AND ts.reps_numeric IS NOT NULL
GROUP BY tw.sequence_order, tw.sheet_name, e.category
ORDER BY tw.sequence_order, e.category;
