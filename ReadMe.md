# ShipIt: Resume-Powered Internship Finder

## Project Structure

- `backend/` — API, resume parser, job aggregator, matcher
- `mobile/` — React Native/Expo mobile app

## Getting Started

### Environment Setup

#### Option 1: Using Conda (Recommended)
```bash
# Create environment from file
conda env create -f environment.yml

# Activate environment
conda activate shipit

# Run tests
pytest
```

#### Option 2: Using pip
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest
```

### Platform-Specific Test Scripts

**Mac/Linux:**
```bash
./run_tests.sh
```

**Windows:**
```cmd
run_tests.bat
```

See each subfolder for additional setup instructions.

---

This is the skeleton for your MVP. Next steps:
- Initialize backend (Node.js/Express or Python/Flask)
- Initialize mobile app (React Native/Expo)
- Implement core modules
