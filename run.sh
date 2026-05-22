#!/bin/bash
cd "$(dirname "$0")"
pip install -r backend/requirements.txt
exec uvicorn backend.app:app --reload --host 0.0.0.0 --port 8080
