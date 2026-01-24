#!/bin/bash

# Stop TFG - Backend + Database
# This script stops the FastAPI backend and PostgreSQL

cd "$(dirname "$0")/.."

if lsof -ti :8888 > /dev/null 2>&1; then
    lsof -ti :8888 | xargs kill -9 2>/dev/null
fi

brew services stop postgresql@15

xcrun simctl shutdown all 2>/dev/null
killall Simulator 2>/dev/null

pkill -9 -f "react-native start" 2>/dev/null
pkill -9 -f "metro" 2>/dev/null
pkill -9 -f "launchPackager" 2>/dev/null
lsof -ti :8081 | xargs kill -9 2>/dev/null

osascript -e 'tell application "Terminal" to close (every window whose name contains "launchPackager" or name contains "metro" or name contains "react-native")' 2>/dev/null
osascript -e 'tell application "Terminal" to close (every window whose contents contains "BUNDLE" or contents contains "Metro")' 2>/dev/null
