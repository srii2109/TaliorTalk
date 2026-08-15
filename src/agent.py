import os
import google.generativeai as genai
from google.generativeai.types import Tool
from src.searcher import SareeSearchEngine

class SareeAgent:
    def __init__(self, api_key: str, search_engine: SareeSearchEngine):
        """
        Initializes the agent with the Gemini API key and the visual search engine.
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.search_engine = search_engine
        
        # Define the system instruction
        self.system_instruction = (
            "You are TailorTalk, an AI fashion assistant specializing in Indian sarees. "
            "You help users browse a saree catalog of 100 images to find matches based on style, weave, print, borders, fabric, and colors.\n\n"
            "Capabilities:\n"
            "1. casual conversation: Talk about sarees, Indian textiles, drape styles, fabrics (silk, cotton, linen, georgette), weaves, or general styling advice.\n"
            "2. Visual Search: Find visually similar sarees using the 'search_similar_sarees' tool.\n\n"
            "How to handle search:\n"
            "- If the user uploads an image, the frontend saves it locally at 'data/temp_query.jpg'. "
            "If the user asks you to find similar sarees, or if they ask a question about this image that requires visual search, "
            "call the 'search_similar_sarees' tool and pass 'data/temp_query.jpg' as the image_url_or_path argument.\n"
            "- If the user asks for a similarity search by text (e.g. 'find a red silk saree'), call the 'search_similar_sarees' tool and pass the query text to 'query_text'.\n"
            "- Provide a natural, friendly summary of the matching sarees returned by the tool, discussing their styles, colors, and border patterns.\n"
            "Avoid mentioning technical details like 'FAISS', 'CLIP', or 'vector database' in casual conversations unless specifically asked."
        )
        
    def get_search_tool(self):
        """
        Returns the python function to be registered as a tool with Gemini.
        """
        def search_similar_sarees(query_text: str = None, image_url_or_path: str = None, limit: int = 5) -> str:
            """
            Search the saree catalogue and find visually or semantically similar sarees.
            
            Args:
                query_text: A description of the saree you are looking for (e.g. 'blue silk saree with gold border'). Optional if an image is provided.
                image_url_or_path: A URL or local path to a saree image to find visual matches for. Optional if text description is provided.
                limit: The maximum number of matches to return (default is 5).
                
            Returns:
                A JSON string containing the list of matching sarees with similarity scores.
            """
            try:
                # Call searcher
                results = self.search_engine.search(
                    query_image=image_url_or_path,
                    query_text=query_text,
                    top_k=limit
                )
                
                # Format results as a readable string for the model
                if not results:
                    return "No matching sarees found."
                
                formatted = []
                for idx, r in enumerate(results):
                    formatted.append(
                        f"Match {idx+1}: Image file '{r['filename']}', Similarity Score: {r['score']:.2f} "
                        f"(Style: {r['clip_score']:.2f}, Color Layout: {r['color_score']:.2f})"
                    )
                return "\n".join(formatted)
                
            except Exception as e:
                return f"Error executing similarity search: {str(e)}"
                
        return search_similar_sarees

    def run_chat(self, messages_history, user_message, temp_image_path=None):
        """
        Runs the chat completion using Gemini function calling.
        - messages_history: list of dicts in Streamlit format (role, content)
        - user_message: the new text message from user
        - temp_image_path: path to the uploaded image if any
        """
        # Convert streamlit messages to Gemini API format
        gemini_history = []
        for msg in messages_history:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})
            
        # Get the tool function
        search_tool = self.get_search_tool()
        
        # Initialize Gemini Model
        # Using gemini-2.5-flash as the latest standard model
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={"temperature": 0.2},
            tools=[search_tool],
            system_instruction=self.system_instruction
        )
        
        # Start chat with history
        chat = model.start_chat(history=gemini_history)
        
        # Send user message. If there is an image uploaded, we can also include a reminder about it.
        content = user_message
        if temp_image_path and os.path.exists(temp_image_path):
            content = f"[User has uploaded an image which is saved at '{temp_image_path}']\n\n{user_message}"
            
        # Send message and handle function calling
        response = chat.send_message(content)
        
        # Handle function call if request is made
        tool_called = False
        tool_results = None
        
        # Safely extract function calls from candidates
        function_calls = []
        try:
            if response.candidates and len(response.candidates) > 0:
                parts = response.candidates[0].content.parts
                for part in parts:
                    if part.function_call:
                        function_calls.append(part.function_call)
        except Exception:
            pass

        if function_calls:
            for call in function_calls:
                if call.name == "search_similar_sarees":
                    tool_called = True
                    # Extract arguments
                    args = call.args
                    query_text = args.get("query_text")
                    image_path = args.get("image_url_or_path")
                    limit = int(args.get("limit", 5))
                    
                    # Execute tool
                    result_str = search_tool(
                        query_text=query_text,
                        image_url_or_path=image_path,
                        limit=limit
                    )
                    
                    # Store results for UI display
                    tool_results = self.search_engine.search(
                        query_image=image_path,
                        query_text=query_text,
                        top_k=limit
                    )
                    
                    # Send function response back to Gemini to get the final conversational answer
                    response = chat.send_message(
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=call.name,
                                response={'result': result_str}
                            )
                        )
                    )
                    break
                    
        return {
            "response_text": response.text,
            "tool_called": tool_called,
            "tool_results": tool_results
        }
