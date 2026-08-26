from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
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
        return {"id": candidate.id, "message": "Candidate already exists"}
    
    new_candidate = Candidate(name=name, email=email)
    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)
    return {"id": new_candidate.id, "message": "Registered successfully"}

@app.post("/interview/start")
async def start_interview(candidate_id: int):
    # Initialize session state (could be in Redis, but we use memory/client-side for MVP)
    state = {
        "current_state": "GREETING",
        "hr_idx": 0,
        "apt_idx": 0,
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
async def next_step(candidate_id: int = Form(...), state_json: str = Form(...), audio: UploadFile = File(None), db=Depends(get_db)):
    state = json.loads(state_json)
    
    # 1. Process Answer if audio provided
    transcription = ""
    if audio:
        in_path = f"data/audio_in/{uuid.uuid4()}.webm"
        with open(in_path, "wb") as f:
            f.write(await audio.read())
        
        # In a real app, we might need to convert webm to wav for some STT engines
        # faster-whisper handles many formats but let's assume it works or add ffmpeg logic
        transcription, state = interview_manager.process_answer(in_path, state)
        
    # 2. Get Next Question
    text, next_state = interview_manager.get_next_step(state)
    audio_path = tts_service.text_to_speech(text)
    
    # 3. If interview finished, calculate and save results
    if next_state["current_state"] == "CLOSING":
        # Finalize
        hr_hist = [h for h in next_state["history"] if not h["is_aptitude"]]
        apt_hist = [h for h in next_state["history"] if h["is_aptitude"]]
        
        comm_s, clar_s = scoring_engine.calculate_interview_heuristics(hr_hist)
        apt_score, apt_results = scoring_engine.calculate_aptitude_score(apt_hist)
        
        int_score = (comm_s + clar_s) * 5 # Scale 10+10 to 100
        total_score, status = scoring_engine.get_final_verdict(int_score, apt_score)
        
        # Save to DB
        # Save answers
        for i, h in enumerate(hr_hist):
            ans = InterviewAnswer(candidate_id=candidate_id, question_index=i, question_text=h["question"], transcribed_answer=h["answer"])
            db.add(ans)
        
        # Save aptitude
        for i, r in enumerate(apt_results):
            res = AptitudeResult(candidate_id=candidate_id, question_index=i, question_text=r["question"], given_answer=r["given"], correct_answer=r["correct"], is_correct=r["is_correct"])
            db.add(res)
           
        final = FinalResult(
            candidate_id=candidate_id,
            interview_score=int_score,
            aptitude_score=apt_score,
            total_score=total_score,
            status=status,
            transcript=json.dumps(next_state["history"])
        )
        db.add(final)
        db.commit()

    return {
        "text": text,
        "audio_url": f"/audio/out/{os.path.basename(audio_path)}" if audio_path else None,
        "state": next_state,
        "transcription": transcription
    }

@app.get("/candidates")
async def list_candidates(db=Depends(get_db)):
    results = db.query(FinalResult).all()
    out = []
    for r in results:
        cand = db.query(Candidate).get(r.candidate_id)
        out.append({
            "name": cand.name,
            "email": cand.email,
            "score": r.total_score,
            "status": r.status,
            "id": cand.id
        })
    return out

@app.get("/candidate/{id}")
async def get_candidate_details(id: int, db=Depends(get_db)):
    cand = db.query(Candidate).get(id)
    final = db.query(FinalResult).filter(FinalResult.candidate_id == id).first()
    answers = db.query(InterviewAnswer).filter(InterviewAnswer.candidate_id == id).all()
    apt_results = db.query(AptitudeResult).filter(AptitudeResult.candidate_id == id).all()
    
    return {
        "candidate": cand,
        "final": final,
        "answers": answers,
        "aptitude": apt_results
    }

@app.delete("/candidate/{id}")
async def delete_candidate(id: int, db=Depends(get_db)):
    try:
        # Delete all related records
        db.query(InterviewAnswer).filter(InterviewAnswer.candidate_id == id).delete()
        db.query(AptitudeResult).filter(AptitudeResult.candidate_id == id).delete()
        db.query(FinalResult).filter(FinalResult.candidate_id == id).delete()
        db.query(Candidate).filter(Candidate.id == id).delete()
        
        db.commit()
        return {"message": "Candidate deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files and generated audio
app.mount("/audio/out", StaticFiles(directory="data/audio_out"), name="audio_out")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
