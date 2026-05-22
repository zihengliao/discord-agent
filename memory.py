from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any


AGENT = "Master Oogway"
CHATLOG_DIR = Path("./memory/chatlogs")
CHATLOG_METADATA_PATH = CHATLOG_DIR / "meta_data.json"
GOALS_PATH = Path("./memory/goals/goals.json")
OPERATIONAL_PATH = Path("./memory/operational/state.json")


def _today() -> str:
    return datetime.now().strftime("%d-%m-%Y")


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default

    text = path.read_text(encoding="utf-8").strip()
    return json.loads(text) if text else default


def _ensure_daily_log_entry(date: str) -> None:
    metadata = _read_json(CHATLOG_METADATA_PATH, {"logs": []})
    if any(log["date"] == date for log in metadata["logs"]):
        return

    metadata["logs"].append({"date": date, "summary": ""})
    CHATLOG_DIR.mkdir(parents=True, exist_ok=True)
    CHATLOG_METADATA_PATH.write_text(json.dumps(metadata, indent=4), encoding="utf-8")


def write_user_message(user_message: str) -> None:
    now = datetime.now()
    today = _today()
    CHATLOG_DIR.mkdir(parents=True, exist_ok=True)
    _ensure_daily_log_entry(today)

    with open(CHATLOG_DIR / f"{today}.txt", "a", encoding="utf-8") as file:
        file.write(f"{now}\n User: {user_message}\n")


def write_bot_response(bot_message: str) -> None:
    now = datetime.now()
    today = _today()
    CHATLOG_DIR.mkdir(parents=True, exist_ok=True)
    _ensure_daily_log_entry(today)

    with open(CHATLOG_DIR / f"{today}.txt", "a", encoding="utf-8") as file:
        file.write(f"{now}\n {AGENT}: {bot_message}\n")


def get_recent_turns(limit: int = 4) -> list[dict[str, str]]:
    #  It returns up to 4 recent turns, shaped like:
    #   [
    #       {
    #           "date": "22-05-2026",
    #           "speaker": "User",
    #           "content": "schedule forecasting tonight"
    #       },
    #       {
    #           "date": "22-05-2026",
    #           "speaker": "Master Oogway",
    #           "content": "Do you want me to block 90 minutes?"
    #       }
    #   ]

    metadata = _read_json(CHATLOG_METADATA_PATH, {"logs": []})
    dated_logs = sorted(
        metadata["logs"],
        key=lambda log: datetime.strptime(log["date"], "%d-%m-%Y"),
    )

    turns: list[dict[str, str]] = []
    for log in dated_logs:
        path = CHATLOG_DIR / f"{log['date']}.txt"
        if not path.exists():
            continue

        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        for index in range(1, len(lines), 2):
            speaker, _, content = lines[index].partition(":")
            turns.append(
                {
                    "date": log["date"],
                    "speaker": speaker.strip(),
                    "content": content.strip(),
                }
            )

    return turns[-limit:]


def get_goal_memory() -> dict[str, Any]:
    return _read_json(GOALS_PATH, {"goals": [], "standalone_tasks": []})


def get_task_memory() -> dict[str, Any]:
    return get_goal_memory()


def get_operational_memory() -> dict[str, Any]:
    return _read_json(OPERATIONAL_PATH, {})
