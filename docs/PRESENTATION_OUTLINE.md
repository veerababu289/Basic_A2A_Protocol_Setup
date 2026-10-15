# Presentation Outline: Distributed A2A Agent Communication

## Slide 1 — Title
**Distributed AI Agents: Discovery and A2A Communication**
- Google ADK coordinator
- LangGraph Order Agent
- Plain-Python Payment Agent
- Local multi-service proof of concept

Speaker note: This is a protocol and architecture demo, not a production payment system.

## Slide 2 — Problem
Independent agents may run on different servers, use different frameworks, and be owned by different teams.
- Agents do not automatically know other agents exist.
- Hardcoding every URL does not scale well.
- Different implementations need a shared communication contract.

## Slide 3 — The three building blocks
- **Registry:** locates agents by ID/capability.
- **Agent Card:** describes agent identity, endpoint, and skills.
- **A2A:** carries the request and response.
Key message: discovery, description, and communication are distinct.

## Slide 4 — Architecture
User → Google ADK Coordinator → Registry lookup → A2A calls → Order Agent / Payment Agent.
- Order Agent internal implementation: LangGraph.
- Payment Agent internal implementation: plain Python.
- Both use the same A2A boundary.

## Slide 5 — Live request flow
1. User asks about order and payment.
2. Coordinator discovers the order capability.
3. Coordinator fetches the Agent Card.
4. Coordinator sends A2A `message/send`.
5. It repeats for payment.
6. Coordinator summarizes returned facts.

## Slide 6 — What the POC proves
- Separate processes and ports.
- Framework-independent communication boundary.
- Registry-backed discovery.
- Agent Cards accessible over HTTP.
- A2A request/response and smoke test.

## Slide 7 — Limitations and next steps
- Local JSON registry and mock business data.
- No production authentication or TLS.
- Migrate the teaching implementation to the current A2A SDK 1.x API.
- Add signed/trusted cards, service authentication, health checks, tracing, retries, and persistent registry.
