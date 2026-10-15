# A2A Protocol and POC Demo Deck

The detailed, 21-slide presentation is [A2A-Protocol-Detailed-Demo.pptx](../A2A-Protocol-Detailed-Demo.pptx).

## Talk track

1. Introduce the goal: explain A2A and demonstrate the local multi-agent POC.
2. Distinguish registry (find), Agent Card (describe), and A2A (communicate).
3. Explain that MCP and A2A are complementary: A2A delegates between agents; MCP gives an AI application access to tools, resources, and prompts. This POC uses A2A and ADK function tools, not an MCP server.
4. Describe A2A Message vs Task, and distinguish `messageId`, `taskId`, and `contextId`.
5. Note the POC’s limits: it sends one `message/send` request at a time and does not explicitly manage task/context follow-ups, streaming, or task polling. The project pins the A2A SDK 0.3.x family; consult version-matched docs when comparing exact wire formats.
6. Show the topology: coordinator on port 8000, two specialist server processes on ports 8001 and 8002, with two mounted A2A agents per specialist process.
7. Inspect the four Agent Cards at their per-agent `/.well-known/agent-card.json` URLs and compare each card’s advertised endpoint with `registry.json`.
8. Follow the coordinator-to-specialist request flow and inspect the `message/send` JSON-RPC shape.
9. Start the services, run `python -m tests.smoke_test`, then test order, delivery, payment, amount, combined requests, unknown orders, and a stopped specialist server.

## Test prompts

- “Check order ORD-1001.” Expected: shipped; estimated delivery 2026-10-14.
- “Check order ORD-1002.” Expected: processing; estimated delivery 2026-10-17.
- “When will ORD-1001 be delivered?” Expected: 2026-10-14.
- “Check payment for ORD-1002.” Expected: pending; 74.50 USD.
- “What is the payment amount for ORD-1001?” Expected: 129.95 USD.
- “Check order ORD-1001 and tell me its payment status.” Expected: order and payment specialist results combined.
- “Find order and payment details for ORD-9999.” Expected: not found; no fabricated details.

## Official references

- [A2A specification](https://a2a-protocol.org/latest/specification/)
- [A2A task lifecycle](https://a2a-protocol.org/latest/topics/life-of-a-task/)
- [A2A Agent Card discovery](https://a2a-protocol.org/latest/topics/agent-discovery/)
- [MCP architecture](https://modelcontextprotocol.io/docs/learn/architecture)
