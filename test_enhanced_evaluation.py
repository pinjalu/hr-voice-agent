"""
Test script for Enhanced HR Interview Evaluation AI
Demonstrates how the evaluation system works with different experience levels
"""

from services.enhanced_evaluation import enhanced_evaluation_engine, ExperienceLevel
import json


def print_separator(title=""):
    """Print a visual separator"""
    print("\n" + "="*80)
    if title:
        print(f"  {title}")
        print("="*80)
    print()


def print_evaluation(eval_result):
    """Pretty print an evaluation result"""
    print(f"📊 Experience Level: {eval_result['experience_level']} ({eval_result.get('experience_years', 0)} years)")
    print(f"📝 Question: {eval_result['question']}")
    print(f"💬 Answer: {eval_result['answer']}")
    print()
    
    print("🎯 Scores by Criteria:")
    for criterion, score in eval_result['scores'].items():
        justification = eval_result['justifications'][criterion]
        bar = "█" * int(score) + "░" * (10 - int(score))
        print(f"  {criterion:25} [{bar}] {score:.1f}/10")
        print(f"    └─ {justification}")
    
    print()
    print(f"⭐ Weighted Score: {eval_result['weighted_score']:.2f}/10")
    print()
    
    assessment = eval_result['overall_assessment']
    print(f"🏆 Overall Rating: {assessment['rating']}")
    print(f"📄 Summary: {assessment['summary']}")
    
    if assessment['strengths']:
        print(f"💪 Strengths:")
        for strength in assessment['strengths']:
            print(f"   ✓ {strength}")
    
    if assessment['areas_for_improvement']:
        print(f"📈 Areas for Improvement:")
        for area in assessment['areas_for_improvement']:
            print(f"   ⚠ {area}")


def test_fresher_candidate():
    """Test evaluation for a fresher candidate"""
    print_separator("TEST 1: FRESHER CANDIDATE - Good Answer")
    
    question = "Why do you want to join our company?"
    answer = "I am very excited about this opportunity because I want to learn from experienced professionals and grow my skills in software development. I am passionate about technology and eager to contribute to meaningful projects."
    
    evaluation = enhanced_evaluation_engine.evaluate_answer(
        question=question,
        answer=answer,
        experience_years=0.5,
        question_type="hr"
    )
    
    print_evaluation(evaluation)


def test_fresher_poor_answer():
    """Test evaluation for a fresher with poor answer"""
    print_separator("TEST 2: FRESHER CANDIDATE - Poor Answer")
    
    question = "What are your career goals?"
    answer = "I dont know maybe something"
    
    evaluation = enhanced_evaluation_engine.evaluate_answer(
        question=question,
        answer=answer,
        experience_years=0.5,
        question_type="hr"
    )
    
    print_evaluation(evaluation)


def test_senior_candidate():
    """Test evaluation for a senior candidate"""
    print_separator("TEST 3: SENIOR CANDIDATE - Good Answer")
    
    question = "Describe a challenging technical decision you made recently."
    answer = "In my recent project, I led the decision to migrate our monolith architecture to microservices. I evaluated multiple approaches including strangler pattern and big bang migration. Based on our team's capacity and business requirements, I proposed a phased approach. First, we identified bounded contexts, then extracted the most critical services incrementally. This allowed us to maintain system stability while modernizing our stack. The result was a 40% improvement in deployment frequency and better team autonomy."
    
    evaluation = enhanced_evaluation_engine.evaluate_answer(
        question=question,
        answer=answer,
        experience_years=8.0,
        question_type="technical"
    )
    
    print_evaluation(evaluation)


def test_senior_poor_answer():
    """Test evaluation for a senior candidate with poor answer"""
    print_separator("TEST 4: SENIOR CANDIDATE - Poor Answer")
    
    question = "How do you handle team conflicts?"
    answer = "I think I just try to solve it"
    
    evaluation = enhanced_evaluation_engine.evaluate_answer(
        question=question,
        answer=answer,
        experience_years=8.0,
        question_type="hr"
    )
    
    print_evaluation(evaluation)


