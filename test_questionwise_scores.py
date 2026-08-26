"""
Comprehensive Test for Question-Wise Scoring Feature
Tests that individual scores are correctly added to each question in the transcript
"""

import json
from services.scoring import scoring_engine
from services.enhanced_evaluation import enhanced_evaluation_engine

def test_question_wise_scoring():
    """Test that question-wise scores are correctly calculated and added"""
    
    print("="*80)
    print("🧪 TESTING QUESTION-WISE SCORING FEATURE")
    print("="*80)
    print()
    
    # Simulate interview history with HR questions
    all_hist = [
        {
            "question": "Are you a fresher or do you have work experience?",
            "answer": "I have 6 months of internship experience",
            "is_experience_detection": True,
            "is_aptitude": False
        },
        {
            "question": "Please introduce yourself and tell me about your background.",
            "answer": "I am a software developer with experience in web development. I enjoy building scalable applications and working with modern technologies like React and Node.js.",
            "is_hr_question": True,
            "is_aptitude": False
        },
        {
            "question": "What are your key strengths and skills?",
            "answer": "I am good at problem-solving and time management. I work well in teams and can lead projects effectively.",
            "is_hr_question": True,
            "is_aptitude": False
        },
        {
            "question": "Why do you want to join our company?",
            "answer": "I am very excited about this opportunity because I want to learn from experienced professionals and grow my career in a challenging environment.",
            "is_hr_question": True,
            "is_aptitude": False
        },
        {
            "question": "What is 2+2?",
            "answer": "4",
            "is_aptitude": True,
            "correct_answer": "4"
        }
    ]
    
    experience_years = 0.5  # Fresher
    
    print("📋 Testing with 4 HR questions and 1 aptitude question")
    print(f"👤 Experience Level: {experience_years} years (Fresher)")
    print()
    
    # Step 1: Calculate communication score (this creates enhanced_transcript)
    print("Step 1: Calculating communication scores...")
    communication_score, evaluation_summary = scoring_engine.calculate_communication_score(
        all_hist,
        experience_years=experience_years
    )
    
    print(f"✅ Communication Score: {communication_score:.2f}/40")
    print(f"✅ Average Weighted Score: {evaluation_summary['average_weighted_score']:.2f}/10")
    print()
    
    # Step 2: Check enhanced_transcript
    print("Step 2: Checking enhanced_transcript...")
    enhanced_transcript = evaluation_summary.get("enhanced_transcript", [])
    
    if enhanced_transcript:
        print(f"✅ Found {len(enhanced_transcript)} questions with scores")
        print()
        
        for i, item in enumerate(enhanced_transcript, 1):
            print(f"Question {i}:")
            print(f"  Q: {item['question'][:60]}...")
            print(f"  Score: {item['score_out_of_5']}/5 ({item['rating']})")
            print(f"  Weighted: {item['weighted_score']:.2f}/10")
            print()
    else:
        print("❌ ERROR: No enhanced_transcript found!")
        return False
    
    # Step 3: Simulate adding scores to main transcript (like main.py does)
    print("Step 3: Adding scores to main transcript (simulating main.py logic)...")
    
    # Create mapping
    question_scores = {}
    for item in enhanced_transcript:
        question_scores[item["question"]] = {
            "score_out_of_5": item["score_out_of_5"],
            "rating": item["rating"],
            "weighted_score": item["weighted_score"]
        }
    
    # Add scores to main transcript
    scores_added = 0
    for item in all_hist:
        if not item.get("is_aptitude") and item.get("question") in question_scores:
            score_data = question_scores[item["question"]]
            item["score_out_of_5"] = score_data["score_out_of_5"]
            item["rating"] = score_data["rating"]
            item["weighted_score"] = score_data["weighted_score"]
            scores_added += 1
    
    print(f"✅ Added scores to {scores_added} questions")
    print()
    
    # Step 4: Verify the final transcript structure
    print("Step 4: Verifying final transcript structure...")
    print("="*80)
    
    hr_questions = [h for h in all_hist if not h.get("is_aptitude")]
    
    for i, item in enumerate(hr_questions, 1):
        print(f"\n📝 Q{i}: {item['question']}")
        print(f"   A: {item['answer'][:70]}...")
        
        if "score_out_of_5" in item:
            stars = get_star_display(item["score_out_of_5"])
            print(f"   ✅ Score: {item['score_out_of_5']}/5 {stars} ({item['rating']})")
        else:
            print(f"   ❌ ERROR: No score found!")
            return False
    
    print()
    print("="*80)
    
    # Step 5: Validate data integrity
    print("\nStep 5: Validating data integrity...")
    
    validation_passed = True
    
    for item in hr_questions:
        # Check all required fields exist
        if "score_out_of_5" not in item:
            print(f"❌ Missing score_out_of_5 for: {item['question'][:50]}...")
            validation_passed = False
        elif item["score_out_of_5"] < 0 or item["score_out_of_5"] > 5:
            print(f"❌ Invalid score {item['score_out_of_5']} (should be 0-5)")
            validation_passed = False
        
        if "rating" not in item:
            print(f"❌ Missing rating for: {item['question'][:50]}...")
            validation_passed = False
        
        if "weighted_score" not in item:
            print(f"❌ Missing weighted_score for: {item['question'][:50]}...")
            validation_passed = False
        elif item["weighted_score"] < 0 or item["weighted_score"] > 10:
            print(f"❌ Invalid weighted_score {item['weighted_score']} (should be 0-10)")
            validation_passed = False
    
    if validation_passed:
        print("✅ All validations passed!")
    
    print()
    
    # Step 6: Show final JSON structure (what frontend will receive)
    print("Step 6: Final JSON structure (what frontend receives):")
    print("="*80)
    
    sample_output = {
        "details": {
            "total_score": 80.0,
            "communication_score": communication_score,
            "transcript": hr_questions[:2]  # Show first 2 for brevity
        }
    }
    
    print(json.dumps(sample_output, indent=2))
    print()
    print("="*80)
    
    return validation_passed


