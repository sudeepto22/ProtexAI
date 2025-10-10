# Consumer Dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY consumer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common ./common
COPY sensor ./sensor
COPY slack ./slack
COPY consumer/consumer.py .

RUN mkdir -p /logs

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV LOG_DIR=/logs

CMD ["python", "consumer.py"]