def test_mid_level_candidate():
    """Test evaluation for a mid-level candidate"""
    print_separator("TEST 5: MID-LEVEL CANDIDATE - Good Answer")
    
    question = "Tell me about a time you had to learn a new technology quickly."
    answer = "Last year, our team needed to integrate a new payment gateway API. I had no prior experience with it, but I took the initiative to research the documentation, built a proof of concept in two days, and shared my learnings with the team. I created a step-by-step guide that helped us complete the integration smoothly. This experience taught me the importance of structured learning and knowledge sharing."
    
    evaluation = enhanced_evaluation_engine.evaluate_answer(
        question=question,
        answer=answer,
        experience_years=4.0,
        question_type="hr"
    )
    
    print_evaluation(evaluation)


def test_empty_answer():
    """Test evaluation for empty answer"""
    print_separator("TEST 6: EMPTY ANSWER")
    
    question = "What motivates you?"
    answer = ""
    
    evaluation = enhanced_evaluation_engine.evaluate_answer(
        question=question,
        answer=answer,
        experience_years=2.0,
        question_type="hr"
    )
    
    print_evaluation(evaluation)


def test_holistic_evaluation():
    """Test holistic interview evaluation"""
    print_separator("TEST 7: HOLISTIC INTERVIEW EVALUATION")
    
    interview_history = [
        {
            "question": "Tell me about yourself.",
            "answer": "I am a software engineer with 3 years of experience in full-stack development. I enjoy building scalable web applications and working with modern technologies like React and Node.js.",
            "is_aptitude": False
        },
        {
            "question": "What is your biggest strength?",
            "answer": "I believe my biggest strength is problem-solving. I approach challenges systematically, breaking them down into smaller parts and finding efficient solutions.",
            "is_aptitude": False
        },
        {
            "question": "Where do you see yourself in 5 years?",
            "answer": "I aspire to become a technical lead, mentoring junior developers and contributing to architectural decisions. I want to continue learning and growing in my career.",
            "is_aptitude": False
        },
        {
            "question": "Describe a time you failed.",
            "answer": "In my first project, I underestimated the complexity of a feature and missed the deadline. I learned the importance of better estimation and communication. Since then, I always break down tasks and seek feedback early.",
            "is_aptitude": False
        }
    ]
    
    # Note: This would be called automatically by the scoring engine in the actual system
    # Here we're just demonstrating individual evaluations
    print("Evaluating 4 HR questions for a Junior candidate (3 years experience)...\n")
    
    total_score = 0
    for i, item in enumerate(interview_history, 1):
        print(f"\n--- Question {i} ---")
        evaluation = enhanced_evaluation_engine.evaluate_answer(
            question=item["question"],
            answer=item["answer"],
            experience_years=3.0,
            question_type="hr"
        )
        print(f"Q: {item['question']}")
        print(f"A: {item['answer']}")
        print(f"Weighted Score: {evaluation['weighted_score']:.2f}/10")
        print(f"Rating: {evaluation['overall_assessment']['rating']}")
        total_score += evaluation['weighted_score']
    
    avg_score = total_score / len(interview_history)
    communication_score = (avg_score / 10.0) * 40
    
    print()
    print("="*80)
    print(f"📊 INTERVIEW SUMMARY")
    print("="*80)
    print(f"Average Weighted Score: {avg_score:.2f}/10")
    print(f"Communication Score (out of 40): {communication_score:.2f}")
    print(f"Assuming Aptitude Score of 45/60...")
    print(f"TOTAL INTERVIEW SCORE: {45 + communication_score:.2f}/100")
    print()


def test_experience_level_classification():
    """Test experience level classification"""
    print_separator("TEST 8: EXPERIENCE LEVEL CLASSIFICATION")
    
    test_years = [0, 0.5, 1, 2, 3, 4, 6, 8, 10]
    
    print("Testing experience level classification:")
    print()
    for years in test_years:
        level = ExperienceLevel.determine_level(years)
        print(f"  {years:4.1f} years → {level}")
    print()


if __name__ == "__main__":
    print_separator("🚀 ENHANCED HR INTERVIEW EVALUATION AI - TEST SUITE")
    print("This test suite demonstrates the evaluation system with various scenarios.")
    print("Each test shows how the AI evaluates answers based on experience level.")
    
    # Run all tests
    test_experience_level_classification()
    test_fresher_candidate()
    test_fresher_poor_answer()
    test_mid_level_candidate()
    test_senior_candidate()
    test_senior_poor_answer()
    test_empty_answer()
    test_holistic_evaluation()
    
    print_separator("✅ ALL TESTS COMPLETED")
    print("Review the results above to see how the evaluation system works.")
    print("The system adjusts expectations based on experience level and provides")
    print("detailed justifications for each score across 9 comprehensive criteria.")
    print()
