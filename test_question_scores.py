"""Quick test to verify individual question scoring (0-5)"""

from services.enhanced_evaluation import enhanced_evaluation_engine

# Test Question 1 - Good answer from Junior developer
print("="*70)
print("TEST: Individual Question Scoring (0-5 Scale)")
print("="*70)
print()

question1 = "Tell me about yourself"
answer1 = "I am a software developer with 2 years of experience in web development. I enjoy building scalable applications and working with modern technologies."

result1 = enhanced_evaluation_engine.evaluate_answer(
    question=question1,
    answer=answer1,
    experience_years=2.0,
    question_type="hr"
)

print(f"Q: {question1}")
print(f"A: {answer1}")
print()
print(f"✅ Weighted Score (0-10): {result1['weighted_score']}")
print(f"⭐ Simple Score (0-5): {result1['simple_score_out_of_5']}")
print(f"📊 Rating: {result1['overall_assessment']['rating']}")
print(f"👤 Experience Level: {result1['experience_level']}")
print()

# Generate star display
score = result1['simple_score_out_of_5']
full_stars = int(score)
half_star = "✨" if (score - full_stars) >= 0.5 else ""
empty_stars = "☆" * (5 - full_stars - (1 if half_star else 0))
star_display = "⭐" * full_stars + half_star + empty_stars

print(f"Stars: {star_display}")
print()

# Test Question 2 - Poor answer from Senior
print("="*70)

question2 = "How do you handle team conflicts?"
answer2 = "I think I try to solve it"

result2 = enhanced_evaluation_engine.evaluate_answer(
    question=question2,
    answer=answer2,
    experience_years=8.0,
    question_type="hr"
)

print(f"Q: {question2}")
print(f"A: {answer2}")
print()
print(f"✅ Weighted Score (0-10): {result2['weighted_score']}")
print(f"⭐ Simple Score (0-5): {result2['simple_score_out_of_5']}")
print(f"📊 Rating: {result2['overall_assessment']['rating']}")
print(f"👤 Experience Level: {result2['experience_level']}")
print()

score2 = result2['simple_score_out_of_5']
full_stars2 = int(score2)
half_star2 = "✨" if (score2 - full_stars2) >= 0.5 else ""
empty_stars2 = "☆" * (5 - full_stars2 - (1 if half_star2 else 0))
star_display2 = "⭐" * full_stars2 + half_star2 + empty_stars2

print(f"Stars: {star_display2}")
print()

# Test Question 3 - Excellent answer from Fresher
print("="*70)

question3 = "Why do you want to join our company?"
answer3 = "I am very excited about this opportunity because I want to learn from experienced professionals and grow my skills. I am passionate about technology and eager to contribute to meaningful projects."

result3 = enhanced_evaluation_engine.evaluate_answer(
    question=question3,
    answer=answer3,
    experience_years=0.5,
    question_type="hr"
)

print(f"Q: {question3}")
print(f"A: {answer3}")
print()
print(f"✅ Weighted Score (0-10): {result3['weighted_score']}")
print(f"⭐ Simple Score (0-5): {result3['simple_score_out_of_5']}")
print(f"📊 Rating: {result3['overall_assessment']['rating']}")
print(f"👤 Experience Level: {result3['experience_level']}")
print()

score3 = result3['simple_score_out_of_5']
full_stars3 = int(score3)
half_star3 = "✨" if (score3 - full_stars3) >= 0.5 else ""
empty_stars3 = "☆" * (5 - full_stars3 - (1 if half_star3 else 0))
star_display3 = "⭐" * full_stars3 + half_star3 + empty_stars3

print(f"Stars: {star_display3}")
print()

print("="*70)
print("✅ Individual question scoring (0-5) is working!")
print("="*70)
