FROM python:3.12-slim

ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION} \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .

# Run as a non-root user.
RUN useradd --system --uid 10001 appuser
USER appuser

EXPOSE 8000
# Exec form so uvicorn receives SIGTERM and shuts down gracefully.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
