# EnableMind Web UI - Quick Start

## Run Locally (30 seconds)

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Install web dependencies (if not already installed)
pip install -r requirements-web.txt

# 3. Start the server
uvicorn web.app:app --reload --port 8000

# 4. Open browser
# http://localhost:8000
```

## Deploy to Render.com (5 minutes)

```bash
# 1. Push to GitHub
git add .
git commit -m "Add web UI"
git push

# 2. Go to https://render.com
# 3. Click "New+" → "Blueprint"
# 4. Connect repo (render.yaml auto-detected)
# 5. Add environment variable: GROQ_API_KEY
# 6. Deploy!
```

## Test the Application

```bash
# With server running on port 8001
python test_web_ui.py
```

## Key Files

- `web/app.py` - FastAPI application
- `web/routes/main.py` - Homepage and form submission
- `web/routes/jobs.py` - Job status and progress
- `web/templates/index.html` - Homepage UI
- `render.yaml` - Deployment configuration

## Common Commands

```bash
# Start server
uvicorn web.app:app --reload

# Start on different port
uvicorn web.app:app --port 8001

# View logs
uvicorn web.app:app --log-level debug

# Kill server on port 8000
lsof -ti:8000 | xargs kill -9
```

## Verification Checklist

- ✅ Health check: `curl http://localhost:8000/health`
- ✅ Homepage loads in browser
- ✅ Submit research topic
- ✅ Progress bar updates every 2 seconds
- ✅ Download reports when complete

## Need Help?

- Full docs: `WEB_README.md`
- Deployment: `DEPLOYMENT_GUIDE.md`
- Architecture: See plan document

## Environment Variables

Required:
```bash
GROQ_API_KEY=your_api_key_here
```

Optional:
```bash
LLM_PROVIDER=groq
GROQ_MODEL=llama-3.3-70b-versatile
LOG_LEVEL=INFO
MAX_RESEARCH_ITERATIONS=3
```
