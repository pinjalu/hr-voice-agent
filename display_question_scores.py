"""
Helper script to demonstrate how to access and display individual question scores

This shows how to retrieve the 0-5 scores for each question from the evaluation results
"""

import json
from models.database import SessionLocal, FinalResult


def display_question_scores(result_id: int):
    """
    Display individual question scores from a candidate's interview result
    
    Args:
        result_id: The ID of the FinalResult to display
    """
    db = SessionLocal()
    try:
        # Get the result from database
        result = db.query(FinalResult).get(result_id)
        
        if not result:
            print(f"❌ Result ID {result_id} not found")
            return
        
        # Parse the transcript JSON
        data = json.loads(result.transcript)
        
        print("="*80)
        print(f"📊 CANDIDATE INTERVIEW SCORES")
        print("="*80)
        print(f"Candidate ID: {result.candidate_id}")
        print(f"Total Score: {result.total_score:.1f}/100")
        print(f"Recommendation: {result.status}")
        print()
        
        # Get evaluation summary
        eval_summary = data.get("evaluation_summary", {})
        experience_level = eval_summary.get("experience_level", "Unknown")
        experience_years = eval_summary.get("experience_years", 0)
        
        print(f"👤 Experience Level: {experience_level} ({experience_years} years)")
        print()
        
        # Display individual question scores
        enhanced_transcript = eval_summary.get("enhanced_transcript", [])
        
        if enhanced_transcript:
            print("📝 INTERVIEW QUESTIONS WITH SCORES (0-5):")
            print("-" * 80)
            
            for i, qa in enumerate(enhanced_transcript, 1):
                question = qa.get("question", "")
                answer = qa.get("answer", "")
                score = qa.get("score_out_of_5", 0)
                rating = qa.get("rating", "N/A")
                
                # Visual score representation
                full_stars = int(score)
                half_star = 1 if (score - full_stars) >= 0.5 else 0
                empty_stars = 5 - full_stars - half_star
                
                star_display = "⭐" * full_stars
                if half_star:
                    star_display += "✨"
                star_display += "☆" * empty_stars
                
                print(f"\nQ{i}: {question}")
                print(f"A{i}: {answer[:100]}{'...' if len(answer) > 100 else ''}")
                print(f"Score: {score}/5 {star_display} ({rating})")
            
            print()
            print("=" * 80)
            
        else:
            print("⚠️ No enhanced transcript with scores found")
            print("   (This might be from an older interview before the scoring update)")
            print()
            
            # Fallback: show basic transcript
            basic_transcript = data.get("transcript", [])
            if basic_transcript:
                print("📝 BASIC TRANSCRIPT (No Individual Scores):")
                print("-" * 80)
                hr_questions = [item for item in basic_transcript if not item.get("is_aptitude")]
                
                for i, item in enumerate(hr_questions, 1):
                    print(f"\nQ{i}: {item.get('question', 'N/A')}")
                    print(f"A{i}: {item.get('answer', 'N/A')[:100]}...")
        
        # Display criteria breakdown
        criteria_breakdown = eval_summary.get("criteria_breakdown", {})
        if criteria_breakdown:
            print()
            print("📊 DETAILED CRITERIA BREAKDOWN:")
            print("-" * 80)
            
            for criterion, data in criteria_breakdown.items():
                score = data.get("average_score", 0)
                bar_length = int(score)
                bar = "█" * bar_length + "░" * (10 - bar_length)
                
                # Convert criterion name to readable format
                readable_name = criterion.replace("_", " ").title()
                print(f"{readable_name:30} [{bar}] {score:.1f}/10")
        
        print()
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()


