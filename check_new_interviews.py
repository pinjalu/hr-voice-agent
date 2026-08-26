"""Check the newest interviews for scores"""
import json
from models.database import SessionLocal, FinalResult

db = SessionLocal()

# Get results 23 and 24 (the new ones)
results = db.query(FinalResult).filter(FinalResult.id.in_([23, 24, 25])).all()

for result in results:
    print(f"\n{'='*70}")
    print(f"Result ID: {result.id} | Candidate ID: {result.candidate_id}")
    print(f"Date: {result.created_at}")
    print(f"{'='*70}")
    
    data = json.loads(result.transcript)
    transcript = data.get('transcript', [])
    
    # Check first HR question
    for item in transcript:
        if not item.get('is_aptitude'):
            print(f"\nQ: {item.get('question', '')[:60]}...")
            print(f"A: {item.get('answer', '')[:60]}...")
            
            if 'score_out_of_5' in item:
                print(f"✅ SCORE FOUND: {item['score_out_of_5']}/5 ({item.get('rating', 'N/A')})")
            else:
                print(f"❌ NO SCORE FIELD")
            break
    
    # Check enhanced_transcript
    eval_summary = data.get('evaluation_summary', {})
    if eval_summary:
        print(f"\n✅ evaluation_summary exists")
        enhanced = eval_summary.get('enhanced_transcript', [])
        if enhanced:
            print(f"✅ enhanced_transcript has {len(enhanced)} items")
        else:
            print(f"❌ enhanced_transcript is empty or missing")
    else:
        print(f"\n❌ No evaluation_summary")

db.close()
