from .questions import HR_QUESTIONS, APTITUDE_QUESTIONS
from .llm import llm_service
from .stt import stt_service
from .tts import tts_service
import os

class InterviewManager:
    def __init__(self):
        self.states = ["GREETING", "HR_QUESTIONS", "APTITUDE_TEST", "CLOSING"]
        
    def get_next_step(self, candidate_state):
        """
        candidate_state: {
            "current_state": "GREETING",
            "hr_idx": 0,
            "apt_idx": 0,
            "history": []
        }
        """
        state = candidate_state["current_state"]
        
        if state == "GREETING":
            text = "Welcome to your HR interview. This session will be recorded for evaluation. Let's start with a few questions. " + HR_QUESTIONS[0]
            candidate_state["current_state"] = "HR_QUESTIONS"
            candidate_state["hr_idx"] = 1
            return text, candidate_state

        elif state == "HR_QUESTIONS":
            idx = candidate_state["hr_idx"]
            if idx < len(HR_QUESTIONS):
                text = HR_QUESTIONS[idx]
                candidate_state["hr_idx"] += 1
                return text, candidate_state
            else:
                text = "Thank you. Now we will proceed to a brief aptitude test. First question: " + APTITUDE_QUESTIONS[0]["question"]
                candidate_state["current_state"] = "APTITUDE_TEST"
                candidate_state["apt_idx"] = 1
                return text, candidate_state

        elif state == "APTITUDE_TEST":
            idx = candidate_state["apt_idx"]
            if idx < len(APTITUDE_QUESTIONS):
                text = APTITUDE_QUESTIONS[idx]["question"]
                candidate_state["apt_idx"] += 1
                return text, candidate_state
            else:
                text = "That concludes the aptitude test and the interview. Thank you for your time. We will get back to you soon."
                candidate_state["current_state"] = "CLOSING"
                return text, candidate_state
        
        return "The interview has ended.", candidate_state

    def process_answer(self, audio_path, candidate_state):
        # 1. Transcribe
        transcription = stt_service.transcribe(audio_path)
        
        # 2. Add to history
        current_q = ""
        is_aptitude = False
        
        if candidate_state["current_state"] == "HR_QUESTIONS":
            current_q = HR_QUESTIONS[candidate_state["hr_idx"] - 1]
        elif candidate_state["current_state"] == "APTITUDE_TEST":
            current_q = APTITUDE_QUESTIONS[candidate_state["apt_idx"] - 1]["question"]
            is_aptitude = True
        
        candidate_state["history"].append({
            "question": current_q,
            "answer": transcription,
            "is_aptitude": is_aptitude
        })
        
        # 3. Handle follow-up if it's HR question (simplified: LLM paraphrase/followup)
        # For now, we'll keep it simple and just move to next question.
        # But we could call llm_service.get_follow_up(transcription, current_q)
        
        return transcription, candidate_state

interview_manager = InterviewManager()
