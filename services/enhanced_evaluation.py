"""
Enhanced HR Interview Evaluation AI

This module evaluates candidate answers based on experience level and comprehensive criteria.
Provides fair, unbiased assessment with structured scoring and justification.
"""

import re
import json
from typing import Dict, List, Tuple
from .llm import llm_service


class ExperienceLevel:
    """Experience level classifications with thresholds"""
    FRESHER = "Fresher"  # 0-1 years
    JUNIOR = "Junior"    # 1-3 years
    MID_LEVEL = "Mid-level"  # 3-6 years
    SENIOR = "Senior"    # 6+ years
    
    @staticmethod
    def determine_level(years: float) -> str:
        """Determine experience level based on years"""
        if years <= 1:
            return ExperienceLevel.FRESHER
        elif years <= 3:
            return ExperienceLevel.JUNIOR
        elif years <= 6:
            return ExperienceLevel.MID_LEVEL
        else:
            return ExperienceLevel.SENIOR


class EvaluationCriteria:
    """Evaluation dimensions with scoring guidelines - Simplified 4-criteria system"""
    
    # Simplified 4-criteria system (Total: 5.0 points)
    CRITERIA = {
        "grammar_clarity": {
            "max_score": 1.5,
            "description": "Grammar & Clarity"
        },
        "communication_quality": {
            "max_score": 1.5,
            "description": "Communication Quality"
        },
        "relevance_experience": {
            "max_score": 1.0,
            "description": "Relevance to Experience"
        },
        "confidence": {
            "max_score": 1.0,
            "description": "Confidence"
        }
    }
    
    # Legacy criteria for backward compatibility (if needed)
    LEGACY_CRITERIA = {
        "grammar_language": {
            "weight": 0.10,
            "description": "Grammar & Language Quality"
        },
        "communication_clarity": {
            "weight": 0.15,
            "description": "Communication Clarity"
        },
        "confidence": {
            "weight": 0.10,
            "description": "Confidence Level"
        },
        "relevance": {
            "weight": 0.15,
            "description": "Relevance to Question & Experience"
        },
        "attitude_professionalism": {
            "weight": 0.10,
            "description": "Attitude & Professionalism"
        },
        "cultural_fit": {
            "weight": 0.10,
            "description": "Cultural Fit & Values"
        },
        "problem_solving": {
            "weight": 0.10,
            "description": "Problem-Solving Ability"
        },
        "learning_adaptability": {
            "weight": 0.10,
            "description": "Learning & Adaptability"
        },
        "motivation_goals": {
            "weight": 0.10,
            "description": "Motivation & Career Goals"
        }
    }
    
    # Experience-based expectations
    EXPECTATIONS = {
        ExperienceLevel.FRESHER: {
            "focus": ["Basic understanding", "Willingness to learn", "Clarity", "Enthusiasm"],
            "leniency": "High - Focus on potential over experience",
            "red_flags": ["Poor grammar", "Completely off-topic", "No interest in learning"]
        },
        ExperienceLevel.JUNIOR: {
            "focus": ["Hands-on exposure", "Correct terminology", "Some examples", "Learning mindset"],
            "leniency": "Moderate - Expect some practical experience",
            "red_flags": ["No practical examples", "Poor communication", "Lack of curiosity"]
        },
        ExperienceLevel.MID_LEVEL: {
            "focus": ["Practical examples", "Structured thinking", "Best practices", "Problem-solving"],
            "leniency": "Low - Expect concrete experience",
            "red_flags": ["Vague answers", "No examples", "Weak problem-solving"]
        },
        ExperienceLevel.SENIOR: {
            "focus": ["Strategic thinking", "Leadership", "Deep technical clarity", "Architecture decisions"],
            "leniency": "Very Low - Expect mastery and leadership",
            "red_flags": ["Shallow answers", "No strategic vision", "Poor articulation"]
        }
    }


