"""Unified entrypoint for Northstar Agent."""

from __future__ import annotations

import asyncio
import threading

import uvicorn

from northstar_agent.config import load_config
from northstar_agent.core import NorthstarAgent
from northstar_agent.interfaces.api import create_api
from northstar_agent.interfaces.telegram_bot import create_telegram_app


def main() -> None:
    """Start the configured Northstar Agent runtime."""

    config = load_config()
    config.validate_for_runtime()

    agent = NorthstarAgent(config)
    api = create_api(agent)

    if config.mode == "http":
        uvicorn.run(api, host=config.host, port=config.port, log_level="info")
        return

    server = None

    def start_http_server() -> None:
        nonlocal server
        if server is not None:
            return

        server = uvicorn.Server(
            uvicorn.Config(api, host=config.host, port=config.port, log_level="info")
        )
        threading.Thread(target=server.run, daemon=True).start()

    telegram_app = create_telegram_app(
        config,
        agent,
        on_ready=start_http_server if config.mode == "both" else None,
    )

    try:
        telegram_app.run_polling()
    finally:
        if server is not None:
            server.should_exit = True
        asyncio.run(agent.shutdown())


if __name__ == "__main__":
    main()
