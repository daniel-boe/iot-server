#!/bin/bash
echo 'Starting home server...'
cd $HOME/iot-server/fastserver
uv sync
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0

