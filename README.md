# Powerlifting Training Insights Dashboard

A beautiful, data-driven dashboard for analyzing powerlifting training progress. Built with Streamlit and Plotly for interactive visualizations.

![Dashboard Preview](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

## Features

- **81 Weeks of Training Data** - Comprehensive analysis of long-term progression
- **Main Lift Tracking** - Squat, Bench Press, Deadlift progression with trend lines
- **Volume Analysis** - Weekly tonnage and sets distribution
- **RPE/Intensity Analysis** - Training intensity distribution with optimal zone highlighting
- **Block Comparison** - Compare performance across training blocks
- **Lift Ratios** - Analyze balance between lifts with ideal ratio guidance
- **Smart Insights** - Science-based recommendations for improvement
- **Accessory Analysis** - Track supporting exercise frequency

## Current Stats

| Lift | PR | Goal |
|------|----|----|
| Squat | 220 kg | 240 kg |
| Bench Press | 135 kg | 160 kg |
| Deadlift | 262.5 kg | 290 kg |
| **Total** | **617.5 kg** | **690 kg** |

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
│   ├── app.py              # Main Streamlit dashboard
│   └── data_processor.py   # Excel data processing & analytics
├── Aayush man .xlsx        # Training data (81 weeks)
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Streamlit theme configuration
├── ANALYSIS_AND_PLAN.md    # Detailed analysis & recommendations
└── README.md               # This file
```

## Data Format

The dashboard reads from an Excel file with the following structure:
- Each sheet represents one training week
- Columns: Movement, Prescribed Weight, Actual Weight, RPE, Sets, Reps, Tempo, Rest, Notes

## Key Insights

Based on 81 weeks of training data:

1. **Bench Press Focus Needed** - Current bench (135kg) is 61% of squat (220kg), below the ideal 75-80% ratio
2. **Conservative Training** - Average RPE of 6.3 leaves room for more intensity on main lifts
3. **Strong Deadlift** - Deadlift/Squat ratio of 119% is in the optimal range
4. **Consistent Training** - Averaging 4 sessions per week over 81 weeks

## Technology Stack

- **Frontend**: Streamlit
- **Visualization**: Plotly
- **Data Processing**: Pandas, NumPy
- **Excel Parsing**: OpenPyXL

## License

MIT License - Feel free to use and modify for your own training analysis!

---

*Built with ❤️ for powerlifting progress*
