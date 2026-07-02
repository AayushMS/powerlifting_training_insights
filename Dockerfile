FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (curl for the healthcheck)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and training data
COPY src/ ./src/
COPY ["Aayush man .xlsx", "./Aayush man .xlsx"]

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the Streamlit dashboard (reads directly from the Excel file, no database)
CMD ["python", "-m", "streamlit", "run", "src/app.py", "--server.headless", "true", "--server.address", "0.0.0.0", "--server.port", "8501"]
