"""Payment specialist: plain Python business logic exposed via A2A SDK."""
from __future__ import annotations

import json

from a2a.server.apps import A2AStarletteApplication
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2a.utils import new_agent_text_message


PAYMENTS = {
    "ORD-1001": {"payment_status": "PAID", "amount": 129.95, "currency": "USD"},
    "ORD-1002": {"payment_status": "PENDING", "amount": 74.50, "currency": "USD"},
}


def extract_order_id(text: str) -> str:
    for token in text.upper().replace(",", " ").replace(".", " ").split():
        if token.startswith("ORD-"):
            return token.strip()
    return ""


def lookup_payment(query: str) -> dict:
    order_id = extract_order_id(query)
    payment = PAYMENTS.get(order_id)
    if not payment:
        return {"order_id": order_id or None, "found": False, "message": "Payment record not found"}
    return {"order_id": order_id, "found": True, **payment}


class PaymentAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        query = context.get_user_input()
        result = lookup_payment(query)
        await event_queue.enqueue_event(new_agent_text_message(json.dumps(result)))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        await event_queue.enqueue_event(new_agent_text_message("Payment lookup cancelled."))


skill = AgentSkill(
    id="get_payment_status",
    name="Get Payment Status",
    description="Returns payment status and amount for a demo order ID.",
    tags=["payments", "invoice", "transaction"],
    examples=["Check payment for order ORD-1001"],
)
card = AgentCard(
    name="Payment Agent",
    description="An independent plain-Python agent for demo payment status lookups.",
    url="http://127.0.0.1:8002/",
    version="1.0.0",
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
    capabilities=AgentCapabilities(streaming=False),
    skills=[skill],
)
handler = DefaultRequestHandler(agent_executor=PaymentAgentExecutor(), task_store=InMemoryTaskStore())
app = A2AStarletteApplication(agent_card=card, http_handler=handler).build()
