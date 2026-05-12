from intent_agent import Intent, IntentResult
from chat_agent import ChatAgent

# is this the best design pattern?

class Delegator:
    def __init__(self):
        pass

    def delegate(self, intent_json: IntentResult):
        
        match intent_json.intent:

            # for now, having everything being referred to chatagent
            case Intent.CHAT:
                return ChatAgent

            case Intent.MOTIVATION:
                return ChatAgent

            case Intent.CALENDAR_QUERY:
                return ChatAgent

            case Intent.SCHEDULE_TASK:
                return ChatAgent

            case Intent.ADD_GOAL:
                return ChatAgent

            case Intent.ADD_TASK:
                return ChatAgent

            case Intent.MARK_TASK_DONE:
                return ChatAgent

            case Intent.PLAN_DAY:
                return ChatAgent

            case Intent.REFLECT:
                return ChatAgent

            case Intent.CREATE_REMINDER:
                return ChatAgent

            case Intent.UPDATE_MEMORY:
                return ChatAgent

            case Intent.CANCEL_ACTION:
                return ChatAgent

            case Intent.APPROVAL_RESPONSE:
                return ChatAgent

            case Intent.UNKNOWN:
                return ChatAgent