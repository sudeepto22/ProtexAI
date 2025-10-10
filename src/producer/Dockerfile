# Producer Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY producer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common ./common
COPY sensor ./sensor
COPY producer/producer.py .

RUN mkdir -p /logs

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV LOG_DIR=/logs

CMD ["python", "producer.py"]

