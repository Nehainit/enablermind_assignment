# Render Deployment Fix - tiktoken Build Issue

## Problem Summary

The deployment is failing because:
1. `tiktoken` package requires Rust/Cargo to build
2. Render's buildpack environment has a read-only Cargo registry
3. No pre-built binary wheels available for the Python/platform combination
4. **tiktoken isn't actually needed** since you're using Groq (not OpenAI)

## Solutions (Choose One)

### ✅ **Solution 1: Docker Deployment (RECOMMENDED)**

Docker gives full control over the build environment and avoids buildpack limitations.

**Steps:**
1. Delete the current service in Render dashboard
2. Commit and push the Docker files:
```bash
git add Dockerfile .dockerignore render-docker.yaml
git commit -m "Add Docker deployment configuration"
git push
```

3. In Render dashboard:
   - Click "New +" → "Web Service"
   - Connect your repository
   - **Runtime**: Select "Docker"
   - **Dockerfile Path**: `./Dockerfile`
   - **Docker Context**: `.`
   - Add environment variables:
     - `GROQ_API_KEY`: your_key_here
     - `LLM_PROVIDER`: groq
     - `GROQ_MODEL`: llama-3.3-70b-versatile
   - Deploy!

**Pros:**
- ✅ Full control over build environment
- ✅ More reliable package installation
- ✅ Easier to debug
- ✅ Can handle complex dependencies

**Cons:**
- Takes slightly longer to build (first time)
- Uses Docker build minutes (usually sufficient on free tier)

---

### Solution 2: Use Alternative Hosting (Fallback)

If Docker on Render doesn't work, try these alternatives:

**Railway.app:**
- Similar to Render
- Better Rust/Cargo support
- Free tier available
- Use the existing `requirements.txt` (no Docker needed)

**Fly.io:**
- Good free tier
- Excellent Dockerfile support
- Deploy with: `fly launch` (uses Dockerfile automatically)

**Heroku:**
- Classic PaaS
- Good buildpack support
- Limited free tier

---

### Solution 3: Fix Current Buildpack Deployment (Complex)

If you must use the current buildpack approach:

1. **Create a custom buildpack** that pre-installs Rust with writable Cargo cache
2. **Use a pip index** that hosts pre-built tiktoken wheels
3. **Fork crewai** and remove tiktoken dependency

**This is NOT recommended** due to complexity and maintenance burden.

---

## Quick Start: Docker Deployment

```bash
# 1. Add Docker files (already created)
git add Dockerfile .dockerignore render-docker.yaml

# 2. Commit and push
git commit -m "Switch to Docker deployment to fix tiktoken build issue"
git push

# 3. In Render:
# - Delete existing service (Settings → Delete Service)
# - Create new service with Docker runtime
# - Use render-docker.yaml as blueprint (or manual setup)
# - Add GROQ_API_KEY environment variable
# - Deploy!
```

## Testing Docker Locally (Optional)

```bash
# Build Docker image
docker build -t enablemind-web .

# Run container
docker run -p 8000:8000 \
  -e GROQ_API_KEY="your_key" \
  -e LLM_PROVIDER="groq" \
  enablemind-web

# Test
curl http://localhost:8000/health
```

## Why tiktoken Fails on Render

1. **Rust compilation required**: tiktoken uses Rust extensions (via PyO3)
2. **Cargo needs write access**: Rust's package manager needs writable cache
3. **Render's filesystem**: Build environment has read-only cargo registry
4. **No wheels available**: PyPI doesn't have pre-built wheels for this platform/Python combo

## Why You Don't Need tiktoken

- tiktoken is for OpenAI's token counting
- You're using **Groq LLM**, not OpenAI
- CrewAI can work without tiktoken for Groq
- The dependency is transitive (not directly required)

## Recommendation

**Use Docker deployment (Solution 1)**. It's the cleanest, most maintainable solution that will work reliably on Render's free tier.

If you encounter any issues with Docker deployment, the next best option is **Railway.app** which handles these dependencies better.
