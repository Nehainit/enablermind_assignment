"""End-to-end test of the research system."""

import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"

print("Testing EnableMind End-to-End\n" + "="*60)

# 1. Check health
print("\n1. Checking health...")
response = requests.get(f"{BASE_URL}/health")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

# 2. Submit research
print("\n2. Submitting research...")
data = {
    "topic": "difference between FastAPI and Flask",
    "max_iterations": "1"
}
response = requests.post(f"{BASE_URL}/research", data=data, allow_redirects=False)
print(f"   Status: {response.status_code}")

if response.status_code == 303:
    job_url = response.headers.get("Location")
    job_id = job_url.split("/")[-1]
    print(f"   Job ID: {job_id}")
    print(f"   Job URL: {job_url}")

    # 3. Poll for completion
    print("\n3. Waiting for research to complete...")
    max_wait = 180  # 3 minutes
    start_time = time.time()

    while time.time() - start_time < max_wait:
        response = requests.get(f"{BASE_URL}/api/job/{job_id}/status")
        if "completed" in response.text.lower():
            print("   ✅ Research completed!")
            break
        elif "failed" in response.text.lower():
            print("   ❌ Research failed!")
            print(f"   Response: {response.text[:500]}")
            break
        else:
            elapsed = int(time.time() - start_time)
            print(f"   ⏳ Still running... ({elapsed}s)")
            time.sleep(5)

    # 4. Check final status
    print("\n4. Final status check...")
    response = requests.get(f"{BASE_URL}/job/{job_id}")
    if response.status_code == 200:
        if "Download" in response.text:
            print("   ✅ SUCCESS - Download buttons found!")
        elif "Failed" in response.text:
            print("   ❌ FAILED - Error in response")
            # Extract error message
            if "Research Failed" in response.text:
                start = response.text.find("Research Failed")
                error_section = response.text[start:start+500]
                print(f"   Error: {error_section}")
        else:
            print("   ⏳ Still processing...")
    else:
        print(f"   Status: {response.status_code}")

print("\n" + "="*60)
