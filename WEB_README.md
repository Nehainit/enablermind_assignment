# EnableMind Web UI

Web-based interface for the EnableMind multi-agent research system.

## Features

- 🔍 **Simple Research Submission** - Enter any technical topic via web form
- 📊 **Real-time Progress Tracking** - Watch your research progress with live updates
- 📥 **Multiple Download Formats** - Download reports as Markdown, PDF, or HTML
- 🚀 **Fast & Responsive** - Built with FastAPI and HTMX for snappy interactions
- 🎨 **Modern UI** - Clean, mobile-responsive interface with TailwindCSS

## Quick Start

### Prerequisites

- Python 3.11+
- Groq API key (free tier available at https://console.groq.com)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-web.txt
```

2. Set up environment variables:
```bash
# Create .env file in project root
echo "GROQ_API_KEY=your_api_key_here" > .env
echo "LLM_PROVIDER=groq" >> .env
echo "GROQ_MODEL=llama-3.3-70b-versatile" >> .env
```

### Running Locally

Start the development server:

```bash
uvicorn web.app:app --reload --port 8000
```

Or use Python directly:

```bash
python -m web.app
```

Then open your browser to: **http://localhost:8000**

## Usage

1. **Enter Research Topic** - Type your technical research topic in the text area
2. **Select Research Depth** - Adjust the slider (1-5 iterations)
3. **Submit** - Click "Start Research" and you'll be redirected to the progress page
4. **Monitor Progress** - Watch real-time updates as AI agents research, analyze, and report
5. **Download Reports** - Once complete, download in your preferred format(s)

### Example Topics

- "Kubernetes pod networking and service mesh architecture"
- "Redis caching strategies for high-traffic applications"
- "GraphQL vs REST API performance comparison"
- "Rust async runtime internals and tokio architecture"

## Architecture

### Tech Stack

- **Backend**: FastAPI (async Python web framework)
- **Templating**: Jinja2 (server-side rendering)
- **Interactivity**: HTMX (dynamic updates without JavaScript)
- **Styling**: TailwindCSS (via CDN)
- **Job Queue**: In-memory queue with background worker
- **LLM**: Groq (free tier with llama-3.3-70b-versatile)

### Key Components

```
web/
├── app.py              # FastAPI application entry
├── routes/             # HTTP route handlers
│   ├── main.py         # Homepage & research submission
│   ├── jobs.py         # Job status & progress polling
│   └── downloads.py    # File download endpoints
├── services/           # Business logic
│   ├── job_manager.py  # In-memory job queue & worker
│   └── research_runner.py  # Wrapper for src/main.py
├── templates/          # Jinja2 HTML templates
│   ├── base.html       # Base layout
│   ├── index.html      # Homepage
│   ├── job_status.html # Progress tracking page
│   └── components/     # Reusable UI components
└── static/             # CSS and JS assets
```

### How It Works

1. **Job Submission**: User submits form → FastAPI creates job → Redirects to status page
2. **Background Processing**: Worker thread picks up job → Runs existing `src/main.py::run()` function
3. **Progress Updates**: HTMX polls `/api/job/{id}/status` every 2 seconds for progress
4. **File Discovery**: After completion, discover generated files in `outputs/` directory
5. **Downloads**: Serve files via FastAPI FileResponse

### Session Storage

Reports are stored temporarily in the `outputs/` directory during the current session. Files are kept for:
- Duration of the server process (until restart/sleep)
- Up to 1 hour after completion (automatic cleanup)
- Maximum 50 recent jobs (oldest removed first)

**Important**: Always download reports immediately after generation, especially when deploying to platforms with ephemeral storage.

## Deployment

### Render.com (Recommended)

The app is configured for one-click deployment to Render.com's free tier:

1. **Push to GitHub**:
```bash
git add .
git commit -m "Add web UI"
git push origin main
```

2. **Deploy on Render**:
   - Go to https://render.com
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`
   - Set `GROQ_API_KEY` in environment variables
   - Deploy!

3. **Configure Environment**:
   - In Render dashboard, go to your service
   - Environment → Add `GROQ_API_KEY` with your API key
   - Service will auto-restart

### Other Platforms

The app can run on any platform that supports Python:

- **Heroku**: Use `Procfile` with `web: uvicorn web.app:app --host 0.0.0.0 --port $PORT`
- **Railway**: Auto-detects FastAPI, just set environment variables
- **Fly.io**: Create `fly.toml` with similar config to render.yaml
- **Digital Ocean App Platform**: Use buildpack and set start command

### Environment Variables

Required:
- `GROQ_API_KEY` - Your Groq API key

Optional:
- `LLM_PROVIDER` - Default: `groq`
- `GROQ_MODEL` - Default: `llama-3.3-70b-versatile`
- `LOG_LEVEL` - Default: `INFO`
- `MAX_RESEARCH_ITERATIONS` - Default: `3`

## API Endpoints

### Public Endpoints

- `GET /` - Homepage with research form
- `POST /research` - Submit new research job
- `GET /job/{job_id}` - Job status page
- `GET /api/job/{job_id}/status` - Job status HTML fragment (for HTMX)
- `GET /download/{job_id}/{format}` - Download report (md/pdf/html)
- `GET /health` - Health check

## Development

### Running Tests

```bash
# TODO: Add tests
pytest tests/web/
```

### Local Development Tips

1. **Enable Debug Mode**:
```bash
uvicorn web.app:app --reload --log-level debug
```

2. **Watch Logs**:
   - FastAPI logs show all HTTP requests
   - Job manager logs show research progress
   - Set `LOG_LEVEL=DEBUG` for verbose output

3. **Test Error Cases**:
   - Submit invalid topic (empty, too long)
   - Request non-existent job ID
   - Try to download from incomplete job

### Code Style

The project follows:
- PEP 8 for Python code
- Type hints where appropriate
- Docstrings for all public functions
- Keep it simple - no premature optimization

## Troubleshooting

### "Module not found" errors

Make sure you're in the project root and have installed both requirement files:
```bash
pip install -r requirements.txt
pip install -r requirements-web.txt
```

### HTMX polling not working

Check browser console for errors. Ensure HTMX CDN is loading:
```
https://unpkg.com/htmx.org@1.9.10
```

### Files not found after research

Check `outputs/` directory exists and has correct permissions:
```bash
ls -la outputs/
```

### Groq API errors

Verify your API key is set correctly:
```bash
python -c "from config.settings import get_settings; print(get_settings().groq_api_key)"
```

## Future Enhancements

Planned features (see plan for details):
- [ ] User authentication and persistent storage
- [ ] Email notifications on completion
- [ ] WebSocket support for real-time updates
- [ ] Research history and favorites
- [ ] Advanced filters and search
- [ ] Custom report templates

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Your license here]

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation in `/docs`
