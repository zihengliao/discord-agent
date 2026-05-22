from __future__ import annotations

from typing import Any, Callable

from agents.intent_agent import Intent, IntentResult
from memory import (
    get_operational_memory,
    get_recent_turns,
    get_goal_memory,
)


CONTEXT_BY_INTENT: dict[Intent, set[str]] = {
    Intent.CHAT: set(),
    Intent.MOTIVATION: {"goal_tasks"},
    Intent.CALENDAR_QUERY: set(),
    Intent.SCHEDULE_TASK: {"goal_tasks"},
    Intent.ADD_GOAL: {"goal_tasks"},
    Intent.ADD_TASK: {"goal_tasks"},
    Intent.MARK_TASK_DONE: {"goal_tasks"},
    Intent.GOAL_TASK_QUERY: {"goal_tasks"},
    Intent.PLAN_DAY: {"goal_tasks"},
    Intent.REFLECT: {"goal_tasks"},
    Intent.CREATE_REMINDER: set(),
    Intent.UPDATE_MEMORY: set(),
    Intent.CANCEL_ACTION: {"operational"},
    Intent.APPROVAL_RESPONSE: {"operational"},
    Intent.UNKNOWN: set(),
}

FOLLOW_UP_TERMS = {
    "yes",
    "yep",
    "yeah",
    "no",
    "nah",
    "that",
    "it",
    "same one",
    "do it",
    "cancel that",
}


def get_context_types(intent_result: IntentResult, message: str) -> set[str]:
    types = set(CONTEXT_BY_INTENT[intent_result.intent])
    lowered = message.strip().lower()

    if _contains_follow_up(lowered):
        types.add("recent_turns")

    if intent_result.intent in {Intent.APPROVAL_RESPONSE, Intent.CANCEL_ACTION}:
        types.update({"operational", "recent_turns"})

    return types


def load_context(
    types: set[str],
    loaders: dict[str, Callable[[], Any]] | None = None,
) -> dict[str, Any]:
    loaders = loaders or {
        "goal_tasks": get_goal_memory,
        "recent_turns": get_recent_turns,
        "operational": get_operational_memory,
    }
    return {
        context_type: loader()
        for context_type, loader in loaders.items()
        if context_type in types
    }


def format_context_for_prompt(context: dict[str, Any]) -> str:
    labels = {
        "goal_tasks": "Goal/task memory",
        "recent_turns": "Recent turns",
        "operational": "Operational memory",
    }
    sections = [
        f"{labels[context_type]}:\n{value}"
        for context_type, value in context.items()
        if value
    ]
    return "\n\n".join(sections)


def _contains_follow_up(message: str) -> bool:
    return any(term == message or f" {term} " in f" {message} " for term in FOLLOW_UP_TERMS)
