#!/usr/bin/env python3
"""
Chat-Derived Insights

Curated, dated insights extracted from 4.5 years of coaching chat between
Aayush and coach Ojash Joshi (see docs/chat_insights/ for the full analysis).

This is hand-curated structured data — training-relevant highlights only — that
the dashboard renders alongside the numbers to explain the *why* behind them
(injuries, coaching cues, and mindset). Dates are real (from chat timestamps).
"""

from datetime import datetime

# =============================================================================
# INJURY / RECOVERY
# =============================================================================
# Severity: 'major' (physio / ≥1 week changed training), 'moderate', 'minor', 'illness'.
INJURY_EVENTS = [
    {'date': datetime(2022, 1, 4),  'severity': 'moderate', 'area': 'Right hip', 'lifts': 'Deadlift, Squat',
     'note': 'Tweaked on a new slack-pull technique during 2022 prep.'},
    {'date': datetime(2022, 1, 27), 'severity': 'moderate', 'area': 'Eyes (burst vessels)', 'lifts': '—',
     'note': 'Subconjunctival haemorrhage in both eyes during heavy prep.'},
    {'date': datetime(2024, 5, 2),  'severity': 'moderate', 'area': 'Left arm nerve', 'lifts': 'Deadlift',
     'note': 'Numbness from narrow deadlift grip; eased with straps on back-offs.'},
    {'date': datetime(2024, 9, 11), 'severity': 'major',    'area': 'Hands/arms nerve pinch', 'lifts': 'Squat, Bench, Pull-ups',
     'note': 'Worsening numbness → booked physio; swapped weighted pull-ups for lat pulldown.'},
    {'date': datetime(2024, 11, 24),'severity': 'illness',  'area': 'Fever + food poisoning', 'lifts': 'All',
     'note': '102.8°F in NYFC peak week (office-canteen food).'},
    {'date': datetime(2024, 12, 16),'severity': 'major',    'area': 'Lower back', 'lifts': 'Deadlift, Squat',
     'note': 'Post-NYFC micro-injury; physio found swelling above the left lumbar spine.'},
    {'date': datetime(2025, 3, 6),  'severity': 'moderate', 'area': 'Cervical-spine nerve', 'lifts': 'Bench, Deadlift',
     'note': 'Arm tingling; neck warmups added before training.'},
    {'date': datetime(2025, 6, 27), 'severity': 'illness',  'area': 'Gastritis / food poisoning', 'lifts': 'All',
     'note': 'Lost ~2 kg bodyweight; RPE-based reload after.'},
    {'date': datetime(2025, 10, 2), 'severity': 'major',    'area': 'Car accident (life stress)', 'lifts': 'All',
     'note': 'Weeks of poor sleep/nutrition; main lifts only.'},
    {'date': datetime(2025, 11, 7), 'severity': 'moderate', 'area': 'Right hand/palm numb', 'lifts': 'Bench, Deadlift',
     'note': 'Numbness caused a failed 132.5 bench top set.'},
    {'date': datetime(2025, 12, 13),'severity': 'moderate', 'area': 'Ankle', 'lifts': 'Squat',
     'note': 'Rolled on uneven ground; mobility loss, RPE-based return.'},
    {'date': datetime(2026, 6, 2),  'severity': 'major',    'area': 'Lower back (flare)', 'lifts': 'Deadlift, Squat',
     'note': 'Confidence collapse → block reset; daily core correctives.'},
]

# Windows to call out as injury periods (used to explain strength dips).
INJURY_WINDOWS = [
    {'start': datetime(2024, 12, 16), 'end': datetime(2025, 2, 1),
     'label': 'Post-NYFC lower-back injury'},
    {'start': datetime(2026, 6, 2), 'end': datetime(2026, 6, 18),
     'label': 'Lower-back flare → block reset'},
]

# Pain-free turning points — his strongest positive signal.
PAINLESS_MILESTONES = [
    {'date': datetime(2025, 1, 28), 'note': 'First pain-free deadlift after the post-NYFC injury.'},
    {'date': datetime(2026, 6, 8),  'note': 'Painless deadlift to 220 kg after the June flare.'},
    {'date': datetime(2026, 6, 18), 'note': 'First fully painless squat session of the recovery.'},
]

INJURY_PATTERNS = [
    ("🖐️ Nerve symptoms (hands/arms) are the most recurrent complaint",
     "They cluster around three triggers every time — narrow deadlift grip, weighted pull-ups, "
     "and heavy squat bracing. Proven fixes: wider DL grip, straps on back-offs, lat pulldowns, "
     "neck warmups. Worth making a standing policy, not a per-flare fix."),
    ("🔻 The lower back breaks *after* peaks, not during them",
     "Both major back episodes (post-NYFC Dec 2024, and June 2026) hit in the vulnerable "
     "post-competition window. A structured 2–4 week post-meet re-entry (capped load + core "
     "correctives) would likely prevent the next one."),
    ("🤒 Illness reliably strikes peak weeks",
     "Fever/food poisoning before NYFC, a 103.6°F fever at the meet itself, gastritis in 2025. "
     "Tighten food hygiene and immune load in the final 2–3 weeks of prep."),
    ("📉 Recovery debt from work/study precedes dips",
     "The 2025 job and 2026 Masters semester (3 consecutive training days) both directly "
     "preceded flares. Protect sleep and avoid back-to-back days when externals spike."),
]

