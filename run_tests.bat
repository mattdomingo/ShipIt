@echo off
REM Run tests for ShipIt project on Windows

echo Running ShipIt tests...
set PYTHONPATH=.
pytest backend/parser/tests/ -v

REM Alternative: With the pytest.ini file, you can just run:
REM pytest 