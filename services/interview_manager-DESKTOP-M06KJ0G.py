from .llm import llm_service
from .stt import stt_service
from .questions import QUESTION_BANK
import random
import re

class InterviewManager:
    def __init__(self):
        self.states = ["GREETING", "EXPERIENCE_DETECTION", "HR_QUESTIONS", "APTITUDE_TEST", "CLOSING"]
        
        # HR Questions (asked before aptitude)
        # NOTE: HR questions are open-ended (NO options) - candidates answer in their own words
        # Only aptitude questions have 4 options (A, B, C, D)
        self.hr_questions = [
            "Please introduce yourself and tell me about your background.",
            "What are your key strengths and skills?",
            "What are your career goals and where do you see yourself in 5 years?",
            "Why are you interested in this position?"
        ]
        
        # Topic pools for aptitude questions with difficulty levels
        self.fresher_topics = {
            "easy": ["sequence_prediction", "percentages", "ratios_and_proportions"],
            "medium": ["time_speed_distance", "work_and_time", "profit_and_loss", "logical_puzzles"],
            "hard": ["probability", "permutation_combination", "data_interpretation", "algorithmic_thinking"]
        }
        
        self.experienced_topics = {
            "easy": ["data_structures", "algorithm_basics", "time_speed_distance"],
            "medium": ["system_design_basics", "optimization", "probability", "statistics"],
            "hard": ["complex_algorithms", "architectural_decisions", "advanced_quantitative_analysis"]
        }
        
        # Number of questions
        self.num_hr_questions = 3
        self.num_aptitude_questions = 6
        
    def get_next_step(self, candidate_state):
        """
        candidate_state: {
            "current_state": "GREETING",
            "candidate_type": None | "fresher" | "experienced",
            "experience_years": 0,
            "hr_idx": 0,
            "apt_idx": 0,
            "asked_questions": [],  # List of question texts to prevent repetition
            "generated_questions": [],  # Store question data with answers
            "history": []
        }
        """
        state = candidate_state["current_state"]
        
        if state == "GREETING":
            text = "Welcome to your HR interview. This session will be recorded for evaluation. Let's begin. Are you a fresher or do you have work experience? If experienced, please mention your total years of experience."
            candidate_state["current_state"] = "EXPERIENCE_DETECTION"
            return text, candidate_state

        elif state == "EXPERIENCE_DETECTION":
            # Transition to HR questions
            text = "Thank you. Now let's start with a few questions about yourself. "
            text += self.hr_questions[0]
            candidate_state["current_state"] = "HR_QUESTIONS"
            candidate_state["hr_idx"] = 1
            return text, candidate_state

        elif state == "HR_QUESTIONS":
            # HR questions are open-ended (NO options) - just display the question text
            idx = candidate_state.get("hr_idx", 0)
            
            if idx < self.num_hr_questions and idx < len(self.hr_questions):
                text = self.hr_questions[idx]  # No options for HR questions
                candidate_state["hr_idx"] += 1
                return text, candidate_state
            else:
                # Transition to aptitude intro (separate step)
                text = "Great! Now we will proceed to the aptitude test. This will test your problem-solving and analytical skills. Are you ready to start?"
                candidate_state["current_state"] = "APTITUDE_INTRO"
                return text, candidate_state

        elif state == "APTITUDE_INTRO":
            # Check previous answer for negative intent
            last_answer = ""
            if candidate_state.get("history"):
                last_answer = candidate_state["history"][-1].get("answer", "").lower()

            negative_keywords = ["no", "not ready", "skip", "pass", "don't", "dont", "stop", "cancel"]
            
            is_negative = False
            for kw in negative_keywords:
                # Check keyword match
                if f" {kw} " in f" {last_answer} " or last_answer.startswith(kw) or last_answer == kw:
                    # Special exceptions for positive phrases containing "no"
                    if "no problem" in last_answer or "no worries" in last_answer or "no doubt" in last_answer:
                        continue
                    
                    is_negative = True
                    break
            
            if is_negative:
                candidate_state["current_state"] = "CLOSING"
                return "Understood. We will skip the aptitude test. Thank you for completing the interview. We will review your responses and get back to you.", candidate_state

            # Transition from Intro to First Question
            candidate_state["current_state"] = "APTITUDE_TEST"
            candidate_state["apt_idx"] = 0
            
            # Generate first aptitude question (Easy difficulty)
            next_question = self._generate_unique_aptitude_question(candidate_state, difficulty="easy")
            
            intro_prefix = "Excellent. Let's begin. "
            
            if next_question:
                # REQUIRED: All APTITUDE questions must have 4 options (A, B, C, D)
                # NOTE: Only aptitude questions have options - HR questions are open-ended
                question_text = next_question['question']
                options = next_question.get('options', {})
                
                # STRICT VALIDATION: Question MUST have exactly 4 options
                if not options or len(options) != 4 or not all(key in options for key in ['A', 'B', 'C', 'D']):
                    # CRITICAL: Skip this question - it's invalid without 4 options
                    print(f"ERROR: Question missing 4 options, retrying: {question_text}")
                    # Try up to 5 times to get a valid question with options
                    for retry in range(5):
                        next_question = self._generate_unique_aptitude_question(candidate_state, difficulty="easy")
                        if next_question and next_question.get('options') and len(next_question.get('options', {})) == 4:
                            if all(key in next_question.get('options', {}) for key in ['A', 'B', 'C', 'D']):
                                question_text = next_question['question']
                                options = next_question['options']
                                break
                    else:
                        # Last resort: use default question with options
                        print("Using default question with options")
                        next_question = {
                            "question": "What is 10 + 15?",
                            "options": {"A": "20", "B": "25", "C": "30", "D": "35"},
                            "answer": "B",
                            "explanation": "Basic addition: 10 + 15 = 25"
                        }
                        question_text = next_question['question']
                        options = next_question['options']
                
                # Format question with 4 options (REQUIRED) - ALWAYS show options, one per line
                # Each option on its own line for clear structure
                options_text = f"\n\nA) {options['A']}\nB) {options['B']}\nC) {options['C']}\nD) {options['D']}\n\nPlease choose option A, B, C, or D."
                text = f"{intro_prefix}First question: {question_text}{options_text}"
                candidate_state["apt_idx"] = 1
                # Store the question data for scoring later
                if "generated_questions" not in candidate_state:
                    candidate_state["generated_questions"] = []
                candidate_state["generated_questions"].append(next_question)
                return text, candidate_state
            else:
                 return "Let's begin. Please tell me about a time you solved a complex problem.", candidate_state

        elif state == "APTITUDE_TEST":
            idx = candidate_state.get("apt_idx", 0)
            
            if idx < self.num_aptitude_questions:
                # Progressive difficulty for 6 questions: 
                # 1-2: easy, 3-4: medium, 5-6: hard
                if idx < 2:
                    difficulty = "easy"
                elif idx < 4:
                    difficulty = "medium"
                else:
                    difficulty = "hard"
                
                # Generate next question with retry logic to ensure 4 options
                next_question = None
                question_text = ""
                options = {}
                
                # Retry up to 5 times to get a valid question with 4 options
                for retry in range(5):
                    next_question = self._generate_unique_aptitude_question(candidate_state, difficulty=difficulty)
                    
                    if next_question:
                        question_text = next_question.get("question", "")
                        options = next_question.get('options', {})
                        
                        # Validate that all 4 options exist
                        if options and len(options) == 4 and all(key in options for key in ['A', 'B', 'C', 'D']):
                            # Valid question found
                            break
                        else:
                            # Try fallback
                            print(f"Warning: Question missing 4 options (retry {retry + 1}/5), trying fallback")
                            fallback = self._get_fallback_question(
                                candidate_state.get("candidate_type", "fresher"), 
                                difficulty, 
                                candidate_state.get("asked_questions", [])
                            )
                            if fallback and fallback.get('options') and len(fallback.get('options', {})) == 4:
                                if all(key in fallback.get('options', {}) for key in ['A', 'B', 'C', 'D']):
                                    next_question = fallback
                                    question_text = fallback.get("question", "")
                                    options = fallback['options']
                                    break
                
                # If still no valid question, use default
                if not next_question or not options or len(options) != 4:
                    print("Using default question with options as last resort")
                    next_question = {
                        "question": "What is 10 + 15?",
                        "options": {"A": "20", "B": "25", "C": "30", "D": "35"},
                        "answer": "B",
                        "explanation": "Basic addition: 10 + 15 = 25"
                    }
                    question_text = next_question['question']
                    options = next_question['options']
                
                # Format question with 4 options (REQUIRED) - ALWAYS show options, one per line
                # Each option on its own line for clear structure
                options_text = f"\n\nA) {options['A']}\nB) {options['B']}\nC) {options['C']}\nD) {options['D']}\n\nPlease choose option A, B, C, or D."
                text = f"{question_text}{options_text}"
                candidate_state["apt_idx"] += 1
                # Store the question data for scoring later
                if "generated_questions" not in candidate_state:
                    candidate_state["generated_questions"] = []
                candidate_state["generated_questions"].append(next_question)
                return text, candidate_state
            else:
                text = "That concludes the interview! Thank you for your time. Our HR team will contact you very soon. Have a great day!"
                candidate_state["current_state"] = "CLOSING"
                return text, candidate_state
        
        return "The interview has ended. We will get back to you soon.", candidate_state

    def _calculate_similarity(self, text1, text2):
        """Simple word-set overlap similarity for speed."""
        words1 = re.findall(r'\w+', text1.lower())
        words2 = re.findall(r'\w+', text2.lower())
        s1 = set(words1)
        s2 = set(words2)
        if not s1 or not s2: return 0
        intersection = s1.intersection(s2)
        
        # If response is very short (1-3 words), don't treat it as echo 
        # unless it's an exact match of a very short question
        if len(words1) <= 3:
            return 0.2 # Below threshold
            
        # Use Jaccard-like or averaged similarity to avoid false positives on short subsets
        return len(intersection) / max(len(s1), len(s2))

    def _generate_unique_aptitude_question(self, candidate_state, difficulty="medium", max_attempts=3):
        """
        Generate a unique aptitude question.
        Now uses a static bank for instant response, with LLM as fallback.
        """
        candidate_type = candidate_state.get("candidate_type", "fresher")
        asked_questions = candidate_state.get("asked_questions", [])
        
        # 1. TRY STATIC BANK FIRST (INSTANT)
        # REQUIRED: Only return questions with 4 options (A, B, C, D)
        bank = QUESTION_BANK.get(candidate_type, {}).get(difficulty, [])
        if bank:
            # Shuffle to get a random one
            random.shuffle(bank)
            for q_data in bank:
                # Validate question has 4 options
                options = q_data.get('options', {})
                if options and len(options) == 4 and all(key in options for key in ['A', 'B', 'C', 'D']):
                    if q_data["question"] not in asked_questions:
                        candidate_state["asked_questions"].append(q_data["question"])
                        return q_data
                else:
                    # Skip questions without proper 4 options
                    print(f"Warning: Skipping question without 4 options: {q_data.get('question', 'Unknown')}")

        # 2. FALLBACK TO LLM IF BANK IS EXHAUSTED OR TOPIC SPECIFIC (SLOW)
        if candidate_type == "experienced":
            topics = self.experienced_topics.get(difficulty, self.experienced_topics["medium"])
        else:
            topics = self.fresher_topics.get(difficulty, self.fresher_topics["easy"])
            
        for attempt in range(max_attempts):
            topic = random.choice(topics)
            question_data = llm_service.generate_aptitude_question(
                candidate_type=candidate_type,
                topic=topic,
                difficulty=difficulty,
                asked_questions=asked_questions
            )
            
            # REQUIRED: Validate LLM-generated question has 4 options
            if question_data and "question" in question_data:
                options = question_data.get('options', {})
                if options and len(options) == 4 and all(key in options for key in ['A', 'B', 'C', 'D']):
                    new_q = question_data["question"]
                    if not any(new_q.lower() in aq.lower() for aq in asked_questions):
                        candidate_state["asked_questions"].append(new_q)
                        return question_data
                else:
                    # LLM didn't generate proper options, try again
                    print(f"Warning: LLM question missing 4 options, retrying attempt {attempt + 1}...")
                    continue
        
        # 3. ABSOLUTE FALLBACK (HARDCODED)
        default_q = {
            "question": "What is 10 + 15?",
            "options": {"A": "20", "B": "25", "C": "30", "D": "35"},
            "answer": "B",
            "explanation": "Basic addition: 10 + 15 = 25"
        }
        return default_q

    def process_answer(self, audio_path, candidate_state):
        """
        Process the candidate's audio answer.
        """
        # 1. Transcribe
        transcription = stt_service.transcribe(audio_path)
        return self._handle_response(transcription, candidate_state)

    def process_text_answer(self, text, candidate_state):
        """
        Process the candidate's text answer (for testing).
        """
        return self._handle_response(text, candidate_state)

    def _handle_response(self, transcription, candidate_state):
        """
        Internal method to handle the response text based on state.
        """
        if not transcription or not transcription.strip():
            return transcription, candidate_state

        # FILTER: If user just repeats the question (echo error/noise)
        # Determine the current question being answered
        current_state = candidate_state["current_state"]
        current_q = ""
        
        if current_state == "EXPERIENCE_DETECTION":
            current_q = "Are you a fresher or do you have work experience?"
        elif current_state == "HR_QUESTIONS":
            idx = candidate_state.get("hr_idx", 1) - 1
            if 0 <= idx < len(self.hr_questions):
                current_q = self.hr_questions[idx]
        elif current_state == "APTITUDE_TEST":
            idx = candidate_state.get("apt_idx", 0) - 1
            gen_qs = candidate_state.get("generated_questions", [])
            if 0 <= idx < len(gen_qs):
                current_q = gen_qs[idx]["question"]

        if current_q and self._calculate_similarity(transcription, current_q) > 0.7:
            # If transcription is too similar to the question, treat as empty (trigger retry)
            print(f"DEBUG: Similarity too high ({self._calculate_similarity(transcription, current_q)}). Discarding echo.")
            return "", candidate_state
        
        # 2. Handle based on current state
        if current_state == "EXPERIENCE_DETECTION":
            # Detect if fresher or experienced
            candidate_type, experience_years = self._detect_experience(transcription)
            candidate_state["candidate_type"] = candidate_type
            candidate_state["experience_years"] = experience_years
            
            # CONFIRMATION LOG FOR THE USER
            print(f"--- PATH DETECTION ---")
            print(f"Transcription: {transcription}")
            print(f"Detected Path: {candidate_type.upper()}")
            print(f"Experience: {experience_years} years")
            print(f"----------------------")
            
            # Add to history
            candidate_state["history"].append({
                "question": "Are you a fresher or do you have work experience?",
                "answer": transcription,
                "is_aptitude": False,
                "is_experience_detection": True
            })
        
        elif current_state == "HR_QUESTIONS":
            # Get the current HR question
            idx = candidate_state.get("hr_idx", 1) - 1
            
            if idx >= 0 and idx < len(self.hr_questions):
                current_q = self.hr_questions[idx]
                
                candidate_state["history"].append({
                    "question": current_q,
                    "answer": transcription,
                    "is_aptitude": False,
                    "is_hr_question": True
                })


        elif current_state == "APTITUDE_INTRO":
            # Just record the confirmation
            candidate_state["history"].append({
                "question": "Are you ready to start the aptitude test?",
                "answer": transcription,
                "is_aptitude": False,
                "is_intro": True
            })
            
        elif current_state == "APTITUDE_TEST":
            # Get the current question data
            idx = candidate_state.get("apt_idx", 1) - 1
            generated_questions = candidate_state.get("generated_questions", [])
            
            if idx >= 0 and idx < len(generated_questions):
                question_data = generated_questions[idx]
                
                candidate_state["history"].append({
                    "question": question_data["question"],
                    "answer": transcription,
                    "correct_answer": question_data.get("answer", ""),  # Store correct answer (A/B/C/D or value)
                    "options": question_data.get("options", {}),  # Store options for scoring
                    "is_aptitude": True
                })
        
        return transcription, candidate_state

    def _detect_experience(self, transcription: str):
        """
        Detect if candidate is fresher or experienced based on their response.
        Returns: (candidate_type, experience_years)
        """
        text_lower = transcription.lower()
        
        # Short noise filter
        if len(text_lower) < 5:
             # If text is too short, default to fresher but ideally should retry
             return "fresher", 0

        # Check for "fresher" keywords
        fresher_keywords = ["fresher", "fresh graduate", "just finished college", "student", "no work experience", "beginner", "no experience"]
        if any(w in text_lower for w in fresher_keywords):
            return "fresher", 0
            
        # Check for "experienced" keywords
        exp_keywords = ["working", "experience", "experienced", "professional", "company", "years", "worked at"]
        if any(w in text_lower for w in exp_keywords):
             # Try to find years, if not found default to 1 year experienced
             pass 
        else:
             # If no keywords found, but they are talking about work, assume experienced
             if "at" in text_lower or "role" in text_lower or "project" in text_lower:
                 pass
             else:
                 return "fresher", 0 # Default to fresher if totally unclear
        
        # Look for year mentions
        year_patterns = [
            r'(\d+)\s*year',
            r'(\d+)\s*yr',
            r'(\d+\.?\d*)\s*year',
        ]
        
        for pattern in year_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                try:
                    years = float(matches[0])
                    if years >= 1:
                        return "experienced", years
                    else:
                        return "fresher", 0
                except:
                    pass
        
        # Check for experience-related keywords
        if any(word in text_lower for word in ["experience", "worked", "working", "job", "company", "position"]):
            # Assume experienced if they mention work-related terms
            return "experienced", 1  # Default to 1 year if not specified
        
        # Default to fresher
        return "fresher", 0
    
    def _get_fallback_question(self, candidate_type, difficulty, asked_questions):
        """
        Get a fallback question if LLM generation fails.
        Returns LeetCode-style problems based on difficulty.
        """
        # Comprehensive fallback question bank with LeetCode-style problems
        fallback_bank = {
            "fresher": {
                "easy": [
                    {
                        "question": "Given an array of integers, find the sum of all elements. For example, if array is [1, 2, 3, 4], the sum is 10. How would you approach this?",
                        "answer": "iterate through array and add each element",
                        "type": "array_problems"
                    },
                    {
                        "question": "How would you check if a string is a palindrome? For example, 'racecar' is a palindrome but 'hello' is not.",
                        "answer": "compare string with its reverse",
                        "type": "string_manipulation"
                    },
                    {
                        "question": "What is the time complexity of searching for an element in an unsorted array of size n?",
                        "answer": "O(n) or linear time",
                        "type": "algorithm_basics"
                    },
                    {
                        "question": "Given two sorted arrays, how would you merge them into one sorted array?",
                        "answer": "use two pointers to compare and merge",
                        "type": "array_problems"
                    },
                    {
                        "question": "Explain the difference between a stack and a queue data structure.",
                        "answer": "stack is LIFO, queue is FIFO",
                        "type": "data_structures"
                    }
                ],
                "medium": [
                    {
                        "question": "How would you find the first non-repeating character in a string? For example, in 'leetcode', the answer is 'l'.",
                        "answer": "use hash map to count frequencies then find first with count 1",
                        "type": "string_manipulation"
                    },
                    {
                        "question": "Given an array, find two numbers that add up to a specific target. How would you optimize this?",
                        "answer": "use hash map for O(n) solution",
                        "type": "array_problems"
                    },
                    {
                        "question": "How would you detect if a linked list has a cycle?",
                        "answer": "use two pointers, slow and fast, if they meet there is a cycle",
                        "type": "data_structures"
                    },
                    {
                        "question": "What is the difference between breadth-first search and depth-first search?",
                        "answer": "BFS uses queue and explores level by level, DFS uses stack and explores depth first",
                        "type": "algorithm_basics"
                    }
                ],
                "hard": [
                    {
                        "question": "How would you find the longest substring without repeating characters in a string?",
                        "answer": "use sliding window with hash set",
                        "type": "string_manipulation"
                    },
                    {
                        "question": "Explain how you would implement a LRU cache with O(1) operations.",
                        "answer": "use hash map and doubly linked list",
                        "type": "data_structures"
                    }
                ]
            },
            "experienced": {
                "easy": [
                    {
                        "question": "How would you reverse a linked list? Explain both iterative and recursive approaches.",
                        "answer": "iterative uses three pointers, recursive reverses rest then adjusts pointers",
                        "type": "data_structures"
                    },
                    {
                        "question": "What is the difference between O(n) and O(log n) time complexity? Give examples.",
                        "answer": "O(n) is linear like array search, O(log n) is logarithmic like binary search",
                        "type": "algorithm_basics"
                    },
                    {
                        "question": "How would you find the maximum element in a binary search tree?",
                        "answer": "keep going right until you reach the rightmost node",
                        "type": "data_structures"
                    }
                ],
                "medium": [
                    {
                        "question": "Design a system to handle rate limiting for an API. How would you ensure no user exceeds 100 requests per minute?",
                        "answer": "use sliding window or token bucket algorithm with timestamps",
                        "type": "system_design_basics"
                    },
                    {
                        "question": "How would you find the kth largest element in an unsorted array efficiently?",
                        "answer": "use quickselect algorithm or min heap of size k",
                        "type": "optimization_problems"
                    },
                    {
                        "question": "Explain how you would implement an autocomplete feature for a search engine.",
                        "answer": "use trie data structure to store words and traverse based on prefix",
                        "type": "system_design_basics"
                    },
                    {
                        "question": "Given a matrix, how would you search for a target value if each row and column is sorted?",
                        "answer": "start from top right, move left if target smaller, down if larger",
                        "type": "optimization_problems"
                    }
                ],
                "hard": [
                    {
                        "question": "Design a distributed cache system like Redis. How would you handle consistency, partitioning, and replication?",
                        "answer": "use consistent hashing for partitioning, master-slave replication, eventual consistency",
                        "type": "architectural_decisions"
                    },
                    {
                        "question": "How would you design a URL shortening service like bit.ly? Consider scalability and collision handling.",
                        "answer": "use base62 encoding, distributed ID generation, database sharding",
                        "type": "architectural_decisions"
                    },
                    {
                        "question": "Explain how you would implement a thread-safe singleton pattern and why double-checked locking is used.",
                        "answer": "use double-checked locking with volatile keyword to minimize synchronization overhead",
                        "type": "advanced_problem_solving"
                    }
                ]
            }
        }
        
        # Get questions for candidate type and difficulty
        questions = fallback_bank.get(candidate_type, fallback_bank["fresher"]).get(difficulty, [])
        
        # Filter out already asked questions AND questions without 4 options
        # REQUIRED: Only return questions with 4 options (A, B, C, D)
        available_questions = [
            q for q in questions 
            if q["question"] not in asked_questions 
            and q.get('options') 
            and len(q.get('options', {})) == 4 
            and all(key in q.get('options', {}) for key in ['A', 'B', 'C', 'D'])
        ]
        
        if available_questions:
            # Return a random question from available ones
            selected = random.choice(available_questions)
            return selected
        
        # If no valid questions with 4 options, return None (will use default hardcoded question)
        return None

interview_manager = InterviewManager()
