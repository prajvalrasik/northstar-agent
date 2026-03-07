"""Northstar Agent runtime, memory, and graph orchestration."""

from __future__ import annotations

import asyncio
from pathlib import Path

import aiosqlite
from langchain_core.messages import HumanMessage, RemoveMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, START, MessagesState, StateGraph

from northstar_agent.config import AppConfig
from northstar_agent.core.memory import (
    load_all_memories,
    save_memory_entry,
    search_memories,
)
from northstar_agent.tools.registry import ToolRuntime, build_workspace_tools


class AgentState(MessagesState):
    """Graph state with rolling summary support."""

    summary: str


class NorthstarAgent:
    """Shared runtime used by the HTTP API and Telegram interface."""

    def __init__(self, config: AppConfig):
        self.config = config
        self.identity_prompt = self._load_prompt("identity.md")
        self.tools_prompt = self._load_prompt("tools.md")
        self.runtime = ToolRuntime(
            workspace_dir=config.workspace_dir,
            approvals_file=config.approvals_file,
        )
        self.graph = None
        self.conn: aiosqlite.Connection | None = None
        self.llm: ChatOpenAI | None = None
        self.llm_with_tools = None
        self._setup_lock = asyncio.Lock()

    def _load_prompt(self, name: str) -> str:
        prompt_path = Path(__file__).resolve().parents[1] / "prompts" / name
        return prompt_path.read_text(encoding="utf-8").strip()

    def _system_prompt(self, summary: str = "") -> str:
        prompt_parts = [
            self.identity_prompt,
            self.tools_prompt,
            f"## Workspace Root\nAll file operations are sandboxed to: `{self.config.workspace_dir}`",
            (
                "## Long-Term Memory\n"
                "You can store durable project or user facts with `save_memory` and "
                "retrieve them later with `memory_search`."
            ),
        ]

        long_term_memory = load_all_memories(self.config.memory_dir)
        if long_term_memory:
            prompt_parts.append("[Long-term memory]\n" + long_term_memory)

        if summary:
            prompt_parts.append("[Earlier in this session]\n" + summary)

        return "\n\n".join(prompt_parts)

    def _build_tools(self):
        workspace_tools = build_workspace_tools(self.runtime)

        @tool
        def save_memory(key: str, content: str) -> str:
            """Save durable project context or user preferences to long-term memory."""

            stored_key = save_memory_entry(self.config.memory_dir, key, content)
            return f"Saved to long-term memory as '{stored_key}'."

        @tool
        def memory_search(query: str) -> str:
            """Search the long-term memory store for saved facts."""

            return search_memories(self.config.memory_dir, query)

        return workspace_tools + [save_memory, memory_search]

    async def setup(self) -> None:
        """Initialize the graph and persistence once per process."""

        async with self._setup_lock:
            if self.graph is not None:
                return

            self.config.ensure_directories()
            self.conn = await aiosqlite.connect(self.config.sessions_db)
            checkpointer = AsyncSqliteSaver(self.conn)

            all_tools = self._build_tools()
            self.llm = ChatOpenAI(
                model=self.config.model_name,
                max_tokens=1024,
                api_key=self.config.openai_api_key,
            )
            self.llm_with_tools = self.llm.bind_tools(all_tools)

            builder = StateGraph(AgentState)
            builder.add_node("call_model", self.call_model)
            builder.add_node("tools", self.runtime.tool_node(all_tools))
            builder.add_node("summarize", self.summarize_conversation)
            builder.add_edge(START, "call_model")
            builder.add_conditional_edges("call_model", self.route_after_model)
            builder.add_edge("tools", "call_model")
            builder.add_edge("summarize", END)

            self.graph = builder.compile(checkpointer=checkpointer)

    async def shutdown(self) -> None:
        """Close the SQLite connection when the process stops."""

        if self.conn is not None:
            await self.conn.close()
            self.conn = None

    async def call_model(self, state: AgentState):
        """Core LLM node with summary and long-term memory injection."""

        system_prompt = self._system_prompt(state.get("summary", ""))
        messages = [{"role": "system", "content": system_prompt}] + state["messages"]
        response = await self.llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    async def summarize_conversation(self, state: AgentState):
        """Compact older messages into the rolling session summary."""

        summary = state.get("summary", "")
        if summary:
            summary_prompt = (
                f"Here is the running summary so far:\n{summary}\n\n"
                "Extend it using the conversation above."
            )
        else:
            summary_prompt = "Create a concise working summary of the conversation above."

        response = await self.llm.ainvoke(
            state["messages"] + [HumanMessage(content=summary_prompt)]
        )
        delete_messages = [RemoveMessage(id=message.id) for message in state["messages"][:-2]]
        return {"summary": response.content, "messages": delete_messages}

    def route_after_model(self, state: AgentState):
        """Route to tools, summarization, or finish the turn."""

        messages = state["messages"]
        last_message = messages[-1]

        if getattr(last_message, "tool_calls", None):
            return "tools"

        if len(messages) >= self.config.summary_threshold:
            return "summarize"

        return END

    async def run_turn(self, thread_id: str, user_message: str) -> str:
        """Process one user message through the shared graph."""

        await self.setup()
        self.runtime.set_current_thread_id(thread_id)

        response = await self.graph.ainvoke(
            {"messages": [{"role": "user", "content": user_message}]},
            {"configurable": {"thread_id": thread_id}},
        )
        return response["messages"][-1].content

    def get_pending_approval(self, thread_id: str):
        """Return pending approval metadata for a thread, if any."""

        return self.runtime.get_pending(thread_id)

    def resolve_approval(self, thread_id: str, decision: str) -> str:
        """Approve or deny a pending action for a thread."""

        return self.runtime.resolve_pending(thread_id, decision)
