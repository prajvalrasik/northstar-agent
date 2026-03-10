"""Telegram interface for Northstar Agent."""

from __future__ import annotations

from collections.abc import Callable

from telegram import Update
from telegram.ext import Application, MessageHandler, filters

from northstar_agent.config import AppConfig
from northstar_agent.core.agent import NorthstarAgent
from northstar_agent.core.identity import build_thread_id


def _telegram_identity(update: Update) -> str:
    user = update.effective_user
    if user and user.username:
        return user.username
    return str(update.effective_chat.id)


def create_telegram_app(
    config: AppConfig,
    agent: NorthstarAgent,
    on_ready: Callable[[], None] | None = None,
) -> Application:
    """Build the Telegram polling application."""

    async def post_init(application: Application) -> None:
        del application
        await agent.setup()
        if on_ready:
            on_ready()

    async def handle_message(update: Update, context) -> None:
        del context
        if not update.message or not update.message.text:
            return

        user_message = update.message.text.strip()
        thread_id = build_thread_id(_telegram_identity(update))
        pending = agent.get_pending_approval(thread_id)

        if pending:
            decision = user_message.upper()
            if decision in {"YES", "NO"}:
                result = agent.resolve_approval(thread_id, decision)
                await update.message.reply_text(result)
                return

            await update.message.reply_text(
                "A destructive action is waiting for approval. Reply YES to allow it or NO to deny it."
            )
            return

        response_text = await agent.run_turn(thread_id, user_message)
        await update.message.reply_text(response_text)

    app = (
        Application.builder()
        .token(config.telegram_bot_token)
        .post_init(post_init)
        .build()
    )
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    return app
