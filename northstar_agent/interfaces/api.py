"""FastAPI surface for Northstar Agent."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from northstar_agent.core import NorthstarAgent
from northstar_agent.core.identity import build_thread_id


class ChatRequest(BaseModel):
    """Incoming chat payload."""

    user_id: str
    message: str


class ApproveRequest(BaseModel):
    """Pending approval resolution payload."""

    user_id: str
    decision: str


def create_api(agent: NorthstarAgent) -> FastAPI:
    """Create the FastAPI app bound to a shared agent runtime."""

    api = FastAPI(title="Northstar Agent", version="1.0.0")

    @api.on_event("startup")
    async def startup() -> None:
        await agent.setup()

    @api.on_event("shutdown")
    async def shutdown() -> None:
        await agent.shutdown()

    @api.get("/health")
    async def health():
        return {"status": "ok", "service": "northstar-agent"}

    @api.post("/chat")
    async def chat(req: ChatRequest):
        thread_id = build_thread_id(req.user_id)
        response_text = await agent.run_turn(thread_id, req.message)
        return {
            "response": response_text,
            "pending_approval": agent.get_pending_approval(thread_id),
        }

    @api.post("/approve")
    async def approve(req: ApproveRequest):
        thread_id = build_thread_id(req.user_id)
        pending = agent.get_pending_approval(thread_id)
        if not pending:
            raise HTTPException(status_code=400, detail="No pending approval for this user.")

        result = agent.resolve_approval(thread_id, req.decision)
        return {"result": result, "pending_approval": agent.get_pending_approval(thread_id)}

    @api.get("/pending/{user_id}")
    async def pending(user_id: str):
        thread_id = build_thread_id(user_id)
        return {"pending_approval": agent.get_pending_approval(thread_id)}

    return api
