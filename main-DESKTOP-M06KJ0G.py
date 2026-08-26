from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import uuid
import json
from datetime import datetime

from models.database import init_db, SessionLocal, Candidate, InterviewAnswer, AptitudeResult, FinalResult
from services.stt import stt_service
from services.tts import tts_service
from services.llm import llm_service
from services.interview_manager import interview_manager
from services.scoring import scoring_engine

app = FastAPI(title="HR Voice Assistant API")

# Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("data/audio_in", exist_ok=True)
os.makedirs("data/audio_out", exist_ok=True)
init_db()

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
async def register_candidate(name: str = Form(...), email: str = Form(...), db=Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.email == email).first()
    if candidate:
        # Update name if candidate already exists
        candidate.name = name
        db.commit()
        return {"id": candidate.id, "message": "Candidate name updated and ready for new interview"}
    
    new_candidate = Candidate(name=name, email=email)
    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)
    return {"id": new_candidate.id, "message": "Registered successfully"}

def process_interview_results(candidate_id, final_state):
    """
    Background task to calculate scores and save to DB.
    This prevents the candidate from waiting at the end of the interview.
    """
    db = SessionLocal()
    try:
        print(f"--- [BACKGROUND] Saving results for Candidate {candidate_id} ---")
        
        # 1. Handle deferred transcription if needed
        final_audio = final_state.pop("final_audio_path", None)
        if final_audio:
            print(f"--- [BACKGROUND] Transcribing final answer: {final_audio} ---")
            last_text = stt_service.transcribe(final_audio)
            if final_state.get("history"):
                # Replace placeholder in history
                for h in reversed(final_state["history"]):
                    if h.get("answer") == "[DEFERRED]":
                        h["answer"] = last_text
                        break
        
        # 2. Separate histories
        all_hist = final_state.get("history", [])
        apt_hist = [h for h in all_hist if h.get("is_aptitude", False)]
        
        
        # 2. Calculate scores with enhanced evaluation
        aptitude_score, apt_results = scoring_engine.calculate_aptitude_score(apt_hist)
        
        # Pass experience_years to get comprehensive evaluation
        experience_years = final_state.get("experience_years", 0)
        communication_score, evaluation_summary = scoring_engine.calculate_communication_score(
            all_hist, 
            experience_years=experience_years
        )
        
        total_score, recommendation, strengths, improvement_areas = scoring_engine.get_final_verdict(
            aptitude_score, communication_score
        )
        
        # 3. Add individual question scores to the main transcript
        # This allows displaying score for each question in the Interview Transcript section
        enhanced_transcript = evaluation_summary.get("enhanced_transcript", [])
        
        # Create a mapping of question -> score for easy lookup
        question_scores = {}
        for item in enhanced_transcript:
            question_scores[item["question"]] = {
                "score_out_of_5": item["score_out_of_5"],
                "rating": item["rating"],
                "total_score_out_of_5": item.get("total_score_out_of_5", item["score_out_of_5"]),
                "justification": item.get("justification", ""),
                "scores": item.get("scores", {})
            }
        
        # Add scores to each HR question in the main transcript (only HR questions get scores)
        for item in all_hist:
            if item.get("is_hr_question", False) and item.get("question") in question_scores:
                score_data = question_scores[item["question"]]
                item["score_out_of_5"] = score_data["score_out_of_5"]
                item["rating"] = score_data["rating"]
                item["total_score_out_of_5"] = score_data.get("total_score_out_of_5", score_data["score_out_of_5"])
                item["justification"] = score_data.get("justification", "")
                item["scores"] = score_data.get("scores", {})
        
        
        final_output = {
            "candidate_type": final_state.get("candidate_type", "fresher"),
            "experience_years": final_state.get("experience_years", 0),
            "aptitude_score": round(aptitude_score, 2),
            "communication_score": round(communication_score, 2),
            "total_score": round(total_score, 2),
            "strengths": strengths,
            "improvement_areas": improvement_areas,
            "final_recommendation": recommendation,
            "transcript": all_hist,  # Now includes score_out_of_5 for each HR question
            "aptitude_details": apt_results,
            "evaluation_summary": evaluation_summary  # Detailed criteria-based evaluation
        }
        
        # 3. Save to DB
        # Save exp/HR answers
        other_answers = [h for h in all_hist if h.get("is_experience_detection", False) or h.get("is_hr_question", False)]
        for i, h in enumerate(other_answers):
            ans = InterviewAnswer(
                candidate_id=candidate_id, 
                question_index=i, 
                question_text=h["question"], 
                transcribed_answer=h["answer"]
            )
            db.add(ans)
            
        # Save aptitude results
        for i, r in enumerate(apt_results):
            res = AptitudeResult(
                candidate_id=candidate_id, 
                question_index=i, 
                question_text=r["question"], 
                given_answer=r["given"], 
                correct_answer=r["correct"], 
                is_correct=r["is_correct"]
            )
            db.add(res)
            
        # Save Final Result
        final = FinalResult(
            candidate_id=candidate_id,
            interview_score=communication_score,
            aptitude_score=aptitude_score,
            total_score=total_score,
            status=recommendation,
            transcript=json.dumps(final_output)
        )
        db.add(final)
        db.commit()
        print(f"--- [BACKGROUND] Results saved successfully for Candidate {candidate_id} ---")
    except Exception as e:
        print(f"--- [BACKGROUND ERROR] Failed to save results: {str(e)} ---")
        db.rollback()
    finally:
        db.close()

