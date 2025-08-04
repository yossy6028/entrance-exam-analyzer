#!/bin/bash

# Get the directory where the app bundle is located
APP_DIR="$(cd "$(dirname "$0")/../../../" && pwd)"

# Change to the project directory
cd "$APP_DIR"

# Launch the Python application
/usr/bin/osascript -e 'tell app "Terminal" to do script "cd \"'"$APP_DIR"'\" && python3 run_app.py"'