#!/bin/bash
echo "Starting ProtexAI API Service..."
source venv/bin/activate
cd src 
PYTHONPATH=$(pwd) python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

