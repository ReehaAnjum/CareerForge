# CareerForge

CareerForge is a free, local-first student placement-readiness tracker built with Python, Flask, SQLite, HTML, CSS, and JavaScript. It helps each student record technical skills, coding practice, and interview preparation, then summarizes those inputs as a transparent readiness score. It does not use paid services, cloud APIs, or AI keys.

## Features

- Student registration, login, and logout with signed Flask session cookies, CSRF checks on forms, input validation, and Werkzeug password hashing.
- Private student dashboard with readiness score, a component bar chart, progress statistics, skill-gap suggestions, and empty states.
- Technical skills add, edit, list, and delete flows with proficiency ratings from 1 (Beginner) to 5 (Advanced).
- Coding practice log for solved problem, topic, and practice date.
- Interview topic tracker with practice dates and a toggleable completion status.
- SQLite database stored locally in `instance/careerforge.sqlite` by default.
- Responsive layout and locally hosted application assets. No third-party font, chart, or runtime service is required.

## Windows and VS Code setup

Install Python 3.10 or newer and Git. In VS Code, open the CareerForge folder, then open **Terminal → New Terminal** and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, either allow it for the current terminal with `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, or invoke the virtual environment directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Select the environment in VS Code using **Ctrl+Shift+P → Python: Select Interpreter → `.venv`**.

### Configure and run locally

`.env.example` documents all available environment variables. The app intentionally has no dotenv loader; set variables in the terminal before running. A random secret is generated automatically for a local run if `CAREERFORGE_SECRET_KEY` is omitted. Set a stable secret when you need sessions to survive application restarts:

```powershell
$env:CAREERFORGE_SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
$env:CAREERFORGE_DATABASE = "$PWD\instance\careerforge.sqlite"
```

Initialize the database and start the development server:

```powershell
python -m flask --app app init-db
python app.py
```

Open <http://127.0.0.1:5000>. To stop the server, press **Ctrl+C** in the terminal. The `instance` directory is created automatically. The local Flask development server is for development and demonstration, not public production hosting.

## Architecture

```text
app.py                 Flask application factory and local server entry point
config.py              Environment-backed configuration and score weights
db.py                  SQLite connections, schema, and init-db command support
auth.py                Registration, login/logout, CSRF, and login guard
skills.py              Owner-scoped skill CRUD routes
practice.py            Owner-scoped coding and interview tracker routes
dashboard.py           Dashboard queries, statistics, and suggestions
readiness.py           Pure readiness-score calculation and validation
templates/              Jinja pages and shared layout
static/                 Responsive CSS and lightweight confirmation behavior
tests/                  Isolated pytest tests using temporary SQLite databases
Jenkinsfile             Cross-platform Jenkins test pipeline
```

### SQLite schema

The `init-db` command creates these tables idempotently:

- `users`: unique case-insensitive username, Werkzeug password hash, and account creation time.
- `skills`: student-owned skill name, category, and level from 1–5. A student cannot add the same skill name twice.
- `practice_logs`: student-owned solved problem, topic, and practice date.
- `interview_topics`: student-owned topic, practice date, and completion flag.

Foreign keys cascade when a user is removed. Queries that read or change a student's records include both the record identifier and the authenticated user identifier. SQLite values are passed using parameterized queries.

## Readiness score

The score is an educational progress indicator, not a hiring prediction. The default weights are technical skills **40%**, coding practice **35%**, and interview preparation **25%**:

1. Skills = average proficiency level ÷ 5 × 100 (0 when no skills are recorded).
2. Coding = solved problems ÷ coding target × 100, capped at 100 (default target: 20).
3. Interview = completed interview topics ÷ recorded topics × 100 (0 when no topics are recorded).
4. Overall = weighted sum of the three component scores, rounded to the nearest integer.

Weights must be non-negative and add to exactly 1.0 (within a small floating-point tolerance). Configuration is checked when the app starts; invalid values raise a clear error rather than producing a misleading score. Set these environment variables before startup to customize the values:

```powershell
$env:CAREERFORGE_SKILLS_WEIGHT = "0.40"
$env:CAREERFORGE_CODING_WEIGHT = "0.35"
$env:CAREERFORGE_INTERVIEW_WEIGHT = "0.25"
$env:CAREERFORGE_CODING_TARGET = "20"
```

Update the three weights together so their sum remains 1.0. The same values are shown on the dashboard.

## Tests

Install dependencies, then run the isolated suite:

```powershell
python -m pytest -q
```

Tests create a fresh SQLite database under pytest's temporary directory. They cover registration validation and password hashing, login/logout and CSRF, skills CRUD and ownership, practice date/status tracking and ownership, readiness calculations/configuration, and dashboard privacy/statistics. No live database or real student information is used by the suite.

## Jenkins

Create a Jenkins Pipeline job pointing to the GitHub repository and select **Pipeline script from SCM** with the `Jenkinsfile` path. The agent needs Git and Python available (`python3` on Unix-like agents; the Windows Python launcher `py` on Windows agents). The pipeline checks out the project, installs `requirements.txt`, runs pytest, and publishes the JUnit XML report. No credentials or paid Jenkins plugins are needed for this basic pipeline.

## Git and GitHub

The project directory is not initialized as a Git repository by the application. To create a repository locally, then create an empty GitHub repository in your account and connect it:

```powershell
git init
git add .
git status
git commit -m "Build CareerForge placement readiness platform"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the remote URL with your repository's URL. Authenticate to GitHub using Git Credential Manager or GitHub CLI; do not put a password or token in the remote URL. `.gitignore` excludes `.env`, virtual environments, local databases, and test artifacts. Commit `.env.example`, never a real `.env`, database, password, secret key, or student record.
