# Project Overview: Powerlifting Training Insights Dashboard

## Athlete Profile
- **Name:** Aayush Man Singh
- **Weight Class:** U93kg (Under 93kg)
- **Bodyweight:** 90-91kg
- **Federation:** IPF-style competitions

## Competition History

### Ox Classic 2022 (first meet)
- **Date:** February 13, 2022
- **Results:** Squat 180kg | Bench 110kg | Deadlift 222.5kg | **Total 512.5kg**

### Deadlift Championship Nepal (deadlift-only)
- **Date:** March 9, 2024
- **Results:** Deadlift 250kg — first 250kg pull

### NYFC Classic 2024 Invitational
- **Date:** December 8, 2024
- **Results:** Squat 220kg | Bench 122.5kg | Deadlift 250kg | **Total 592.5kg**
- **Attempts:** 8/9 (Missed 130kg bench on 3rd attempt); competed with a 103.6°F fever
- **Placement:** 4th

### OX Classic Summerslam
- **Date:** April 27, 2025
- **Results:** Squat 220kg | Bench 130kg | Deadlift 255kg | **Total 605.0kg**
- **Attempts:** 9/9 (Perfect meet!); played safe for the podium
- **Placement:** 3rd
- **Note:** Made the bench that was missed at NYFC

### Iconic Clash Deadlift Championship (deadlift-only)
- **Date:** February 7, 2026
- **Results:** Deadlift 275kg PR (attempts 245/262.5/275) — "more in the tank"

### Upcoming
- **WRPF Himalayan Pro Nationals (U90)** — ~Sep 2026 (registered Jun 26, 2026)

## Current Training PRs (from data)
- **Squat:** 220kg
- **Bench Press:** 135kg
- **Deadlift:** 275kg
- **Total:** 630kg

## Data Source
- **File:** `Aayush man .xlsx` (exported from two training-log Google Sheets)
- **Duration:** 117 training weeks — the 2022 Ox Classic prep block (12 weeks, Nov 2021–Feb
  2022, from Ojash's "Aayush meet prep" sheet) + the continuous ~March 2024–mid 2026 stint.
  The ~2-year layoff between the two is dated independently and excluded from consistency.
- **Sessions:** ~389 total sessions
- **Frequency:** ~3.7 sessions per week
- **Total volume:** ~186 tons (Squat 71 / Bench 38 / Deadlift 76)

## Key Insights

### Lift Ratios
- **Bench/Squat:** 61.4% (Target: 65-80%) - Bench is the biggest opportunity
- **Deadlift/Squat:** 125.0% (Target: 110-125%) - At the top of the balanced range

### Progression Rates
Computed from first-10-week vs last-10-week average working weights (the dashboard's
conservative basis; recent light "Reset"/deload weeks pull the recent average down):
- **Squat:** ~0.4 kg/month
- **Bench Press:** ~0.6 kg/month
- **Deadlift:** ~0.3 kg/month

### Training Structure
- **Primary Days (Day 1-2):** Competition lifts, heavier weights, 961 tons total
- **Secondary Days (Day 3-4):** Variations, accessories, 1,224 tons total

## Known Data Issues (Fixed)
1. **177.5kg Bench Anomaly:** Was a typo for 117.5kg - corrected in code
2. **Latest Week:** Marked as "in progress" (not skipped)
3. **Skipped Exercises:** Tracked separately for main lifts vs accessories
4. **RPE-as-date (2026):** Google Sheets converts RPE like "8/9" into dates. The 2026
   dates were producing garbage RPE (~1017); `parse_rpe` now handles datetime cells and
   clamps every value to 1-10. See KNOWN_ISSUES_AND_FIXES.md.
5. **Empty scratch tabs:** `Sheet7`-`Sheet10` in the source Google Sheet are dropped
   during export so they don't count as training weeks.

## Missing Weeks in Source Sheet (not recoverable from files)
A few weeks were never duplicated in the Google Sheet (holes between existing weeks):
**build up 2/5, build week 4/5, build 4/5**. These predate the earliest repo snapshot
(Dec 2025) and cannot be recovered from files or the Drive API — only via Google Sheets'
built-in Version History (if still within its retention window). Several block tails
(e.g. B6 3-5/5, Prep 5-8/8) appear cut short and may be intentional.
