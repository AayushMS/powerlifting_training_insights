# Powerlifting Training Insights

A comprehensive training analytics dashboard for powerlifters. Ingest your training data from Excel, store it in PostgreSQL, and visualize your progress with interactive charts.

## Features

- **Training Progression Tracking**: Visualize squat, bench press, and deadlift progression over time
- **Volume Analysis**: Track weekly tonnage and training volume by lift category
- **Intensity Distribution**: Analyze RPE patterns across your training
- **Block-by-Block Comparison**: Compare performance across training blocks
- **Accessory Work Analytics**: Track frequency and volume of accessory exercises
- **Training Frequency**: Monitor sessions per week and training consistency
- **Data Quality Validation**: Automatic detection of data entry errors and typos

## Tech Stack

- **Database**: PostgreSQL 16
- **Backend**: Python 3.12
- **Dashboard**: Streamlit + Plotly
- **Containerization**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.10+ (for local development)
- Your training data in Excel format

### 1. Clone the Repository

```bash
git clone https://github.com/AayushMS/powerlifting_training_insights.git
cd powerlifting_training_insights
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your database credentials if needed
```

### 3. Start with Docker

```bash
# Start PostgreSQL and Dashboard
docker compose up -d

# Run data ingestion (place your training_log.xlsx in the project root)
docker exec powerlifting_dashboard python3 src/ingest.py
```

### 4. Access the Dashboard

Open your browser to: **http://localhost:8501**

## Local Development

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL (Docker)
docker compose up -d postgres

# Run ingestion
python src/ingest.py

# Start dashboard
streamlit run src/dashboard.py
```

## Deploying to Streamlit Cloud

### 1. Set Up a Cloud PostgreSQL Database

You'll need a cloud-hosted PostgreSQL database. Recommended options:
- [Supabase](https://supabase.com/) (free tier available)
- [Neon](https://neon.tech/) (free tier available)
- [Railway](https://railway.app/)

### 2. Initialize the Database

Run the `init.sql` script on your cloud database to create the schema:
```sql
-- Copy contents of init.sql and run in your database
```

### 3. Ingest Your Data

Update your `.env` with cloud database credentials and run:
```bash
python src/ingest.py
```

### 4. Deploy to Streamlit Cloud

1. Push your code to GitHub (without `.env` and `training_log.xlsx`)
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Connect your GitHub repository
4. Set the main file path to: `src/dashboard.py`
5. Add your database secrets in the app settings:

```toml
[database]
DB_HOST = "your-postgres-host.com"
DB_PORT = "5432"
DB_NAME = "training_insights"
DB_USER = "your_username"
DB_PASSWORD = "your_password"
```

## Project Structure

```
powerlifting_training_insights/
├── src/
│   ├── __init__.py
│   ├── dashboard.py      # Streamlit dashboard
│   └── ingest.py         # Data ingestion script
├── .streamlit/
│   ├── config.toml       # Streamlit configuration
│   └── secrets.toml.example
├── docker-compose.yml    # Docker services configuration
├── Dockerfile            # Dashboard container
├── init.sql              # Database schema
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore
└── README.md
```

## Excel Data Format

The ingestion script expects an Excel file with:
- Multiple sheets (one per training week)
- Training days as headers (Sunday, Monday, etc.)
- Exercise data with columns: Movement, Prescribed Weight, Actual Weight, RPE, Sets, Reps, Tempo, Rest, Notes

### Supported Exercise Naming

The script automatically normalizes exercise names:
- "Squat", "Back Squat", "Comp Squat" → **Squat**
- "Bench Press", "Bench", "Comp Bench Press" → **Bench Press**
- "Sumo Deadlift", "Deadlift" → **Sumo Deadlift**

## Data Validation

The ingestion script includes automatic validation:
- **Weight Deviation Check**: Flags weights >50% different from prescribed
- **Weight Range Parsing**: Correctly handles "75-80" format
- **Bounds Checking**: Catches obvious typos (e.g., 1775kg instead of 177.5kg)
- **Date Parsing**: Handles Excel date conversion issues for RPE values

## Current PRs (Configurable)

Default maxes in the dashboard:
- Squat: 220 kg
- Bench Press: 135 kg
- Deadlift: 260 kg
- **Total: 615 kg**

Update these in `src/dashboard.py` under `CURRENT_PRS`.

## Screenshots

*Add screenshots of your dashboard here*

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use this for your own training analytics!

## Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/)
- [Plotly](https://plotly.com/)
- [PostgreSQL](https://www.postgresql.org/)
