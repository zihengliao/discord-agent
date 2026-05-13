from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, ValidationError
import json
from pprint import pprint

"""
The purpose of this agent is to classify the type of message and request being sent.

"""



class Intent(str, Enum):
    CHAT = "chat"
    MOTIVATION = "motivation"
    CALENDAR_QUERY = "calendar_query"
    SCHEDULE_TASK = "schedule_task"
    ADD_GOAL = "add_goal"
    ADD_TASK = "add_task"
    MARK_TASK_DONE = "mark_task_done"
    PLAN_DAY = "plan_day"
    REFLECT = "reflect"
    CREATE_REMINDER = "create_reminder"
    UPDATE_MEMORY = "update_memory"
    CANCEL_ACTION = "cancel_action"
    APPROVAL_RESPONSE = "approval_response"
    UNKNOWN = "unknown"

class IntentEntities(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_title: Optional[str] = None
    goal_title: Optional[str] = None
    date: Optional[str] = None
    time_preference: Optional[str] = None
    duration_minutes: Optional[int] = None
    reminder_text: Optional[str] = None
    completed_task: Optional[str] = None

class IntentResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: Intent
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)

    needs_calendar: bool = False
    needs_goal_memory: bool = False
    needs_task_memory: bool = False
    needs_operational_memory: bool = False
    needs_conversation_history: bool = False

    updates_goal_memory: bool = False
    updates_task_memory: bool = False
    updates_user_memory: bool = False
    updates_reflection_memory: bool = False

    requires_approval: bool = False
    needs_clarification: bool = False
    clarifying_question: Optional[str] = None

    entities: IntentEntities = Field(default_factory=IntentEntities)

class IntentAgent:

    def __init__(self, gemini_client, model):
        with open("intent.md", "r", encoding="utf-8") as file:
            self.prompt_intent = file.read()
        self.gemini_client = gemini_client
        self.model = model

    def define_intent(self, message):
        """
        Classifies a user message and returns a validated IntentResult.

        Returns
        -------
        IntentResult
            A Pydantic model representing the classified intent.

            On success, this will contain the model's validated classification.

            Example successful return:

                IntentResult(
                    intent=Intent.SCHEDULE_TASK,
                    confidence=0.94,
                    needs_calendar=True,
                    needs_goal_memory=True,
                    needs_task_memory=True,
                    needs_operational_memory=False,
                    needs_conversation_history=False,
                    updates_goal_memory=False,
                    updates_task_memory=False,
                    updates_user_memory=False,
                    updates_reflection_memory=False,
                    requires_approval=True,
                    needs_clarification=False,
                    clarifying_question=None,
                    entities=IntentEntities(
                        task_title="forecasting",
                        goal_title=None,
                        date="tomorrow",
                        time_preference="morning",
                        duration_minutes=60,
                        reminder_text=None,
                        completed_task=None
                    )
                )

            On failure, this will return a fallback result:

                IntentResult(
                    intent=Intent.UNKNOWN,
                    confidence=0.0,
                    needs_clarification=True,
                    clarifying_question="I couldn't parse the classifier output as JSON.",
                    entities=IntentEntities()
                )
    
    """
        
        #TODO: Need to handle 503 error from models
        response = self.gemini_client.models.generate_content(
            model=self.model,
            contents=f"""{self.prompt_intent}

        \n {message}"""
        )

        intent_json = self.validate_schema(response.text)
        pprint(f"Intent JSON {intent_json}")

        return intent_json

    def validate_schema(self, raw_model_output: str) -> IntentResult:
        """
        Validate a non-deterministic AI response to make sure it matches
        the expected intent classifier schema.

        If validation fails, return Intent.UNKNOWN so the orchestrator
        can ask a clarification instead of crashing.
        """

        try:
            cleaned_output = self._clean_json_output(raw_model_output)
            data = json.loads(cleaned_output)
            return IntentResult.model_validate(data)

        except json.JSONDecodeError as e:
            print("JSON parsing failed:")
            print(e)
            print("Raw model output:")
            print(raw_model_output)

            # TODO: chuck it back to gemini to regenerate the json if json is bad instead of deferring to user
            return self._fallback_unknown(
                "I couldn't parse the classifier output as JSON."
            )

        except ValidationError as e:
            print("Pydantic schema validation failed:")
            print(e)
            print("Raw model output:")
            print(raw_model_output)

            return self._fallback_unknown(
                "I couldn't classify that cleanly. What would you like me to do?"
            )

    def _fallback_unknown(self, question: str) -> IntentResult:
        return IntentResult(
            intent=Intent.UNKNOWN,
            confidence=0.0,
            needs_clarification=True,
            clarifying_question=question,
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

