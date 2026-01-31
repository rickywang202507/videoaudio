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
        4. Generate a professional reply in the same language as the caller, following these STRICT LOGIC rules:
           
           DECISION TREE (Follow this exactly):
           
           A. REFUND / CHANGE TICKET:
              - IF user bought on Official Website (ceair.com):
                -> Instruct to email: MUYVR@chinaeastern.ca
              - IF user bought via Agent / Third-Party:
                -> Instruct to contact original purchase channel.
              - IF UNKNOWN source:
                -> Provide BOTH options clearly.
           
           B. SPECIAL SERVICES (Wheelchair, Unaccompanied Minor, Pets, etc.):
              - IF flight departs from VANCOUVER (YVR):
                -> Instruct to email: MUYVR@chinaeastern.ca
              - IF flight departs from TORONTO (YYZ):
                -> Instruct to email: MUyyzSales@chinaeastern.ca
              - IF UNKNOWN departure city:
                -> Provide BOTH email options clearly (e.g. "If departing YVR... If departing YYZ...").

           C. NAME CHANGE:
              -> Always instruct to call: 011 86 21 2069 5530
           
           D. GENERAL INQUIRIES / OTHER:
              -> Instruct to email: MUyyzSales@chinaeastern.ca

        CRITICAL CONTENT RULES (MUST INCLUDE IN SUGGESTED REPLY):
        - You MUST include the full email addresses and phone numbers as dictated by the logic above.
        - You MUST include the HQ phone number (011 86 21 2069 5530) for name changes or urgent global support if applicable.
        - DO NOT summarize these details away.
        - DO NOT ALTER MEANING: The provided contact channels are the ONLY valid solutions. Do not suggest alternatives.
        
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

    def paraphrase_content(self, text: str, tone: str = "polite and professional") -> str:
        """
        Rewrites the given text to be unique while preserving all variables, numbers, emails, and URLs.
        """
        system_prompt = f"""
        You are a professional customer service assistant for China Eastern Airlines.
        Your task is to REWRITE the provided message to sound natural, unique, and human-like.
        
        CRITICAL RULES:
        1. PRESERVE ALL FACTS: Do NOT change any phone numbers, email addresses (e.g. MUYVR@chinaeastern.ca), URLs, or policy details.
        2. PRESERVE KEY INFO: Keep the bilingual nature if you cannot detect a specific target language, BUT you can condense the text. Avoid literal word-for-word translation if it makes the message too long.
        3. TONE: {tone}.
        4. VARIATION: Change the sentence structure and greeting slightly so it doesn't look like a bot template.
        5. DO NOT remove the [Ref: ...] ID at the end if it exists.
        
        Input text is a template with variables already filled.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.7 
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI Paraphrase failed: {e}")
            return text # Fallback to original

    
    def generate_reply_from_history(self, history_text: str, template_text: str = "") -> str:
        """
        Analyzes the conversation history to determine language (CN/EN) and generates an appropriate reply.
        Returns the final localized message.
        """
        # Optimized small prompt for speed and cost
        system_prompt = f"""
        You are a smart CS assistant for China Eastern Airlines (MU).
        Analyze the recent chat history to detect the user's language (Chinese or English).
        
        SOURCE OF TRUTH (Use ONLY information from this text):
        ---
        {template_text}
        ---
        
        TASK:
        1. Detect Language: If user speaks Chinese, reply in Chinese. If English, reply in English.
        2. Generate Reply based on the following STRICT LOGIC (Do not guess):

           A. REFUND / CHANGE TICKET:
              - IF user bought on Official Website (ceair.com):
                -> Instruct to email: MUYVR@chinaeastern.ca
              - IF user bought via Agent / Third-Party:
                -> Instruct to contact original purchase channel.
              - IF UNKNOWN source:
                -> Provide BOTH options.
           
           B. SPECIAL SERVICES (Wheelchair, Unaccompanied Minor, Pets, etc.):
              - IF flight departs from VANCOUVER (YVR):
                -> Instruct to email: MUYVR@chinaeastern.ca
              - IF flight departs from TORONTO (YYZ):
                -> Instruct to email: MUyyzSales@chinaeastern.ca
              - IF UNKNOWN departure city:
                -> Provide BOTH email options clearly.

           C. NAME CHANGE:
              -> Always instruct to call: 011 86 21 2069 5530
           
           D. GENERAL INQUIRIES / ALL OTHER MATTERS:
              -> Instruct to email: MUyyzSales@chinaeastern.ca
        
        CRITICAL CONTENT RULES (MUST INCLUDE):
        - You MUST include the full email addresses and phone numbers as dictated by the logic above.
        - You MUST include the HQ phone number (011 86 21 2069 5530) if applicable.
        - DO NOT summarize these details away.
        
        3. Tone: Polite, Professional, Helpful.
        4. Important: Do NOT invent new phone numbers or emails. Use only info found in these rules or the template provided.
        5. DO NOT ALTER MEANING: You must NOT change the original meaning of the instructions. The contact methods (emails/phones) must be presented exactly as the solution to the user's problem.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Conversation History:\n{history_text}\n\n[Action: Generate Missed Call Auto-Reply]"}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI Language Reply failed: {e}")
            return None # Return None to trigger fallback to standard bilingual template
