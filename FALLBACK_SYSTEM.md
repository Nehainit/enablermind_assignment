# 🚀 Automatic LLM Fallback System

## Overview

EnableMind now features an **intelligent fallback system** that automatically switches between multiple LLM providers when rate limits are hit. This ensures uninterrupted service even on free tiers!

## How It Works

### Fallback Chain

When you configure multiple API keys, the system creates an automatic fallback chain:

```
1. Groq Fast (llama-3.1-8b-instant)     ← PRIMARY (fastest, ~1000 tokens/sec)
   ↓ Rate limit hit
2. Groq Large (llama-3.3-70b-versatile) ← FALLBACK 1 (highest quality)
   ↓ Rate limit hit
3. Kimi (moonshot-v1-8k)                ← FALLBACK 2 (8k-128k context, great for complex research)
   ↓ Rate limit hit
4. Gemini Flash (gemini-1.5-flash)      ← FALLBACK 3 (free, reliable)
   ↓ Rate limit hit
5. OpenAI (gpt-4o-mini)                 ← FALLBACK 4 (paid, most reliable)
```

### Speed Comparison

| Model | Provider | Tokens/Sec | Quality | Context | Free Tier |
|-------|----------|------------|---------|---------|-----------|
| llama-3.1-8b-instant | Groq | ~1000 | Good | 128k | ✅ 14,400 req/day |
| llama-3.3-70b-versatile | Groq | ~300 | Excellent | 128k | ✅ 14,400 req/day |
| moonshot-v1-8k | Kimi/Moonshot | ~400 | Very Good | 8k-128k | 💰 Paid |
| gemini-1.5-flash | Google | ~200 | Very Good | 1M | ✅ 15 req/min |
| gpt-4o-mini | OpenAI | ~100 | Excellent | 128k | ❌ Paid only |

### Rate Limit Detection

The system automatically detects rate limit errors:
- HTTP 429 (Too Many Requests)
- "rate limit exceeded" messages
- "quota exceeded" messages
- "resource exhausted" messages

When detected, it instantly switches to the next provider in the fallback chain.

## Configuration

### For Maximum Reliability (Recommended)

Set **all three free tier API keys**:

```bash
# .env file
LLM_PROVIDER=groq

# Primary: Groq (FASTEST, recommended)
GROQ_API_KEY=your-groq-key-here
GROQ_MODEL=llama-3.1-8b-instant

# Backup 1: Gemini (FREE)
GEMINI_API_KEY=your-gemini-key-here

# Backup 2: OpenAI (Paid, optional)
OPENAI_API_KEY=your-openai-key-here
```

### For Speed (Single Provider)

Use only Groq with the fastest model:

```bash
LLM_PROVIDER=groq
GROQ_API_KEY=your-groq-key-here
GROQ_MODEL=llama-3.1-8b-instant
```

### For Quality (Single Provider)

Use the largest model:

```bash
LLM_PROVIDER=groq
GROQ_API_KEY=your-groq-key-here
GROQ_MODEL=llama-3.3-70b-versatile
```

## Getting Free API Keys

### 1. Groq (Recommended - Fastest)

1. Visit https://console.groq.com/
2. Sign up with email or GitHub
3. Go to "API Keys" section
4. Create new key
5. **Free Tier:** 14,400 requests/day + 60 requests/minute

### 2. Google Gemini (Backup)

1. Visit https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. **Free Tier:** 15 requests/minute

### 3. OpenAI (Optional Paid Backup)

1. Visit https://platform.openai.com/
2. Sign up and add payment method
3. Generate API key
4. **Pricing:** Pay per token (~$0.15-0.60 per 1M tokens)

## Deployment on Render

### Option 1: Multiple API Keys (Recommended)

In Render dashboard environment variables:

```
GROQ_API_KEY = your-groq-key
GEMINI_API_KEY = your-gemini-key
GROQ_MODEL = llama-3.1-8b-instant
```

### Option 2: Single API Key

```
GROQ_API_KEY = your-groq-key
GROQ_MODEL = llama-3.1-8b-instant
```

**Note:** Even with a single key, Groq provides 3 fallback models automatically!

## Usage Example

