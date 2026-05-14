from agents.intent_agent import Intent, IntentResult
from agents.chat_agent import ChatAgent
from agents.goal_task_agent import GoalTaskAgent

# is this the best design pattern?

class Delegator:
    def __init__(self, gemini_client, model):
        self.client = gemini_client
        self.model = model

    def delegate(self, intent_json: IntentResult):
        
        match intent_json.intent:

            #TODO: low key should have an abstract class for all this
            case Intent.CHAT:
                return ChatAgent(self.client, self.model)

            case Intent.MOTIVATION:
                return ChatAgent(self.client, self.model)

            case Intent.CALENDAR_QUERY:
                return ChatAgent(self.client, self.model)

            case Intent.SCHEDULE_TASK:
                return ChatAgent(self.client, self.model)

            case Intent.ADD_GOAL:
                return GoalTaskAgent(self.client, self.model, intent_json)

            case Intent.ADD_TASK:
                return GoalTaskAgent(self.client, self.model, intent_json)

            case Intent.MARK_TASK_DONE:
                return GoalTaskAgent(self.client, self.model, intent_json)
            
            case Intent.GOAL_TASK_QUERY:
                return GoalTaskAgent(self.client, self.model, intent_json)

            case Intent.PLAN_DAY:
                return ChatAgent(self.client, self.model)

            case Intent.REFLECT:
                return ChatAgent(self.client, self.model)

            case Intent.CREATE_REMINDER:
                return ChatAgent(self.client, self.model)

            case Intent.UPDATE_MEMORY:
                return ChatAgent(self.client, self.model)

            case Intent.CANCEL_ACTION:
                return ChatAgent(self.client, self.model)

            case Intent.APPROVAL_RESPONSE:
                return ChatAgent(self.client, self.model)

            case Intent.UNKNOWN:
                return ChatAgent(self.client, self.model)