# Toolkit that has repeatedly worked, per the coach.
RECOVERY_TOOLKIT = [
    "Don't fully rest an injury — light primary movement + correctives",
    "Core activation: 3-way plank, dead bug, dead hang, pelvic tilt",
    "Hip-opening mobility on rest days (pigeon, hip CARs, 90-90, hip aeroplane)",
    "Wider deadlift grip + straps on back-off sets",
    "Lat pulldown instead of weighted pull-ups (nerve relief)",
    "RPE-capped reload weeks after illness/layoff",
]

# =============================================================================
# COACHING CUES (Ojash) — the cues he repeats most, per lift
# =============================================================================
COACHING_CUES = {
    'Squat': [
        "Patience out of the hole — don't rush; just stand up",
        "Stay on mid-foot (not the toes); sit back",
        "Fight your knees — if the knees shift, the load shifts",
        "Expand the ribs to brace; don't let them collapse",
        "Lean forward naturally on the descent; neck neutral",
    ],
    'Bench Press': [
        "Dead-stop the bar on the chest — don't sink, don't bounce",
        "Straight bar path down; load both elbows equally",
        "Leg drive: push the floor forward, dig upper back into the bench",
        "Keep elbows OUT (moving them triggers your shoulder/elbow pain)",
        "The setup is tiresome — but that's the key; then it moves smoothly",
    ],
    'Deadlift': [
        "⭐ Pull the slack, wedge into position, THEN pull — be patient",
        "Create tension off the floor — smooth over fast",
        "Don't explosively lock the hips — just stand tall, don't hyperextend",
        "Same mixed grip (no alternating), slightly wider, knuckles down",
        "Bar path straight down under the armpit; don't let it spin",
    ],
}

TOP_CUES = [
    "Deadlift: pull the slack, wedge, *then* pull — be patient.",
    "Squat: stay on mid-foot; patience out of the hole; fight your knees.",
    "Bench: dead-stop on the chest, straight bar path, load both elbows equally.",
    "All lifts: hold the prescribed RPE — \"everything is RPE.\"",
    "Recovery: don't fully rest an injury; respect the post-peak vulnerable window.",
    "Mindset: be patient; strong is strong; the first rep is what counts.",
]

GENERAL_CUES = [
    "\"Everything is RPE\" — hold the prescribed RPE regardless of the load on the bar",
    "Secondary days = nail technique and rehearse the primary lift",
    "Diagnose from warm-ups; film multiple angles; change ONE thing at a time",
    "Meet-day: 15 kg jumps, pick attempts off the last warm-up, the first rep is what counts",
    "\"Peak early and balance the fatigue to build confidence\" (his best 2025 prep)",
]

# =============================================================================
# MINDSET / MOTIVATION
# =============================================================================
MINDSET_INSIGHTS = [
    ("🩹 Confidence tracks pain, not just numbers",
     "Both of the deepest motivation lows (Jan 2025, Jun 2026) were injury + life-stress "
     "compounds — and both turning points were a *painless session*, not a PR. \"Painless\" "
     "is the strongest positive signal; worth tracking as a KPI."),
    ("🔁 Adherence is exceptional",
     "Nearly every session logged with video + RPE for 4.5 years. Gaps are almost always "
     "external — travel, illness, the 2025 job, the 2026 Masters semester — not lost motivation."),
    ("🏆 Resilience: he PRs *through* adversity",
     "Fever at NYFC (still 8/9), gastritis then a 615 kg training total, a back injury then "
     "registering for Nationals. The coach's steady \"be patient / strong is strong\" framing "
     "is a consistent stabiliser in the dips."),
]

# Motivation vs stress drivers.
MOTIVATION_DRIVERS = [
    "Competition & rivalry (podium chases at NYFC / Ox Classic)",
    "Explicit goals — the 600 → 650 total, a 240 squat",
    "Coach reassurance in dips (\"tension na leu, will get it on meet day\")",
    "Post-injury painless sessions",
]
STRESS_DRIVERS = [
    "Long work hours (2025 job) and study load (2026 Masters)",
    "Travel-induced detraining guilt",
    "Illness in peak weeks",
    "Admin frustration (missed meet registration)",
]

# Best ACTUAL same-day totals (the headline 630 is a theoretical sum of best-ever lifts).
BEST_ACTUAL_TOTALS = {
    'training': {'total': 615, 'date': datetime(2025, 10, 7)},
    'meet': {'total': 605, 'date': datetime(2025, 4, 27)},
}
