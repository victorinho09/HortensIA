# TFG - React Native + FastAPI

Mobile application developed with React Native and REST API backend with FastAPI.

## Prerequisites

- [Conda](https://docs.conda.io/en/latest/) installed
- Xcode (for iOS)

## Installation

### 1. Create and activate conda environment

```bash
# Create environment (first time only)
conda create -n TFG_HP

# Activate environment
conda activate TFG_HP

conda install python nodejs
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Node.js dependencies

```bash
npm install
```

## Running the application

### Backend (FastAPI)

```bash
# Make sure the environment is activated
conda activate TFG_HP

# Run development server
uvicorn src.backend.service.main:app --reload --host 0.0.0.0 --port 8000
```

The server will be available at:

- API: http://localhost:8000
- Interactive documentation: http://localhost:8000/docs

### Frontend (React Native)

In another terminal:

```bash
# Run on iOS
npm run ios
```

## Project structure

```
TFG/
├── src/
│   ├── backend/
│   │   ├── service/          # FastAPI REST API
│   │   └── databases/        # Database configuration
│   └── frontend/
│       ├── components/       # React Native components
│       └── index.js         # Frontend entry point
├── ios/                     # iOS native code
├── requirements.txt         # Python dependencies
└── package.json            # Node.js dependencies
```
