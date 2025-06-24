#!/usr/bin/env bash
# install_dependencies.sh
# Setup script for the ShipIt project (macOS / Linux)
# ---------------------------------------------------
# 1. Backend  – uses Conda if available, otherwise falls back to pip.
# 2. Front-end – installs React-Native / Expo packages with npm.

set -euo pipefail

GREEN="\033[0;32m"
NC="\033[0m" # No Color

echo -e "${GREEN}🛠  Installing backend dependencies...${NC}"
if command -v conda &> /dev/null; then
  echo "Conda detected. Creating/updating environment 'shipit' from config/environment.yml"
  # Try create first; if env exists, update instead.
  if conda env create -f config/environment.yml 2>/dev/null; then
    echo "Environment created. Activate with: conda activate shipit"
  else
    echo "Environment already exists. Updating packages..."
    conda env update -f config/environment.yml
  fi
else
  echo "Conda not detected. Falling back to system Python + pip."
  pip install --upgrade pip
  pip install -r config/requirements.txt
fi

echo -e "${GREEN}📦  Installing mobile (React Native) dependencies...${NC}"
if [ -d "mobile" ]; then
  pushd mobile > /dev/null
  if command -v npm &> /dev/null; then
    npm install --legacy-peer-deps
  else
    echo "npm is required but not found. Please install Node.js and npm, then re-run this script."
    exit 1
  fi
  popd > /dev/null
else
  echo "Mobile directory not found! Skipping front-end setup."
fi

echo -e "${GREEN}✅  All dependencies installed. Happy hacking!${NC}" 