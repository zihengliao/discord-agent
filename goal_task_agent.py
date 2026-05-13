
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, ValidationError
import json
from pprint import pprint
from datetime import datetime

"""
The purpose of this agent is to decide what should happen to the user's
goal/task memory.

This agent does not directly edit the markdown file.

It returns a structured GoalTaskResult object, and the backend should use that
object to update goals_tasks.md safely.
"""

import json
from pathlib import Path
from datetime import datetime


GOAL_TASKS_FILE_PATH = Path("./memory/goals/goals.json")


def today_str() -> str:
    return datetime.now().strftime("%d/%m/%Y")


def load_goals_data() -> dict:
    default_data = {
        "goals": [],
        "standalone_tasks": []
    }

    if not GOAL_TASKS_FILE_PATH.exists():
        return default_data
    
    text = GOAL_TASKS_FILE_PATH.read_text(encoding="utf-8").strip()

    if not text:
        return default_data

    with open(GOAL_TASKS_FILE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_goals_data(data: dict) -> None:
    with open(GOAL_TASKS_FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def generate_next_goal_id(data: dict) -> str:
    existing_numbers = []

    for goal in data["goals"]:
        goal_id = goal["id"]  # e.g. goal_001
        number = int(goal_id.split("_")[1])
        existing_numbers.append(number)

    next_number = max(existing_numbers, default=0) + 1
    return f"goal_{next_number:03d}"


def generate_next_task_id(data: dict) -> str:
    existing_numbers = []

    for goal in data["goals"]:
        for task in goal.get("tasks", []):
            task_id = task["id"]
            number = int(task_id.split("_")[1])
            existing_numbers.append(number)

    for task in data["standalone_tasks"]:
        task_id = task["id"]
        number = int(task_id.split("_")[1])
        existing_numbers.append(number)

    next_number = max(existing_numbers, default=0) + 1
    return f"task_{next_number:03d}"


class GoalTaskAction(str, Enum):
    ADD_GOAL = "add_goal"
    ADD_TASK = "add_task"
    ADD_STANDALONE_TASK = "add_standalone_task"
    MARK_GOAL_COMPLETE = "mark_goal_complete"
    MARK_TASK_COMPLETE = "mark_task_complete"
    LIST_GOALS = "list_goals"
    LIST_TASKS = "list_tasks"
    PRIORITISE_TASKS = "prioritise_tasks"
    CLARIFY = "clarify"
    NO_ACTION = "no_action"


class GoalPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: Optional[str] = None
    title: Optional[str] = None
    due: Optional[str] = None
    priority: Optional[str] = None


class TaskPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: Optional[str] = None
    title: Optional[str] = None
    goal_id: Optional[str] = None
    due: Optional[str] = None
    effort: Optional[int] = None
    priority: Optional[str] = None
    category: Optional[str] = None


class GoalTaskResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: GoalTaskAction
    requires_clarification: bool = False
    clarifying_question: Optional[str] = None

    goal: GoalPayload = Field(default_factory=GoalPayload)
    task: TaskPayload = Field(default_factory=TaskPayload)

    matched_goal_id: Optional[str] = None
    matched_task_id: Optional[str] = None

    response: str = ""


class GoalTaskAgent:

    def __init__(self, gemini_client, model, intent):
        PROMPT_FILE_PATH = "./prompts/goal_task_prompt.md"

        with open(PROMPT_FILE_PATH, "r", encoding="utf-8") as file:
            self.prompt_goal_task = file.read()

        # TODO: separate the goal_task files into goals and tasks

        self.goals_tasks_json = load_goals_data()

        self.gemini_client = gemini_client
        self.model = model
        self.intent_result = intent

    def respond(self, user_message):

        """
        Example of JSON file structure:
        
        {
            "goals": [
                {
                "id": "goal_001",
                "title": "Build Discord accountability agent",
                "status": "active",
                "due": "01/06/2026",
                "priority": "high",
                "created_at": "13/05/2026",
                "completed_at": null,
                "tasks": [
                    {
                    "id": "task_001",
                    "title": "Build intent classifier",
                    "status": "completed",
                    "due": null,
                    "effort": 60,
                    "priority": "high",
                    "category": "project",
                    "created_at": "10/05/2026",
                    "completed_at": "12/05/2026"
                    },
                    {
                    "id": "task_002",
                    "title": "Build goal/task memory",
                    "status": "open",
                    "due": "14/05/2026",
                    "effort": 90,
                    "priority": "high",
                    "category": "project",
                    "created_at": "13/05/2026",
                    "completed_at": null
                    },
                    {
                    "id": "task_003",
                    "title": "Add operational memory for approvals",
                    "status": "open",
                    "due": null,
                    "effort": 60,
                    "priority": "medium",
                    "category": "project",
                    "created_at": "13/05/2026",
                    "completed_at": null
                    }
                ]
                },
                {
                "id": "goal_002",
                "title": "Run a marathon at a 4 minute pace",
                "status": "active",
                "due": null,
                "priority": "medium",
                "created_at": "13/05/2026",
                "completed_at": null,
                "tasks": []
                }
            ],
            "standalone_tasks": [
                {
                "id": "task_004",
                "title": "Do the dishes",
                "status": "open",
                "due": "13/05/2026",
                "effort": 15,
                "priority": "low",
                "category": "life admin",
                "created_at": "13/05/2026",
                "completed_at": null
                },
                {
                "id": "task_005",
                "title": "Buy groceries",
                "status": "open",
                "due": "14/05/2026",
                "effort": 30,
                "priority": "medium",
                "category": "errands",
                "created_at": "13/05/2026",
                "completed_at": null
                }
            ]
        }"""

        action_result = self.decide_action(user_message)
        action = action_result.action

        data = self.goals_tasks_json

        if action == GoalTaskAction.ADD_GOAL:
            new_goal = {
                "id": generate_next_goal_id(data),
                "title": action_result.goal.title,
                "status": "active",
                "due": action_result.goal.due,
                "priority": action_result.goal.priority or "medium",
                "created_at": today_str(),
                "completed_at": None,
                "tasks": []
            }

            data["goals"].append(new_goal)
            save_goals_data(data)
            return f"Added goal: {new_goal['title']}."

        if action == GoalTaskAction.ADD_TASK:
            goal_id = action_result.task.goal_id
            target_goal = None

            for goal in data["goals"]:
                if goal["id"] == goal_id:
                    target_goal = goal
                    break

            if target_goal is None:
                return f"I couldn't find the goal with id {goal_id}."

            new_task = {
                "id": generate_next_task_id(data),
                "title": action_result.task.title,
                "status": "open",
                "due": action_result.task.due,
                "effort": action_result.task.effort,
                "priority": action_result.task.priority or "medium",
                "category": action_result.task.category or "project",
                "created_at": today_str(),
                "completed_at": None
            }

            target_goal["tasks"].append(new_task)
            save_goals_data(data)
            return f"Added task: {new_task['title']}."

        if action == GoalTaskAction.ADD_STANDALONE_TASK:
            new_task = {
                "id": generate_next_task_id(data),
                "title": action_result.task.title,
                "status": "open",
                "due": action_result.task.due,
                "effort": action_result.task.effort,
                "priority": action_result.task.priority or "medium",
                "category": action_result.task.category or "other",
                "created_at": today_str(),
                "completed_at": None
            }

            data["standalone_tasks"].append(new_task)
            save_goals_data(data)
            return f"Added standalone task: {new_task['title']}."

        if action == GoalTaskAction.MARK_GOAL_COMPLETE:
            goal_id = action_result.matched_goal_id

            for goal in data["goals"]:
                if goal["id"] == goal_id:
                    goal["status"] = "completed"
                    goal["completed_at"] = today_str()
                    save_goals_data(data)
                    return f"Marked goal complete: {goal['title']}."

            return f"I couldn't find goal {goal_id}."

        if action == GoalTaskAction.MARK_TASK_COMPLETE:
            task_id = action_result.matched_task_id

            for goal in data["goals"]:
                for task in goal.get("tasks", []):
                    if task["id"] == task_id:
                        task["status"] = "completed"
                        task["completed_at"] = today_str()
                        save_goals_data(data)
                        return f"Marked task complete: {task['title']}."

            for task in data["standalone_tasks"]:
                if task["id"] == task_id:
                    task["status"] = "completed"
                    task["completed_at"] = today_str()
                    save_goals_data(data)
                    return f"Marked task complete: {task['title']}."

            return f"I couldn't find task {task_id}."

        if action == GoalTaskAction.CLARIFY:
            return action_result.clarifying_question or "Can you clarify what you want me to do?"

        if action == GoalTaskAction.NO_ACTION:
            return action_result.response or "No action taken."

        if action == GoalTaskAction.LIST_GOALS:
            active_goals = [goal for goal in data["goals"] if goal["status"] == "active"]

            if not active_goals:
                return "You do not have any active goals."

            return "\n".join([f"- {goal['title']}" for goal in active_goals])

        if action == GoalTaskAction.LIST_TASKS:
            open_tasks = []

            for goal in data["goals"]:
                for task in goal.get("tasks", []):
                    if task["status"] == "open":
                        open_tasks.append(f"- {task['title']} ({goal['title']})")

            for task in data["standalone_tasks"]:
                if task["status"] == "open":
                    open_tasks.append(f"- {task['title']}")

            if not open_tasks:
                return "You do not have any open tasks."

            return "\n".join(open_tasks)

        if action == GoalTaskAction.PRIORITISE_TASKS:
            return action_result.response

        return "I couldn't apply that goal/task action."


    def decide_action(self, message: str) -> GoalTaskResult:
        """
        Decides what goal/task action should be performed.

        Returns:
            GoalTaskResult: A validated Pydantic object containing:
                - action: what the backend should do
                - goal/task payloads
                - matched goal/task IDs
                - clarification flags
                - response text

        This method does not edit the markdown file directly.
        """

        now = datetime.now()
        today = now.strftime("%d-%m-%Y")

        response = self.gemini_client.models.generate_content(
            model=self.model,
            contents=f"""
                {self.prompt_goal_task}

                Today:
                {today}

                User message:
                {message}

                Intent result:
                {self.intent_result.model_dump_json()}

                Current goals/tasks markdown:
                {self.goals_tasks_json}

                Return valid JSON only.
                Do not include markdown.
                Do not include explanations.
                """
        )

        goal_task_json = self.validate_schema(response.text)
        pprint(f"GoalTask JSON {goal_task_json}")

        return goal_task_json

    def validate_schema(self, raw_model_output: str) -> GoalTaskResult:
        """
        Validates the AI model output against the GoalTaskResult schema.

        If validation fails, returns a safe clarification result.
        """

        try:
            cleaned_output = self._clean_json_output(raw_model_output)
            data = json.loads(cleaned_output)
            return GoalTaskResult.model_validate(data)

        except json.JSONDecodeError as e:
            print("JSON parsing failed:")
            print(e)
            print("Raw model output:")
            print(raw_model_output)

            return self._fallback_clarify(
                "I couldn't parse the goal/task action as JSON."
            )

        except ValidationError as e:
            print("Pydantic schema validation failed:")
            print(e)
            print("Raw model output:")
            print(raw_model_output)

            return self._fallback_clarify(
                "I couldn't decide the goal/task action cleanly."
            )

    def _fallback_clarify(self, question: str) -> GoalTaskResult:
        return GoalTaskResult(
            action=GoalTaskAction.CLARIFY,
            requires_clarification=True,
            clarifying_question=question,
            response=question,
        )

    def _clean_json_output(self, text: str) -> str:
        """
        Handles cases where the model accidentally wraps JSON in markdown fences.

        Example:
        ```json
        { ... }
        ```
        """

        text = text.strip()

        if text.startswith("```json"):
            text = text.removeprefix("```json").strip()

        if text.startswith("```"):
            text = text.removeprefix("```").strip()

        if text.endswith("```"):
            text = text.removesuffix("```").strip()

        return text