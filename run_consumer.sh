#!/bin/bash
source venv/bin/activate
cd src
PYTHONPATH=$(pwd) python consumer/consumer.py