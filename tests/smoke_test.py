"""Direct A2A smoke test; run after starting the specialist services."""
import json
import sys
import uuid
from pathlib import Path

import httpx


def call(agent: dict, message: str) -> dict:
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
        card = client.get(agent["card_url"])
        card.raise_for_status()
        card_data = card.json()
        if card_data.get("name") != agent["name"]:
            raise RuntimeError(f"Unexpected Agent Card name for {agent['id']}")
        if card_data.get("url", "").rstrip("/") != agent["base_url"].rstrip("/"):
            raise RuntimeError(f"Agent Card endpoint does not match registry for {agent['id']}")
        print(f"Agent Card: {card_data['name']}")
        print(f"Agent Card details...: {json.dumps(card_data, indent=2)}")
        response = client.post(agent["base_url"], json=payload)
        response.raise_for_status()
        body = response.json()
        # print(f"Agent Response: {json.dumps(body, indent=2)}")
        if "error" in body:
            raise RuntimeError(body["error"])
        return body


def main() -> int:
    registry_path = Path(__file__).resolve().parents[1] / "registry.json"
    agents = json.loads(registry_path.read_text(encoding="utf-8"))["agents"]
    messages = {
        "order-agent": "Check order ORD-1001",
        "order-delivery-agent": "When will ORD-1001 be delivered?",
        "payment-agent": "Check payment for order ORD-1001",
        "payment-amount-agent": "What is the payment amount for ORD-1001?",
    }
    for agent in agents:
        print(f"\nCalling {agent['id']} at {agent['base_url']}")
        result = call(agent, messages[agent["id"]])
        print(json.dumps(result, indent=2))
    print("\nSmoke test completed. Inspect results above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
