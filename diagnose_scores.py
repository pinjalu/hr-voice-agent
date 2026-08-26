"""
Quick check - verify if the latest interview has question-wise scores
"""

import json
from models.database import SessionLocal, FinalResult, Candidate

db = SessionLocal()

try:
    # Get the most recent result for candidate "eee"
    candidate = db.query(Candidate).filter(Candidate.email == "eee@gmail.com").first()
    
    if not candidate:
        print("❌ Candidate 'eee' not found")
        print("Checking latest result instead...")
        result = db.query(FinalResult).order_by(FinalResult.id.desc()).first()
    else:
        print(f"✅ Found candidate: {candidate.name} ({candidate.email})")
        result = db.query(FinalResult).filter(
            FinalResult.candidate_id == candidate.id
        ).order_by(FinalResult.id.desc()).first()
    
    if not result:
        print("❌ No results found")
    else:
        print(f"\n📊 Result ID: {result.id}")
        print(f"Total Score: {result.total_score}")
        print(f"Date: {result.created_at}")
        print()
        
        # Parse transcript
        data = json.loads(result.transcript)
        transcript = data.get("transcript", [])
        
        print(f"📝 Checking transcript ({len(transcript)} items)...")
        print()
        
        # Check first 3 questions
        for i, item in enumerate(transcript[:3], 1):
            print(f"Q{i}: {item.get('question', 'N/A')[:50]}...")
            print(f"A{i}: {item.get('answer', 'N/A')[:50]}...")
            
            # Check for score
            if 'score_out_of_5' in item:
                print(f"✅ HAS SCORE: {item['score_out_of_5']}/5 ({item.get('rating', 'N/A')})")
            else:
                print(f"❌ NO SCORE FIELD")
            
            print()
        
        # Check if enhanced_transcript exists
        eval_summary = data.get("evaluation_summary", {})
        enhanced_transcript = eval_summary.get("enhanced_transcript", [])
        
        if enhanced_transcript:
            print(f"✅ Enhanced transcript exists with {len(enhanced_transcript)} scored questions")
            print("\nFirst scored question:")
            if enhanced_transcript:
                first = enhanced_transcript[0]
                print(f"  Q: {first.get('question', 'N/A')[:50]}...")
                print(f"  Score: {first.get('score_out_of_5', 'N/A')}/5")
                print(f"  Rating: {first.get('rating', 'N/A')}")
        else:
            print("❌ No enhanced_transcript found")
            print("   This interview was done BEFORE the update!")
        
        print()
        print("="*70)
        print("DIAGNOSIS:")
        print("="*70)
        
        # Check if scores are in main transcript
        has_scores_in_transcript = any('score_out_of_5' in item for item in transcript)
        
        if has_scores_in_transcript:
            print("✅ Scores ARE in the main transcript")
            print("   Problem: Frontend is not displaying them")
            print("   Solution: Update your frontend HTML/JS to show the scores")
        elif enhanced_transcript:
            print("⚠️  Scores are in enhanced_transcript but NOT in main transcript")
            print("   Problem: Score merging didn't happen")
            print("   Solution: Server needs to be restarted to use new code")
        else:
            print("❌ No scores anywhere - interview was before the update")
            print("   Solution: Conduct a NEW interview after restarting server")
        
finally:
    db.close()
