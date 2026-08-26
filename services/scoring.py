import re
from .questions import APTITUDE_QUESTIONS

class ScoringEngine:
    def calculate_aptitude_score(self, aptitude_history):
        """
        aptitude_history: list of {question, answer, is_aptitude=True}
        """
        correct_count = 0
        total_questions = len(APTITUDE_QUESTIONS)
        results = []

        for item in aptitude_history:
            q_text = item["question"]
            ans_text = item["answer"].lower().strip()
            
            # Find the index of this question in the master list
            q_data = next((q for q in APTITUDE_QUESTIONS if q["question"] == q_text), None)
            if not q_data:
                continue
                
            correct_ans = q_data["answer"].lower()
            
            # Simple rule-based match
            is_correct = False
            
            # CRITICAL: If answer is empty or too short, it's incorrect
            if len(ans_text) < 1:
                is_correct = False
            else:
                # Handle math transcriptions like "6-0" for "60"
                if q_data["type"] == "math":
                    # Remove hyphens and spaces for numeric comparison
                    clean_ans = ans_text.replace("-", "").replace(" ", "")
                    if correct_ans == clean_ans:
                        is_correct = True
                    else:
                        nums = re.findall(r'\d+', ans_text)
                        if nums and correct_ans in nums:
                            is_correct = True
                else:
                    # Fuzzy match for text: only if ans_text is not empty
                    if correct_ans in ans_text or ans_text in correct_ans:
                        is_correct = True

            if is_correct:
                correct_count += 1
            
            results.append({
                "question": q_text,
                "given": ans_text if ans_text else "Not Answered",
                "correct": correct_ans,
                "is_correct": is_correct
            })

        score_percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        return score_percentage, results

    def calculate_interview_heuristics(self, interview_history):
        """
        interview_history: list of {question, answer, is_aptitude=False}
        """
        total_words = 0
        response_count = 0
        valid_responses = 0
        
        for item in interview_history:
            ans = item["answer"]
            words = len(ans.split())
            total_words += words
            response_count += 1
            if words > 3:  # Only count as valid if more than 3 words
                valid_responses += 1
            
        avg_length = total_words / response_count if response_count > 0 else 0
        
        # Heuristic Scoring:
        # Communication (1-10): based on average length and presence of content
        comm_score = 0
        
        # STRICT RULE: If total words is very low (e.g. user said nothing), score is 0
        if total_words < 10:
            return 1.0, 1.0  # Minimum score for silence
            
        if avg_length > 30: comm_score = 9
        elif avg_length > 20: comm_score = 8
        elif avg_length > 10: comm_score = 6
        elif avg_length > 5: comm_score = 4
        else: comm_score = 2
        
        # Clarity (1-10): check for fillers but start lower if responses are short
        clarity_score = 7 # Default starting point
        
        if valid_responses < response_count / 2:
            clarity_score = 4 # Penalize if many answers were too short
            
        fillers = ["um", "uh", "like", "actually", "basically"]
        filler_count = sum(1 for item in interview_history for word in item["answer"].lower().split() if word in fillers)
        
        if filler_count > 10: clarity_score -= 3
        elif filler_count > 5: clarity_score -= 1
        
        # Ensure scores are within 1-10 range
        comm_score = max(1, min(10, comm_score))
        clarity_score = max(1, min(10, clarity_score))
        
        return float(comm_score), float(clarity_score)

    def get_final_verdict(self, int_score, apt_score):
        total = (int_score + apt_score) / 2
        status = "Review"
        if total >= 80: status = "Shortlisted"
        elif total < 50: status = "Reject"
        return total, status

scoring_engine = ScoringEngine()
