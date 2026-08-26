import requests

def test_api():
    base_url = "http://localhost:8000"
    
    # Test Register
    print("Testing /register...")
    resp = requests.post(f"{base_url}/register", data={"name": "Test Candidate", "email": "test@example.com"})
    print(f"Status: {resp.status_code}, Body: {resp.json()}")
    assert resp.status_code == 200
    candidate_id = resp.json()["id"]
    
    # Test Interview Start
    print("Testing /interview/start...")
    resp = requests.post(f"{base_url}/interview/start?candidate_id={candidate_id}")
    print(f"Status: {resp.status_code}, Body: {resp.json()}")
    assert resp.status_code == 200
    
    print("\nAPI Test Passed!")

if __name__ == "__main__":
    try:
        test_api()
    except Exception as e:
        print(f"API Test Failed: {e}")
