# Manager Demo Script (5–7 minutes)

## Opening (30 seconds)

"This POC demonstrates how independently deployed AI agents can discover one another and collaborate using A2A. The coordinator uses Google ADK, the order status specialist uses LangGraph, and the other specialists use plain Python."

## Demo 1: Show independent services (1 minute)

1. Start the Order server on port 8001 and Payment server on port 8002.
2. Open these URLs:
   - `http://127.0.0.1:8001/status/.well-known/agent-card.json`
   - `http://127.0.0.1:8001/delivery/.well-known/agent-card.json`
   - `http://127.0.0.1:8002/status/.well-known/agent-card.json`
   - `http://127.0.0.1:8002/amount/.well-known/agent-card.json`
3. Explain that each server process hosts two agents at separate paths, and each agent publishes its own capability description.

Talking point: "The card describes an agent; it does not by itself provide discovery."
Talking point: "The shared port is the same server process; the URL path selects which agent card and executor handles the request."

## Demo 2: Show the registry (45 seconds)

Open `registry.json`. Show that it maps four agent IDs and capabilities to their base URLs and card URLs, even though there are only two specialist server processes.

Talking point: "This is the discovery mechanism. Agent A reads this registry when it needs a capability rather than assuming all agent URLs are built into the LLM."

## Demo 3: Test the protocol directly (1 minute)

Run:

```powershell
python -m tests.smoke_test
```

Explain that this bypasses the LLM and verifies the A2A request/response path.

## Demo 4: End-to-end ADK interaction (2 minutes)

Open `http://127.0.0.1:8000`, select the coordinator, and ask:

> Check order ORD-1001 and tell me its payment status.

Expected facts:

- Order is shipped.
- Estimated delivery is 2026-10-14.
- Payment is paid.
- Amount is 129.95 USD.

Then ask about `ORD-1002` to show a different result.

Optionally ask: "When will ORD-1001 be delivered?" and "What is the payment amount for ORD-1001?" to exercise the two additional agents.

## Closing (45 seconds)

"The POC separates discovery, agent description, and communication. A registry locates the agents, Agent Cards advertise capabilities, and A2A carries requests and responses. Next steps for production would include authentication, trusted discovery, telemetry, robust error handling, and a persistent registry."

## If the LLM does not call tools

Ask explicitly: "Discover the order status agent and call it for ORD-1001, then discover the payment status agent and call it for ORD-1001." If the coordinator UI fails, run the direct smoke test to show protocol calls independently of the model.
