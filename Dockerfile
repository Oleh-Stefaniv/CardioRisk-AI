FROM python:3.11-slim

WORKDIR /app

# Встановлення системних залежностей (libgomp1 для XGBoost та OpenMP)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копіювання файлу залежностей та інсталяція
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання коду застосунку та навчених моделей
COPY app.py .
COPY models/ ./models/

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