def get_frontend_json_example(result_id: int):
    """
    Generate JSON structure for frontend display
    
    Args:
        result_id: The ID of the FinalResult
        
    Returns:
        Dictionary suitable for frontend consumption
    """
    db = SessionLocal()
    try:
        result = db.query(FinalResult).get(result_id)
        
        if not result:
            return {"error": "Result not found"}
        
        data = json.loads(result.transcript)
        eval_summary = data.get("evaluation_summary", {})
        enhanced_transcript = eval_summary.get("enhanced_transcript", [])
        
        # Format for frontend
        frontend_data = {
            "candidate_id": result.candidate_id,
            "total_score": round(result.total_score, 1),
            "aptitude_score": round(result.aptitude_score, 1),
            "interview_score": round(result.interview_score, 1),
            "recommendation": result.status,
            "experience_level": eval_summary.get("experience_level", "Unknown"),
            "experience_years": eval_summary.get("experience_years", 0),
            "questions_with_scores": [
                {
                    "question_number": i + 1,
                    "question": qa.get("question"),
                    "answer": qa.get("answer"),
                    "score_out_of_5": qa.get("score_out_of_5"),
                    "rating": qa.get("rating"),
                    "stars": int(qa.get("score_out_of_5", 0))  # For star display
                }
                for i, qa in enumerate(enhanced_transcript)
            ],
            "criteria_scores": {
                criterion: {
                    "score": data.get("average_score", 0),
                    "percentage": round((data.get("average_score", 0) / 10) * 100, 1)
                }
                for criterion, data in eval_summary.get("criteria_breakdown", {}).items()
            }
        }
        
        return frontend_data
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def print_frontend_html_example():
    """Print example HTML for displaying question scores"""
    
    html_example = """
<!-- Example HTML for displaying question scores in your frontend -->

<div class="interview-transcript">
    <h3>📝 Interview Questions</h3>
    
    <!-- Loop through questions_with_scores from API -->
    <div class="question-card" *ngFor="let qa of questionsWithScores">
        <div class="question-header">
            <span class="q-number">Q{{ qa.question_number }}</span>
            <span class="score-badge">
                <span class="score-value">{{ qa.score_out_of_5 }}</span>
                <span class="score-max">/5</span>
            </span>
        </div>
        
        <div class="question-text">{{ qa.question }}</div>
        
        <div class="answer-section">
            <div class="answer-label">Answer:</div>
            <div class="answer-text">{{ qa.answer }}</div>
        </div>
        
        <div class="rating-section">
            <!-- Star rating display -->
            <span class="stars">
                <i class="star filled" *ngFor="let i of [].constructor(qa.stars)">⭐</i>
                <i class="star empty" *ngFor="let i of [].constructor(5 - qa.stars)">☆</i>
            </span>
            <span class="rating-label">{{ qa.rating }}</span>
        </div>
    </div>
</div>

<!-- CSS Styling -->
<style>
.question-card {
    background: #f8f9fa;
    border-left: 4px solid #007bff;
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 4px;
}

.question-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.q-number {
    font-weight: bold;
    color: #007bff;
    font-size: 14px;
}

.score-badge {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 5px 12px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 14px;
}

.score-value {
    font-size: 18px;
}

.question-text {
    font-weight: 600;
    color: #333;
    margin-bottom: 10px;
}

.answer-section {
    background: white;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 10px;
}

.answer-label {
    font-size: 12px;
    color: #666;
    text-transform: uppercase;
    margin-bottom: 5px;
}

.answer-text {
    color: #333;
    line-height: 1.5;
}

.rating-section {
    display: flex;
    align-items: center;
    gap: 10px;
}

.stars {
    font-size: 16px;
}

.rating-label {
    font-size: 13px;
    color: #666;
    font-weight: 500;
}

/* Score color coding */
.score-badge {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); /* Low score */
}

.score-badge[data-score="4"], 
.score-badge[data-score="5"] {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); /* Medium score */
}

.score-badge[data-score="4.5"],
.score-badge[data-score="5"] {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); /* High score */
}
</style>

<!-- JavaScript/TypeScript for API call -->
<script>
// Fetch candidate results with question scores
async function loadCandidateResults(resultId) {
    const response = await fetch(`/result/${resultId}`);
    const data = await response.json();
    
    // Access the enhanced transcript with scores
    const questionsWithScores = data.details.evaluation_summary.enhanced_transcript;
    
    // Display each question with its score
    questionsWithScores.forEach((qa, index) => {
        console.log(`Q${index + 1}: ${qa.question}`);
        console.log(`Score: ${qa.score_out_of_5}/5 (${qa.rating})`);
        console.log(`Answer: ${qa.answer}`);
        console.log('---');
    });
    
    return questionsWithScores;
}
</script>
"""
    
    print("="*80)
    print("FRONTEND HTML/CSS EXAMPLE")
    print("="*80)
    print(html_example)


if __name__ == "__main__":
    print("="*80)
    print("📊 QUESTION SCORE DISPLAY HELPER")
    print("="*80)
    print()
    print("This script demonstrates how to display individual question scores (0-5)")
    print("from the enhanced evaluation system.")
    print()
    
    # Example usage
    print("USAGE EXAMPLES:")
    print("-" * 80)
    print()
    print("1. Display scores for a specific result:")
    print("   >>> display_question_scores(result_id=1)")
    print()
    print("2. Get JSON for frontend:")
    print("   >>> json_data = get_frontend_json_example(result_id=1)")
    print()
    print("3. View HTML example:")
    print("   >>> print_frontend_html_example()")
    print()
    print("=" * 80)
    
    # If you want to test with an actual result, uncomment below:
    # display_question_scores(result_id=1)
