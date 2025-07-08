#!/bin/bash

# ShipIt Mobile App Startup Script
# Configures and starts the Expo development server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MOBILE_DIR="$PROJECT_ROOT/mobile"
CONFIG_FILE="$MOBILE_DIR/config.ts"  # Deprecated: config is now via env var

print_header() {
    echo -e "${BLUE}"
    echo "=========================================="
    echo "📱 ShipIt Mobile App Startup Script"
    echo "=========================================="
    echo -e "${NC}"
}

get_local_ip() {
    # Try to get local IP address
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        LOCAL_IP=$(ip route get 8.8.8.8 | awk '{print $7; exit}')
    else
        # Windows/Other
        LOCAL_IP=$(ipconfig | grep "IPv4" | awk '{print $NF}' | head -1)
    fi
    
    if [ -z "$LOCAL_IP" ]; then
        echo -e "${RED}Could not detect local IP address${NC}"
        echo "Please manually update mobile/config.ts with your IP address"
        exit 1
    fi
    
    echo "$LOCAL_IP"
}

set_dev_api_url() {
    echo -e "${YELLOW}Configuring development API URL...${NC}"

    LOCAL_IP=$(get_local_ip)
    DEV_URL="http://$LOCAL_IP:8000/v1"
    export DEV_API_URL="$DEV_URL"

    echo -e "${GREEN}DEV_API_URL set to: $DEV_URL${NC}"
}

check_backend() {
    echo -e "${YELLOW}Checking if backend is running...${NC}"
    
    LOCAL_IP=$(get_local_ip)
    
    if curl -s "http://$LOCAL_IP:8000/health" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is running and accessible${NC}"
    else
        echo -e "${YELLOW}⚠ Backend not detected. Make sure to run ./start_servers.sh first${NC}"
        echo -e "${BLUE}You can start the backend in another terminal with:${NC}"
        echo -e "${BLUE}  ./start_servers.sh${NC}"
        echo ""
        read -p "Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

setup_mobile() {
    echo -e "${YELLOW}Setting up mobile app...${NC}"
    
    cd "$MOBILE_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing dependencies...${NC}"
        npm install
    else
        echo -e "${GREEN}Dependencies already installed${NC}"
    fi
    
    # Check if Expo CLI is available
    if ! command -v expo &> /dev/null; then
        if ! command -v npx &> /dev/null; then
            echo -e "${RED}Neither expo nor npx found. Please install Node.js${NC}"
            exit 1
        fi
        echo -e "${YELLOW}Using npx expo (Expo CLI not globally installed)${NC}"
    fi
}

start_expo() {
    echo -e "${YELLOW}Starting Expo development server...${NC}"
    
    cd "$MOBILE_DIR"
    
    echo -e "${GREEN}Starting mobile app...${NC}"
    echo -e "${BLUE}Scan the QR code with Expo Go app or press 'i' for iOS simulator${NC}"
    echo ""
    
    # Start Expo with appropriate command
    if command -v expo &> /dev/null; then
        expo start
    else
        npx expo start
    fi
}

show_instructions() {
    LOCAL_IP=$(get_local_ip)
    
    echo -e "\n${BLUE}=========================================="
    echo "📱 Mobile App Setup Complete!"
    echo "==========================================${NC}"
    echo -e "${GREEN}Backend API:${NC} http://$LOCAL_IP:8000"
    echo -e "${GREEN}DEV_API_URL:${NC} $DEV_API_URL"
    echo ""
    echo -e "${YELLOW}To use the mobile app:${NC}"
    echo "1. Install 'Expo Go' on your phone from the App Store"
    echo "2. Make sure your phone is on the same WiFi network"
    echo "3. Scan the QR code that appears"
    echo "4. The app will load on your phone"
    echo ""
    echo -e "${YELLOW}For iOS Simulator:${NC}"
    echo "• Press 'i' in the terminal"
    echo ""
    echo -e "${YELLOW}For Android Emulator:${NC}"
    echo "• Press 'a' in the terminal"
    echo ""
    echo -e "${YELLOW}For Web Browser:${NC}"
    echo "• Press 'w' in the terminal"
    echo ""
}

# Main execution
main() {
    print_header
    
    # Check if mobile directory exists
    if [ ! -d "$MOBILE_DIR" ]; then
        echo -e "${RED}Mobile directory not found at $MOBILE_DIR${NC}"
        exit 1
    fi
    
    set_dev_api_url
    check_backend
    setup_mobile
    show_instructions
    start_expo
}

# Run main function
main "$@" 