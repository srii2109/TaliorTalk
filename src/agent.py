import os
import json
from google import genai
from google.genai import types
from src.searcher import SareeSearchEngine


class SareeAgent:
    def __init__(self, api_key: str, search_engine: SareeSearchEngine):
        self.api_key = api_key
        self.search_engine = search_engine
        self.client = genai.Client(api_key=api_key)

        self.system_instruction = (
            "You are TailorTalk, a warm and knowledgeable AI fashion assistant specializing in Indian sarees. "
            "You help users discover sarees from a curated catalogue of 649 unique designs based on style, weave, print, borders, fabric, and colors.\n\n"
            "Capabilities:\n"
            "1. Casual conversation: Talk about sarees, Indian textiles, drape styles, fabrics (silk, cotton, georgette, organza), weaves, and styling advice.\n"
            "2. Visual Search: Find visually similar sarees using the 'search_similar_sarees' tool when users describe what they want or upload an image.\n\n"
            "Rules:\n"
            "- Always call 'search_similar_sarees' when a user asks to find, show, or discover sarees.\n"
            "- If the user uploaded an image (path: 'data/temp_query.jpg'), use it as image_url_or_path.\n"
            "- Respond warmly and describe the results in a friendly, fashionable tone.\n"
            "- Never mention FAISS, CLIP, or vector databases to users."
        )

        self.search_tool = types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name="search_similar_sarees",
                    description="Search the saree catalogue for visually or semantically similar sarees based on text description or image.",
                    parameters=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "query_text": types.Schema(
                                type=types.Type.STRING,
                                description="Text description of the saree to find (e.g. 'pink silk saree with gold border'). Optional if image provided."
                            ),
                            "image_url_or_path": types.Schema(
                                type=types.Type.STRING,
                                description="Local path to uploaded saree image. Use 'data/temp_query.jpg' if user uploaded an image."
                            ),
                            "limit": types.Schema(
                                type=types.Type.INTEGER,
                                description="Maximum number of matches to return. Default is 6."
                            ),
                        },
                        required=[]
                    )
                )
            ]
        )

    def _execute_search(self, query_text=None, image_url_or_path=None, limit=6):
        try:
            results = self.search_engine.search(
                query_image=image_url_or_path,
                query_text=query_text,
                top_k=limit
            )
            if not results:
                return "No matching sarees found.", []
            formatted = []
            for idx, r in enumerate(results):
                name = r.get('name', r['filename'])
                formatted.append(
                    f"Match {idx+1}: '{name}', Score: {r['score']:.2f} "
                    f"(Style: {r['clip_score']:.2f}, Color: {r['color_score']:.2f})"
                )
            return "\n".join(formatted), results
        except Exception as e:
            return f"Search error: {str(e)}", []

    def run_chat(self, messages_history, user_message, temp_image_path=None):
        # Build conversation history in genai format
        history = []
        for msg in messages_history:
            role = "user" if msg["role"] == "user" else "model"
            history.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))

        # Prepare user message
        content = user_message
        if temp_image_path and os.path.exists(temp_image_path):
            content = f"[User uploaded an image at '{temp_image_path}']\n\n{user_message}"

        history.append(types.Content(role="user", parts=[types.Part(text=content)]))

        # Send to Gemini with tool
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=history,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                tools=[self.search_tool],
                temperature=0.2
            )
        )

        tool_called = False
        tool_results = []

        # Check for function call
        candidate = response.candidates[0]
        parts = candidate.content.parts

        fn_call = None
        for part in parts:
            if part.function_call:
                fn_call = part.function_call
                break

        if fn_call and fn_call.name == "search_similar_sarees":
            tool_called = True
            args = dict(fn_call.args) if fn_call.args else {}
            query_text = args.get("query_text")
            image_path = args.get("image_url_or_path")
            limit = int(args.get("limit", 6))

            result_str, tool_results = self._execute_search(
                query_text=query_text,
                image_url_or_path=image_path,
                limit=limit
            )

            # Send tool result back
            history.append(types.Content(role="model", parts=[types.Part(function_call=fn_call)]))
            history.append(types.Content(
                role="user",
                parts=[types.Part(
                    function_response=types.FunctionResponse(
                        name=fn_call.name,
                        response={"result": result_str}
                    )
                )]
            ))

            follow_up = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=history,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    tools=[self.search_tool],
                    temperature=0.2
                )
            )
            response_text = follow_up.text
        else:
            response_text = response.text

        return {
            "response_text": response_text,
            "tool_called": tool_called,
            "tool_results": tool_results
        }