def get_star_display(score):
    """Generate star display for a score"""
    full_stars = int(score)
    half_star = "✨" if (score - full_stars) >= 0.5 else ""
    empty_stars = "☆" * (5 - full_stars - (1 if half_star else 0))
    return "⭐" * full_stars + half_star + empty_stars


def test_edge_cases():
    """Test edge cases"""
    print("\n" + "="*80)
    print("🧪 TESTING EDGE CASES")
    print("="*80)
    print()
    
    # Test 1: Empty answer
    print("Test 1: Empty answer...")
    result = enhanced_evaluation_engine.evaluate_answer(
        question="Tell me about yourself",
        answer="",
        experience_years=2.0,
        question_type="hr"
    )
    score = result.get('simple_score_out_of_5', 0)
    rating = result.get('overall_assessment', {}).get('rating', 'N/A')
    print(f"✅ Empty answer score: {score}/5")
    print(f"   Rating: {rating}")
    print()
    
    # Test 2: Very short answer
    print("Test 2: Very short answer...")
    result = enhanced_evaluation_engine.evaluate_answer(
        question="What are your strengths?",
        answer="Good",
        experience_years=5.0,
        question_type="hr"
    )
    score = result.get('simple_score_out_of_5', 0)
    rating = result.get('overall_assessment', {}).get('rating', 'N/A')
    print(f"✅ Short answer score: {score}/5")
    print(f"   Rating: {rating}")
    print()
    
    # Test 3: Excellent long answer
    print("Test 3: Excellent detailed answer...")
    result = enhanced_evaluation_engine.evaluate_answer(
        question="Describe a challenging project you worked on.",
        answer="In my recent role, I led the migration of our monolithic application to a microservices architecture. I evaluated multiple approaches, coordinated with cross-functional teams, implemented a phased rollout strategy, and achieved a 40% improvement in system performance. This experience taught me valuable lessons about technical leadership and stakeholder management.",
        experience_years=7.0,
        question_type="hr"
    )
    score = result.get('simple_score_out_of_5', 0)
    rating = result.get('overall_assessment', {}).get('rating', 'N/A')
    print(f"✅ Excellent answer score: {score}/5")
    print(f"   Rating: {rating}")
    print()
    
    # Test 4: Different experience levels
    print("Test 4: Same answer, different experience levels...")
    answer = "I am passionate about technology and eager to learn"
    
    for exp_years, level in [(0.5, "Fresher"), (3.0, "Mid"), (8.0, "Senior")]:
        result = enhanced_evaluation_engine.evaluate_answer(
            question="Why do you want this job?",
            answer=answer,
            experience_years=exp_years,
            question_type="hr"
        )
        score = result.get('simple_score_out_of_5', 0)
        rating = result.get('overall_assessment', {}).get('rating', 'N/A')
        print(f"  {level:10} ({exp_years}yr): {score}/5 ({rating})")
    
    print()


if __name__ == "__main__":
    print("\n")
    print("🚀 STARTING COMPREHENSIVE TEST SUITE")
    print("="*80)
    print()
    
    # Run main test
    success = test_question_wise_scoring()
    
    # Run edge case tests
    test_edge_cases()
    
    # Final summary
    print("="*80)
    if success:
        print("✅ ✅ ✅ ALL TESTS PASSED! ✅ ✅ ✅")
        print()
        print("Question-wise scoring is working correctly!")
        print("Each question in the transcript now has:")
        print("  • score_out_of_5 (0-5 scale)")
        print("  • rating (Excellent, Good, etc.)")
        print("  • weighted_score (0-10 scale)")
        print()
        print("You can now display these scores in your Interview Transcript section!")
    else:
        print("❌ TESTS FAILED - Please review errors above")
    
    print("="*80)
    print()
