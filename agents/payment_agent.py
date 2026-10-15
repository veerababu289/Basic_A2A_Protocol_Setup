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
from starlette.applications import Starlette
from starlette.routing import Mount


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


class PaymentAmountAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        result = lookup_payment(context.get_user_input())
        if result["found"]:
            result = {
                "order_id": result["order_id"],
                "found": True,
                "amount": result["amount"],
                "currency": result["currency"],
            }
        await event_queue.enqueue_event(new_agent_text_message(json.dumps(result)))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        await event_queue.enqueue_event(new_agent_text_message("Payment amount lookup cancelled."))


def build_agent_app(card: AgentCard, executor: AgentExecutor):
    handler = DefaultRequestHandler(agent_executor=executor, task_store=InMemoryTaskStore())
    return A2AStarletteApplication(agent_card=card, http_handler=handler).build()


payment_status_card = AgentCard(
    name="Payment Agent",
    description="An independent plain-Python agent for demo payment status lookups.",
    url="http://127.0.0.1:8002/status/",
    version="1.0.0",
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
    capabilities=AgentCapabilities(streaming=False),
    skills=[
        AgentSkill(
            id="get_payment_status",
            name="Get Payment Status",
            description="Returns payment status and amount for a demo order ID.",
            tags=["payments", "invoice", "transaction"],
            examples=["Check payment for order ORD-1001"],
        )
    ],
)
payment_amount_card = AgentCard(
    name="Payment Amount Agent",
    description="Returns the amount and currency for a demo order payment.",
    url="http://127.0.0.1:8002/amount/",
    version="1.0.0",
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
    capabilities=AgentCapabilities(streaming=False),
    skills=[
        AgentSkill(
            id="get_payment_amount",
            name="Get Payment Amount",
            description="Returns the amount and currency for a demo order ID.",
            tags=["payments", "amount", "currency"],
            examples=["What is the payment amount for ORD-1001?"],
        )
    ],
)

app = Starlette(
    routes=[
        Mount("/status", app=build_agent_app(payment_status_card, PaymentAgentExecutor())),
        Mount("/amount", app=build_agent_app(payment_amount_card, PaymentAmountAgentExecutor())),
    ]
)
