#!/bin/bash
set -e

echo "Starting FastAPI..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

echo "Starting Streamlit..."
streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0