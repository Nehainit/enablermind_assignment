# EnableMind Web UI - Deployment Guide

## ✅ Implementation Complete

All components of the EnableMind Web UI have been successfully implemented and tested.

## 📁 What Was Built

### Backend Services
- ✅ **JobManager** (`web/services/job_manager.py`) - In-memory job queue with background worker
- ✅ **ResearchRunner** (`web/services/research_runner.py`) - Wrapper around existing research system
- ✅ **FastAPI App** (`web/app.py`) - Main application with lifespan management

### API Routes
- ✅ **Main Routes** (`web/routes/main.py`) - Homepage and research submission
- ✅ **Job Routes** (`web/routes/jobs.py`) - Progress tracking and status API
- ✅ **Download Routes** (`web/routes/downloads.py`) - Report file serving

### Frontend
- ✅ **Templates** - Jinja2 templates with HTMX for dynamic updates
  - `base.html` - Base layout with Tailwind CSS + HTMX
  - `index.html` - Homepage with research form
  - `job_status.html` - Real-time progress tracking
  - `components/` - Reusable UI components

- ✅ **Static Assets**
  - `custom.css` - Animations and custom styles
  - `app.js` - Client-side enhancements

### Configuration
- ✅ **render.yaml** - Render.com deployment blueprint
- ✅ **requirements-web.txt** - Web-specific dependencies
- ✅ **Integration tests** - Full workflow testing

## 🚀 Local Development

### 1. Setup Environment

```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate

# Install web dependencies
pip install -r requirements-web.txt

# Verify Groq API key is set
cat .env | grep GROQ_API_KEY
```

### 2. Start Development Server

```bash
# From project root
uvicorn web.app:app --reload --port 8000

# Or with hot-reload
uvicorn web.app:app --reload --log-level debug
```

### 3. Access the Application

Open your browser to: **http://localhost:8000**

### 4. Run Tests

```bash
# Start server in background
uvicorn web.app:app --host 127.0.0.1 --port 8001 &

# Run integration tests
python test_web_ui.py

# Stop server
pkill -f "uvicorn web.app:app"
```

## 📦 Deployment to Render.com

### Option 1: Blueprint Deployment (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add EnableMind Web UI"
   git push origin main
   ```

2. **Deploy on Render**
   - Go to https://render.com/dashboard
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will detect `render.yaml` automatically
   - Click "Apply"

3. **Set Environment Variables**
   - In Render dashboard, go to your service
   - Navigate to "Environment" tab
   - Add: `GROQ_API_KEY` = `your_groq_api_key_here`
   - Service will auto-deploy

### Option 2: Manual Deployment

1. **Create Web Service**
   - Go to https://render.com/dashboard
   - Click "New +" → "Web Service"
   - Connect your repository
   - Configure:
     - **Name**: enablemind-research
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt && pip install -r requirements-web.txt`
     - **Start Command**: `uvicorn web.app:app --host 0.0.0.0 --port $PORT`

2. **Environment Variables**
   ```
   PYTHON_VERSION=3.11
   LLM_PROVIDER=groq
   GROQ_API_KEY=<your_key>
   GROQ_MODEL=llama-3.3-70b-versatile
   LOG_LEVEL=INFO
   MAX_RESEARCH_ITERATIONS=3
   ```

3. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (3-5 minutes)
   - Access your app at: `https://enablemind-research.onrender.com`

## 🔍 Verification Steps

### After Local Deployment

1. ✅ Homepage loads: `http://localhost:8000`
2. ✅ Submit research topic: "Kubernetes networking"
3. ✅ Progress updates every 2 seconds
4. ✅ Download reports in all formats (MD, PDF, HTML)
5. ✅ Check recent reports section on homepage

### After Render Deployment

1. ✅ Health check passes: `https://your-app.onrender.com/health`
2. ✅ Submit test research
3. ✅ Wait for completion (2-5 minutes)
4. ✅ Download reports
5. ✅ Test after 15-minute sleep (cold start)

## 📊 Monitoring

### Check Application Logs

**Render Dashboard:**
- Go to your service
- Click "Logs" tab
- Watch for:
  - `Starting EnableMind Web Application`
  - `JobManager worker started`
  - Job creation and completion logs

**Local:**
```bash
# Watch logs in real-time
uvicorn web.app:app --log-level debug

# Or tail server logs
tail -f /tmp/enablemind_server.log
```

### Health Monitoring

```bash
# Check if service is healthy
curl https://your-app.onrender.com/health

# Should return:
# {
#   "status": "healthy",
#   "service": "enablemind-research",
#   "version": "0.1.0"
# }
```

