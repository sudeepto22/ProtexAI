FROM python:3.12-slim

WORKDIR /app

# Copy common modules
COPY common/ /app/common/

# Copy sensor module (needed for common imports)
COPY sensor/ /app/sensor/

# Copy API requirements and install
COPY api/requirements.txt /app/api/
RUN pip install --no-cache-dir -r /app/api/requirements.txt

# Copy API source
COPY api/ /app/api/

# Set PYTHONPATH so Python can find the common module
ENV PYTHONPATH=/app

WORKDIR /app/api

# Expose port
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

