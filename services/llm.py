import requests
import json

class LLMService:
    def __init__(self, model="mistral", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = f"{base_url}/api/generate"

    def query(self, prompt: str, system_prompt: str = ""):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False
        }
        
        try:
            response = requests.post(self.base_url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception as e:
            print(f"LLM Error: {e}")
            return "I'm sorry, I'm having trouble processing that right now."

    def paraphrase_question(self, question: str):
        system = "You are an HR interviewer. Paraphrase the following question to sound natural and professional. Keep it to one sentence."
        return self.query(question, system)

    def get_follow_up(self, answer: str, context: str):
        system = "You are an HR interviewer. The candidate just answered a question. Provide a VERY short (max 1 sentence) follow-up or acknowledgement. Do not start a new topic."
        prompt = f"Context: {context}\nCandidate Answer: {answer}"
        return self.query(prompt, system)

llm_service = LLMService()
