"""Test script to verify Groq models are available."""

import os
from crewai import LLM

# Get Groq API key from environment
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    print("❌ GROQ_API_KEY not set in environment")
    exit(1)

# Models to test
models_to_test = [
    ("DeepSeek-R1-Distill", "deepseek-r1-distill-llama-70b"),
    ("Kimi K2", "moonshotai/kimi-k2-instruct"),
    ("Llama 3.1 8B Instant", "llama-3.1-8b-instant"),
    ("Llama 3.1 70B Versatile", "llama-3.1-70b-versatile"),
    ("Llama 3.3 70B Versatile", "llama-3.3-70b-versatile"),
]

print("Testing Groq models...\n")
print("=" * 60)

working_models = []
failed_models = []

for name, model_id in models_to_test:
    print(f"\nTesting {name} ({model_id})...")
    try:
        # Create LLM instance
        llm = LLM(
            model=model_id,
            api_key=groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )

        # Try a simple completion
        response = llm.call(["Say 'OK' if you can read this"])

        print(f"✅ {name}: WORKING")
        print(f"   Response: {response[:100]}...")
        working_models.append((name, model_id))

    except Exception as e:
        error_msg = str(e)
        print(f"❌ {name}: FAILED")
        print(f"   Error: {error_msg[:150]}...")
        failed_models.append((name, model_id, error_msg))

print("\n" + "=" * 60)
print("\nSUMMARY:")
print(f"✅ Working models: {len(working_models)}/{len(models_to_test)}")
print(f"❌ Failed models: {len(failed_models)}/{len(models_to_test)}")

if working_models:
    print("\n✅ WORKING MODELS:")
    for name, model_id in working_models:
        print(f"   - {name}: {model_id}")

if failed_models:
    print("\n❌ FAILED MODELS:")
    for name, model_id, error in failed_models:
        print(f"   - {name}: {model_id}")
        print(f"     Error: {error[:100]}...")

print("\n" + "=" * 60)
