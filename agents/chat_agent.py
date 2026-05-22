from .abstract_agent import AbstractAgent
from context_flow import format_context_for_prompt


class ChatAgent(AbstractAgent):
    def __init__(self, gemini_client, model):
        super().__init__(
            gemini_client = gemini_client,
            model = model
        )
        with open("./personality/oogway.md", "r", encoding="utf-8") as file:
            self.system_prompt = file.read()

    def respond(self, user_message: str, context: dict | None = None):
        prompt_context = format_context_for_prompt(context or {})
        response = self.call_model(
            contents=(
                f"{self.system_prompt}\n\n"
                f"{prompt_context}\n\n"
                f"User message to you:{user_message}"
            )
        )
    
        return response.text
