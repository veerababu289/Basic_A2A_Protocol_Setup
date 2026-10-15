"""Google ADK coordinator that discovers and calls remote agents over A2A."""
from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from google.adk.agents import Agent

load_dotenv()
ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registry.json"
MODEL = os.getenv("ADK_MODEL", "gemini-3.8-flash")


def discover_agents(capability: str = "") -> dict[str, Any]:
    """Find registered agents, optionally filtering by a capability.

    Args:
        capability: Optional capability identifier, e.g. get_order_status.
    """
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    agents = registry.get("agents", [])
    if capability:
        agents = [a for a in agents if capability in a.get("capabilities", [])]
    return {
        "count": len(agents),
        "agents": [
            {
                "id": a["id"],
                "name": a["name"],
                "description": a["description"],
                "capabilities": a["capabilities"],
                "card_url": a["card_url"],
                "base_url": a["base_url"],
            }
            for a in agents
        ],
    }


def call_agent(agent_id: str, message: str) -> dict[str, Any]:
    """Send an A2A message/send JSON-RPC request to a registered agent.

    Args:
        agent_id: Registry ID such as order-agent or payment-amount-agent.
        message: Natural-language task for the remote agent.
    """
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    match = next((a for a in registry["agents"] if a["id"] == agent_id), None)
    if not match:
        return {"ok": False, "error": f"Unknown agent_id: {agent_id}"}

    # Verify the card is reachable and read it at call time. This demonstrates
    # card discovery separately from the registry's endpoint lookup.
    try:
        with httpx.Client(timeout=10.0) as client:
            card_response = client.get(match["card_url"])
            card_response.raise_for_status()
            card = card_response.json()

            # POC allowlist: require card URL to match the registry's expected base.
            if card.get("url", "").rstrip("/") != match["base_url"].rstrip("/"):
                return {"ok": False, "error": "Agent Card URL does not match registry allowlist"}

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
            response = client.post(match["base_url"], json=payload)
            response.raise_for_status()
            result = response.json()
            if "error" in result:
                return {"ok": False, "agent": match["name"], "error": result["error"]}
            return {
                "ok": True,
                "agent": card.get("name", match["name"]),
                "card_skills": card.get("skills", []),
                "a2a_response": result.get("result", result),
            }
    except httpx.HTTPError as exc:
        return {"ok": False, "agent": match["name"], "error": f"HTTP/A2A call failed: {exc}"}
    except (ValueError, KeyError) as exc:
        return {"ok": False, "agent": match["name"], "error": f"Invalid registry/card/response: {exc}"}


root_agent = Agent(
    name="a2a_coordinator",
    model=MODEL,
    description="Coordinates work across independent agents discovered through a registry.",
    instruction=(
        "You are an enterprise coordinator agent. For requests about order status, first use "
        "discover_agents with capability get_order_status and call order-agent. For delivery "
        "estimates, discover get_estimated_delivery and call order-delivery-agent. For payment "
        "status, discover get_payment_status and call payment-agent. For payment amount or currency, "
        "discover get_payment_amount and call payment-amount-agent. If a user asks for multiple "
        "kinds of information, discover and call each relevant specialist, then combine only the "
        "returned facts. Never invent results. Explain that discovery uses a registry and each "
        "agent's Agent Card, while requests use A2A message/send. If a tool returns an error, report "
        "it clearly."
    ),
    tools=[discover_agents, call_agent],
)
