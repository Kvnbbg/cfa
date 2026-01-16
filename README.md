# 🌍 CFA – Caraïbes France Asie

[![GitHub Repo stars](https://img.shields.io/github/stars/kvnbbg/cfa?style=social)](https://github.com/kvnbbg/cfa)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)

**Community-Driven Knowledge & Supply Chain Platform**

CFA is a Flask-powered web application for railway logistics, supply chain management, and indigenous knowledge preservation. It emphasizes digital sovereignty, cultural inclusivity, and accessibility, connecting communities across Caraïbes, France, and Asia.

**Keywords for AI/Agents**: Flask app, railway optimization, supply chain analytics, indigenous knowledge preservation, digital sovereignty, community-driven platform, multi-regional (Caraïbes, France, Asia).

🚆🌍 Support the CFA vision: community, culture & supply chain.  
🖌️ Artistic work grows mind, body & work together.  

❤️ Like, 🔄 Share & 🙌 Join the movement!  
👉 [See post](https://www.instagram.com/p/DMSr19WIe7W/?img_index=9&igsh=N2xwajlzZDR5MXF2)  
📍 Repository: [github.com/kvnbbg/cfa](https://github.com/kvnbbg/cfa)

---

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Development Patterns](#development-patterns)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contribution Guidelines](#contribution-guidelines)
- [Things to Avoid](#things-to-avoid)
- [API Endpoints](#api-endpoints)
- [License](#license)
- [Vision](#vision)

---

## Overview
CFA bridges railway systems, supply chains, and cultural preservation. Core modules:
- **Railway Tools**: Logistics tracking, route optimization.
- **Supply Chain**: Inventory, analytics (subscriber-only).
- **Knowledge Hub**: Story sharing, tradition archiving with community controls.

Built for low-bandwidth access; supports offline-first via PWA patterns.

---

## Features
| Category | Feature | Description | Access |
|----------|---------|-------------|--------|
| 🚆 Railway | Route Optimization | AI-assisted path planning using NetworkX. | Free |
| 📦 Supply Chain | Analytics Dashboard | Real-time metrics (e.g., delay predictions). | Plus |
| 🧑‍🤝‍🧑 Community | Knowledge Sharing | Upload stories with metadata tags; sovereignty controls. | Free |
| 📖 Preservation | Archival Search | Semantic search via Whoosh; indigenous filters. | Free |
| 🔐 Sovereignty | Data Ownership | User-owned exports; no vendor lock-in. | All |
| 🌍 Multi-Regional | Localization | i18n for FR/EN; region-specific modules. | Free |
| 🌿 Onboarding | Nature Sounds | Calming audio integration (see [cfa-nature-sounds-onboarding-guide.md](cfa-nature-sounds-onboarding-guide.md)). | Free |

---

## Quick Start
```bash
git clone https://github.com/kvnbbg/cfa.git
cd cfa
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run
```
Visit `http://127.0.0.1:5000` for demo.

---

## Installation
1. **Prerequisites**:
   - Python 3.8+.
   - Git.
   - Optional: PostgreSQL for prod DB.

2. **Clone & Setup**:
   ```bash
   git clone https://github.com/kvnbbg/cfa.git
   cd cfa
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt  # Includes Flask, SQLAlchemy, NetworkX
   ```

3. **Database Init**:
   ```bash
   flask db init  # If using Flask-Migrate
   flask db migrate
   flask db upgrade
   ```

4. **Static Assets**:
   - Download audio for onboarding: Place in `/static/audio/` (see guide).
   - Run `npm install` if extending JS (optional).

---

## Configuration
Use `.env` file (create from `.env.example`):
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key  # Used for Flask sessions + JWT signing; keep consistent across services.
DATABASE_URL=sqlite:///cfa.db  # Or postgresql://...
AUDIO_ENABLED=True
DEFAULT_SOUND=rain.mp3
SOUND_VOLUME=0.3
USE_FALLBACKS=True
SUBSCRIPTION_KEY=your-stripe-key  # For Plus features
```

Load via `python-dotenv` in `app.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

For AI/Agents: Export config as YAML for parsing:
```yaml
# config.yaml
app:
  env: development
  database: sqlite:///cfa.db
features:
  audio:
    enabled: true
    default: rain.mp3
```

---

## Usage
- **Local Dev**: `flask run --debug`.
- **Onboarding**: Access `/onboarding` for new users; triggers nature sounds.
- **Knowledge Upload**: POST to `/knowledge` with form-data (story, tags, region).
- **Railway Dashboard**: GET `/railway/routes` (auth required for Plus).
- **CLI Commands**:
  ```bash
  flask knowledge import --file stories.csv  # Bulk upload
  flask supplychain optimize --from paris --to tokyo
  ```

Example API call (curl):
```bash
curl -X POST http://localhost:5000/knowledge \
  -H "Content-Type: multipart/form-data" \
  -F "story=Ancient Caraïbes tale" \
  -F "tags=tradition,oral"
```

---

## Development Patterns
- **Code Style**: PEP 8; use Black formatter (`pip install black; black .`).
- **Branching**: `main` for stable; `feature/*` for dev; `hotfix/*` for urgent.
- **Commits**: Conventional: `feat: add onboarding audio`, `fix: resolve DB migration`.
- **Modular Structure**:
  ```
  cfa/
  ├── app.py          # Main Flask app
  ├── models.py       # DB models (SQLAlchemy)
  ├── routes/         # Blueprints: railway.py, knowledge.py
  ├── static/         # CSS/JS/audio
  ├── templates/      # HTML
  ├── tests/          # Unit/integration
  └── utils/          # Helpers: audio_loader.py
  ```
- **Error Handling**: Use `@app.errorhandler(404)`; log with `logging`.
- **Security**: Sanitize inputs (WTForms); HTTPS in prod.
- **AI-Friendly**: Add docstrings; type hints (`from typing import Optional`).

---

## Testing
- **Unit Tests**: Pytest (`pip install pytest`).
  ```bash
  pytest tests/ -v
  ```
- **Coverage**: `pip install pytest-cov; pytest --cov=.`.
- **E2E**: Selenium for UI (e.g., onboarding flow).
- **Mock Patterns**: Use `unittest.mock` for external deps (e.g., audio fetch).

Run full suite:
```bash
tox  # If tox.ini configured
```

---

## Deployment
- **Heroku/Railway**: 
  ```bash
  # Procfile: web: gunicorn app:app
  git push heroku main
  ```
- **Vercel (easy deploy)**:
  [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/kvnbbg/cfa)
  1. Import the repository in Vercel.
  2. Ensure `vercel.json` is present (already in this repo).
  3. Set environment variables in Vercel:
     - `SECRET_KEY`
     - `DATABASE_URL` (optional; defaults to SQLite)
     - `FLASK_DEBUG=false`
  4. Deploy and verify `/health`.
- **Docker** (docker-compose.yml):
  ```yaml
  version: '3'
  services:
    app:
      build: .
      ports: ["5000:5000"]
      env_file: .env
    db:
      image: postgres:13
      environment:
        POSTGRES_DB: cfa
  ```
  ```bash
  docker-compose up
  ```
- **CI/CD**: GitHub Actions (.github/workflows/ci.yml) for lint/test/deploy.
- **Scaling**: Gunicorn + Nginx; Redis for caching.

---

## Contribution Guidelines
1. **Fork & Branch**: `git checkout -b feat/your-feature`.
2. **Code Review**: PRs must pass tests; 2 approvals needed.
3. **Docs Update**: Edit README.md for changes.
4. **Community Focus**: Tag `@community-leads`; reference indigenous input.

**Dos**:
- Consult elders for cultural features.
- Add accessibility (ARIA, WCAG 2.1).
- Use semantic commits.

**Don'ts**:
- Hardcode secrets.
- Ignore type hints.
- Submit without tests.

PR Template (in .github/pull_request_template.md):
```markdown
## Description
- What: Brief summary.
- Why: Ties to vision.

## Changes
- Files: list
- Tests: Added/Updated

## Checklist
- [ ] Tests pass
- [ ] Docs updated
- [ ] Community reviewed
```

---

## Things to Avoid
- **Security**: No SQL injection (use params); avoid eval/exec.
- **Performance**: Limit queries (<100ms); compress audio (<1MB).
- **Cultural**: Don't assume universal symbols; validate with stakeholders.
- **Accessibility**: Skip auto-play without controls; test with screen readers.
- **AI Pitfalls**: Overfit models to one region; ensure bias checks in analytics.
- **Deps**: No unvetted pip installs; pin versions in requirements.txt.

---

## API Endpoints
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/knowledge` | List stories | Optional |
| POST | `/knowledge` | Upload story | User |
| GET | `/railway/routes` | Fetch optimized routes | Plus |
| POST | `/supplychain/analyze` | Run analytics | Plus |
| GET | `/onboarding` | Entry with audio | Guest |

Swagger docs: Run `flask run` + visit `/api/docs` (if Flask-RESTX added).

---

## License
[MIT License](LICENSE) – Free to use, adapt, improve with attribution.

---

## Vision
CFA is a resilient bridge: preserving indigenous wisdom while optimizing global supply chains. Join to co-create equity across Caraïbes, France, Asia. 🌱
