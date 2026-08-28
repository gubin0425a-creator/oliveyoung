import sys
import requests
import json
import time

try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

base_url = "http://127.0.0.1:5000"

def test_endpoints():
    print("Testing /health...")
    try:
        r = requests.get(f"{base_url}/health", timeout=5)
        print("Health Response:", r.status_code, r.json())
    except Exception as e:
        print("Health check failed:", e)

    print("\nTesting /api/user/me...")
    try:
        r = requests.get(f"{base_url}/api/user/me", timeout=5)
        print("User Me Response:", r.status_code, r.json())
    except Exception as e:
        print("User Me failed:", e)

    print("\nTesting /api/shortform/generate...")
    try:
        r = requests.post(f"{base_url}/api/shortform/generate", json={"topic": "올리브영 인기 세럼", "category": "뷰티"}, timeout=5)
        print("Shortform Response:", r.status_code, r.json().get('title'))
    except Exception as e:
        print("Shortform failed:", e)

    print("\nTesting /v1/chat/completions (Smart Demo Mode)...")
    try:
        r = requests.post(f"{base_url}/v1/chat/completions", json={
            "model": "paw-ai-studio",
            "messages": [{"role": "user", "content": "구독자 10만~50만 뷰티 유튜버 추천해줘"}]
        }, timeout=10)
        print("Chat Response:", r.status_code, r.json()['choices'][0]['message']['content'][:100] + "...")
    except Exception as e:
        print("Chat failed:", e)

    print("\nTesting /api/billing/recharge...")
    try:
        r = requests.post(f"{base_url}/api/billing/recharge", json={"amount": 50}, timeout=5)
        print("Recharge Response:", r.status_code, r.json())
    except Exception as e:
        print("Recharge failed:", e)

if __name__ == '__main__':
    test_endpoints()
