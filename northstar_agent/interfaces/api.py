"""FastAPI surface for Northstar Agent."""

from __future__ import annotations

import asyncio
import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from northstar_agent.core.identity import build_thread_id
from northstar_agent.core.agent import NorthstarAgent
from northstar_agent.interfaces.dashboard import render_dashboard_html


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

    @api.get("/", response_class=HTMLResponse)
    async def dashboard():
        return HTMLResponse(
            render_dashboard_html(),
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )

    @api.get("/dashboard", response_class=HTMLResponse)
    async def dashboard_alias():
        return HTMLResponse(
            render_dashboard_html(),
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )

    @api.get("/activity")
    async def activity(limit: int = 50):
        return {"events": agent.recent_activity(limit=limit)}

    @api.get("/events")
    async def events():
        """Server-Sent Events stream — pushes a ping every 2s and an activity snapshot on each new event."""

        async def generate():
            last_fingerprint = ""
            while True:
                current = agent.recent_activity(limit=50)
                fingerprint = json.dumps(current[-1], sort_keys=True) if current else ""
                if fingerprint != last_fingerprint:
                    last_fingerprint = fingerprint
                    payload = json.dumps({"events": current})
                    yield f"data: {payload}\n\n"
                else:
                    yield ": ping\n\n"
                await asyncio.sleep(2)

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    @api.get("/memories")
    async def memories():
        return {"memories": agent.list_memories()}

    @api.get("/pending")
    async def pending_all():
        return {"pending_approvals": agent.list_pending_approvals()}

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
