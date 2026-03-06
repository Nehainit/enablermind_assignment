"""Simple test to verify Groq models using OpenAI client."""

import os
from openai import OpenAI

# Get Groq API key
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    print("❌ GROQ_API_KEY not set")
    exit(1)

# Create OpenAI client for Groq
client = OpenAI(
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1"
)

# Models to test
models = [
    ("DeepSeek-R1-Distill", "deepseek-r1-distill-llama-70b"),
    ("Kimi K2", "moonshotai/kimi-k2-instruct"),
    ("Llama 3.1 8B", "llama-3.1-8b-instant"),
    ("Llama 3.1 70B", "llama-3.1-70b-versatile"),
    ("Llama 3.3 70B", "llama-3.3-70b-versatile"),
]

print("Testing Groq Models\n" + "="*60)

working = []
failed = []

for name, model_id in models:
    print(f"\n{name} ({model_id})...", end=" ")
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": "Say OK"}],
            max_tokens=5
        )
        print("✅ WORKS")
        working.append((name, model_id))
    except Exception as e:
        error = str(e)
        print(f"❌ FAILED")
        print(f"  Error: {error[:100]}")
        failed.append((name, model_id))

print("\n" + "="*60)
print(f"\n✅ Working: {len(working)}/{len(models)}")
print(f"❌ Failed: {len(failed)}/{len(models)}")

if working:
    print("\n✅ VERIFIED MODELS:")
    for name, model_id in working:
        print(f"   • {model_id}")
