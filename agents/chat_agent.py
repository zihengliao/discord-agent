from .abstract_agent import AbstractAgent


class ChatAgent(AbstractAgent):
    def __init__(self, gemini_client, model):
        super().__init__(
            gemini_client = gemini_client,
            model = model
        )
        with open("./personality/oogway.md", "r", encoding="utf-8") as file:
            self.system_prompt = file.read()

    def respond(self, user_message):
        response = self.call_model(
            contents= f"{self.system_prompt} \n\n User message to you:{user_message}"
        )
    
        return response.text