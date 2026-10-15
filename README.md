# Distributed A2A Agent Communication POC

A local demonstration of **agent discovery + Agent Cards + A2A calls** with independently running services.

## What this POC demonstrates

- **Coordinator:** Google ADK agent (port `8000`) with tools to discover agents from a registry and call them.
- **Order server:** one process on port `8001` hosts two A2A agents: Order Management and Order Delivery.
- **Payment server:** one process on port `8002` hosts two A2A agents: Payment Status and Payment Amount.
- **A2A transport:** each mounted agent has its own Agent Card URL and accepts A2A `message/send` JSON-RPC requests.
- **Registry:** `registry.json` maps capabilities to agent base URLs. The coordinator reads it at request time; it does not assume it knows every agent in advance.

> POC scope: the registry is a local JSON file and the demo data is mocked. This is for local learning/demo only, not production security or payment processing.

## Architecture

```mermaid
flowchart TD
    U[User / ADK Web UI :8000] --> C[Google ADK Coordinator]
    C --> R[Agent Registry: registry.json]
    C -->|A2A :8001/status/| O[Order Management Agent]
    C -->|A2A :8001/delivery/| D[Order Delivery Agent]
    C -->|A2A :8002/status/| P[Payment Agent]
    C -->|A2A :8002/amount/| A[Payment Amount Agent]
    O --> LG[LangGraph workflow]
    D --> DB1[Demo order data]
    P --> PY1[Plain Python payment lookup]
    A --> PY2[Plain Python payment lookup]
```

## Prerequisites

- Python 3.11 or 3.12
- A Google AI API key if using Gemini through Google ADK
- Internet access during dependency installation

## Setup (PowerShell)

From this directory:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `GOOGLE_API_KEY`. Do not commit `.env`.

## Start the services

Open **four terminals** in the project root. Activate the virtual environment in each terminal.

**Terminal 1 — Order server (port 8001; hosts two agents)**

```powershell
uvicorn agents.order_agent:app --host 127.0.0.1 --port 8001
```

**Terminal 2 — Payment server (port 8002; hosts two agents)**

```powershell
uvicorn agents.payment_agent:app --host 127.0.0.1 --port 8002
```

**Terminal 3 — Coordinator UI (port 8000)**

```powershell
adk web coordinator --port 8000
```

**Terminal 4 — health / card checks**

```powershell
Invoke-RestMethod http://127.0.0.1:8001/status/.well-known/agent-card.json
Invoke-RestMethod http://127.0.0.1:8001/delivery/.well-known/agent-card.json
Invoke-RestMethod http://127.0.0.1:8002/status/.well-known/agent-card.json
Invoke-RestMethod http://127.0.0.1:8002/amount/.well-known/agent-card.json
Invoke-RestMethod http://127.0.0.1:8000
```

Open `http://127.0.0.1:8000`, select `coordinator`, and ask:

> Check order ORD-1001 and tell me its payment status.

Expected demo data:

- Order `ORD-1001`: shipped, estimated delivery `2026-10-14`
- Payment `ORD-1001`: paid, amount `129.95 USD`

Try `ORD-1002` too to see a different result.

You can also ask for one specialist capability at a time, for example:

- “When will ORD-1001 be delivered?” — Order Delivery Agent
- “What is the payment amount for ORD-1001?” — Payment Amount Agent

## Verify direct A2A calls without the LLM

Run the built-in smoke test after starting the Order and Payment agents:

```powershell
python -m tests.smoke_test
```

This reads all four agents from the registry, fetches each Agent Card, and calls each A2A `message/send` endpoint directly. It validates connectivity/protocol shape independently of the coordinator's model.

## How discovery works

1. Each mounted agent serves its own card at `<agent-path>/.well-known/agent-card.json`.
2. `registry.json` stores agent names, capabilities, and base URLs.
3. The coordinator's `discover_agents` tool reads the registry when invoked.
4. The coordinator selects an agent based on its capability.
5. `call_agent` sends an A2A JSON-RPC `message/send` request to the selected endpoint.
6. The result is returned to the coordinator, which summarizes it for the user.

Each server process mounts two independent A2A applications under separate URL paths. Each mounted application has its own executor, task store, and Agent Card; the shared port does not mean the agents share an identity. The registry is deliberately a separate concept from Agent Cards: **the registry helps find agents; the card describes an agent; A2A carries the request and response.**

## Troubleshooting

- **`GOOGLE_API_KEY` missing:** set it in `.env`, then restart `adk web`.
- **Port already in use:** change the port and update the matching URL in `registry.json`.
- **Card loads but call fails:** check that the card's `url`, mounted path, and registry `base_url` match.
- **Dependency/API mismatch:** this POC uses the A2A Python SDK 0.3.x API family for a compact teaching implementation. The current A2A project recommends targeting SDK 1.x for new production integrations; see the references and migration note in `docs/TECHNICAL_DESIGN.md`.
- **Model doesn't call tools:** ask explicitly to “discover the order agent and call it for ORD-1001,” then inspect the coordinator tool instructions and logs.

## Files

- `docs/IMPLEMENTATION_PLAN.md` — phases and acceptance criteria
- `docs/TECHNICAL_DESIGN.md` — architecture and protocol flow
- `docs/DEMO_SCRIPT.md` — manager demonstration script
- `docs/PRESENTATION_OUTLINE.md` — slide-by-slide talking points
- `coordinator/agent.py` — Google ADK coordinator and tools
- `agents/order_agent.py` — two separately mounted order agents wrapped in A2A
- `agents/payment_agent.py` — two separately mounted payment agents wrapped in A2A
- `registry.json` — simple capability registry
- `tests/smoke_test.py` — direct protocol smoke test
