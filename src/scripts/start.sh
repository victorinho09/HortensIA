#!/usr/bin/env bash

# Start TFG - Database + Backend + iOS App
# This script starts PostgreSQL, FastAPI backend and React Native app

# Disable update prompts (oh-my-zsh and npm)
export DISABLE_AUTO_UPDATE=true
export DISABLE_UPDATE_PROMPT=true
export NO_UPDATE_NOTIFIER=true
export DISABLE_OPENCOLLECTIVE=true
export ADBLOCK=true

cd "$(dirname "$0")/.."

# Load configuration from config.json
echo "📋 Loading configuration..."
CONFIG_FILE="config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    #echo "❌ Error: config.json not found"
    exit 1
fi

# Extract configuration values using Python
BACKEND_PORT=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['backend']['api']['port'])")
BACKEND_HOST=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['backend']['api']['host'])")
POSTGRES_PORT=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['database']['postgresql']['port'])")
IOS_SIMULATOR=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['frontend']['ios']['simulator'])")

#echo "✅ Configuration loaded"
#echo "   Backend: $BACKEND_HOST:$BACKEND_PORT"
#echo "   PostgreSQL: localhost:$POSTGRES_PORT"
#echo "   iOS Simulator: $IOS_SIMULATOR"

# Activate Python virtual environment
#echo "🐍 Activating virtual environment..."
source backend/.tfg/bin/activate
#echo "✅ Virtual environment activated"

# Ensure dependencies are installed
#echo "📦 Checking dependencies..."
if [ ! -d "frontend/node_modules" ]; then
    #echo "Installing npm dependencies..."
    cd frontend && npm install && cd ..
fi

#echo "🗄️  Starting PostgreSQL..."
brew services start postgresql@15
sleep 2
#echo "✅ PostgreSQL running"

if lsof -ti :$BACKEND_PORT > /dev/null 2>&1; then
    : # Backend already running
else
    uvicorn backend.service.main:app --reload --host $BACKEND_HOST --port $BACKEND_PORT > /dev/null 2>&1 &
    BACKEND_PID=$!
    sleep 2
fi

#echo "🚀 Starting TFG iOS App..."

# Change to frontend directory for React Native commands
cd frontend

# Check if simulator is already running with better detection
BOOTED_DEVICES=$(xcrun simctl list devices | grep "Booted")
if [ ! -z "$BOOTED_DEVICES" ]; then
    #echo "✅ Simulator already running"
    DEVICE_ID=$(echo "$BOOTED_DEVICES" | grep -o "[0-9A-F]\{8\}-[0-9A-F]\{4\}-[0-9A-F]\{4\}-[0-9A-F]\{4\}-[0-9A-F]\{12\}" | head -1)
    #echo "📱 Building and installing app on device: $DEVICE_ID"
    npx react-native run-ios --udid "$DEVICE_ID"
else
    #echo "📱 Launching simulator and app..."
    npx react-native run-ios --simulator="$IOS_SIMULATOR"
fi