## 🐛 Troubleshooting

### Port Already in Use (Local)

```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn web.app:app --port 8001
```

### Module Import Errors

```bash
# Ensure you're in project root
pwd  # Should be /path/to/enablemind

# Reinstall dependencies
pip install -r requirements.txt -r requirements-web.txt
```

### HTMX Not Updating

- Check browser console for errors
- Verify HTMX CDN is loading: https://unpkg.com/htmx.org@1.9.10
- Check `/api/job/{id}/status` endpoint returns HTML

### Files Not Found After Research

```bash
# Check outputs directory
ls -la outputs/

# Verify permissions
chmod 755 outputs/
```

### Render Cold Starts

Free tier sleeps after 15 minutes of inactivity:
- First request after sleep takes 30-60 seconds
- Jobs in progress during sleep are lost (acceptable for MVP)
- Downloads only available during active session

## 🎯 Usage Tips

### For Users

1. **Research Depth**
   - 1-2 iterations: Quick overview (1-2 minutes)
   - 3 iterations: Balanced research (2-3 minutes) - **Recommended**
   - 4-5 iterations: Comprehensive analysis (3-5 minutes)

2. **Download Immediately**
   - Reports are session-scoped
   - Download all formats right after completion
   - Files deleted after 1 hour or server restart

3. **Good Research Topics**
   - Specific: "Redis persistence strategies: RDB vs AOF"
   - Technical: "Kubernetes service mesh: Istio vs Linkerd comparison"
   - Avoid: Overly broad topics like "programming" or "AI"

### For Developers

1. **Adding Features**
   - Routes: Add to `web/routes/`
   - Services: Add to `web/services/`
   - Templates: Add to `web/templates/`

2. **Database Integration** (Future)
   - Replace `JobManager` in-memory storage
   - Add PostgreSQL for job persistence
   - Update `render.yaml` to include database service

3. **Authentication** (Future)
   - Add auth middleware to `web/app.py`
   - Protect routes with `Depends(get_current_user)`
   - Store user-job associations in database

## 📈 Performance

### Free Tier Limits (Render)

- **RAM**: 512 MB (sufficient for sequential processing)
- **CPU**: Shared
- **Disk**: Ephemeral (files lost on restart)
- **Sleep**: After 15 minutes inactivity
- **Monthly hours**: 750 free hours

### Optimization Tips

1. **Single Worker** - Jobs process sequentially (by design)
2. **Progress Polling** - 2-second interval (balance between UX and load)
3. **File Cleanup** - Automatic cleanup after 1 hour
4. **Job Limit** - Maximum 50 jobs in memory

## 🔒 Security Notes

### Current Implementation

- ✅ CORS enabled (restrict in production)
- ✅ Form validation (XSS protection via Jinja2 auto-escaping)
- ✅ File serving via FileResponse (safe)
- ⚠️ No rate limiting (add for production)
- ⚠️ No authentication (public access)

### Production Recommendations

1. **Add Rate Limiting**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   ```

2. **Restrict CORS**
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

3. **Add Authentication**
   - OAuth2 with JWT tokens
   - User-specific job access
   - API key for programmatic access

## 📚 Next Steps

### Immediate (Post-MVP)

- [ ] Add comprehensive error messages
- [ ] Implement graceful degradation for Groq API failures
- [ ] Add research topic suggestions/autocomplete
- [ ] Show queue position when multiple jobs running

### Short-term

- [ ] Email notifications on completion
- [ ] WebSocket support for real-time updates
- [ ] Persistent storage (S3/R2)
- [ ] User authentication and history

### Long-term

- [ ] Research templates (academic, industry, etc.)
- [ ] Advanced filters and search
- [ ] Research quality scoring
- [ ] Export to additional formats (DOCX, LaTeX)

## 🎉 Success!

Your EnableMind Web UI is now fully functional and ready for deployment.

**Key Features:**
- ✅ Simple web interface for research submission
- ✅ Real-time progress tracking with HTMX
- ✅ Multiple download formats (MD/PDF/HTML)
- ✅ Mobile-responsive design
- ✅ One-click deployment to Render.com

**What's Next:**
1. Test locally: `uvicorn web.app:app --reload`
2. Deploy to Render: Follow deployment steps above
3. Share with users and gather feedback
4. Iterate based on usage patterns

For questions or issues, refer to `WEB_README.md` or open a GitHub issue.

---
**Built with:** FastAPI, HTMX, TailwindCSS, CrewAI, and Groq LLM
