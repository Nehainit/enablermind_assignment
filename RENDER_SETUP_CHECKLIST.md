# EnableMind - Fresh Service Setup Checklist

## ✅ Step-by-Step Instructions

### Step 1: Access Render Dashboard
- [ ] Browser opened to: https://dashboard.render.com/create?type=web
- [ ] You should see "Create a new Web Service" page

### Step 2: Connect Repository
- [ ] Click "Connect a repository" or select from existing
- [ ] Search for: **Nehainit/enablermind_assignment**
- [ ] Click "Connect"

### Step 3: Configure Service

**Basic Settings:**
- [ ] **Name:** `enablemind-web` (or any name you prefer)
- [ ] **Region:** Choose closest to you (e.g., Oregon, Frankfurt)
- [ ] **Branch:** `main`
- [ ] **Root Directory:** (leave blank)

**Build Settings:**
- [ ] **Runtime:** Select **"Docker"** from dropdown ⚠️ IMPORTANT!
- [ ] **Dockerfile Path:** `./Dockerfile`
- [ ] **Docker Context:** `.` (or leave blank)
- [ ] **Docker Build Command:** (leave blank - uses default)

### Step 4: Environment Variables

Click "+ Add Environment Variable" for each:

1. **GROQ_API_KEY**
   - [ ] Key: `GROQ_API_KEY`
   - [ ] Value: `[YOUR_GROQ_API_KEY_HERE]` ← Paste your actual key
   - [ ] ⚠️ This is REQUIRED - get it from https://console.groq.com

2. **LLM_PROVIDER**
   - [ ] Key: `LLM_PROVIDER`
   - [ ] Value: `groq`

3. **GROQ_MODEL**
   - [ ] Key: `GROQ_MODEL`
   - [ ] Value: `llama-3.3-70b-versatile`

4. **LOG_LEVEL** (optional)
   - [ ] Key: `LOG_LEVEL`
   - [ ] Value: `INFO`

5. **MAX_RESEARCH_ITERATIONS** (optional)
   - [ ] Key: `MAX_RESEARCH_ITERATIONS`
   - [ ] Value: `3`

### Step 5: Advanced Settings (Scroll Down)

- [ ] **Health Check Path:** `/health`
- [ ] **Auto-Deploy:** Yes (should be enabled by default)
- [ ] **Plan:** Free

### Step 6: Create Service

- [ ] Review all settings above
- [ ] Click **"Create Web Service"** button at the bottom
- [ ] Wait for deployment to start (2-3 minutes)

---

## 🔍 What to Watch For

### During Deployment:

1. **Initial Setup** (30 seconds)
   - Cloning repository
   - Detecting Dockerfile

2. **Building Docker Image** (2-3 minutes)
   - Installing system dependencies
   - Installing Python packages
   - Should see: "Successfully installed langchain..."

3. **Starting Application** (30 seconds)
   - Running uvicorn
   - Health check passing

### Success Indicators:
- ✅ Status changes to "Live" (green)
- ✅ URL becomes active: `https://enablemind-web.onrender.com`
- ✅ Health check: `https://enablemind-web.onrender.com/health` returns:
  ```json
  {
    "status": "healthy",
    "service": "enablemind-research",
    "version": "0.1.0"
  }
  ```

---

## 🚨 Troubleshooting

### If Build Fails:

**Check logs for:**
- "ModuleNotFoundError" → Missing dependency (should be fixed)
- "Port binding" error → Dockerfile PORT issue (should be fixed in commit de25dfc)
- "No module named 'langchain'" → Should be fixed, but check requirements.txt

**Common Fixes:**
1. Verify GROQ_API_KEY is set correctly
2. Check Docker runtime is selected (not Python/Node)
3. Verify branch is `main` with latest commit (de25dfc)

### If Health Check Fails:

1. Click on service → "Logs" tab
2. Look for startup errors
3. Check if port binding is correct
4. Verify all environment variables are set

---

## 📊 Expected Timeline

- **Build Time:** 2-3 minutes
- **First Deploy:** 3-4 minutes total
- **Subsequent Deploys:** 1-2 minutes (with cache)

---

## ✨ After Successful Deployment

1. **Test the application:**
   - Visit: `https://[your-service-name].onrender.com`
   - Should see EnableMind homepage

2. **Try a research job:**
   - Enter a topic: "Kubernetes networking"
   - Click "Start Research"
   - Watch progress bar update
   - Download reports when complete

3. **Share the URL:**
   - Your app is now live and accessible to anyone!

---

## 🎯 Current Configuration

**Latest Code (commit de25dfc):**
- ✅ Docker with Python 3.10
- ✅ langchain dependencies included
- ✅ PORT environment variable support
- ✅ Proper PYTHONPATH configuration
- ✅ All web dependencies installed

**Repository:**
- https://github.com/Nehainit/enablermind_assignment

**Branch:**
- main

**Latest Commit:**
- de25dfc - "Fix Dockerfile to use Render PORT env variable"

---

## 💡 Need Help?

If you get stuck:
1. Take a screenshot of the error
2. Copy the error message from logs
3. Share it and I'll help debug

**Ready to create the service? Follow the checklist above! ✨**
