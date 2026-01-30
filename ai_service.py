import os
import json
import openai
from typing import Dict, Optional

class AIService:
    def __init__(self, config: dict):
        self.config = config
        self.active_provider = config.get("ACTIVE_AI", "OpenAI")
        provider_settings = config.get("AI_PROVIDERS", {}).get(self.active_provider, {})
        
        self.api_key = provider_settings.get("api_key", "")
        self.base_url = provider_settings.get("base_url", "https://api.openai.com/v1")
        self.model = provider_settings.get("model", "gpt-3.5-turbo")
        
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)

    def analyze_transcription(self, text: str) -> Dict[str, str]:
        """
        Analyzes the transcription to identify urgency and generate a reply based on business rules.
        """
        system_prompt = """
        You are an intelligent assistant for China Eastern Airlines customer service.
        Your task is to analyze a phone call transcription and:
        1. Identification of the core request.
        2. Detect if it's an URGENT matter (e.g., flight today, medical emergency, lost minor).
        3. Detect the language of the call.
        4. Generate a professional reply in the same language as the caller, following these rules:
           - Buy tickets: Visit official website www.ceair.com, use agents, or third-party websites.
           - Refund/Change: If bought on official website, email MUYVR@chinaeastern.ca. Otherwise, contact the original channel (agent/website).
           - Special services: If starting from Vancouver (YVR), email MUYVR@chinaeastern.ca. If starting from Toronto (YYZ), email MUyyzSales@chinaeastern.ca.
           - Name change: Call 011 86 21 20695530.
           - Other matters: Email MUyyzSales@chinaeastern.ca.
        
        Return the result in JSON format:
        {
            "summary": "Concise but comprehensive summary of the call. For long conversations, ensure key details are captured.",
            "is_urgent": true/false,
            "urgency_reason": "Reason for urgency if any",
            "detected_language": "Language name",
            "suggested_reply": "Content to copy"
        }
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Transcription Text:\n{text}"}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"AI Analysis failed ({self.active_provider}): {e}")
            return {
                "summary": f"Error analyzing text with {self.active_provider}",
                "is_urgent": False,
                "urgency_reason": "",
                "detected_language": "Unknown",
                "suggested_reply": "Error generating reply."
            }
