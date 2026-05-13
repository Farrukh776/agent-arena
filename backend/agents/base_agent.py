import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class Agent:
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.conversation_history = []
        self.client = Groq()

    def respond(self, user_message: str, memory_context: str = "") -> str:
        """Standard blocking response — used by debate_engine.py"""
        full_message = user_message
        if memory_context:
            full_message = f"{memory_context}\n\n{user_message}"

        self.conversation_history.append({
            "role": "user",
            "content": full_message
        })

        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + self.conversation_history

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1000,
            messages=messages
        )

        reply = response.choices[0].message.content

        self.conversation_history.append({
            "role": "assistant",
            "content": reply
        })

        return reply

    def respond_streaming(self, user_message: str, memory_context: str = ""):
        """
        Streaming response — yields text chunks as they arrive.
        Used by the WebSocket handler so frontend gets live updates.
        
        Concept — Streaming:
        Instead of waiting for the full response, Groq sends back
        small chunks of text as they're generated. We yield each
        chunk so the WebSocket can forward it to the browser instantly.
        """
        full_message = user_message
        if memory_context:
            full_message = f"{memory_context}\n\n{user_message}"

        self.conversation_history.append({
            "role": "user",
            "content": full_message
        })

        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + self.conversation_history

        # stream=True tells Groq to send chunks instead of waiting
        stream = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1000,
            messages=messages,
            stream=True
        )

        full_reply = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                full_reply += delta
                yield delta  # send each chunk immediately

        # Store complete reply in history after streaming finishes
        self.conversation_history.append({
            "role": "assistant",
            "content": full_reply
        })

    def reset(self):
        self.conversation_history = []