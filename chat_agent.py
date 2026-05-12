



class ChatAgent:
    def __init__(self, gemini_client, model):
        self.gemini_client = gemini_client
        self.model = model

        with open("./personality/obama.md", "r", encoding="utf-8") as file:
            self.system_prompt = file.read()

    def respond(self, user_message):
        response = self.gemini_client.models.generate_content(
            model=self.model,
            contents= f"{self.system_prompt} \n\n User message to you:{user_message}"
        )
    
        return response.text