FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
# Cloud Run will send traffic to $PORT; tell Flask to listen there
CMD exec python -m flask --app main:app run --host=0.0.0.0 --port=$PORT
