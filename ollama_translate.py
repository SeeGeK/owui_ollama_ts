from typing import List, Optional
from schemas import OpenAIChatMessage
from pydantic import BaseModel
import requests
import os
import json

from utils.pipelines.main import get_last_user_message, get_last_assistant_message

class Translator:
    def __init__(self, ollama_endpoint="http://127.0.0.1:11434/api/generate", ollama_model="phi4:latest"):
        self.ollama_endpoint = ollama_endpoint
        self.ollama_model = ollama_model
        
        # Системный промпт (только английская версия)
        self.system_prompt = """\
You act as a translator. \
You must translate the text into {target_lang}. \
Your answers should only contain the translation of the requested text. \
No explanations or comments are allowed. \
The text to be translated is enclosed in <text> tags. If the translated text contains symbols < or >, replace them with - (for example: <cctype> -> -cctype-). \
Please format it as Markdown when possible. \
The answer should not be enclosed in any tags!"""

    def translate(self, text, target_lang="russian"):
        """Переводит текст с помощью выбранной модели Ollama"""
        # Подготовка запроса
        req = {
            "model": self.ollama_model,
            "system": self.system_prompt.format(target_lang=target_lang),
            "prompt": f"<text>{text}</text>",
            "stream": False,
            "options": {
                "temperature": 0
            },
            "num_ctx": 512,
            "format": {
                "type": "object",
                "properties": {
                    "origin_lang": {
                        "type": "string",
                        "description": "The language of the original text"
                    },
                    "translated_text": {
                        "type": "string",
                        "description": "Translated text"
                    },
                    "translation_lang": {
                        "type": "string",
                        "description": "The language of the translated text"
                    }
                },
                "required": [
                    "origin_lang",
                    "translation_lang",
                    "translated_text"
                ]
            }
        }
        
        try:
            # Отправка запроса
            response = requests.post(self.ollama_endpoint, 
                                   json=req)
            response.raise_for_status()
            
            # Обработка ответа
            response_data = response.json()
            translated_text = response_data["response"]
            
            if isinstance(translated_text, str):
                return translated_text
            else:
                return translated_text.get("translated_text", "")
                
        except Exception as e:
            print(f"Error during translation: {e}")
            return None

class Pipeline:

    class Valves(BaseModel):
        # List target pipeline ids (models) that this filter will be connected to.
        # If you want to connect this filter to all pipelines, you can set pipelines to ["*"]
        # e.g. ["llama3:latest", "gpt-3.5-turbo"]
        pipelines: List[str] = []

        # Assign a priority level to the filter pipeline.
        # The priority level determines the order in which the filter pipelines are executed.
        # The lower the number, the higher the priority.
        priority: int = 0

        # Valves
        ollama_url: str
        ollama_model: str

        # Source languages
        # User message will be translated from source_user to target_user
        target_user: Optional[str] = "en"

        # Assistant languages
        # Assistant message will be translated from source_assistant to target_assistant
        target_assistant: Optional[str] = "ru"

    def __init__(self):
        # Pipeline filters are only compatible with Open WebUI
        # You can think of filter pipeline as a middleware that can be used to edit the form data before it is sent to the OpenAI API.
        self.type = "filter"

        # Optionally, you can set the id and name of the pipeline.
        # Best practice is to not specify the id so that it can be automatically inferred from the filename, so that users can install multiple versions of the same pipeline.
        # The identifier must be unique across all pipelines.
        # The identifier must be an alphanumeric string that can include underscores or hyphens. It cannot contain spaces, special characters, slashes, or backslashes.
        # self.id = "libretranslate_filter_pipeline"
        self.name = "OllamaTs Filter"

        # Initialize
        self.valves = self.Valves(
            **{
                "pipelines": ["*"],  # Connect to all pipelines
                "ollama_url": "http://localhost:11434/api/generate",
                "ollama_model": "qwen2.5-coder:7b-instruct"
            }
        )

        pass

    async def on_startup(self):
        # This function is called when the server is started.
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        # This function is called when the server is stopped.
        print(f"on_shutdown:{__name__}")
        pass

    async def on_valves_updated(self):
        # This function is called when the valves are updated.
        pass

    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        print(f"inlet:{__name__}")

        messages = body["messages"]
        user_message = get_last_user_message(messages)

        print(f"User message: {user_message}")

        # Translate user message
        translator = Translator(self.valves.ollama_url, self.valves.ollama_model)
        text_to_translate = user_message
        translated_user_message = translator.translate(text_to_translate, target_lang=self.valves.target_user)

        print(f"Translated user message: {translated_user_message}")

        for message in reversed(messages):
            if message["role"] == "user":
                message["content"] = translated_user_message
                break

        body = {**body, "messages": messages}
        return body

    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        print(f"outlet:{__name__}")

        messages = body["messages"]
        assistant_message = get_last_assistant_message(messages)

        print(f"Assistant message: {assistant_message}")

        # Translate assistant message
        translator = Translator(self.valves.ollama_url, self.valves.ollama_model)
        text_to_translate = assistant_message
        translated_assistant_message = translator.translate(text_to_translate, target_lang=self.valves.target_assistant)
      
        print(f"Translated assistant message: {translated_assistant_message}")

        for message in reversed(messages):
            if message["role"] == "assistant":
                message["content"] = translated_assistant_message
                break

        body = {**body, "messages": messages}
        return body