Railway deployment notes for the `cfa` app

Quick summary

- This app is a Flask application with a factory function `create_app()` exposed from `src.__init__`.
- The repo root `main.py` imports `create_app()` and exposes `app` for WSGI servers.
- The app listens on the port provided by the `PORT` environment variable (default 5000 locally).
- A `Procfile` is included to run with Gunicorn: `web: gunicorn -b 0.0.0.0:$PORT "main:app"`.

Railway settings

- Service port: 5000 (the app reads $PORT at runtime, so set Railway target port to 5000).
- Start command: use the Procfile; Railway will use it automatically when present. Alternatively set custom start command:
  - `gunicorn -b 0.0.0.0:$PORT "main:app"`
- Build command: Railway auto-detects Python when `requirements.txt` exists.
  - If you need a custom build step, set: `pip install -r requirements.txt`

Environment variables

- `PORT` - provided by Railway automatically.
- `DATABASE_URL` - optional. By default the app uses a local SQLite file under `src/database/app.db`.
  - To use Postgres on Railway, set `DATABASE_URL` to Railway Postgres and update `app.config['SQLALCHEMY_DATABASE_URI']` to use it (see notes below).
- `SECRET_KEY` - set for production.
- `FLASK_DEBUG` - set to `false` in production.

Database notes

- By default, `src.create_app()` configures SQLite:
  `sqlite:////absolute/path/to/src/database/app.db` (relative path under the app directory).
- To use Railway Postgres, set `DATABASE_URL` in Railway variables and update `src/__init__.py` before `db.init_app(app)`:

```python
# inside create_app before db.init_app(app)
database_url = os.environ.get('DATABASE_URL')
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
```

Healthcheck

- The app exposes `/health` which returns a small JSON blob. Use `/health` as the Railway health check path.

Static files

- The Flask app serves static files from `src/static` (if present). Ensure your frontend `index.html` is built into that folder before deploy.

Local test commands

```bash
# create venv and install
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# run locally (dev)
export FLASK_DEBUG=true
export PORT=5000
python main.py

# run with gunicorn (production-like)
gunicorn -b 0.0.0.0:5000 "main:app"
```

If you want, I can add a small change to `src/__init__.py` to respect `DATABASE_URL` automatically and commit it. Reply `yes` to proceed and I'll make that edit and run a quick local smoke test.