@app.post("/interview/start")
async def start_interview(candidate_id: int):
    # Initialize session state with new fields for dynamic interview
    state = {
        "current_state": "GREETING",
        "candidate_type": None,  # Will be set to "fresher" or "experienced"
        "experience_years": 0,
        "apt_idx": 0,
        "asked_questions": [],  # Track asked questions to prevent repetition
        "generated_questions": [],  # Store question data with answers
        "history": []
    }
    text, next_state = interview_manager.get_next_step(state)
    audio_path = tts_service.text_to_speech(text)
    
    return {
        "text": text,
        "audio_url": f"/audio/out/{os.path.basename(audio_path)}" if audio_path else None,
        "state": next_state
    }

@app.post("/interview/next")
async def next_step(
    background_tasks: BackgroundTasks,
    candidate_id: int = Form(...), 
    state_json: str = Form(...), 
    audio: UploadFile = File(None), 
    text_answer: str = Form(None),
    db=Depends(get_db)
):
    state = json.loads(state_json)
    
    # 1. Process Answer
    transcription = ""
    # FAST WRAP-UP: If this is the last question, we skip transcription on the main thread
    is_final_answer = (state.get("current_state") == "APTITUDE_TEST" and state.get("apt_idx") == 6)
    
    if audio:
        in_path = f"data/audio_in/{uuid.uuid4()}.webm"
        with open(in_path, "wb") as f:
            f.write(await audio.read())
            
        if is_final_answer:
            # Skip STT for instant closing
            transcription = "[DEFERRED]"
            _, state = interview_manager._handle_response(transcription, state)
            state["final_audio_path"] = in_path
        else:
            transcription, state = interview_manager.process_answer(in_path, state)
    elif text_answer:
        transcription, state = interview_manager.process_text_answer(text_answer, state)
        
    # Check for empty input (Retry Logic)
    if not transcription or not transcription.strip():
        retry_text = "I didn't hear any input. Please may you repeat that?"
        audio_path = tts_service.text_to_speech(retry_text)
        return {
            "candidate_id": candidate_id,
            "text": retry_text,
            "audio_url": f"/audio/out/{os.path.basename(audio_path)}" if audio_path else None,
            "state": state, # Return same state to retry
            "is_retry": True,
            "transcription": ""
        }

    # 2. Get Next Question
    text, next_state = interview_manager.get_next_step(state)
    audio_path = tts_service.text_to_speech(text)
    
    # 3. If interview finished, calculate results in background
    if next_state["current_state"] == "CLOSING":
        background_tasks.add_task(process_interview_results, candidate_id, next_state)
        
    return {
        "text": text,
        "audio_url": f"/audio/out/{os.path.basename(audio_path)}" if audio_path else None,
        "state": next_state,
        "transcription": transcription
    }

    return {
        "text": text,
        "audio_url": f"/audio/out/{os.path.basename(audio_path)}" if audio_path else None,
        "state": next_state,
        "transcription": transcription
    }

@app.get("/candidates")
async def list_candidates(db=Depends(get_db)):
    # Query FinalResults directly to support multiple attempts for same candidate
    results = db.query(FinalResult).order_by(FinalResult.id.desc()).all()
    out = []
    for r in results:
        cand = db.query(Candidate).get(r.candidate_id)
        out.append({
            "name": cand.name,
            "email": cand.email,
            "score": round(r.total_score, 2),
            "status": r.status,
            "result_id": r.id,  # Use result ID for unique row
            "candidate_id": cand.id
        })
    return out

@app.get("/result/{result_id}")
async def get_result_details(result_id: int, db=Depends(get_db)):
    final = db.query(FinalResult).get(result_id)
    if not final:
        raise HTTPException(status_code=404, detail="Result not found")
        
    cand = db.query(Candidate).get(final.candidate_id)
    
    # Use the structured data stored in the transcript blob
    try:
        details = json.loads(final.transcript)
    except:
        details = {}
        
    return {
        "candidate": cand,
        "final": final,
        "details": details
    }

@app.delete("/result/{result_id}")
async def delete_result(result_id: int, db=Depends(get_db)):
    try:
        db.query(FinalResult).filter(FinalResult.id == result_id).delete()
        db.commit()
        return {"message": "Result deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files and generated audio
app.mount("/audio/out", StaticFiles(directory="data/audio_out"), name="audio_out")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
