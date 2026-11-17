FROM python:3.11.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.1.3

# Dependency layer (cached unless dependency files change)
COPY pyproject.toml poetry.lock README.md ./
RUN poetry install --only main --no-root --no-ansi \
    && rm -rf /root/.cache/pypoetry /root/.cache/pip

# Application files only; .env, .git and logs/ are never copied
COPY app.py ./
COPY data_cleaning_agent/ ./data_cleaning_agent/
COPY data/ ./data/
RUN find /app -type d -name "__pycache__" -prune -exec rm -rf {} +

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