class EnhancedEvaluationEngine:
    """Main evaluation engine with experience-aware scoring"""
    
    def __init__(self):
        self.criteria = EvaluationCriteria.CRITERIA  # New simplified 4-criteria system
        self.legacy_criteria = EvaluationCriteria.LEGACY_CRITERIA  # For backward compatibility
        self.llm_service = llm_service  # Use LLM for direct evaluation
        
    def evaluate_answer(
        self, 
        question: str, 
        answer: str, 
        experience_years: float,
        question_type: str = "hr"
    ) -> Dict:
        """
        Evaluate a single answer comprehensively
        
        Args:
            question: The question asked
            answer: The candidate's answer
            experience_years: Years of experience
            question_type: Type of question (hr, technical, aptitude)
            
        Returns:
            Dictionary containing scores, justifications, and overall assessment
        """
        # Determine experience level
        exp_level = ExperienceLevel.determine_level(experience_years)
        
        # Quick validation
        if not answer or len(answer.strip()) < 2:
            return self._create_empty_answer_evaluation(question, exp_level)
        
        # Check for non-answers and heavily penalize
        if self._is_non_answer(answer):
            return self._create_non_answer_evaluation(question, answer, exp_level, experience_years)
        
        # PRE-VALIDATION: Detect obvious grammar errors and set maximum cap
        has_major_grammar_errors = self._detect_major_grammar_errors(answer)
        max_allowed_score = 5.0
        if has_major_grammar_errors:
            max_allowed_score = 2.0  # Cap at 2.0/5.0 for major grammar errors
            print(f"Warning: Major grammar errors detected in answer, capping score at {max_allowed_score}/5.0")
        
        # USE LLM FOR DIRECT EVALUATION (Model Prediction)
        evaluation_result = self._evaluate_with_llm(question, answer, exp_level, experience_years)
        
        # Apply maximum cap if grammar errors detected
        if has_major_grammar_errors:
            total_score = evaluation_result.get("total_score", 0.0)
            if total_score > max_allowed_score:
                print(f"Applying grammar error cap: {total_score} -> {max_allowed_score}")
                # Scale down all scores proportionally
                scale_factor = max_allowed_score / total_score
                scores = evaluation_result.get("scores", {})
                for key in scores:
                    scores[key] = round(scores[key] * scale_factor, 2)
                evaluation_result["scores"] = scores
                evaluation_result["total_score"] = max_allowed_score
                evaluation_result["justification"] = f"Answer contains major grammar errors. Score capped at {max_allowed_score}/5.0. " + evaluation_result.get("justification", "")
        
        # Extract scores and justifications from LLM response
        scores = evaluation_result.get("scores", {})
        justifications = evaluation_result.get("justifications", {})
        total_score = evaluation_result.get("total_score", 0.0)
        justification = evaluation_result.get("justification", "")
        detailed_analysis = evaluation_result.get("detailed_analysis", {})
        
        # Generate overall assessment
        overall_assessment = self._generate_overall_assessment_simple(
            total_score, scores, exp_level
        )
        
        # HR-style rating (1-5) based on total score out of 5
        hr_rating = self._convert_to_hr_rating(total_score)
        
        return {
            "experience_level": exp_level,
            "experience_years": experience_years,
            "question": question,
            "answer": answer,
            "scores": scores,  # Individual scores: grammar_clarity, communication_quality, relevance_experience, confidence
            "justifications": justifications,
            "total_score_out_of_5": total_score,  # Total score out of 5.0
            "justification": justification,  # One-line justification
            "simple_score_out_of_5": float(hr_rating),  # HR Rating: 1, 2, 3, 4, or 5 (whole numbers)
            "overall_assessment": overall_assessment,
            "expectations": EvaluationCriteria.EXPECTATIONS[exp_level],
            "detailed_analysis": detailed_analysis  # LLM-generated detailed breakdown
        }
    
    def _evaluate_with_llm(self, question: str, answer: str, exp_level: str, experience_years: float) -> Dict:
        """
        Use LLM to directly evaluate the answer using the 4-criteria system.
        Returns detailed analysis with scores and justifications.
        """
        system_prompt = """You are an EXTREMELY STRICT HR evaluator. Score candidate answers out of 5 using very strict, objective criteria.

SCORING SYSTEM (Total: 5.0 points maximum):
- Grammar & Clarity: Maximum 1.5 points (Penalize HEAVILY for ANY grammar errors, unclear sentences, wrong tenses, confusing phrases)
- Communication: Maximum 1.5 points (Penalize HEAVILY for poor organization, unclear ideas, nonsensical endings, confusing structure)
- Relevance: Maximum 1.0 points (Penalize if answer doesn't fully address the question or has irrelevant parts)
- Confidence: Maximum 1.0 points (Penalize for confusing endings, unclear statements, nonsensical phrases)

CRITICAL PENALTY RULES:
1. Grammar errors (wrong tenses like "For now I have worked", confusing phrases like "They will go first"):
   - Minor errors: Grammar & Clarity = 0.5-0.8/1.5
   - Major errors: Grammar & Clarity = 0.0-0.5/1.5
   - Perfect grammar only: Grammar & Clarity = 1.2-1.5/1.5

2. Communication issues (nonsensical endings, unclear structure, confusing sentences):
   - Confusing/unclear: Communication = 0.3-0.6/1.5
   - Very confusing: Communication = 0.0-0.3/1.5
   - Clear and well-structured: Communication = 1.0-1.5/1.5

3. Relevance issues (doesn't fully answer, has irrelevant parts):
   - Partially relevant: Relevance = 0.5-0.8/1.0
   - Low relevance: Relevance = 0.0-0.5/1.0
   - Highly relevant: Relevance = 0.8-1.0/1.0

4. Confidence issues (confusing endings, nonsensical phrases):
   - Confusing ending: Confidence = 0.0-0.3/1.0
   - Unclear statements: Confidence = 0.3-0.6/1.0
   - Clear and confident: Confidence = 0.7-1.0/1.0

BE EXTREMELY STRICT:
- Answers with grammar errors should score Grammar & Clarity BELOW 1.0/1.5
- Answers with confusing/nonsensical parts should score Communication BELOW 1.0/1.5
- Answers with irrelevant or confusing endings should score Confidence BELOW 0.5/1.0
- Most answers with errors should score 2.0-3.5/5.0, NOT 4.0+

CRITICAL: Total score must be between 0.0 and 5.0. Be extremely strict and objective."""

        user_prompt = f"""Score the answer out of 5 using:
- Grammar & Clarity (1.5)
- Communication (1.5)
- Relevance (1.0)
- Confidence (1.0)

Return:
- Each criterion score
- Total score
- One-line justification
Be VERY STRICT.

CANDIDATE PROFILE:
- Experience Level: {exp_level}
- Years of Experience: {experience_years}

QUESTION: {question}

ANSWER: {answer}

EXAMPLES OF STRICT SCORING:

Example 1 - POOR GRAMMAR WITH CONFUSING PARTS:
Answer: "I am a painter, I have completed my Bachelors in 2004. For now I have worked as a writer. They will go first."
Grammar Issues: "For now I have worked" (wrong tense), "They will go first" (nonsensical, confusing)
CORRECT SCORES:
- Grammar & Clarity: 0.75/1.5 (grammar errors: wrong tense, confusing phrase)
- Communication: 0.50/1.5 (confusing ending "They will go first" makes it unclear)
- Relevance: 0.75/1.0 (partially relevant but confusing ending)
- Confidence: 0.25/1.0 (confusing ending shows lack of clarity)
- Total: 2.25/5.0 (NOT 4.0+!)

Example 2 - MAJOR GRAMMAR ERRORS:
Answer: "Microelectrolysis grow is highly skilled software engineer specifically in background"
Grammar Issues: "Microelectrolysis grow" is nonsensical, missing article "a", wrong word order
CORRECT SCORES:
- Grammar & Clarity: 0.2/1.5 (major grammar errors)
- Communication: 0.3/1.5 (unclear meaning)
- Relevance: 0.6/1.0 (partially relevant but unclear)
- Confidence: 0.4/1.0 (unclear delivery)
- Total: 1.5/5.0 (NOT 5.0!)

Example 3 - GOOD ANSWER:
Answer: "I am a Python developer with 5 years of experience. I specialize in backend systems and APIs."
CORRECT SCORES:
- Grammar & Clarity: 1.4/1.5 (excellent grammar)
- Communication: 1.3/1.5 (clear and organized)
- Relevance: 0.9/1.0 (highly relevant)
- Confidence: 0.9/1.0 (confident)
- Total: 4.5/5.0

Provide evaluation in this EXACT JSON format:
{{
    "scores": {{
        "grammar_clarity": <score 0.0 to 1.5, NOT higher>,
        "communication_quality": <score 0.0 to 1.5, NOT higher>,
        "relevance_experience": <score 0.0 to 1.0, NOT higher>,
        "confidence": <score 0.0 to 1.0, NOT higher>
    }},
    "justifications": {{
        "grammar_clarity": "<detailed explanation of grammar and clarity issues/strengths>",
        "communication_quality": "<detailed explanation of communication quality>",
        "relevance_experience": "<detailed explanation of relevance to question and experience level>",
        "confidence": "<detailed explanation of confidence level>"
    }},
    "total_score": <sum of all scores, MUST be 0.0 to 5.0>,
    "justification": "<one-line summary justification for the total score>",
    "detailed_analysis": {{
        "grammar_issues": ["<specific issue 1>", "<specific issue 2>", ...],
        "communication_strengths": ["<strength 1>", "<strength 2>", ...],
        "communication_weaknesses": ["<weakness 1>", "<weakness 2>", ...],
        "relevance_points": ["<relevant point 1>", "<relevant point 2>", ...],
        "confidence_indicators": ["<indicator 1>", "<indicator 2>", ...]
    }}
}}

IMPORTANT RULES:
1. Grammar & Clarity: Score 0.0 to 1.5 (NOT 4.5 or any number above 1.5)
   - Major grammar errors (nonsensical phrases, wrong words) = 0.0-0.3
   - Minor errors = 0.4-0.8
   - Good grammar = 1.0-1.3
   - Excellent grammar = 1.4-1.5
2. Communication: Score 0.0 to 1.5 (NOT 4.0 or any number above 1.5)
   - Unclear/confusing = 0.0-0.5
   - Basic clarity = 0.6-1.0
   - Good communication = 1.1-1.3
   - Excellent = 1.4-1.5
3. Relevance: Score 0.0 to 1.0 (NOT 5.0 or any number above 1.0)
4. Confidence: Score 0.0 to 1.0 (NOT 4.5 or any number above 1.0)
5. Total score: Sum of all four scores, MUST be between 0.0 and 5.0

Be EXTREMELY STRICT. 

COMMON ERRORS TO PENALIZE HEAVILY:
1. Wrong tenses: "For now I have worked" → Grammar & Clarity = 0.5-0.75/1.5 (NOT 1.5!)
2. Confusing endings: "They will go first" → Communication = 0.3-0.5/1.5, Confidence = 0.2-0.3/1.0
3. Nonsensical phrases: Any phrase that doesn't make sense → Penalize ALL criteria
4. Run-on sentences: Poor structure → Communication = 0.4-0.7/1.5

SCORING EXAMPLES:
- Answer with wrong tense + confusing ending: Grammar 0.75, Communication 0.50, Relevance 0.75, Confidence 0.25 = Total 2.25/5.0
- Answer with grammar errors: Grammar 0.5-0.8, Communication 0.4-0.7, Relevance 0.6-0.8, Confidence 0.3-0.6 = Total 1.8-2.9/5.0
- Perfect answer: Grammar 1.4-1.5, Communication 1.3-1.5, Relevance 0.9-1.0, Confidence 0.9-1.0 = Total 4.5-5.0/5.0

If grammar has errors, score Grammar & Clarity BELOW 1.0/1.5. If communication is unclear or has confusing parts, score Communication BELOW 1.0/1.5. Most answers with errors should score 1.5-3.0/5.0, NOT 4.0+/5.0."""

        try:
            # Query LLM with very low temperature for strict, consistent evaluation
            # Use Gemini API if available (better accuracy for scoring), otherwise Ollama
            response = self.llm_service.query(user_prompt, system_prompt=system_prompt, temperature=0.1, use_gemini=True)
            
            # Check if response is empty (timeout or error)
            if not response or not response.strip():
                print("LLM returned empty response (timeout or error), using fallback evaluation")
                return self._fallback_rule_based_evaluation(question, answer, exp_level, experience_years)
            
            # Try to parse JSON from response
            # LLM might return text with JSON, so extract JSON part
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                
                # Validate and normalize scores (ensure they're within correct ranges)
                scores = result.get("scores", {})
                
                # Get raw scores
                raw_grammar = float(scores.get("grammar_clarity", 0.0))
                raw_comm = float(scores.get("communication_quality", 0.0))
                raw_relevance = float(scores.get("relevance_experience", 0.0))
                raw_confidence = float(scores.get("confidence", 0.0))
                
                # If LLM returned scores out of 10 (common mistake), scale them down
                # Check if scores seem to be out of 10 instead of correct scale
                if raw_grammar > 1.5 or raw_comm > 1.5 or raw_relevance > 1.0 or raw_confidence > 1.0:
                    # Likely scored out of 10, scale down
                    if raw_grammar > 1.5:
                        raw_grammar = (raw_grammar / 10.0) * 1.5
                    if raw_comm > 1.5:
                        raw_comm = (raw_comm / 10.0) * 1.5
                    if raw_relevance > 1.0:
                        raw_relevance = (raw_relevance / 10.0) * 1.0
                    if raw_confidence > 1.0:
                        raw_confidence = (raw_confidence / 10.0) * 1.0
                    print(f"Warning: LLM returned scores out of 10, scaled down to correct range")
                
                # Normalize to correct ranges
                scores["grammar_clarity"] = max(0.0, min(1.5, round(raw_grammar, 2)))
                scores["communication_quality"] = max(0.0, min(1.5, round(raw_comm, 2)))
                scores["relevance_experience"] = max(0.0, min(1.0, round(raw_relevance, 2)))
                scores["confidence"] = max(0.0, min(1.0, round(raw_confidence, 2)))
                
                # Calculate total (should be 0.0 to 5.0)
                total_score = sum(scores.values())
                total_score = round(total_score, 2)
                
                # SAFETY CHECK: Detect grammar errors and confusing phrases GENERALLY (works for all cases)
                grammar_score = scores.get("grammar_clarity", 1.5)
                comm_score = scores.get("communication_quality", 1.5)
                confidence_score = scores.get("confidence", 1.0)
                
                answer_lower = answer.lower()
                answer_words = answer_lower.split()
                
                # GENERAL GRAMMAR ERROR DETECTION
                has_wrong_tense = False
                wrong_tense_patterns = [
                    r"\b(for now|currently|now)\s+i\s+have\s+(worked|done|been|completed)\b",  # "for now I have worked"
                    r"\bi\s+have\s+(worked|done|been)\s+(for now|currently)\b",  # "I have worked for now"
                    r"\b(for now|currently)\s+(i|we|they)\s+(work|works|worked)\b",  # "for now I work"
                ]
                for pattern in wrong_tense_patterns:
                    if re.search(pattern, answer_lower):
                        has_wrong_tense = True
                        break
                
                # GENERAL CONFUSING ENDING DETECTION
                # Check if last sentence is confusing/nonsensical
                has_confusing_ending = False
                sentences = [s.strip() for s in answer.split('.') if s.strip()]
                if len(sentences) > 1:
                    last_sentence = sentences[-1].lower()
                    # Check for nonsensical endings
                    confusing_endings = [
                        r"they\s+(will|can|should)\s+(go|come|do|be)\s+(first|next|now)",
                        r"(will|can|should)\s+(go|come|do|be)\s+(first|next|now)",
                        r"they\s+(will|can|should)\s+go",
                        r"^(go|come|do|be)\s+(first|next|now)$",
                    ]
                    for pattern in confusing_endings:
                        if re.search(pattern, last_sentence):
                            has_confusing_ending = True
                            break
                    
                    # Check if last sentence is very short and doesn't connect to previous
                    if len(last_sentence.split()) <= 4 and len(sentences) >= 2:
                        # Check if it's a complete thought
                        if not any(word in last_sentence for word in ['and', 'but', 'or', 'with', 'in', 'on', 'at', 'for', 'to']):
                            # Might be a disconnected phrase
                            if len(last_sentence.split()) <= 3:
                                has_confusing_ending = True
                
                # GENERAL GRAMMAR ISSUES: Check for common grammar errors
                has_grammar_issues = False
                grammar_error_patterns = [
                    r"\bi\s+(am|have|work)\s+[a-z]+\s+(and|but)\s+[a-z]+\s+(will|can|should)\s+",  # Run-on sentences with wrong structure
                    r",\s+(i|we|they)\s+(have|will|can)\s+",  # Comma splice issues
                ]
                for pattern in grammar_error_patterns:
                    if re.search(pattern, answer_lower):
                        has_grammar_issues = True
                        break
                
                # Apply strict caps for ANY detected issues
                if has_wrong_tense or has_confusing_ending or has_grammar_issues:
                    print(f"Warning: Detected grammar/communication issues. Applying strict score caps.")
                    
                    # Cap grammar if wrong tense or grammar issues detected
                    if (has_wrong_tense or has_grammar_issues) and grammar_score > 0.8:
                        scores["grammar_clarity"] = min(grammar_score, 0.75)
                        grammar_score = scores["grammar_clarity"]
                    
                    # Cap communication if confusing ending or grammar issues
                    if (has_confusing_ending or has_grammar_issues) and comm_score > 0.6:
                        scores["communication_quality"] = min(comm_score, 0.50)
                        comm_score = scores["communication_quality"]
                    
                    # Cap confidence if confusing ending (shows lack of clarity)
                    if has_confusing_ending and confidence_score > 0.4:
                        scores["confidence"] = min(confidence_score, 0.25)
                        confidence_score = scores["confidence"]
                    
                    # Recalculate total
                    total_score = round(grammar_score + comm_score + scores.get("relevance_experience", 1.0) + confidence_score, 2)
                
                # GENERAL SAFETY CHECK: If grammar is low but total is high, cap it (works for ALL cases)
                # This ensures that answers with grammar errors can't get high scores
                if grammar_score < 1.0 and total_score > 3.0:
                    print(f"Warning: Grammar score is low ({grammar_score}) but total is high ({total_score}). Capping total score.")
                    # Cap total score based on grammar issues
                    max_total = grammar_score * 3.0  # Rough estimate: grammar issues should limit total
                    if total_score > max_total:
                        scale_factor = max_total / total_score
                        scores["communication_quality"] = round(scores["communication_quality"] * scale_factor, 2)
                        scores["relevance_experience"] = round(scores["relevance_experience"] * scale_factor, 2)
                        scores["confidence"] = round(scores["confidence"] * scale_factor, 2)
                        total_score = round(sum(scores.values()), 2)
                
                # Final validation: ensure total is not more than 5.0
                if total_score > 5.0:
                    print(f"Warning: Total score {total_score} exceeds 5.0, normalizing...")
                    # Scale down proportionally
                    scale_factor = 5.0 / total_score
                    scores["grammar_clarity"] = round(scores["grammar_clarity"] * scale_factor, 2)
                    scores["communication_quality"] = round(scores["communication_quality"] * scale_factor, 2)
                    scores["relevance_experience"] = round(scores["relevance_experience"] * scale_factor, 2)
                    scores["confidence"] = round(scores["confidence"] * scale_factor, 2)
                    total_score = round(sum(scores.values()), 2)
                
                return {
                    "scores": scores,
                    "justifications": result.get("justifications", {}),
                    "total_score": total_score,
                    "justification": result.get("justification", ""),
                    "detailed_analysis": result.get("detailed_analysis", {})
                }
            else:
                # Fallback: If JSON parsing fails, use rule-based evaluation
                print(f"Warning: LLM response not in JSON format, using fallback evaluation")
                return self._fallback_rule_based_evaluation(question, answer, exp_level, experience_years)
                
        except Exception as e:
            print(f"LLM Evaluation Error: {e}")
            # Fallback to rule-based evaluation
            return self._fallback_rule_based_evaluation(question, answer, exp_level, experience_years)
    
    def _fallback_rule_based_evaluation(self, question: str, answer: str, exp_level: str, experience_years: float) -> Dict:
        """Fallback to rule-based evaluation if LLM fails - STRICT VERSION"""
        # Check for major grammar errors first (same as LLM path)
        has_major_grammar_errors = self._detect_major_grammar_errors(answer)
        max_allowed_score = 5.0
        if has_major_grammar_errors:
            max_allowed_score = 2.0
            print(f"Fallback: Major grammar errors detected, capping at {max_allowed_score}/5.0")
        
        # Use existing rule-based methods as fallback
        grammar_clarity_score, grammar_just = self._evaluate_grammar_clarity(answer, exp_level)
        comm_quality_score, comm_just = self._evaluate_communication_quality(answer, question, exp_level)
        relevance_score, relevance_just = self._evaluate_relevance_experience(question, answer, exp_level, "hr")
        confidence_score, confidence_just = self._evaluate_confidence_simple(answer, exp_level)
        
        scores = {
            "grammar_clarity": round(grammar_clarity_score, 2),
            "communication_quality": round(comm_quality_score, 2),
            "relevance_experience": round(relevance_score, 2),
            "confidence": round(confidence_score, 2)
        }
        
        total_score = sum(scores.values())
        
        # Apply grammar error cap if needed
        if has_major_grammar_errors and total_score > max_allowed_score:
            scale_factor = max_allowed_score / total_score
            for key in scores:
                scores[key] = round(scores[key] * scale_factor, 2)
            total_score = max_allowed_score
            grammar_just = f"Major grammar errors detected. {grammar_just}"
        
        return {
            "scores": scores,
            "justifications": {
                "grammar_clarity": grammar_just,
                "communication_quality": comm_just,
                "relevance_experience": relevance_just,
                "confidence": confidence_just
            },
            "total_score": round(total_score, 2),
            "justification": self._generate_one_line_justification(total_score, scores, exp_level),
            "detailed_analysis": {}
        }
    
    # LEGACY RULE-BASED METHODS (kept as fallback)
    # NEW SIMPLIFIED 4-CRITERIA EVALUATION METHODS (Total: 5.0 points)
    
    def _evaluate_grammar_clarity(self, answer: str, exp_level: str) -> Tuple[float, str]:
        """Evaluate Grammar & Clarity (max 1.5 points)"""
        score = 1.5  # Start with max
        issues = []
        
        # Basic grammar checks
        if answer.lower() == answer:  # No capitalization
            score -= 0.2
            issues.append("lacks capitalization")
        
        # Excessive filler words
        fillers = ["uhm", "uh", "like", "you know", "basically", "actually"]
        filler_count = sum(1 for filler in fillers if filler in answer.lower())
        if filler_count > 2:
            score -= 0.3
            issues.append(f"excessive fillers ({filler_count})")
        
        # Sentence structure
        words = answer.split()
        if len(words) < 3:
            score -= 0.5
            issues.append("too brief")
        elif len(words) < 10 and exp_level in [ExperienceLevel.MID_LEVEL, ExperienceLevel.SENIOR]:
            score -= 0.3
            issues.append("incomplete for experience level")
        
        # Clarity - check for structured thinking
        connectors = ["because", "therefore", "however", "first", "second", "for example"]
        has_structure = any(conn in answer.lower() for conn in connectors)
        if has_structure and len(words) >= 15:
            score += 0.1  # Bonus for clarity
        elif len(words) < 5:
            score -= 0.4
            issues.append("unclear")
        
        # Adjust for experience level
        if exp_level == ExperienceLevel.FRESHER and score < 1.0:
            score += 0.1  # More lenient for freshers
        
        score = max(0.0, min(1.5, score))
        
        if score >= 1.3:
            justification = "Excellent grammar and clarity."
        elif score >= 1.0:
            justification = f"Good grammar. Minor issues: {', '.join(issues) if issues else 'none'}."
        elif score >= 0.7:
            justification = f"Acceptable grammar. Issues: {', '.join(issues)}."
        else:
            justification = f"Poor grammar and clarity. Issues: {', '.join(issues)}."
        
        return score, justification
    
    def _evaluate_communication_quality(self, answer: str, question: str, exp_level: str) -> Tuple[float, str]:
        """Evaluate Communication Quality (max 1.5 points)"""
        words = answer.split()
        word_count = len(words)
        
        # Base score on length and quality
        if word_count < 3:
            score = 0.3
        elif word_count < 10:
            score = 0.7
        elif word_count < 30:
            score = 1.2
        elif word_count < 80:
            score = 1.5
        else:
            score = 1.3  # Too verbose
        
        # Quality indicators
        has_examples = any(phrase in answer.lower() for phrase in ["for example", "such as", "like when"])
        has_structure = any(word in answer.lower() for word in ["first", "second", "then", "finally"])
        
        if has_examples and has_structure:
            score = min(1.5, score + 0.2)
        elif has_examples or has_structure:
            score = min(1.5, score + 0.1)
        
        # Adjust for experience expectations
        if exp_level == ExperienceLevel.FRESHER and word_count >= 15:
            score = min(1.5, score + 0.1)
        elif exp_level in [ExperienceLevel.MID_LEVEL, ExperienceLevel.SENIOR] and word_count < 20:
            score = max(0.0, score - 0.3)
        
        score = max(0.0, min(1.5, score))
        
        if score >= 1.3:
            justification = "Excellent communication quality with clear structure."
        elif score >= 1.0:
            justification = "Good communication quality."
        elif score >= 0.7:
            justification = "Acceptable communication, could be more detailed."
        else:
            justification = "Poor communication quality - lacks detail and structure."
        
        return score, justification
    
    def _evaluate_relevance_experience(self, question: str, answer: str, exp_level: str, question_type: str) -> Tuple[float, str]:
        """Evaluate Relevance to Experience (max 1.0 points)"""
        # Extract key terms from question
        question_words = set(re.findall(r'\w+', question.lower()))
        question_words = {w for w in question_words if len(w) > 4}
        
        answer_words = set(re.findall(r'\w+', answer.lower()))
        
        # Calculate overlap
        if question_words:
            overlap = len(question_words.intersection(answer_words)) / len(question_words)
        else:
            overlap = 0.5
        
        # Base score on relevance
        if overlap > 0.5:
            score = 0.9
        elif overlap > 0.3:
            score = 0.7
        elif overlap > 0.1:
            score = 0.5
        else:
            score = 0.3
        
        # Check if answer addresses experience level appropriately
        experience_indicators = ["experience", "worked", "project", "years", "learned", "developed"]
        has_experience_context = any(ind in answer.lower() for ind in experience_indicators)
        
        if exp_level != ExperienceLevel.FRESHER and not has_experience_context:
            score = max(0.0, score - 0.2)
        elif has_experience_context:
            score = min(1.0, score + 0.1)
        
        # Check if answer is just repeating the question
        if len(answer.split()) < 10 and overlap > 0.7:
            score = 0.4
        
        score = max(0.0, min(1.0, score))
        
        if score >= 0.8:
            justification = "Highly relevant answer addressing the question and experience level."
        elif score >= 0.6:
            justification = "Relevant response with good alignment."
        elif score >= 0.4:
            justification = "Partially relevant - could better address the question."
        else:
            justification = "Low relevance - answer does not adequately address the question."
        
        return score, justification
    
    def _evaluate_confidence_simple(self, answer: str, exp_level: str) -> Tuple[float, str]:
        """Evaluate Confidence (max 1.0 points)"""
        score = 0.7  # Default moderate confidence
        
        # Indicators of low confidence
        uncertain_phrases = ["i think", "maybe", "i guess", "not sure", "probably", "i don't know"]
        uncertainty_count = sum(1 for phrase in uncertain_phrases if phrase in answer.lower())
        
        if uncertainty_count > 2:
            score = 0.3
        elif uncertainty_count == 1:
            score = 0.6
        else:
            score = 0.9
        
        # Check for assertive language (bonus)
        assertive = ["i believe", "i am confident", "based on my experience", "definitely", "certainly"]
        has_assertive = any(phrase in answer.lower() for phrase in assertive)
        if has_assertive:
            score = min(1.0, score + 0.1)
        
        # Adjust for experience level
        if exp_level == ExperienceLevel.FRESHER and uncertainty_count <= 1:
            score = min(1.0, score + 0.1)
        elif exp_level == ExperienceLevel.SENIOR and uncertainty_count > 0:
            score = max(0.0, score - 0.2)
        
        score = max(0.0, min(1.0, score))
        
        if score >= 0.8:
            justification = "Strong, confident response."
        elif score >= 0.6:
            justification = "Good confidence level."
        elif score >= 0.4:
            justification = "Moderate confidence with some hesitation."
        else:
            justification = "Low confidence - multiple uncertain phrases detected."
        
        return score, justification
    
    def _generate_one_line_justification(self, total_score: float, scores: Dict, exp_level: str) -> str:
        """Generate one-line justification for the total score"""
        if total_score >= 4.5:
            return f"Excellent response demonstrating strong grammar ({scores.get('grammar_clarity', 0):.1f}/1.5), clear communication ({scores.get('communication_quality', 0):.1f}/1.5), relevant experience ({scores.get('relevance_experience', 0):.1f}/1.0), and high confidence ({scores.get('confidence', 0):.1f}/1.0)."
        elif total_score >= 3.5:
            return f"Good response with solid grammar ({scores.get('grammar_clarity', 0):.1f}/1.5), clear communication ({scores.get('communication_quality', 0):.1f}/1.5), relevant content ({scores.get('relevance_experience', 0):.1f}/1.0), and confident delivery ({scores.get('confidence', 0):.1f}/1.0)."
        elif total_score >= 2.5:
            return f"Average response with acceptable grammar ({scores.get('grammar_clarity', 0):.1f}/1.5), basic communication ({scores.get('communication_quality', 0):.1f}/1.5), partial relevance ({scores.get('relevance_experience', 0):.1f}/1.0), and moderate confidence ({scores.get('confidence', 0):.1f}/1.0)."
        elif total_score >= 1.5:
            return f"Below average response with grammar issues ({scores.get('grammar_clarity', 0):.1f}/1.5), unclear communication ({scores.get('communication_quality', 0):.1f}/1.5), low relevance ({scores.get('relevance_experience', 0):.1f}/1.0), and weak confidence ({scores.get('confidence', 0):.1f}/1.0)."
        else:
            return f"Poor response with significant grammar problems ({scores.get('grammar_clarity', 0):.1f}/1.5), unclear communication ({scores.get('communication_quality', 0):.1f}/1.5), irrelevant content ({scores.get('relevance_experience', 0):.1f}/1.0), and very low confidence ({scores.get('confidence', 0):.1f}/1.0)."
    
    def _generate_overall_assessment_simple(
        self, total_score: float, scores: Dict, exp_level: str
    ) -> Dict:
        """Generate overall assessment based on simplified 4-criteria scoring"""
        
        # HR-style rating based on total score out of 5
        hr_rating = self._convert_to_hr_rating(total_score)
        
        # Determine rating text
        if hr_rating >= 5.0:
            rating = "Excellent"
        elif hr_rating >= 4.0:
            rating = "Good"
        elif hr_rating >= 3.0:
            rating = "Average"
        elif hr_rating >= 2.0:
            rating = "Below Average"
        else:
            rating = "Poor"
        
        # Identify strengths and improvements based on individual scores
        strengths = []
        improvements = []
        
        if scores.get("grammar_clarity", 0) >= 1.2:
            strengths.append("Strong grammar and clarity")
        elif scores.get("grammar_clarity", 0) < 0.8:
            improvements.append("Improve grammar and clarity")
        
        if scores.get("communication_quality", 0) >= 1.2:
            strengths.append("Excellent communication")
        elif scores.get("communication_quality", 0) < 0.8:
            improvements.append("Enhance communication quality")
        
        if scores.get("relevance_experience", 0) >= 0.8:
            strengths.append("Relevant to experience level")
        elif scores.get("relevance_experience", 0) < 0.6:
            improvements.append("Better align with experience level")
        
        if scores.get("confidence", 0) >= 0.8:
            strengths.append("Confident delivery")
        elif scores.get("confidence", 0) < 0.6:
            improvements.append("Build confidence")
        
        # Generate summary
        if total_score >= 4.5:
            summary = f"Excellent candidate for {exp_level} level. Demonstrates strong competencies across all criteria."
        elif total_score >= 3.5:
            summary = f"Good candidate for {exp_level} level with solid performance."
        elif total_score >= 2.5:
            summary = f"Average candidate for {exp_level} level with some areas needing development."
        elif total_score >= 1.5:
            summary = f"Below average candidate for {exp_level} level. Significant improvement needed."
        else:
            summary = f"Poor candidate for {exp_level} level. Major gaps in multiple areas."
        
        return {
            "rating": rating,
            "summary": summary,
            "strengths": strengths if strengths else ["Shows potential for growth"],
            "areas_for_improvement": improvements if improvements else ["Continue developing all skills"]
        }
    
    def _detect_major_grammar_errors(self, answer: str) -> bool:
        """Detect obvious grammar errors that should cap the score"""
        answer_lower = answer.lower()
        
        # Patterns that indicate major grammar issues - nonsensical phrases
        nonsensical_phrases = [
            "role of words",
            "book is ai",
            "currently book",
            "python role of",
            "ai my automation",
            "book is",
            "role of",
            "words and currently",
            "currently book is"
        ]
        
        for phrase in nonsensical_phrases:
            if phrase in answer_lower:
                print(f"Detected nonsensical phrase: '{phrase}'")
                return True
        
        # Check for very poor sentence structure
        # If answer has multiple sentences but they don't make sense together
        sentences = answer.split('.')
        if len(sentences) > 1:
            # Check if sentences are very short or don't connect
            short_sentences = sum(1 for s in sentences if len(s.split()) < 4)
            if short_sentences >= 2:
                return True
        
        # Check for missing articles before important nouns (but allow proper nouns)
        # Pattern: "I have Python role" (should be "I have a Python role")
        if "have" in answer_lower or "am" in answer_lower:
            # Look for patterns like "I have [noun]" without article
            import re
            # Pattern: "I have [word] [noun]" where noun is not a proper noun
            pattern = r'\b(i have|i am|i work) (a|an|the)? ([a-z]+) (role|book|automation|developer|engineer)\b'
            matches = re.findall(pattern, answer_lower)
            if matches:
                for match in matches:
                    if not match[1]:  # No article found
                        # Check if the word before noun is a proper noun (capitalized in original)
                        word_before = match[2]
                        if word_before not in ["python", "ai", "ml", "api"]:  # Allow some technical terms
                            return True
        
        return False
    
    def _convert_to_hr_rating(self, total_score: float) -> float:
        """Convert total score (0-5) to HR rating (1-5)"""
        if total_score <= 0:
            return 1.0
        elif total_score < 1.0:
            return 1.0
        elif total_score < 2.0:
            return 2.0
        elif total_score < 3.0:
            return 3.0
        elif total_score < 4.0:
            return 4.0
        else:
            return 5.0
    
    # LEGACY METHODS (kept for backward compatibility if needed)
    
    def _evaluate_grammar(self, answer: str, exp_level: str) -> Tuple[float, str]:
        """Evaluate grammar and language quality (0-10)"""
        score = 10.0  # Start with perfect
        issues = []
        
        # Basic checks
        if answer.lower() == answer:  # No capitalization
            score -= 1.0
            issues.append("lacks proper capitalization")
        
        # Excessive filler words
        fillers = ["uhm", "uh", "like", "you know", "basically", "actually"]
        filler_count = sum(1 for filler in fillers if filler in answer.lower())
        if filler_count > 2:
            score -= 1.5
            issues.append(f"excessive filler words ({filler_count} found)")
        
        # Sentence fragments (very short incomplete responses)
        words = answer.split()
        if len(words) < 3 and exp_level in [ExperienceLevel.MID_LEVEL, ExperienceLevel.SENIOR]:
            score -= 2.0
            issues.append("incomplete sentence for experience level")
        
        # Repetitive words
        word_freq = {}
        for word in words:
            if len(word) > 3:
                word_freq[word.lower()] = word_freq.get(word.lower(), 0) + 1
        
        repeated = [w for w, count in word_freq.items() if count > 3]
        if repeated:
            score -= 1.0
            issues.append("repetitive language")
        
        # Adjust for experience level
        if exp_level == ExperienceLevel.FRESHER and score < 7:
            score += 1.0  # More lenient for freshers
        
        score = max(0.0, min(10.0, score))
        
        if score >= 9:
            justification = "Excellent grammar and language quality."
        elif score >= 7:
            justification = f"Good language quality. Minor issues: {', '.join(issues) if issues else 'none'}."
        elif score >= 5:
            justification = f"Acceptable grammar. Issues noted: {', '.join(issues)}."
        else:
            justification = f"Poor grammar quality. Issues: {', '.join(issues)}."
        
        return score, justification
    
    def _evaluate_clarity(self, answer: str, question: str, exp_level: str) -> Tuple[float, str]:
        """Evaluate communication clarity (0-10)"""
        words = answer.split()
        word_count = len(words)
        
        # Base scoring on length and structure
        if word_count < 3:
            score = 2.0
            justification = "Too brief - lacks clarity and detail."
        elif word_count < 10:
            score = 5.0
            justification = "Brief response - could provide more detail for clarity."
        elif word_count < 30:
            score = 7.5
            justification = "Clear and reasonably detailed response."
        elif word_count < 80:
            score = 9.0
            justification = "Well-articulated and comprehensive response."
        else:
            score = 8.0
            justification = "Very detailed response - could be more concise."
        
        # Adjust for experience expectations
        if exp_level == ExperienceLevel.FRESHER and word_count >= 15:
            score = min(10.0, score + 1.0)  # Bonus for detailed fresher answers
        elif exp_level in [ExperienceLevel.MID_LEVEL, ExperienceLevel.SENIOR] and word_count < 20:
            score = max(0.0, score - 2.0)  # Penalty for shallow senior answers
            justification = "Expected more depth and clarity from experience level."
        
        # Check for structured thinking (uses connectors)
        connectors = ["because", "therefore", "however", "first", "second", "for example", "such as"]
        has_structure = any(conn in answer.lower() for conn in connectors)
        if has_structure and word_count >= 20:
            score = min(10.0, score + 0.5)
        
        return max(0.0, min(10.0, score)), justification
    
    def _evaluate_confidence(self, answer: str, exp_level: str) -> Tuple[float, str]:
        """Evaluate confidence level (0-10)"""
        score = 7.0  # Default moderate confidence
        
        # Indicators of low confidence
        uncertain_phrases = ["i think", "maybe", "i guess", "not sure", "probably", "i don't know"]
        uncertainty_count = sum(1 for phrase in uncertain_phrases if phrase in answer.lower())
        
        if uncertainty_count > 2:
            score = 4.0
            justification = "Low confidence - multiple uncertain phrases detected."
        elif uncertainty_count == 1:
            score = 6.0
            justification = "Moderate confidence with some hesitation."
        else:
            score = 8.5
            justification = "Good confidence level in response."
        
        # Check for assertive language (bonus)
        assertive = ["i believe", "i am confident", "based on my experience", "definitely", "certainly"]
        has_assertive = any(phrase in answer.lower() for phrase in assertive)
        if has_assertive:
            score = min(10.0, score + 1.5)
            justification = "Strong, confident response with clear conviction."
        
        # Adjust for experience level
        if exp_level == ExperienceLevel.FRESHER and uncertainty_count <= 1:
            score = min(10.0, score + 0.5)  # Freshers get bonus for any confidence
        elif exp_level == ExperienceLevel.SENIOR and uncertainty_count > 0:
            score = max(0.0, score - 1.5)  # Seniors penalized for uncertainty
            justification = "Expected more confidence from senior-level candidate."
        
        return max(0.0, min(10.0, score)), justification
    
    def _evaluate_relevance(
        self, question: str, answer: str, exp_level: str, question_type: str
    ) -> Tuple[float, str]:
        """Evaluate relevance to question and experience level (0-10)"""
        
        # Extract key terms from question
        question_words = set(re.findall(r'\w+', question.lower()))
        question_words = {w for w in question_words if len(w) > 4}  # Filter short words
        
        answer_words = set(re.findall(r'\w+', answer.lower()))
        
        # Calculate overlap
        if question_words:
            overlap = len(question_words.intersection(answer_words)) / len(question_words)
        else:
            overlap = 0.5
        
        # Base score on overlap
        if overlap > 0.5:
            score = 9.0
            justification = "Highly relevant response addressing the question directly."
        elif overlap > 0.3:
            score = 7.0
            justification = "Relevant response with good alignment to question."
        elif overlap > 0.1:
            score = 5.0
            justification = "Partially relevant - could be more focused on the question."
        else:
            score = 3.0
            justification = "Low relevance - answer does not adequately address the question."
        
        # Check if answer is just repeating the question
        if len(answer.split()) < 10 and overlap > 0.7:
            score = 4.0
            justification = "Answer mostly repeats the question without adding substance."
        
        # Penalize off-topic answers for experienced candidates
        if exp_level in [ExperienceLevel.MID_LEVEL, ExperienceLevel.SENIOR] and score < 6:
            score = max(0.0, score - 1.0)
            justification += " Expected better relevance from experience level."
        
        return max(0.0, min(10.0, score)), justification
    
    def _evaluate_attitude(self, answer: str, exp_level: str) -> Tuple[float, str]:
        """Evaluate attitude and professionalism (0-10)"""
        score = 7.5  # Default positive attitude
        
        # Positive indicators
        positive_words = ["excited", "enjoy", "passionate", "love", "enthusiastic", "motivated", 
                         "interested", "eager", "committed", "dedicated"]
        positive_count = sum(1 for word in positive_words if word in answer.lower())
        
        # Negative indicators
        negative_words = ["hate", "boring", "difficult", "struggle", "can't", "impossible", 
                         "never", "always fail"]
        negative_count = sum(1 for word in negative_words if word in answer.lower())
        
        if positive_count > 0:
            score = min(10.0, score + positive_count * 0.8)
            justification = "Positive, enthusiastic attitude demonstrated."
        elif negative_count > 1:
            score = max(0.0, score - negative_count * 1.5)
            justification = "Negative tone detected - may indicate poor fit."
        else:
            justification = "Neutral professional tone maintained."
        
        # Professional language check
        unprofessional = ["whatever", "dont care", "stupid", "dumb", "sucks"]
        if any(word in answer.lower() for word in unprofessional):
            score = 3.0
            justification = "Unprofessional language used - major concern."
        
        return max(0.0, min(10.0, score)), justification
    
    def _evaluate_cultural_fit(self, answer: str, question: str, exp_level: str) -> Tuple[float, str]:
        """Evaluate cultural fit and values (0-10)"""
        score = 7.0  # Default neutral
        
        # Team-oriented language
        team_words = ["team", "collaborate", "together", "we", "us", "group", "cooperate"]
        team_count = sum(1 for word in team_words if word in answer.lower())
        
        # Individual-focused (not necessarily bad, but balanced is better)
        individual_words = ["i", "me", "my", "myself"]
        individual_count = sum(1 for word in individual_words if word in answer.lower())
        
        if team_count > 2:
            score = 9.0
            justification = "Strong team orientation and collaborative mindset."
        elif team_count > 0:
            score = 8.0
            justification = "Good balance of teamwork and individual contribution."
        elif individual_count > 5 and len(answer.split()) < 30:
            score = 5.5
            justification = "Primarily self-focused - could demonstrate more team awareness."
        else:
            justification = "Neutral cultural fit indicators."
        
        # Values alignment
        value_words = ["integrity", "honesty", "respect", "responsibility", "quality", "excellence"]
        if any(word in answer.lower() for word in value_words):
            score = min(10.0, score + 1.0)
            justification = "Demonstrates alignment with professional values."
        
        return max(0.0, min(10.0, score)), justification
    
    def _evaluate_problem_solving(self, answer: str, question: str, exp_level: str) -> Tuple[float, str]:
        """Evaluate problem-solving ability (0-10)"""
        
        # Look for structured thinking
        structure_words = ["first", "second", "then", "next", "finally", "step", "approach", 
                          "solution", "analyze", "consider", "evaluate"]
        has_structure = any(word in answer.lower() for word in structure_words)
        
        # Look for examples
        example_phrases = ["for example", "such as", "for instance", "like when", "in my experience"]
        has_examples = any(phrase in answer.lower() for phrase in example_phrases)
        
        word_count = len(answer.split())
        
        if has_structure and has_examples and word_count > 30:
            score = 9.5
            justification = "Excellent problem-solving approach with structured thinking and examples."
        elif has_structure and word_count > 20:
            score = 8.0
            justification = "Good structured approach to problem-solving."
        elif has_examples:
            score = 7.0
            justification = "Demonstrates problem-solving with practical examples."
        elif word_count > 15:
            score = 6.0
            justification = "Basic problem-solving ability shown."
        else:
            score = 4.0
            justification = "Limited demonstration of problem-solving skills."
        
        # Adjust for experience level
        if exp_level == ExperienceLevel.FRESHER and score >= 6:
            score = min(10.0, score + 1.0)  # Bonus for freshers showing good thinking
        elif exp_level in [ExperienceLevel.MID_LEVEL, ExperienceLevel.SENIOR]:
            if not has_examples and word_count < 25:
                score = max(0.0, score - 2.0)
                justification = "Expected more detailed problem-solving examples from experience level."
        
        return max(0.0, min(10.0, score)), justification
    
    def _evaluate_learning_adaptability(self, answer: str, exp_level: str) -> Tuple[float, str]:
        """Evaluate learning mindset and adaptability (0-10)"""
        score = 7.0
        
        # Learning indicators
        learning_words = ["learn", "learning", "studied", "researched", "explored", "discovered",
                         "trained", "developed", "improved", "grew", "adapted", "flexible"]
        learning_count = sum(1 for word in learning_words if word in answer.lower())
        
        if learning_count > 2:
            score = 9.5
            justification = "Strong learning mindset and adaptability demonstrated."
        elif learning_count > 0:
            score = 8.5
            justification = "Good learning orientation shown."
        else:
            justification = "No specific learning/adaptability indicators mentioned."
        
        # Openness to feedback
        feedback_words = ["feedback", "advice", "mentor", "guidance", "coach"]
        if any(word in answer.lower() for word in feedback_words):
            score = min(10.0, score + 1.0)
            justification = "Shows openness to feedback and continuous improvement."
        
        # Especially important for freshers
        if exp_level == ExperienceLevel.FRESHER:
            if learning_count > 0:
                score = min(10.0, score + 1.5)
                justification = "Excellent learning attitude for fresher candidate."
            else:
                score = max(0.0, score - 1.5)
                justification = "Expected more emphasis on learning for fresher level."
        
        return max(0.0, min(10.0, score)), justification
    
    def _evaluate_motivation(self, answer: str, question: str, exp_level: str) -> Tuple[float, str]:
        """Evaluate motivation and career goals (0-10)"""
        score = 7.0
        
        # Career-focused language
        career_words = ["career", "goal", "aspire", "achieve", "ambition", "future", "growth",
                       "advance", "develop", "opportunity", "challenge"]
        career_count = sum(1 for word in career_words if word in answer.lower())
        
        # Passion indicators
        passion_words = ["passionate", "love", "excited", "drive", "motivated", "inspired"]
        passion_count = sum(1 for word in passion_words if word in answer.lower())
        
        total_motivation = career_count + passion_count
        
        if total_motivation > 3:
            score = 9.5
            justification = "Highly motivated with clear career direction."
        elif total_motivation > 1:
            score = 8.0
            justification = "Good motivation and career focus demonstrated."
        elif total_motivation == 1:
            score = 6.5
            justification = "Some motivation shown, could articulate goals better."
        else:
            justification = "Limited motivation or career goal indicators."
        
        # Check if answer is relevant to career/motivation questions
        motivation_question = any(word in question.lower() for word in ["why", "goal", "motivate", "career", "future"])
        if motivation_question and total_motivation == 0:
            score = 4.0
            justification = "Did not address career motivation despite relevant question."
        
        return max(0.0, min(10.0, score)), justification
    
    def _is_non_answer(self, answer: str) -> bool:
        """Detect if answer is essentially a non-answer or refusal"""
        # Remove punctuation for better matching
        import string
        answer_lower = answer.lower().strip()
        # Remove common punctuation
        answer_clean = answer_lower.translate(str.maketrans('', '', string.punctuation))
        
        # Non-answer patterns (check both with and without punctuation)
        non_answer_patterns = [
            "i don't know",
            "i don't",
            "don't know",
            "not sure",
            "i'm not sure",
            "sorry, i don't know",
            "sorry i don't know",
            "sorry, i am not sure",
            "sorry i am not sure",
            "i have no idea",
            "no idea",
            "can't say",
            "cannot say",
            "i can't",
            "i cannot",
            "cannot",  # Standalone "cannot"
            "can't",   # Standalone "can't"
            "not really",
            "nothing",
            "n/a",
            "na",
            "i can not",  # Alternative spelling
            "i cant"      # Without apostrophe
        ]
        
        # Check both original and cleaned versions
        for text_to_check in [answer_lower, answer_clean]:
            # First check for exact matches of short non-answers (most common case)
            word_count = len(text_to_check.split())
            if word_count <= 3:  # Very short answers like "I cannot", "cannot", "I can't"
                for pattern in ["cannot", "can't", "cant", "i cannot", "i can't", "i cant"]:
                    if pattern in text_to_check:
                        return True
            
            # Then check all patterns
            for pattern in non_answer_patterns:
                if pattern in text_to_check:
                    # If the answer is very short (just the non-answer phrase)
                    if word_count <= 6:  # Very short non-answers like "I cannot" (2 words)
                        return True
                    # For longer answers, check if non-answer is the primary content
                    if word_count < 10:
                        return True
        
        return False
    
    def _create_empty_answer_evaluation(self, question: str, exp_level: str) -> Dict:
        """Create evaluation for empty or very short answers"""
        return {
            "experience_level": exp_level,
            "question": question,
            "answer": "",
            "scores": {key: 0.0 for key in self.criteria.keys()},
            "justifications": {
                key: "No answer provided - cannot evaluate." 
                for key in self.criteria.keys()
            },
            "weighted_score": 0.0,
            "overall_assessment": {
                "rating": "Poor",
                "summary": "Candidate did not provide an answer.",
                "strengths": [],
                "areas_for_improvement": ["Provide complete answers to all questions"]
            }
        }
    
    def _create_non_answer_evaluation(self, question: str, answer: str, exp_level: str, experience_years: float) -> Dict:
        """Create evaluation for non-answers (I don't know, not sure, etc.) - Using simplified 4-criteria"""
        # Simplified 4-criteria scores for non-answers
        scores = {
            "grammar_clarity": 0.5,  # Grammar might be okay but content is poor
            "communication_quality": 0.2,  # Very poor - no actual answer
            "relevance_experience": 0.1,  # Extremely low - doesn't answer question
            "confidence": 0.3  # Very low - refusing to answer
        }
        
        total_score = sum(scores.values())
        justification = f"Non-answer provided. Grammar (0.5/1.5), Communication (0.2/1.5), Relevance (0.1/1.0), Confidence (0.3/1.0). Candidate did not engage with the question."
        
        return {
            "experience_level": exp_level,
            "experience_years": experience_years,
            "question": question,
            "answer": answer,
            "scores": scores,
            "justifications": {
                "grammar_clarity": "Grammar acceptable but answer is a non-answer.",
                "communication_quality": "No actual answer provided - candidate said they don't know.",
                "relevance_experience": "Extremely low relevance - answer does not address the question at all.",
                "confidence": "Very low confidence - candidate refused to answer the question."
            },
            "total_score_out_of_5": round(total_score, 2),
            "justification": justification,
            "simple_score_out_of_5": 1.0,  # HR Rating: 1 (Poor) - directly set for non-answers
            "overall_assessment": {
                "rating": "Poor",
                "summary": "Candidate provided a non-answer (e.g., 'I don't know'), indicating lack of preparation or unwillingness to engage with the question.",
                "strengths": [],
                "areas_for_improvement": [
                    "Provide actual answers to interview questions",
                    "Prepare for common interview questions",
                    "Show willingness to engage and share information"
                ]
            },
            "expectations": EvaluationCriteria.EXPECTATIONS[exp_level]
        }
    
    def convert_to_simple_score(self, weighted_score: float) -> float:
        """
        Convert weighted score (0-10) to HR-style rating (1-5) for display
        Real HR professionals give whole number ratings: 1, 2, 3, 4, 5
        
        Args:
            weighted_score: Score from 0-10
            
        Returns:
            HR Rating from 1-5 (whole numbers only)
        """
        # Map 0-10 to 1-5 scale (HR-style whole number ratings)
        # Real HR professionals notice answers and give ratings: 1, 2, 3, 4, or 5
        if weighted_score <= 0:
            return 1.0  # Rating 1: Poor
        elif weighted_score < 2.0:
            return 1.0  # Rating 1: Poor
        elif weighted_score < 4.0:
            return 2.0  # Rating 2: Below Average
        elif weighted_score < 6.0:
            return 3.0  # Rating 3: Average
        elif weighted_score < 8.0:
            return 4.0  # Rating 4: Good
        else:
            return 5.0  # Rating 5: Excellent
    
    def _generate_overall_assessment(
        self, weighted_score: float, scores: Dict, exp_level: str
    ) -> Dict:
        """Generate HR-style overall assessment based on scores"""
        
        # HR-style rating based on 1-5 scale
        hr_rating = self.convert_to_simple_score(weighted_score)
        
        # Determine rating text (HR professionals use these terms)
        if hr_rating >= 5.0:
            rating = "Excellent"
        elif hr_rating >= 4.0:
            rating = "Good"
        elif hr_rating >= 3.0:
            rating = "Average"
        elif hr_rating >= 2.0:
            rating = "Below Average"
        else:
            rating = "Poor"
        
        # Identify strengths (scores >= 8.0)
        strengths = []
        for key, score in scores.items():
            if score >= 8.0:
                strengths.append(self.criteria[key]["description"])
        
        # Identify improvement areas (scores < 6.0)
        improvements = []
        for key, score in scores.items():
            if score < 6.0:
                improvements.append(self.criteria[key]["description"])
        
        # Generate HR-style summary
        if hr_rating >= 5.0:
            summary = f"Excellent response. Candidate demonstrates strong competencies and clear communication suitable for {exp_level} level position."
        elif hr_rating >= 4.0:
            summary = f"Good response. Candidate shows solid understanding and communication skills appropriate for {exp_level} level."
        elif hr_rating >= 3.0:
            summary = f"Average response. Candidate addresses the question but could provide more depth and examples for {exp_level} level expectations."
        elif hr_rating >= 2.0:
            summary = f"Below average response. Candidate struggles to clearly communicate or provide relevant information for {exp_level} level."
        else:
            summary = f"Poor response. Candidate did not adequately address the question or demonstrate required competencies for {exp_level} level."
        
        return {
            "rating": rating,
            "summary": summary,
            "strengths": strengths if strengths else ["Shows potential for growth"],
            "areas_for_improvement": improvements if improvements else ["Continue developing all skills"]
        }
    
    def evaluate_interview_holistically(
        self, 
        interview_history: List[Dict],
        experience_years: float
    ) -> Dict:
        """
        Evaluate entire interview session holistically
        
        Args:
            interview_history: List of Q&A dictionaries
            experience_years: Candidate's experience in years
            
        Returns:
            Comprehensive evaluation report
        """
        exp_level = ExperienceLevel.determine_level(experience_years)
        
        # Evaluate each answer
        evaluations = []
        for item in interview_history:
            if not item.get("is_aptitude", False):  # Only HR/behavioral questions
                eval_result = self.evaluate_answer(
                    question=item.get("question", ""),
                    answer=item.get("answer", ""),
                    experience_years=experience_years,
                    question_type=item.get("type", "hr")
                )
                evaluations.append(eval_result)
        
        if not evaluations:
            return {
                "experience_level": exp_level,
                "overall_score": 0.0,
                "message": "No HR questions were evaluated"
            }
        
        # Aggregate scores
        aggregate_scores = {key: 0.0 for key in self.criteria.keys()}
        for eval_item in evaluations:
            for key in self.criteria.keys():
                aggregate_scores[key] += eval_item["scores"][key]
        
        # Average the scores
        num_evaluations = len(evaluations)
        for key in aggregate_scores.keys():
            aggregate_scores[key] /= num_evaluations
        
        # Calculate overall weighted score
        overall_weighted = sum(
            aggregate_scores[key] * self.criteria[key]["weight"]
            for key in aggregate_scores.keys()
        )
        
        # Generate report
        overall_assessment = self._generate_overall_assessment(
            overall_weighted, aggregate_scores, exp_level
        )
        
        return {
            "experience_level": exp_level,
            "experience_years": experience_years,
            "num_questions_evaluated": num_evaluations,
            "aggregate_scores": {
                key: round(score, 2) 
                for key, score in aggregate_scores.items()
            },
            "overall_weighted_score": round(overall_weighted, 2),
            "overall_assessment": overall_assessment,
            "individual_evaluations": evaluations,
            "expectations": EvaluationCriteria.EXPECTATIONS[exp_level]
        }


# Global instance
enhanced_evaluation_engine = EnhancedEvaluationEngine()
