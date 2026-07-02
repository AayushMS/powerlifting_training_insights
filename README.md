# Powerlifting Training Insights Dashboard

A beautiful, data-driven dashboard for analyzing powerlifting training progress. Built with Streamlit and Plotly for interactive visualizations.

![Dashboard Preview](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

## Deployment

- **Dashboard:** https://aayushms-powerlifting.streamlit.app/
- **Data source:** `Aayush man .xlsx` (exported from the training-log Google Sheet — no database)
- **Repo:** https://github.com/AayushMS/powerlifting_training_insights

## Features

- **117 Weeks of Training Data** - The 2022 Ox Classic prep block plus the continuous Mar 2024–mid 2026 stint
- **Main Lift Tracking** - Squat, Bench Press, Deadlift progression with trend lines
- **Volume Analysis** - Weekly tonnage and sets distribution
- **RPE/Intensity Analysis** - Training intensity distribution with optimal zone highlighting
- **Block Comparison** - Compare performance across training blocks
- **Lift Ratios** - Analyze balance between lifts with ideal ratio guidance
- **Smart Insights** - Science-based recommendations for improvement
- **Accessory Analysis** - Track supporting exercise frequency

## Current Stats

| Lift | PR | 2026 Goal |
|------|----|----|
| Squat | 220 kg | 240 kg |
| Bench Press | 135 kg | 150 kg |
| Deadlift | 275 kg | 280 kg |
| **Total** | **630 kg** | **670 kg** |

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/training_insights.git
   cd training_insights
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard**
   ```bash
   streamlit run src/app.py
   ```

4. **Open in browser**
   Navigate to `http://localhost:8501`

### Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select your repository
5. Set main file path: `src/app.py`
6. Deploy!

## Project Structure

```
training_insights/
├── src/
│   ├── app.py              # Main Streamlit dashboard (deployed entrypoint)
│   ├── data_processor.py   # Excel data processing & analytics
│   └── interpretations.py  # Plain-English metric interpretations
├── Aayush man .xlsx        # Training data (105 weeks, 1 sheet per week)
├── knowledge_base/         # Living project documentation
├── docs/archive/           # Historical planning docs
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container image (runs src/app.py)
├── docker-compose.yml      # Local container orchestration
├── .streamlit/
│   └── config.toml         # Streamlit theme configuration
└── README.md               # This file
```

## Data Format

The dashboard reads from an Excel file with the following structure:
- Each sheet represents one training week
- Columns: Movement, Prescribed Weight, Actual Weight, RPE, Sets, Reps, Tempo, Rest, Notes

## Key Insights

Based on 117 weeks of training data (2022 Ox Classic prep + Mar 2024 – mid 2026):

1. **Bench Press Focus Needed** - Current bench (135kg) is 61% of squat (220kg), below the ideal 65-80% ratio
2. **Conservative Training** - Average RPE of ~6.4 leaves room for more intensity on main lifts
3. **Strong Deadlift** - Deadlift/Squat ratio of 125% (deadlift now at a 275kg PR) sits at the top of the optimal range
4. **Consistent Training** - Averaging ~3.7 sessions per week across 117 training weeks and ~389 sessions

## Competition History

| Date | Meet | Squat | Bench | Deadlift | Total |
|------|------|-------|-------|----------|-------|
| Feb 13, 2022 | Ox Classic 2022 | 180 | 110 | 222.5 | 512.5 |
| Mar 9, 2024 | Deadlift Championship Nepal | — | — | 250 | — |
| Dec 8, 2024 | NYFC Classic | 220 | 122.5 | 250 | 592.5 |
| Apr 27, 2025 | OX Classic Summerslam | 220 | 130 | 255 | 605 |
| Feb 7, 2026 | Iconic Clash Deadlift Championship | — | — | 275 | — |

## Technology Stack

- **Frontend**: Streamlit
- **Visualization**: Plotly
- **Data Processing**: Pandas, NumPy
- **Excel Parsing**: OpenPyXL

## License

MIT License - Feel free to use and modify for your own training analysis!

---

*Built with ❤️ for powerlifting progress*
