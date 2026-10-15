# Implementation Plan

## Objective

Demonstrate how independently running agents discover each other and exchange tasks using the A2A protocol, with a Google ADK coordinator and specialist agents implemented with different frameworks.

## Scope

### In scope
- Google ADK coordinator agent.
- LangGraph-based Order Agent.
- Plain-Python Payment Agent.
- Separate local ports.
- Agent Cards served at the well-known path.
- Registry-backed discovery at request time.
- A2A `message/send` requests and responses.
- Direct smoke test, logs, technical documentation, and presentation.

### Out of scope
- Real payment execution or production order-system integration.
- Public internet discovery.
- Enterprise identity provider / OAuth setup.
- Durable registry, multi-instance high availability, and production observability.
- Production readiness certification.

## Phases and acceptance criteria

1. **Design**
   - Confirm responsibilities, ports, discovery mechanism, and message flow.
   - Acceptance: architecture and sequence diagrams are documented.

2. **Specialist agents**
   - Implement Order Agent and Payment Agent as independent processes.
   - Acceptance: each exposes an Agent Card and handles an A2A request.

3. **Registry and coordinator**
   - Register IDs, capabilities, base URLs, and card URLs.
   - ADK tools discover registered agents and call them over A2A.
   - Acceptance: coordinator can locate an agent by capability and invoke it.

4. **Verification**
   - Run direct smoke tests without requiring an LLM.
   - Run an end-to-end request in ADK Web.
   - Acceptance: order and payment results are returned; failure cases are visible.

5. **Documentation and presentation**
   - Explain the distinction between registry, Agent Card, and A2A transport.
   - Include setup steps, demo script, known limitations, and next steps.
   - Acceptance: a teammate can set up the POC using the README.

## Port plan

| Service | Port | Purpose |
|---|---:|---|
| ADK coordinator UI | 8000 | User interaction |
| Order Agent | 8001 | A2A server |
| Payment Agent | 8002 | A2A server |

## Key design decision

The registry is a simple `registry.json` file for this local POC. This is intentional: it demonstrates discovery without requiring an additional registry server. A production registry could be backed by a database or service catalog and should enforce ownership, health checks, access policy, and trusted-card validation.
