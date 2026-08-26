import requests
import json
import random
import os

# Try to load Gemini API key from config file (optional, for convenience)
try:
    from config import GEMINI_API_KEY as CONFIG_GEMINI_KEY
except ImportError:
    CONFIG_GEMINI_KEY = None

class LLMService:
    def __init__(self, model="mistral", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = f"{base_url}/api/generate"
        # Gemini API configuration
        # Priority: 1) Environment variable, 2) Config file, 3) Empty (use Ollama)
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "") or (CONFIG_GEMINI_KEY if CONFIG_GEMINI_KEY else "")
        
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        self.use_gemini_for_evaluation = bool(self.gemini_api_key)  # Use Gemini if API key is set
        
        if self.use_gemini_for_evaluation:
            print("✅ Gemini API configured - will use Gemini for evaluation/scoring tasks")

    def _query_gemini(self, prompt: str, system_prompt: str = "", temperature: float = 0.7):
        """
        Query Google Gemini API for better accuracy and reliability.
        Used for evaluation/scoring tasks when API key is available.
        """
        if not self.gemini_api_key:
            return None
        
        # Combine system prompt and user prompt
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": full_prompt
                }]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 2048,
                "topP": 0.95,
                "topK": 40
            }
        }
        
        try:
            # Gemini is faster and more reliable, use shorter timeout
            timeout = 60 if ("evaluate" in prompt.lower() or "score" in prompt.lower() or "grammar" in prompt.lower()) else 30
            response = requests.post(
                f"{self.gemini_api_url}?key={self.gemini_api_key}",
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()
            result = response.json()
            
            # Extract text from Gemini response
            if "candidates" in result and len(result["candidates"]) > 0:
                content = result["candidates"][0].get("content", {})
                parts = content.get("parts", [])
                if parts and "text" in parts[0]:
                    return parts[0]["text"].strip()
            
            return ""
        except requests.exceptions.Timeout:
            print(f"Gemini API Error: Request timed out after {timeout} seconds.")
            return None
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return None

    def query(self, prompt: str, system_prompt: str = "", temperature: float = 0.7, use_gemini: bool = None):
        """
        Query LLM (Gemini API if available, otherwise Ollama).
        For evaluation/scoring tasks, prefers Gemini if API key is set.
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Temperature for generation
            use_gemini: Force use Gemini (True) or Ollama (False). If None, auto-detect based on task.
        """
        # Auto-detect: Use Gemini for evaluation tasks if available
        is_evaluation_task = ("evaluate" in prompt.lower() or "score" in prompt.lower() or "grammar" in prompt.lower())
        
        if use_gemini is None:
            use_gemini = is_evaluation_task and self.use_gemini_for_evaluation
        elif use_gemini and not self.gemini_api_key:
            print("Warning: Gemini API key not set, falling back to Ollama")
            use_gemini = False
        
        # Try Gemini first if requested
        if use_gemini:
            gemini_response = self._query_gemini(prompt, system_prompt, temperature)
            if gemini_response is not None and gemini_response:
                return gemini_response
            # Fallback to Ollama if Gemini fails
            print("Gemini API failed, falling back to Ollama")
        
        # Use Ollama (local LLM)
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 150,  # Limit output tokens (faster generation)
                "num_ctx": 2048      # Limit context window (heaps faster processing)
            }
        }
        
        try:
            # Increased timeout for evaluation requests (can take longer)
            # Evaluation requests need more time to generate detailed analysis
            timeout = 120 if is_evaluation_task else 90
            response = requests.post(self.base_url, json=payload, timeout=timeout)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except requests.exceptions.Timeout:
            print(f"LLM Error: Request timed out after {timeout} seconds. Using fallback evaluation.")
            return ""
        except Exception as e:
            print(f"LLM Error: {e}")
            return ""

    def generate_aptitude_question(self, candidate_type: str, topic: str, difficulty: str = "medium", asked_questions: list = None):
        """
        Generate a unique aptitude question dynamically using local LLM.
        
        Args:
            candidate_type: "fresher" or "experienced"
            topic: "array_problems", "string_manipulation", "basic_math", "system_design", etc.
            difficulty: "easy", "medium", or "hard"
            asked_questions: list of previously asked questions to avoid repetition
        
        Returns:
            dict with "question", "options" (dict with A, B, C, D), "answer" (A/B/C/D), "type"
        """
        if asked_questions is None:
            asked_questions = []
            
        system_prompt = f"""You are an offline AI HR interview agent generating technical aptitude questions.
Generate ONE unique {difficulty} difficulty MULTIPLE CHOICE question about '{topic}' suitable for a {candidate_type} candidate.

Your goal is to test LOGIC, QUANTITATIVE REASONING, and PROBLEM SOLVING.
Avoid trivial arithmetic (e.g., "2+2"). 
Questions must be mathematically sound and professionally phrased.

IMPORTANT REQUIREMENTS:
- Question MUST have exactly 4 options (A, B, C, D)
- All 4 options must be related to the question and plausible
- Only ONE option should be correct
- Options should be clearly distinct and well-structured
- Format options clearly, one per line

For topics like 'time_speed_distance', 'profit_and_loss', 'work_and_time', generate standard word problems (e.g. Train passing a platform, Worker efficiency).

Example format:
Question: "What is the next number in the sequence: 2, 4, 8, 16, ...?"
Options:
A) 24
B) 32
C) 40
D) 48
Answer: B) 32

RULES:
- Question must be clear, unambiguous, and answerable verbally.
- Include exactly 4 options labeled A, B, C, D
- All options must be related to the question topic
- The correct answer must be accurate and clearly marked
- Ensure the difficulty level matches '{difficulty}'.
- Do NOT repeat or paraphrase any of these previously asked questions: {asked_questions}
- Output ONLY in this exact JSON format:
{{"question": "Question text here", "options": {{"A": "Option A text", "B": "Option B text", "C": "Option C text", "D": "Option D text"}}, "answer": "A" or "B" or "C" or "D", "explanation": "Brief step-by-step logic", "type": "{topic}"}}"""

        prompt = f"Generate a unique {difficulty} level {topic} question for a {candidate_type} candidate."
        
        response = self.query(prompt, system_prompt, temperature=0.8)
        
        # Parse JSON response
        try:
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                question_data = json.loads(json_str)
                return question_data
        except:
            pass
        
        # Fallback: create a logical question with 4 options if LLM fails
        fallback_questions = {
            "sequence_prediction": {
                "fresher": {
                    "question": "What is the next number in the sequence: 2, 6, 12, 20, ...?",
                    "options": {"A": "28", "B": "30", "C": "32", "D": "36"},
                    "answer": "B"
                },
                "experienced": {
                    "question": "Find the next term: 1, 4, 9, 16, 25, ...",
                    "options": {"A": "30", "B": "36", "C": "42", "D": "49"},
                    "answer": "B"
                }
            },
            "percentages": {
                "fresher": {
                    "question": "A shirt is discounted by 20% and now costs $80. What was the original price?",
                    "options": {"A": "$90", "B": "$100", "C": "$110", "D": "$120"},
                    "answer": "B"
                },
                "experienced": {
                    "question": "A company revenue increased by 15% to $230,000. What was last year's revenue?",
                    "options": {"A": "$195,000", "B": "$200,000", "C": "$205,000", "D": "$210,000"},
                    "answer": "B"
                }
            },
            "logical_puzzles": {
                "fresher": {
                    "question": "If all A are B and all B are C, are all A necessarily C?",
                    "options": {"A": "Yes", "B": "No", "C": "Sometimes", "D": "Cannot determine"},
                    "answer": "A"
                },
                "experienced": {
                    "question": "A team of 5 completes a task in 10 days. How many days would 10 people take?",
                    "options": {"A": "3 days", "B": "5 days", "C": "7 days", "D": "10 days"},
                    "answer": "B"
                }
            }
        }
        
        default_q = {
            "question": "What is the next number in the sequence: 3, 9, 27, ...?",
            "options": {"A": "54", "B": "81", "C": "108", "D": "243"},
            "answer": "B",
            "type": topic
        }
        fallback = fallback_questions.get(topic, {}).get(candidate_type, default_q)
        
        return {
            "question": fallback.get("question"),
            "options": fallback.get("options", {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}),
            "answer": fallback.get("answer", "A"),
            "type": topic,
            "explanation": "Calculated based on logical pattern."
        }

    def check_semantic_similarity(self, new_question: str, asked_questions: list):
        """
        Check if new_question is semantically similar to any in asked_questions.
        Returns True if similar (should regenerate), False if unique.
        """
        if not asked_questions:
            return False
        
        system_prompt = """You are checking if a new question is semantically similar to previously asked questions.
Answer ONLY with 'YES' if the new question is similar to any previous question, or 'NO' if it's unique.
Consider questions similar if they test the same concept or require the same type of reasoning."""

        prompt = f"""New Question: {new_question}

Previously Asked Questions:
{chr(10).join(f"- {q}" for q in asked_questions)}

Is the new question semantically similar to any previous question? Answer YES or NO only."""

        response = self.query(prompt, system_prompt, temperature=0.3).upper()
        
        return "YES" in response

    def evaluate_communication(self, question: str, answer: str):
        """
        Evaluate communication quality of an answer given the question.
        Returns a score from 0-10.
        """
        if not answer or len(answer.strip()) < 1:
            return 0.0
        
        system_prompt = """You are evaluating communication quality in an interview answer.
Rate the answer on a scale of 0-10 based on:
- Clarity (is it easy to understand?)
- Fluency (does it flow naturally?)
- Relevance (does it directly answer the specific question?)
- Conciseness (is it appropriate length for the question?)

Context is important:
- For simple math/logic questions, a short direct answer is perfect (10/10).
- For open-ended HR questions, a well-structured detailed answer is required.

Output ONLY a number between 0 and 10."""

        prompt = f"Question: {question}\nAnswer: {answer}\n\nScore (0-10):"
        
        response = self.query(prompt, system_prompt, temperature=0.3)
        
        # Extract number
        try:
            import re
            numbers = re.findall(r'\d+\.?\d*', response)
            if numbers:
                score = float(numbers[0])
                return max(0.0, min(10.0, score))
        except:
            pass
        
        # Fallback heuristic
        word_count = len(answer.split())
        if word_count > 30:
            return 7.5
        elif word_count > 15:
            return 6.0
        elif word_count > 5:
            return 4.0
        else:
            return 2.0

    def evaluate_aptitude_answer(self, question: str, given_answer: str, correct_answer: str):
        """
        Evaluate if the given answer is correct using LLM reasoning.
        Returns True if correct, False otherwise.
        """
        system_prompt = """You are evaluating an aptitude test answer.
Determine if the given answer is correct or equivalent to the expected answer.
Consider:
- Numerical equivalence (e.g., "60" = "sixty" = "6-0")
- Semantic equivalence (e.g., "not necessarily" = "cannot be determined")
- Partial correctness for complex answers

Answer ONLY with 'CORRECT' or 'INCORRECT'."""

        prompt = f"""Question: {question}
Expected Answer: {correct_answer}
Given Answer: {given_answer}

Is the given answer correct? Answer CORRECT or INCORRECT only."""

        response = self.query(prompt, system_prompt, temperature=0.2).upper()
        
        return "CORRECT" in response

    def paraphrase_question(self, question: str):
        system = "You are an HR interviewer. Paraphrase the following question to sound natural and professional. Keep it to one sentence."
        return self.query(question, system)

    def get_follow_up(self, answer: str, context: str):
        system = "You are an HR interviewer. The candidate just answered a question. Provide a VERY short (max 1 sentence) follow-up or acknowledgement. Do not start a new topic."
        prompt = f"Context: {context}\nCandidate Answer: {answer}"
        return self.query(prompt, system)

llm_service = LLMService()