No code changes needed! The system handles fallbacks transparently:

```python
# User submits research request
"Explain Kubernetes networking"

# System automatically:
1. Tries llama-3.1-8b-instant (fastest)
   → Success! (typically 2-3 minutes)

# If rate limit hit:
2. Automatically switches to mixtral-8x7b-32768
   → Success! (typically 3-4 minutes)

# If still rate limited:
3. Falls back to llama-3.3-70b-versatile
   → Success! (typically 4-5 minutes)

# And so on...
```

## Monitoring

The system logs all fallback events:

```
INFO: using_llm_provider name=groq-fast model=llama-3.1-8b-instant
WARNING: rate_limit_detected error=429 Too Many Requests
WARNING: falling_back_to_next_provider from=groq-fast to=groq-medium
INFO: using_llm_provider name=groq-medium model=mixtral-8x7b-32768
INFO: research_complete provider=groq-medium duration=187s
```

## Benefits

### For Users
- **Faster research**: 3x faster with llama-3.1-8b-instant vs 70b model
- **More reliable**: Automatic fallback prevents failures
- **No downtime**: Seamless provider switching
- **Free tier friendly**: Maximizes free quota usage

### For Deployment
- **Production ready**: Handles rate limits gracefully
- **Cost effective**: Uses free tiers first, paid as last resort
- **Self-healing**: Automatically recovers from provider issues
- **Transparent**: No user intervention needed

## Testing Fallback Locally

```bash
# 1. Set up multiple providers
export GROQ_API_KEY="your-groq-key"
export GEMINI_API_KEY="your-gemini-key"

# 2. Start server
uvicorn web.app:app --reload

# 3. Submit multiple research requests quickly
# Watch logs for fallback messages

# 4. If rate limited, you'll see:
WARNING: rate_limit_detected
WARNING: falling_back_to_next_provider from=groq-fast to=groq-medium
```

## Architecture

### LLM Manager (`web/services/llm_manager.py`)

Singleton service that:
- Maintains ordered list of LLM providers
- Creates CrewAI LLM instances on demand
- Tracks current provider
- Handles fallback logic
- Logs all provider switches

### Research Runner Integration (`web/services/research_runner.py`)

- Wraps research execution with try/catch
- Detects rate limit errors
- Calls LLM manager for fallback
- Retries with new provider
- Updates job progress with provider info

### Zero Code Changes Needed

The fallback system works automatically:
- ✅ Existing agents unchanged
- ✅ Existing tasks unchanged
- ✅ Existing prompts unchanged
- ✅ Only configuration changed

## Troubleshooting

### "No LLM providers available"

**Cause:** No API keys set

**Fix:** Set at least one API key:
```bash
export GROQ_API_KEY="your-key"
```

### "All X providers failed"

**Cause:** All providers hit rate limits or have errors

**Fix:**
1. Wait 1 minute for rate limits to reset
2. Add more API keys for more fallbacks
3. Check API key validity

### Slow performance

**Cause:** Using slow model

**Fix:** Set faster model:
```bash
export GROQ_MODEL="llama-3.1-8b-instant"
```

### Rate limits hit frequently

**Cause:** High traffic on single API key

**Fix:**
1. Add multiple API keys (Groq + Gemini)
2. Both providers = 2x capacity
3. Consider upgrading to paid tier

## Future Enhancements

- [ ] Load balancing across providers (round-robin)
- [ ] Per-provider rate limit tracking
- [ ] Automatic provider health checks
- [ ] User-configurable fallback order
- [ ] Provider performance metrics dashboard
- [ ] Cost tracking per provider

---

## Summary

**The fallback system makes EnableMind:**
1. **3x faster** with llama-3.1-8b-instant
2. **More reliable** with automatic fallbacks
3. **Free tier friendly** using Groq + Gemini
4. **Production ready** with graceful degradation

**Recommended Setup:**
```bash
GROQ_API_KEY=xxx        # Primary (free, fast)
GEMINI_API_KEY=yyy      # Backup (free, reliable)
GROQ_MODEL=llama-3.1-8b-instant
```

This gives you **5 automatic fallbacks** and ~30,000 free requests per day! 🚀
