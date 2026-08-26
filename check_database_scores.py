"""
Check if question-wise scores exist in the database
"""

import json
from models.database import SessionLocal, FinalResult

def check_questionwise_scores():
    print("="*80)
    print("🔍 CHECKING DATABASE FOR QUESTION-WISE SCORES")
    print("="*80)
    print()
    
    db = SessionLocal()
    
    try:
        # Get the most recent result
        results = db.query(FinalResult).order_by(FinalResult.id.desc()).limit(3).all()
        
        if not results:
            print("❌ No results found in database")
            print("   You need to conduct at least one interview first!")
            return
        
        print(f"📊 Found {len(results)} recent results. Checking the latest ones...")
        print()
        
        for i, result in enumerate(results, 1):
            print(f"\n{'='*80}")
            print(f"Result #{i} (ID: {result.id})")
            print(f"{'='*80}")
            print(f"Candidate ID: {result.candidate_id}")
            print(f"Total Score: {result.total_score:.1f}/100")
            print(f"Date: {result.created_at}")
            print()
            
            # Parse transcript
            try:
                data = json.loads(result.transcript)
                transcript = data.get("transcript", [])
                
                if not transcript:
                    print("⚠️  No transcript found")
                    continue
                
                # Check if question-wise scores exist
                hr_questions = [item for item in transcript if not item.get("is_aptitude")]
                
                print(f"📝 Found {len(hr_questions)} HR questions in transcript")
                print()
                
                has_scores = False
                for j, item in enumerate(hr_questions[:3], 1):  # Show first 3
                    print(f"Q{j}: {item.get('question', 'N/A')[:60]}...")
                    print(f"A{j}: {item.get('answer', 'N/A')[:60]}...")
                    
                    # Check for score fields
                    if 'score_out_of_5' in item:
                        has_scores = True
                        print(f"✅ Score: {item['score_out_of_5']}/5 ({item.get('rating', 'N/A')})")
                        print(f"   Weighted: {item.get('weighted_score', 'N/A')}/10")
                    else:
                        print(f"❌ No score_out_of_5 found (old interview)")
                    
                    print()
                
                if has_scores:
                    print("🎉 SUCCESS! Question-wise scores ARE present!")
                    print("   This interview has the new scoring feature.")
                else:
                    print("⚠️  This interview was conducted BEFORE the scoring update")
                    print("   You need to conduct a NEW interview to see scores.")
                
                # Check evaluation_summary
                eval_summary = data.get("evaluation_summary", {})
                enhanced_transcript = eval_summary.get("enhanced_transcript", [])
                
                if enhanced_transcript:
                    print()
                    print(f"✅ Enhanced transcript found with {len(enhanced_transcript)} scored questions")
                else:
                    print()
                    print("⚠️  No enhanced_transcript (interview before update)")
                
            except json.JSONDecodeError:
                print("❌ Error parsing transcript JSON")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print()
        print("="*80)
        print("📋 SUMMARY")
        print("="*80)
        print()
        print("To test the NEW question-wise scoring:")
        print("1. Open http://localhost:8000 in your browser")
        print("2. Register a new candidate (e.g., 'Test New Scoring')")
        print("3. Complete the interview with answers")
        print("4. Check the results - you should see scores for each question!")
        print()
        print("OLD interviews (before this update) won't have scores.")
        print("You MUST conduct a FRESH interview to see the feature working.")
        print()
        
    finally:
        db.close()


if __name__ == "__main__":
    check_questionwise_scores()
