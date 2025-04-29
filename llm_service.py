import os
import json
import requests
from typing import Dict, List, Optional

class LLMService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("LLM_API_KEY")
        self.api_url = "https://api.anthropic.com/v1/messages"  # For Claude
        # Alternative: "https://api.openai.com/v1/chat/completions"  # For ChatGPT

    def generate_response(self, messages, context=None):
        """Generate a response using the LLM API"""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"  # For Claude
        }

        # Prepare system message with context
        system_message = """You are a payment API integration assistant. Your job is to help developers integrate payment services like Stripe and PayPal into their applications.
Use the provided documentation context to answer questions accurately."""

        if context:
            system_message += "\n\nHere's some relevant documentation to help answer the question:\n"
            for i, doc in enumerate(context, 1):
                system_message += f"\n{i}. {doc['text']}\n"
                if 'code' in doc:
                    system_message += f"Code example ({doc.get('language', 'code')}):\n{doc['code']}\n"

        # Format messages for Claude
        payload = {
            "model": "claude-3-opus-20240229",  # Or use another model
            "messages": messages,
            "system": system_message,
            "max_tokens": 1000
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()['content'][0]['text']
        except Exception as e:
            print(f"Error calling LLM API: {e}")
            return "I encountered an error while processing your request. Please try again."

