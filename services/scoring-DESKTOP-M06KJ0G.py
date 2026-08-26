import re
from .llm import llm_service
from .enhanced_evaluation import enhanced_evaluation_engine, ExperienceLevel

class ScoringEngine:
    def calculate_aptitude_score(self, aptitude_history):
        """
        Calculate aptitude score (60% of total).
        Uses fast matching first, LLM only as fallback.
        """
        if not aptitude_history:
            return 0.0, []
        
        correct_count = 0
        total_questions = len(aptitude_history)
        results = []

        for item in aptitude_history:
            q_text = item["question"]
            ans_text = item["answer"].strip()
            correct_ans = item.get("correct_answer", "")
            question_options = item.get("options", {})  # REQUIRED: All questions must have options
            
            # REQUIRED: Validate question has 4 options
            if not question_options or len(question_options) != 4 or not all(key in question_options for key in ['A', 'B', 'C', 'D']):
                print(f"Warning: Question missing 4 options in scoring: {q_text}")
                # Skip scoring for invalid questions
                results.append({
                    "question": q_text,
                    "given": ans_text if ans_text else "Not Answered",
                    "correct": correct_ans,
                    "is_correct": False
                })
                continue
            
            is_correct = False
            if correct_ans:
                # 1. PREPARE CLEAN STRINGS
                ans_lower = ans_text.lower().strip()
                correct_lower = correct_ans.lower().strip()
                ans_clean = ans_lower.rstrip(".?! ").strip()
                correct_clean = correct_lower.strip()
                
                # 2. EXTRACT OPTION LETTER FROM ANSWER (STRICT)
                # Look for patterns like "option a", "option b", "a)", "b)", "answer is b", etc.
                extracted_option = None
                option_patterns = [
                    r'\boption\s+([a-d])\b',  # "option a", "option b"
                    r'\b([a-d])\s*\)',        # "a)", "b)"
                    r'\banswer\s+is\s+([a-d])\b',  # "answer is b"
                    r'\bkey\s+([a-d])\b',     # "key b"
                    r'^([a-d])$',             # Just "a" or "b" alone
                    r'\b([a-d])\s*$',         # "a" or "b" at end
                ]
                
                for pattern in option_patterns:
                    match = re.search(pattern, ans_clean)
                    if match:
                        extracted_option = match.group(1).lower()
                        break
                
                # If no pattern found but answer is very short, check if it's just a letter
                if not extracted_option and len(ans_clean) <= 2:
                    if ans_clean in ['a', 'b', 'c', 'd']:
                        extracted_option = ans_clean
                
                # 3. CHECK FOR OPTION-BASED ANSWER (A/B/C/D) - STRICT MATCHING
                if extracted_option:
                    # Normalize correct answer to option letter
                    correct_option_letter = None
                    correct_option_value = None
                    
                    if correct_clean in ['a', 'b', 'c', 'd']:
                        correct_option_letter = correct_clean
                        # Get the value of the correct option
                        correct_key = correct_clean.upper()
                        if correct_key in question_options:
                            correct_option_value = str(question_options[correct_key]).lower().strip()
                    elif correct_clean.upper() in ['A', 'B', 'C', 'D']:
                        correct_option_letter = correct_clean.lower()
                        # Get the value of the correct option
                        if correct_clean.upper() in question_options:
                            correct_option_value = str(question_options[correct_clean.upper()]).lower().strip()
                    else:
                        # Check if correct answer is stored as option key in question_options
                        for key in ['A', 'B', 'C', 'D']:
                            if key in question_options:
                                option_value = str(question_options[key]).lower().strip()
                                if option_value == correct_clean:
                                    correct_option_letter = key.lower()
                                    correct_option_value = option_value
                                    break
                    
                    # STRICT: Only mark correct if extracted option matches correct option letter
                    if correct_option_letter:
                        if extracted_option == correct_option_letter:
                            is_correct = True
                        else:
                            # Explicitly wrong - they said one option but correct is another
                            is_correct = False
                
                # 3b. CHECK IF ANSWER MATCHES OPTION VALUE (e.g., candidate says "25" when correct is B=25)
                if not is_correct and not extracted_option:
                    # Check if answer matches any option value, and if that option is the correct one
                    for key in ['A', 'B', 'C', 'D']:
                        if key in question_options:
                            option_value = str(question_options[key]).lower().strip()
                            # Check if answer matches this option's value
                            if ans_clean == option_value or ans_clean in option_value or option_value in ans_clean:
                                # Check if this option is the correct answer
                                correct_option_letter = None
                                if correct_clean in ['a', 'b', 'c', 'd']:
                                    correct_option_letter = correct_clean.upper()
                                elif correct_clean.upper() in ['A', 'B', 'C', 'D']:
                                    correct_option_letter = correct_clean.upper()
                                else:
                                    # Find which option has the correct value
                                    for opt_key in ['A', 'B', 'C', 'D']:
                                        if opt_key in question_options:
                                            opt_val = str(question_options[opt_key]).lower().strip()
                                            if opt_val == correct_clean:
                                                correct_option_letter = opt_key
                                                break
                                
                                # If this option matches the correct answer, mark as correct
                                if correct_option_letter and key == correct_option_letter:
                                    is_correct = True
                                    break
                    
                    # Also check numeric matching for option values (e.g., "25" matches option B=25)
                    if not is_correct:
                        given_nums = re.findall(r'\d+\.?\d*', ans_clean)
                        if given_nums:
                            # Check each option's value for numeric match
                            for key in ['A', 'B', 'C', 'D']:
                                if key in question_options:
                                    option_value = str(question_options[key]).lower().strip()
                                    option_nums = re.findall(r'\d+\.?\d*', option_value)
                                    
                                    # Check if numbers match
                                    if option_nums and given_nums:
                                        given_num = float(given_nums[0])
                                        option_num = float(option_nums[0])
                                        if abs(given_num - option_num) < 0.1:
                                            # Check if this option is the correct answer
                                            correct_option_letter = None
                                            if correct_clean in ['a', 'b', 'c', 'd']:
                                                correct_option_letter = correct_clean.upper()
                                            elif correct_clean.upper() in ['A', 'B', 'C', 'D']:
                                                correct_option_letter = correct_clean.upper()
                                            else:
                                                # Find which option has the correct value
                                                for opt_key in ['A', 'B', 'C', 'D']:
                                                    if opt_key in question_options:
                                                        opt_val = str(question_options[opt_key]).lower().strip()
                                                        if opt_val == correct_clean:
                                                            correct_option_letter = opt_key
                                                            break
                                            
                                            # If this option matches the correct answer, mark as correct
                                            if correct_option_letter and key == correct_option_letter:
                                                is_correct = True
                                                break
                
                # 4. NUMERIC MATCHING (Strict for Math/Logic) - ONLY if no option letter was extracted
                # Skip if we already extracted an option letter (means they're choosing an option, not giving a number)
                is_numeric_q = False
                if not is_correct and not extracted_option:
                    given_nums_str = re.findall(r'\d+\.?\d*', ans_lower)
                    correct_nums_str = re.findall(r'\d+\.?\d*', correct_lower)
                    
                    is_numeric_q = len(correct_nums_str) > 0 and len(correct_clean) < 10
                    num_match = False
                    
                    if correct_nums_str and given_nums_str:
                        # STRICT: Must match the primary number
                        correct_primary = float(correct_nums_str[0])
                        given_primary = float(given_nums_str[0])
                        # Only match if very close (within 0.1) or exact whole number match
                        if abs(correct_primary - given_primary) < 0.1:
                            num_match = True
                    
                    if num_match:
                        is_correct = True
                
                # 5. TEXT/SEMANTIC MATCHING (VERY STRICT - Only if no option letter and not numeric)
                # Skip this entirely if they mentioned an option letter (they're choosing, not describing)
                if not is_correct and not extracted_option and not is_numeric_q:
                    # Only allow exact match or very high similarity for text answers
                    if ans_clean == correct_clean:
                        is_correct = True
                    else:
                        # Very strict word overlap - must be > 0.9 (90% match)
                        ans_words = set(re.findall(r'\w+', ans_clean))
                        correct_words = set(re.findall(r'\w+', correct_clean))
                        
                        if correct_words and len(correct_words) > 2:  # Only for multi-word answers
                            overlap = len(ans_words.intersection(correct_words)) / len(correct_words)
                            if overlap > 0.9:  # Very strict threshold
                                is_correct = True
                        
                        # 6. LLM FALLBACK (VERY RESTRICTIVE - Only for long descriptive answers)
                        # Skip LLM if answer is too short or contains option references
                        if not is_correct and len(ans_clean) > 15 and 'option' not in ans_clean:
                            try:
                                is_llm_correct = llm_service.evaluate_aptitude_answer(
                                    question=q_text,
                                    given_answer=ans_text,
                                    correct_answer=correct_ans
                                )
                                if is_llm_correct:
                                    is_correct = True
                            except:
                                # If LLM fails, don't mark as correct
                                pass

            if is_correct:
                correct_count += 1
            
            results.append({
                "question": q_text,
                "given": ans_text if ans_text else "Not Answered",
                "correct": correct_ans,
                "is_correct": is_correct
            })

        score_percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        aptitude_score = (score_percentage / 100) * 60
        return aptitude_score, results

    def calculate_communication_score(self, all_answers, experience_years=0):
        """
        Calculate communication score (40% of total) using Enhanced Evaluation AI.
        
        This method evaluates candidates based on their experience level across 9 comprehensive criteria:
        1. Grammar & Language Quality
        2. Communication Clarity
        3. Confidence Level
        4. Relevance to Question & Experience
        5. Attitude & Professionalism
        6. Cultural Fit & Values
        7. Problem-Solving Ability
        8. Learning & Adaptability
        9. Motivation & Career Goals
        
        Adjusts expectations based on experience level:
        - Fresher (0-1 years): Focus on willingness to learn, clarity, enthusiasm
        - Junior (1-3 years): Expect some hands-on exposure and correct terminology
        - Mid-level (3-6 years): Require practical examples and structured thinking
        - Senior (6+ years): Demand strategic thinking, leadership, deep technical clarity
        """
        if not all_answers:
            return 0.0, {}
        
        # Filter only HR questions (exclude aptitude, intro, and experience detection)
        relevant_answers = [h for h in all_answers if h.get("is_hr_question", False)]
        if not relevant_answers:
            # Fallback if no HR questions found
            relevant_answers = []
        
        if not relevant_answers:
            return 0.0, {}
        
        # Use enhanced evaluation engine for comprehensive assessment
        # SIMPLE METHOD: Average HR ratings (1-5) directly instead of weighted scores
        total_hr_rating = 0.0
        detailed_evaluations = []
        enhanced_transcript = []  # Store Q&A with scores
        
        for item in relevant_answers:
            question = item.get("question", "")
            answer = item.get("answer", "")
            question_type = "hr"  # Can be enhanced to detect technical vs behavioral
            
            # Evaluate this answer comprehensively
            evaluation = enhanced_evaluation_engine.evaluate_answer(
                question=question,
                answer=answer,
                experience_years=experience_years,
                question_type=question_type
            )
            
            detailed_evaluations.append(evaluation)
            
            # Get the detailed total score out of 5.0 (not the rounded HR rating)
            # This uses the actual detailed score (e.g., 4.4, 4.9, 3.0) not the whole number rating (e.g., 4, 5, 3)
            total_score_out_of_5 = evaluation.get("total_score_out_of_5", evaluation.get("simple_score_out_of_5", 0.0))
            hr_rating = evaluation["simple_score_out_of_5"]  # Keep for display (whole number 1-5)
            
            # Use detailed total_score_out_of_5 for accurate average calculation
            total_hr_rating += total_score_out_of_5
            
            # Add enhanced Q&A with score for transcript display
            enhanced_qa = {
                "question": question,
                "answer": answer,
                "score_out_of_5": hr_rating,  # Individual question HR rating (1-5) for display
                "total_score_out_of_5": total_score_out_of_5,  # Detailed total score out of 5.0 (e.g., 4.4, 4.9, 3.0)
                "justification": evaluation.get("justification", ""),  # One-line justification
                "scores": evaluation.get("scores", {}),  # Individual criterion scores
                "rating": evaluation["overall_assessment"]["rating"],
                "is_hr_question": True
            }
            enhanced_transcript.append(enhanced_qa)
        
        # ACCURATE AVERAGE: Average detailed total scores (out of 5.0) directly
        # Example: (4.4 + 4.9 + 3.0) / 3 = 4.1/5
        avg_hr_rating = total_hr_rating / len(relevant_answers) if relevant_answers else 0.0
        
        # SIMPLE CONVERSION: Convert average HR rating to communication score (0-40)
        # Formula: (Average HR Rating / 5) × 40
        # Example: (4.1 / 5) × 40 = 32.8/40
        communication_score = (avg_hr_rating / 5.0) * 40
        
        # Compile detailed breakdown
        evaluation_summary = {
            "experience_level": ExperienceLevel.determine_level(experience_years),
            "experience_years": experience_years,
            "num_questions_evaluated": len(relevant_answers),
            "average_hr_rating": round(avg_hr_rating, 2),  # Simple average HR rating (1-5)
            "average_total_score": round(sum(e.get("total_score_out_of_5", e.get("simple_score_out_of_5", 0)) for e in detailed_evaluations) / len(detailed_evaluations) if detailed_evaluations else 0.0, 2),  # Average total score out of 5.0
            "communication_score_out_of_40": round(communication_score, 2),
            "detailed_evaluations": detailed_evaluations,
            "criteria_breakdown": self._aggregate_criteria_scores(detailed_evaluations),
            "enhanced_transcript": enhanced_transcript  # Q&A pairs with individual scores
        }
        
        return communication_score, evaluation_summary
    
    def _aggregate_criteria_scores(self, evaluations):
        """Aggregate scores across all evaluations for each criterion"""
        if not evaluations:
            return {}
        
        criteria_sums = {}
        for eval_item in evaluations:
            for criterion, score in eval_item["scores"].items():
                if criterion not in criteria_sums:
                    criteria_sums[criterion] = []
                criteria_sums[criterion].append(score)
        
        # Calculate averages
        criteria_averages = {}
        for criterion, scores in criteria_sums.items():
            criteria_averages[criterion] = {
                "average_score": round(sum(scores) / len(scores), 2),
                "num_evaluations": len(scores)
            }
        
        return criteria_averages

    def get_final_verdict(self, aptitude_score, communication_score):
        """
        Calculate final score and recommendation.
        
        Args:
            aptitude_score: Score out of 60
            communication_score: Score out of 40
        
        Returns: (total_score, recommendation, strengths, improvement_areas)
        """
        total_score = aptitude_score + communication_score
        
        # Determine recommendation
        if total_score >= 80:
            recommendation = "Strong Hire"
        elif total_score >= 65:
            recommendation = "Hire"
        elif total_score >= 50:
            recommendation = "Borderline"
        else:
            recommendation = "Reject"
        
        # Determine strengths and improvement areas
        strengths = []
        improvement_areas = []
        
        # Aptitude analysis
        if aptitude_score >= 48:  # 80% of 60
            strengths.append("Strong analytical and problem-solving skills")
        elif aptitude_score >= 36:  # 60% of 60
            strengths.append("Good aptitude for logical reasoning")
        else:
            improvement_areas.append("Needs improvement in analytical thinking and problem-solving")
        
        # Communication analysis
        if communication_score >= 32:  # 80% of 40
            strengths.append("Excellent communication clarity and confidence")
        elif communication_score >= 24:  # 60% of 40
            strengths.append("Clear and structured communication")
        else:
            improvement_areas.append("Should work on communication clarity and confidence")
        
        # Overall balance
        if abs(aptitude_score - communication_score * 1.5) < 10:
            strengths.append("Well-balanced technical and soft skills")
        
        # Ensure we have at least one item in each list
        if not strengths:
            strengths.append("Shows potential for growth")
        
        if not improvement_areas:
            improvement_areas.append("Continue developing all skills")
        
        return total_score, recommendation, strengths, improvement_areas

    # Legacy method for backward compatibility
    def calculate_interview_heuristics(self, interview_history):
        """
        Legacy method - kept for backward compatibility.
        Now redirects to calculate_communication_score.
        """
        comm_score = self.calculate_communication_score(interview_history)
        # Return as two separate scores for compatibility
        return comm_score / 2, comm_score / 2

scoring_engine = ScoringEngine()
