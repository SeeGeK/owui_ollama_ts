

                "ollama_model": "qwen2.5-coder:7b-instruct",
                "show_orig_text": "false"
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




        user_message = body["messages"][-1]["content"]




        print(f"User message: {user_message}")




        # Translate user message
        translator = Translator(self.valves.ollama_url, self.valves.ollama_model)
        text_to_translate = user_message
        translated_user_message = translator.translate(text_to_translate, target_lang=self.valves.target_user)




        print(f"Translated user message: {translated_user_message}")




        body["messages"][-1]["content"] = translated_user_message
        return body




    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        print(f"outlet:{__name__}")




        messages = body["messages"]
        assistant_message = get_last_assistant_message(messages)




        print(f"Assistant message: {assistant_message}")




        # Translate assistant message
        translator = Translator(self.valves.ollama_url, self.valves.ollama_model)
        text_to_translate = assistant_message
        text_to_translate = text_to_translate.replace("\"", "-")
        translated_assistant_message = translator.translate(text_to_translate, target_lang=self.valves.target_assistant)
      
        print(f"Translated assistant message: {translated_assistant_message}")




        for message in reversed(messages):
            if message["role"] == "assistant":
                message["content"] = translated_assistant_message if not self.valves.show_orig_text else text_to_translate + "\n\n<translated>" + translated_assistant_message + "</<translated>>"
                break




        #body = {**body, "messages": messages}
        return body
