import sys
import os

# Add the current directory to sys.path to import local modules
sys.path.append(os.getcwd())

# Mock services before importing interview_manager
import unittest.mock as mock

mock_stt = mock.MagicMock()
mock_stt.transcribe.return_value = "Mocked answer"

mock_tts = mock.MagicMock()
mock_tts.text_to_speech.return_value = "mock_audio.wav"

sys.modules['services.stt'] = mock.MagicMock(stt_service=mock_stt)
sys.modules['services.tts'] = mock.MagicMock(tts_service=mock_tts)
sys.modules['services.llm'] = mock.MagicMock(llm_service=mock.MagicMock())

from services.interview_manager import interview_manager
from services.scoring import scoring_engine
from services.questions import HR_QUESTIONS, APTITUDE_QUESTIONS

def test_interview_flow():
    print("--- Testing Interview Flow Logic ---")
    state = {
        "current_state": "GREETING",
        "hr_idx": 0,
        "apt_idx": 0,
        "history": []
    }
    
    # 1. Greeting
    text, state = interview_manager.get_next_step(state)
    print(f"Step 1 (Greeting): {text}")
    assert "Welcome" in text
    assert state["current_state"] == "HR_QUESTIONS"
    
    # 2. Simulate answering first HR question
    # We mock the process_answer part since it requires audio
    state["history"].append({
        "question": HR_QUESTIONS[0],
        "answer": "My name is John and I have a background in software engineering.",
        "is_aptitude": False
    })
    
    # 3. Next HR questions
    for i in range(1, len(HR_QUESTIONS)):
        text, state = interview_manager.get_next_step(state)
        print(f"HR Question {i}: {text}")
        state["history"].append({
            "question": text,
            "answer": "This is a sample answer for testing.",
            "is_aptitude": False
        })
        
    # 4. Transition to Aptitude
    text, state = interview_manager.get_next_step(state)
    print(f"Transition to Aptitude: {text}")
    assert "aptitude test" in text.lower()
    assert state["current_state"] == "APTITUDE_TEST"
    
    # 5. Aptitude Questions
    for i in range(len(APTITUDE_QUESTIONS)):
        # Simulate answering
        q_text = APTITUDE_QUESTIONS[i]["question"]
        correct_ans = APTITUDE_QUESTIONS[i]["answer"]
        
        state["history"].append({
            "question": q_text,
            "answer": correct_ans, # giving correct answer
            "is_aptitude": True
        })
        
        text, state = interview_manager.get_next_step(state)
        print(f"Next step: {text}")

    print(f"Final State: {state['current_state']}")
    assert state["current_state"] == "CLOSING"
    
    # 6. Test Scoring
    print("\n--- Testing Scoring Engine ---")
    hr_hist = [h for h in state["history"] if not h["is_aptitude"]]
    apt_hist = [h for h in state["history"] if h["is_aptitude"]]
    
    comm_s, clar_s = scoring_engine.calculate_interview_heuristics(hr_hist)
    apt_score, apt_results = scoring_engine.calculate_aptitude_score(apt_hist)
    
    print(f"Communication Score: {comm_s}")
    print(f"Clarity Score: {clar_s}")
    print(f"Aptitude Score: {apt_score}%")
    
    assert apt_score == 100.0
    
    total_score, status = scoring_engine.get_final_verdict((comm_s + clar_s) * 5, apt_score)
    print(f"Total Score: {total_score}, Status: {status}")
    
    print("\nLogic Test Passed!")

if __name__ == "__main__":
    test_interview_flow()
