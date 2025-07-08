# ShipIt Quick Start Guide

## 🚀 One-Command Startup

### 1. Start All Backend Services
```bash
./start_servers.sh
```

This single command will:
- ✅ Check dependencies (Python venv, Redis)
- ✅ Start Redis server
- ✅ Start FastAPI backend (with auto-reload)
- ✅ Start Celery worker for background jobs
- ✅ Start Flower dashboard for monitoring
- ✅ Show you all the URLs and log locations
- ✅ Keep everything running until you press Ctrl+C

### 2. Start Mobile App (New Terminal)
```bash
./start_mobile.sh
```

This will:
- ✅ Auto-detect your local IP address
- ✅ Set `DEV_API_URL` environment variable for the app
- ✅ Install dependencies if needed
- ✅ Start Expo development server
- ✅ Show QR code for your phone

## 📱 Using the Mobile App

1. **Install Expo Go** on your phone (App Store/Google Play)
2. **Connect to same WiFi** as your computer
3. **Scan the QR code** that appears in the terminal
4. **Upload a resume** and test the parsing!

## 🔧 What's Running

After both scripts start, you'll have:

| Service | URL | Purpose |
|---------|-----|---------|
| FastAPI Backend | http://localhost:8000 | Main API |
| Swagger UI | http://localhost:8000/docs | API documentation |
| Celery Worker | (background) | Resume parsing jobs |
| Flower Dashboard | http://localhost:5555 | Job monitoring |
| Redis | localhost:6379 | Message broker |
| Expo Dev Server | http://localhost:19006 | Mobile app |

## 🛑 Stopping Everything

**Backend:** Press `Ctrl+C` in the terminal running `./start_servers.sh`  
**Mobile:** Press `Ctrl+C` in the terminal running `./start_mobile.sh`

## 📋 Prerequisites

- Python 3.8+ with virtual environment at `.venv/`
- Redis installed (`brew install redis` on macOS)
- Node.js and npm installed
- Both your computer and phone on the same WiFi network

## 🔧 Troubleshooting

**"Redis not found"**
```bash
# macOS
brew install redis

# Ubuntu/Debian
sudo apt-get install redis-server
```

**"Network request failed" on phone**
- Make sure both devices are on the same WiFi
- Check that `./start_servers.sh` is running
- Ensure `DEV_API_URL` points to your computer's IP (set automatically by `start_mobile.sh`)

**"Virtual environment not found"**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r config/requirements.txt
```

## 📝 Manual Setup (if scripts don't work)

<details>
<summary>Click to expand manual steps</summary>

### Backend (3 terminals)
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: FastAPI
source .venv/bin/activate
python backend/api/run_server.py

# Terminal 3: Celery
source .venv/bin/activate
celery -A backend.api.jobs.celery_app worker --loglevel=info
```

### Mobile (1 terminal)
```bash
cd mobile
npm install
npx expo start
```

</details>

---

That's it! The startup scripts handle all the complexity for you. 🎉 