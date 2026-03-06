#!/usr/bin/env python3
"""Simple integration test for EnableMind Web UI."""

import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8001"

def test_health_check():
    """Test health endpoint."""
    print("Testing health check...", end=" ")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✓")

def test_homepage():
    """Test homepage loads."""
    print("Testing homepage...", end=" ")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "EnableMind" in response.text
    assert "Start Research" in response.text
    print("✓")

def test_form_validation():
    """Test form validation."""
    print("Testing form validation...", end=" ")

    # Test empty topic (FastAPI returns 422 for validation errors)
    response = requests.post(
        f"{BASE_URL}/research",
        data={"topic": "", "max_iterations": "3"},
        allow_redirects=False
    )
    assert response.status_code in [400, 422]  # 422 = Unprocessable Entity

    # Test invalid max_iterations
    response = requests.post(
        f"{BASE_URL}/research",
        data={"topic": "Test topic", "max_iterations": "10"},
        allow_redirects=False
    )
    assert response.status_code in [400, 422]

    print("✓")

def test_job_creation():
    """Test creating a research job."""
    print("Testing job creation...", end=" ")

    # Submit valid research request
    response = requests.post(
        f"{BASE_URL}/research",
        data={"topic": "Test research topic", "max_iterations": "1"},
        allow_redirects=False
    )
    assert response.status_code == 303  # See Other redirect
    assert "Location" in response.headers

    # Extract job_id from redirect URL
    location = response.headers["Location"]
    assert "/job/" in location
    job_id = location.split("/job/")[1]

    print(f"✓ (Job ID: {job_id[:8]}...)")
    return job_id

def test_job_status_page(job_id):
    """Test job status page loads."""
    print("Testing job status page...", end=" ")

    response = requests.get(f"{BASE_URL}/job/{job_id}")
    assert response.status_code == 200
    assert job_id in response.text
    assert "Test research topic" in response.text

    print("✓")

def test_job_status_api(job_id):
    """Test job status API endpoint."""
    print("Testing job status API...", end=" ")

    response = requests.get(f"{BASE_URL}/api/job/{job_id}/status")
    assert response.status_code == 200
    # Should return HTML fragment
    assert "progress" in response.text.lower() or "pending" in response.text.lower()

    print("✓")

def test_invalid_job():
    """Test accessing non-existent job."""
    print("Testing invalid job handling...", end=" ")

    response = requests.get(f"{BASE_URL}/job/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404

    print("✓")

def main():
    """Run all tests."""
    print("=" * 60)
    print("EnableMind Web UI Integration Tests")
    print("=" * 60)
    print()

    try:
        # Basic tests
        test_health_check()
        test_homepage()
        test_form_validation()
        test_invalid_job()

        # Job workflow tests
        job_id = test_job_creation()
        test_job_status_page(job_id)
        test_job_status_api(job_id)

        print()
        print("=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to server. Make sure it's running on port 8001")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
