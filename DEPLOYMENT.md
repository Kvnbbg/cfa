Railway deployment notes for the `cfa` app

Quick summary

- This app is a Flask application with a factory function `create_app()` exposed from `src.__init__`.
- The repo root `main.py` imports `create_app()` and exposes `app` for WSGI servers.
- The Vercel entry point is `app.py`, which also exposes `app` for serverless runtime.
- The app listens on the port provided by the `PORT` environment variable (default 5000 locally).
- A `Procfile` is included to run with Gunicorn: `web: gunicorn -b 0.0.0.0:$PORT "main:app"`.

Vercel easy deploy

- Click the Deploy button in README or import the repository in Vercel.
- Vercel uses `vercel.json` to build with `@vercel/python` and route all traffic to `app.py`.
- Environment variables to configure in Vercel:
  - `SECRET_KEY` - required for production sessions/JWT.
  - `DATABASE_URL` - optional. Defaults to SQLite if unset.
  - `FLASK_DEBUG=false` - ensure production behavior.
- Healthcheck: after deploy, visit `/health` to confirm the service is live.

Railway settings

- Service port: 5000 (the app reads $PORT at runtime, so set Railway target port to 5000).
- Start command: use the Procfile; Railway will use it automatically when present. Alternatively set custom start command:
  - `gunicorn -b 0.0.0.0:$PORT "main:app"`
- Build command: Railway auto-detects Python when `requirements.txt` exists.
  - If you need a custom build step, set: `pip install -r requirements.txt`

Environment variables

- `PORT` - provided by Railway automatically.
- `DATABASE_URL` - optional. By default the app uses a local SQLite file under `src/database/app.db`.
  - To use Postgres on Railway, set `DATABASE_URL` to Railway Postgres.
- `SECRET_KEY` - set for production. Used for Flask sessions and JWT signing; keep it stable across deployments to avoid token invalidation.
- `FLASK_DEBUG` - set to `false` in production.

Database notes

- By default, `src.create_app()` configures SQLite:
  `sqlite:////absolute/path/to/src/database/app.db` (relative path under the app directory).
- To use Railway Postgres, set `DATABASE_URL` in Railway variables. The app already prioritizes `DATABASE_URL` when present.

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
