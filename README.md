# Industrial Asset Monitor

A lightweight FastAPI + Jinja2 + Tailwind dashboard for tracking manufacturing
parts and flagging low-stock conditions on a factory floor.

## What's included

```
industrial-asset-monitor/
├── main.py                  # FastAPI backend
├── templates/
│   └── index.html            # Dashboard UI (Tailwind, server-rendered)
├── requirements.txt
└── README.md
```

## Features

- **Live stock dashboard** — each part shows current quantity, minimum safe
  stock, and a STABLE / CRITICAL LOW badge.
- **Use 1 Part** — decrements quantity by 1 (never below 0).
- **Restock (+5)** — increments quantity by 5.
- **Add New Item** *(new)* — a modal form lets you create a new inventory
  item (name, starting quantity, minimum required) directly from the UI,
  with validation against empty names, duplicates, and negative values.
- **Delete item** *(new)* — a small "×" button removes an item you no longer
  track, with a confirm prompt to avoid accidental deletes.
- **Persistent storage** — inventory is stored in `factory_data.json` on
  disk, seeded with sample data the first time it runs.

## Run it locally

Requires Python 3.9+.

```bash
# 1. Clone/unzip the project and move into it
cd industrial-asset-monitor

# 2. (Recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python main.py
# or, equivalently:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then open **http://localhost:8000** in your browser.

`factory_data.json` will be created automatically in the project folder on
first run — delete it any time to reset to the default sample inventory.

## Deploying

### Option A — Docker (works on almost any host)

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t asset-monitor .
docker run -p 8000:8000 -v $(pwd)/data:/app/data asset-monitor
```

> Tip: mount a volume (as above) if you want `factory_data.json` to survive
> container restarts — otherwise data resets whenever the container rebuilds.

### Option B — Render.com (free tier friendly)

1. Push this project to a GitHub repo.
2. In Render, click **New → Web Service** and connect the repo.
3. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy. Render provides the `$PORT` env var automatically, which
   `main.py` already reads via `os.environ.get("PORT", 8000)`.

### Option C — Railway.app

1. Push to GitHub, then **New Project → Deploy from GitHub repo** in Railway.
2. Railway auto-detects Python; if it doesn't, set the start command to:
   `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Deploy — Railway injects `$PORT` automatically.

### Option D — Fly.io

```bash
fly launch      # generates a fly.toml, follow the prompts
fly deploy
```
Make sure `fly.toml`'s `internal_port` matches the port your app listens on
(8000, or whatever `$PORT` resolves to).

### A note on storage in production

This app persists inventory to a local JSON file (`factory_data.json`).
That's fine for a single-instance demo or internal tool, but:

- On most PaaS platforms (Render, Railway, Fly) the filesystem is
  **ephemeral** — the JSON file will reset on redeploys/restarts unless you
  attach a persistent volume/disk.
- If you scale to multiple instances, each instance gets its own file and
  they won't stay in sync.

For anything beyond a single-instance internal tool, consider swapping
`load_data()` / `save_data()` for a real database (SQLite for a quick
upgrade, Postgres for multi-instance deployments).

## Extending further

Some natural next steps if you keep building this out:

- Add authentication so only authorized floor staff can restock/delete.
- Add a "units used today" audit log for reporting.
- Move from JSON file storage to SQLite/Postgres for durability.
- Add barcode/QR scanning for faster "Use 1 Part" actions on the floor.
