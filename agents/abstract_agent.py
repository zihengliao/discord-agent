from abc import ABC, abstractmethod
from pathlib import Path
import requests



class AbstractAgent(ABC):
    def __init__(self, gemini_client, model: str):
        self.gemini_client = gemini_client
        self.model = model

    def call_model(self, contents: str):
        return self.gemini_client.models.generate_content(
            model=self.model,
            contents=contents
        )
        # response = requests.post(
        #     "http://localhost:11434/api/chat",
        #     json={
        #         "model": f"{self.model}",
        #         "messages": [
        #             {
        #                 "role": "system",
        #                 "content": (
        #                     f"{system_prompt}"
        #                 ),
        #             },
        #             {
        #                 "role": "user",
        #                 "content": f"{contents}",
        #             },
        #         ],
        #         "stream": False,
        #         "think": False,
        #         "options": {
        #             "temperature": 0.2,
        #             "num_predict": 1200,
        #             "repeat_penalty": 1.15,
        #         },
        #     },
        # )

        return response.text
    

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

    @abstractmethod
    def respond(self, user_message: str):
        pass