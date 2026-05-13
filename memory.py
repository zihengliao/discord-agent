
from datetime import datetime
import json
from pprint import pprint


AGENT = "Master Oogway"


def handle_context(user_message):
    # fetching the last 3 most recent days worth of chat logs
    """
    Grabbing last 3 recent days of chat history
    """

    now = datetime.now()
    today = now.strftime("%d-%m-%Y")

    FILE_PATH = "./memory/chatlogs/"
    META_DATA_PATH = "./memory/chatlogs/meta_data.json"

    
    with open(META_DATA_PATH, "r", encoding="utf-8") as file:
        meta_data = json.load(file)

    logs = meta_data["logs"]

    sorted_logs = sorted(
        logs,
        key=lambda log: datetime.strptime(log["date"], "%d-%m-%Y"),
        reverse=True
    )

    recent_logs = sorted_logs[:3]

    # need to include what was just said into the chatlog files
    files_to_query = [log["date"] for log in recent_logs]

    write_user_message(user_message)

    chat_history = ""
    for file_to_open in files_to_query:
        with open(f"{FILE_PATH}{file_to_open}.txt", "r", encoding="utf-8") as file:
            chat_history += file.read()

    # include what was said today in the metadata
    if today not in files_to_query:
        meta_data["logs"].append({
            "date": today,
            "summary": ""
        })

        with open(META_DATA_PATH, "w", encoding="utf-8") as file:
            json.dump(meta_data, file, indent=4)

    return chat_history 


def write_bot_response(bot_message):
    now = datetime.now()
    today = now.strftime("%d-%m-%Y")

    FILE_PATH = "./memory/chatlogs/"

    with open(f"{FILE_PATH}{today}.txt", "a", encoding="utf-8") as file:
        file.write(f"{now}\n {AGENT}: {bot_message}\n")


def write_user_message(user_message):
    now = datetime.now()
    today = now.strftime("%d-%m-%Y")

    FILE_PATH = "./memory/chatlogs/"

    with open(f"{FILE_PATH}{today}.txt", "a", encoding="utf-8") as file:
        file.write(f"{now}\n User: {user_message}\n")