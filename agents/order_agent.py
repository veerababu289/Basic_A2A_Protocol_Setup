"""Order specialist: LangGraph business workflow exposed via A2A SDK."""
from __future__ import annotations

import json
from typing import TypedDict

from a2a.server.apps import A2AStarletteApplication
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from a2a.utils import new_agent_text_message
from langgraph.graph import END, START, StateGraph


class OrderState(TypedDict):
    query: str
    order_id: str
    result: str


ORDERS = {
    "ORD-1001": {"status": "SHIPPED", "estimated_delivery": "2026-10-14"},
    "ORD-1002": {"status": "PROCESSING", "estimated_delivery": "2026-10-17"},
}


def parse_order_id(text: str) -> str:
    for token in text.upper().replace(",", " ").replace(".", " ").split():
        if token.startswith("ORD-"):
            return token.strip()
    return ""


def lookup_order(state: OrderState) -> OrderState:
    order_id = state["order_id"]
    order = ORDERS.get(order_id)
    if not order:
        result = json.dumps({"order_id": order_id or None, "found": False, "message": "Order not found"})
    else:
        result = json.dumps({"order_id": order_id, "found": True, **order})
    return {**state, "result": result}


graph = StateGraph(OrderState)
graph.add_node("lookup_order", lookup_order)
graph.add_edge(START, "lookup_order")
graph.add_edge("lookup_order", END)
order_workflow = graph.compile()


class OrderAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        query = context.get_user_input()
        order_id = parse_order_id(query)
        result = order_workflow.invoke({"query": query, "order_id": order_id, "result": ""})
        await event_queue.enqueue_event(new_agent_text_message(result["result"]))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        await event_queue.enqueue_event(new_agent_text_message("Order lookup cancelled."))


skill = AgentSkill(
    id="get_order_status",
    name="Get Order Status",
    description="Returns the status and estimated delivery date for a demo order ID.",
    tags=["orders", "shipping", "delivery"],
    examples=["Check order ORD-1001"],
)
card = AgentCard(
    name="Order Management Agent",
    description="An independent LangGraph-based agent for order status lookups.",
    url="http://127.0.0.1:8001/",
    version="1.0.0",
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
    capabilities=AgentCapabilities(streaming=False),
    skills=[skill],
)
handler = DefaultRequestHandler(agent_executor=OrderAgentExecutor(), task_store=InMemoryTaskStore())
app = A2AStarletteApplication(agent_card=card, http_handler=handler).build()
