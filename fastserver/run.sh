#!/bin/bash
echo 'Starting home server...'
cd $HOME/iot-server
source venv/bin/activate
uvicorn fastserver.main:app --host 0.0.0.0

