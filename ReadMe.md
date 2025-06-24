# ShipIt: Resume-Powered Internship Finder

ShipIt turns a student résumé into a personalised internship feed and helps them stay on track during the recruiting season.

## Project Structure
- `backend/` — Python modules for résumé parsing, job aggregation and matching
- `mobile/`  — React-Native / Expo client
- `config/`  — Conda + pip requirements, PyTest config
- `tools/`   — helper scripts (test runner, etc.)

## Key Features
1. **Smart Résumé Parser** (implemented)  
   Rule-based + layout-aware extraction of contact info, education, skills & experience from PDF/DOCX.
2. **Internship Matcher** (road-map)  
   Rank live job postings against the extracted profile with keyword / TF-IDF scoring.
3. **Industry News Feed** (road-map)  
   Curated tech and internship-related news so students keep up with trends.
4. **Weekly Goals** (Duolingo-style streaks)  
   Nudge users to apply to _N_ roles each week; visualised as streaks & XP.
5. **Application Tracker**  
   Replaces the spreadsheet many students maintain; Kanban board & analytics for offers, rejections and upcoming interviews.

---

## Installing Dependencies
The quickest way is to run the platform-specific script at the repo root.

### macOS / Linux
```bash
chmod +x install_dependencies.sh   # first time only
./install_dependencies.sh           # sets up Conda env (or pip) + npm packages
```

### Windows
```cmd
install_dependencies.bat           # does the same via conda/pip + npm
```
These scripts:
1. Create / update the Conda environment `shipit` from `config/environment.yml` (if Conda is installed), **or** fall back to `pip install -r config/requirements.txt`.
2. Run `npm install` inside the `mobile/` folder to install the React-Native dependencies.

---

## Running Tests (backend)
```bash
# From project root
./tools/run_tests.sh        # macOS / Linux
run_tests.bat               # Windows
```

## Running the Mobile App
```bash
cd mobile
npm start           # or: npm run ios / android / web
```
Expo Dev Tools will open; follow its instructions to launch the simulator or connect a device.

## Contributing
1. Fork & clone the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Commit + push, then open a PR.

Please ensure new Python / TypeScript code has accompanying tests.

---

Happy shipping! 🚀
