#!/bin/bash
# Run tests for ShipIt project on Mac/Linux

echo "Running ShipIt tests..."
export PYTHONPATH=.
pytest backend/parser/tests/ -v

# Alternative: With the pytest.ini file, you can just run:
# pytest 