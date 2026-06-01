#!/usr/bin/env bash
uvicorn api.main_api:app --host 0.0.0.0 --port $PORT