#!/bin/bash
echo 'Starting home server...'
cd $HOME/home-server
venv/bin/activate
waitress-serve --host 0.0.0.0 --call server:create_app