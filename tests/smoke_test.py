"""Direct A2A smoke test; run after starting the specialist services."""
import json
import sys
import uuid

import httpx


def call(base_url: str, message: str) -> dict:
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message/send",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "parts": [{"type": "text", "text": message}],
            }
        },
    }
    with httpx.Client(timeout=10.0) as client:
        card = client.get(base_url.rstrip("/") + "/.well-known/agent-card.json")
        card.raise_for_status()
        print(f"Agent Card: {card.json().get('name')}")
        response = client.post(base_url.rstrip("/") + "/", json=payload)
        response.raise_for_status()
        body = response.json()
        if "error" in body:
            raise RuntimeError(body["error"])
        return body


def main() -> int:
    for base_url, message in [
        ("http://127.0.0.1:8001", "Check order ORD-1001"),
        ("http://127.0.0.1:8002", "Check payment for order ORD-1001"),
    ]:
        print(f"\nCalling {base_url}")
        result = call(base_url, message)
        print(json.dumps(result, indent=2))
    print("\nSmoke test completed. Inspect results above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
