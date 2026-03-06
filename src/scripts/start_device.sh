#!/usr/bin/env bash

# Start TFG - Database + Backend + iOS App (physical device)
# This script starts PostgreSQL, FastAPI backend and React Native app on a connected iPhone

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
    echo "❌ Error: config.json not found"
    exit 1
fi

# Extract configuration values using Python
BACKEND_PORT=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['backend']['api']['port'])")
BACKEND_HOST=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['backend']['api']['host'])")
POSTGRES_PORT=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['database']['postgresql']['port'])")
IOS_DEVICE=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['frontend']['ios']['device'])")

# Activate Python virtual environment
source backend/.venv/bin/activate

# Ensure npm dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    cd frontend && npm install && cd ..
fi

# Start PostgreSQL
brew services start postgresql@15
sleep 2

# Start backend if not already running
# Use 0.0.0.0 so the physical device can reach it over the network
if lsof -ti :$BACKEND_PORT > /dev/null 2>&1; then
    : # Backend already running
else
    uvicorn backend.service.main:app --reload --host 0.0.0.0 --port $BACKEND_PORT > /dev/null 2>&1 &
    sleep 2
fi

# Detect current local IP and update frontend config.ts
MAC_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)
if [ -z "$MAC_IP" ]; then
    echo "❌ Could not detect local IP. Make sure the Mac is connected to a network."
    exit 1
fi
echo "🌐 Detected local IP: $MAC_IP"
sed -i '' \
    "s|host: '[^']*'|host: '$MAC_IP'|g" \
    frontend/config.ts
sed -i '' \
    "s|url: 'http://[^']*:$BACKEND_PORT'|url: 'http://$MAC_IP:$BACKEND_PORT'|g" \
    frontend/config.ts
sed -i '' \
    "s|docs_url: 'http://[^']*:$BACKEND_PORT/docs'|docs_url: 'http://$MAC_IP:$BACKEND_PORT/docs'|g" \
    frontend/config.ts
sed -i '' \
    "s|url: 'ws://[^']*:$BACKEND_PORT'|url: 'ws://$MAC_IP:$BACKEND_PORT'|g" \
    frontend/config.ts

# Check that a physical device is connected
DEVICE_UDID=$(xcrun xctrace list devices 2>/dev/null | grep -v "Simulator" | grep -v "==" | grep "$IOS_DEVICE" | grep -o "([0-9A-Fa-f-]*)" | tail -1 | tr -d "()")

if [ -z "$DEVICE_UDID" ]; then
    echo "❌ Device '$IOS_DEVICE' not found. Make sure the iPhone is connected via USB and trusted."
    exit 1
fi

echo "📱 Launching app on device: $IOS_DEVICE ($DEVICE_UDID)"

cd frontend
npx react-native run-ios --udid "$DEVICE_UDID"
