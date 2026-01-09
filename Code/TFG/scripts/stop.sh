#!/bin/bash

# Stop TFG - Backend + Database
# This script stops the FastAPI backend and PostgreSQL

cd "$(dirname "$0")/.."

echo "🛑 Stopping Backend (FastAPI)..."
if lsof -ti :8888 > /dev/null 2>&1; then
    lsof -ti :8888 | xargs kill -9 2>/dev/null
    echo "✅ Backend stopped"
else
    echo "ℹ️  Backend was not running"
fi

echo "🗄️  Stopping PostgreSQL..."
brew services stop postgresql@15
echo "✅ PostgreSQL stopped"

echo "📱 Closing iOS Simulator..."
xcrun simctl shutdown all 2>/dev/null
killall Simulator 2>/dev/null
echo "✅ iOS Simulator closed"

echo "📦 Stopping Metro Bundler..."
pkill -9 -f "react-native start" 2>/dev/null
pkill -9 -f "metro" 2>/dev/null
pkill -9 -f "launchPackager" 2>/dev/null
lsof -ti :8081 | xargs kill -9 2>/dev/null
echo "✅ Metro Bundler stopped"

echo "🖥️  Closing Metro Terminal window..."
osascript -e 'tell application "Terminal" to close (every window whose name contains "launchPackager" or name contains "metro" or name contains "react-native")' 2>/dev/null
osascript -e 'tell application "Terminal" to close (every window whose contents contains "BUNDLE" or contents contains "Metro")' 2>/dev/null
echo "✅ Terminal windows closed"

echo "🏁 All services stopped"
