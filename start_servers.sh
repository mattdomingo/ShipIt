#!/bin/bash

# ShipIt Server Startup Script
# Starts Redis, FastAPI backend, and Celery worker in the correct order

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
REDIS_PORT=6379
API_PORT=8000
FLOWER_PORT=5555

# PID file locations
PIDS_DIR="$PROJECT_ROOT/.pids"
REDIS_PID_FILE="$PIDS_DIR/redis.pid"
API_PID_FILE="$PIDS_DIR/api.pid"
CELERY_PID_FILE="$PIDS_DIR/celery.pid"
FLOWER_PID_FILE="$PIDS_DIR/flower.pid"

# Create PID directory
mkdir -p "$PIDS_DIR"

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Shutting down servers...${NC}"
    
    # Kill processes if PID files exist
    for pid_file in "$REDIS_PID_FILE" "$API_PID_FILE" "$CELERY_PID_FILE" "$FLOWER_PID_FILE"; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                echo "Stopping process $pid..."
                kill "$pid" 2>/dev/null || true
            fi
            rm -f "$pid_file"
        fi
    done
    
    echo -e "${GREEN}Cleanup complete${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

print_header() {
    echo -e "${BLUE}"
    echo "=========================================="
    echo "🚀 ShipIt Server Startup Script"
    echo "=========================================="
    echo -e "${NC}"
}

check_dependencies() {
    echo -e "${YELLOW}Checking dependencies...${NC}"
    
    # Check if virtual environment exists
    if [ ! -d "$VENV_PATH" ]; then
        echo -e "${RED}Virtual environment not found at $VENV_PATH${NC}"
        echo "Please create it first with: python -m venv .venv"
        exit 1
    fi
    
    # Check if Redis is available
    if ! command -v redis-server &> /dev/null; then
        echo -e "${RED}Redis not found. Please install it:${NC}"
        echo "  macOS: brew install redis"
        echo "  Ubuntu: sudo apt-get install redis-server"
        exit 1
    fi
    
    echo -e "${GREEN}Dependencies OK${NC}"
}

start_redis() {
    echo -e "${YELLOW}Starting Redis server...${NC}"
    
    # Check if Redis is already running
    if lsof -Pi :$REDIS_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}Redis already running on port $REDIS_PORT${NC}"
        return 0
    fi
    
    # Start Redis in background
    redis-server --daemonize yes --pidfile "$REDIS_PID_FILE" --port $REDIS_PORT
    
    # Wait for Redis to start
    for i in {1..10}; do
        if redis-cli -p $REDIS_PORT ping >/dev/null 2>&1; then
            echo -e "${GREEN}Redis started successfully${NC}"
            return 0
        fi
        sleep 1
    done
    
    echo -e "${RED}Failed to start Redis${NC}"
    exit 1
}

start_api() {
    echo -e "${YELLOW}Starting FastAPI server...${NC}"
    
    # Check if API is already running
    if lsof -Pi :$API_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}API already running on port $API_PORT${NC}"
        return 0
    fi
    
    # Activate virtual environment and start API
    cd "$PROJECT_ROOT"
    source "$VENV_PATH/bin/activate"
    
    # Install/update dependencies
    pip install -q -r config/requirements.txt
    
    # Start API in background
    nohup python backend/api/run_server.py > logs/api.log 2>&1 &
    echo $! > "$API_PID_FILE"
    
    # Wait for API to start
    for i in {1..30}; do
        if curl -s "http://localhost:$API_PORT/health" >/dev/null 2>&1; then
            echo -e "${GREEN}FastAPI started successfully${NC}"
            echo -e "${BLUE}API Documentation: http://localhost:$API_PORT/docs${NC}"
            return 0
        fi
        sleep 1
    done
    
    echo -e "${RED}Failed to start FastAPI${NC}"
    exit 1
}

start_celery() {
    echo -e "${YELLOW}Starting Celery worker...${NC}"
    
    cd "$PROJECT_ROOT"
    source "$VENV_PATH/bin/activate"
    
    # Start Celery worker in background
    nohup celery -A backend.api.jobs.celery_app worker --loglevel=info > logs/celery.log 2>&1 &
    echo $! > "$CELERY_PID_FILE"
    
    # Give Celery a moment to start
    sleep 3
    
    # Check if Celery is running
    if kill -0 $(cat "$CELERY_PID_FILE") 2>/dev/null; then
        echo -e "${GREEN}Celery worker started successfully${NC}"
    else
        echo -e "${RED}Failed to start Celery worker${NC}"
        exit 1
    fi
}

start_flower() {
    echo -e "${YELLOW}Starting Flower (Celery monitoring)...${NC}"
    
    cd "$PROJECT_ROOT"
    source "$VENV_PATH/bin/activate"
    
    # Check if flower is installed
    if ! pip show flower >/dev/null 2>&1; then
        echo "Installing Flower..."
        pip install flower
    fi
    
    # Start Flower in background
    nohup flower -A backend.api.jobs.celery_app --port=$FLOWER_PORT > logs/flower.log 2>&1 &
    echo $! > "$FLOWER_PID_FILE"
    
    # Wait for Flower to start
    for i in {1..15}; do
        if curl -s "http://localhost:$FLOWER_PORT" >/dev/null 2>&1; then
            echo -e "${GREEN}Flower started successfully${NC}"
            echo -e "${BLUE}Flower Dashboard: http://localhost:$FLOWER_PORT${NC}"
            return 0
        fi
        sleep 1
    done
    
    echo -e "${YELLOW}Flower may still be starting (check logs/flower.log)${NC}"
}

show_status() {
    echo -e "\n${BLUE}=========================================="
    echo "🎉 All servers started successfully!"
    echo "==========================================${NC}"
    echo -e "${GREEN}✓ Redis:${NC} localhost:$REDIS_PORT"
    echo -e "${GREEN}✓ FastAPI:${NC} http://localhost:$API_PORT"
    echo -e "${GREEN}✓ Swagger UI:${NC} http://localhost:$API_PORT/docs"
    echo -e "${GREEN}✓ Celery Worker:${NC} Running"
    echo -e "${GREEN}✓ Flower Dashboard:${NC} http://localhost:$FLOWER_PORT"
    echo ""
    echo -e "${YELLOW}Logs are available in:${NC}"
    echo "  • API: logs/api.log"
    echo "  • Celery: logs/celery.log"
    echo "  • Flower: logs/flower.log"
    echo ""
    echo -e "${YELLOW}To stop all servers: Ctrl+C${NC}"
}

# Main execution
main() {
    print_header
    
    # Create logs directory
    mkdir -p logs
    
    check_dependencies
    start_redis
    start_api
    start_celery
    start_flower
    
    show_status
    
    # Keep script running and monitor processes
    echo -e "\n${YELLOW}Monitoring servers... Press Ctrl+C to stop all${NC}"
    while true; do
        sleep 5
        
        # Check if any process died
        for pid_file in "$API_PID_FILE" "$CELERY_PID_FILE"; do
            if [ -f "$pid_file" ]; then
                pid=$(cat "$pid_file")
                if ! kill -0 "$pid" 2>/dev/null; then
                    echo -e "${RED}Process $pid died unexpectedly${NC}"
                    cleanup
                fi
            fi
        done
    done
}

# Run main function
main "$@" 