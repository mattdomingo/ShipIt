# ShipIt: Resume-Powered Internship Finder

ShipIt turns a student résumé into a personalised internship feed and helps them stay on track during the recruiting season.

## 🚀 Quick Start

**Start all backend services:**
```bash
./start_servers.sh
```

**Start mobile app (new terminal):**
```bash
./start_mobile.sh
```

See [QUICK_START.md](QUICK_START.md) for detailed instructions.

## Project Structure
- `backend/` — Python modules for résumé parsing, job aggregation and matching
- `mobile/`  — React-Native / Expo client
- `config/`  — Conda + pip requirements, PyTest config
- `tools/`   — utility scripts (testing, data formatting, etc.)
- `docs/`    — project documentation and summaries

## Key Features
1. **Smart Résumé Parser** (implemented)  
   Rule-based + layout-aware extraction of contact info, education, skills & experience from PDF/DOCX.
2. **Résumé Tailor / Optimizer** (road-map)  
   Generate a job-specific version of your résumé by analysing a posting's keywords and re-ordering / re-phrasing bullets for maximum ATS match.
3. **Internship Matcher** (road-map)  
   Rank live job postings against the extracted profile with keyword / TF-IDF scoring.
4. **Industry News Feed** (road-map)  
   Curated tech and internship-related news so students keep up with trends.
5. **Weekly Goals** (Duolingo-style streaks)  
   Nudge users to apply to _N_ roles each week; visualised as streaks & XP.
6. **Application Tracker**  
   Replaces the spreadsheet many students maintain; Kanban board & analytics for offers, rejections and upcoming interviews.

---

## Manual Setup (if startup scripts don't work)

### Prerequisites
- Python 3.8+ with virtual environment at `.venv/`
- Redis installed (`brew install redis` on macOS)
- Node.js and npm installed

### Backend Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r config/requirements.txt

# Start services (3 terminals)
redis-server                                                    # Terminal 1
python backend/api/run_server.py                              # Terminal 2
celery -A backend.api.jobs.celery_app worker --loglevel=info  # Terminal 3
```

### Mobile Setup
```bash
cd mobile
npm install
npx expo start
```

---

## Running Tests
```bash
# Backend tests
pytest

# Integration tests
python tools/test_upload_parsing.py <resume_file>
python tools/test_real_resume.py <resume_file>
```

## Utility Scripts
- `tools/test_upload_parsing.py` — Full pipeline integration test
- `tools/test_real_resume.py` — Direct parser testing with detailed output
- `tools/get_parsed_resume.py` — Fetch and display parsed data from API
- `tools/format_resume_output.py` — Quick formatting for parsed data

## Contributing
1. Fork & clone the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Commit + push, then open a PR.

Please ensure new Python / TypeScript code has accompanying tests.

---

Happy shipping! 🚀
