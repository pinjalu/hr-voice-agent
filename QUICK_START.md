# Quick Start Guide - Offline AI HR Voice Interview Agent

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Ollama
```bash
# Download and install from: https://ollama.ai
# Or use package manager:
# Windows: Download installer from website
# Mac: brew install ollama
# Linux: curl https://ollama.ai/install.sh | sh
```

### Step 2: Download AI Model
```bash
ollama pull mistral
```

### Step 3: Start Ollama (if not auto-started)
```bash
ollama serve
```

### Step 4: Verify Ollama is Running
```bash
# Test command:
curl http://localhost:11434/api/tags

# Should return list of models including mistral
```

### Step 5: Install Python Dependencies
```bash
pip install fastapi uvicorn sqlalchemy faster-whisper pyttsx3 requests
```

### Step 6: Run the Application
```bash
python main.py
```

### Step 7: Open Browser
```
http://localhost:8000
```

## ✅ Verify Installation

### Test 1: Check Ollama Connection
```bash
python -c "import requests; print(requests.get('http://localhost:11434/api/tags').json())"
```

### Test 2: Run Test Suite
```bash
python test_enhanced_agent.py
```

Expected output:
```
============================================================
✓ ALL TESTS PASSED!
============================================================
```

### Test 3: Test Question Generation
```python
from services.llm import llm_service

question = llm_service.generate_aptitude_question(
    candidate_type="fresher",
    topic="math",
    asked_questions=[]
)
print(question)
```

Expected output:
```python
{
    'question': 'What is 25 + 17?',
    'answer': '42',
    'type': 'math'
}
```

## 🎯 Usage

### Start an Interview

1. **Register Candidate**
   - Open http://localhost:8000
   - Enter name and email
   - Click "Start Interview"

2. **Experience Detection**
   - Agent asks: "Are you a fresher or experienced?"
   - Candidate responds via voice
   - System detects and classifies

3. **Aptitude Test**
   - 5 dynamically generated questions
   - Questions adapt to candidate level
   - No repetition guaranteed

4. **Results**
   - Automatic scoring (60% aptitude, 40% communication)
   - Structured JSON output
   - Recommendation: Strong Hire | Hire | Borderline | Reject

### View Results

1. **Dashboard**
   - Navigate to: http://localhost:8000/dashboard.html
   - View all candidates
   - Click to see detailed results

2. **API Access**
   ```bash
   curl http://localhost:8000/candidates
   ```

## 🔧 Configuration

### Change Number of Questions
Edit `services/interview_manager.py`:
```python
self.num_aptitude_questions = 5  # Change this number
```

### Change AI Model
Edit `services/llm.py`:
```python
def __init__(self, model="mistral", ...):
    # Try: "llama2", "codellama", "neural-chat"
```

### Adjust Scoring Thresholds
Edit `services/scoring.py`:
```python
if total_score >= 80:  # Strong Hire
if total_score >= 65:  # Hire
if total_score >= 50:  # Borderline
# else: Reject
```

### Customize Topics
Edit `services/interview_manager.py`:
```python
self.fresher_topics = [
    "math",
    "logical_reasoning",
    "pattern_recognition",
    "basic_problem_solving"
]

self.experienced_topics = [
    "analytical_reasoning",
    "decision_making",
    "logical_reasoning",
    "math"
]
```

## 🐛 Troubleshooting

### Issue: "Connection refused" error
**Solution:**
```bash
# Check if Ollama is running
ollama list

# If not, start it
ollama serve
```

### Issue: "Model not found"
**Solution:**
```bash
# Download the model
ollama pull mistral

# Verify it's installed
ollama list
```

### Issue: Questions are repetitive
**Solution:**
1. Check Ollama is running (semantic similarity needs LLM)
2. Increase temperature in `llm.py`:
   ```python
   response = self.query(prompt, system_prompt, temperature=0.9)  # Higher = more random
   ```

### Issue: Scoring seems incorrect
**Solution:**
1. Verify LLM is evaluating answers:
   ```python
   from services.llm import llm_service
   result = llm_service.evaluate_aptitude_answer(
       question="What is 2+2?",
       given_answer="4",
       correct_answer="4"
   )
   print(result)  # Should be True
   ```

### Issue: Port 8000 already in use
**Solution:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

## 📊 Understanding the Output

### Sample Final Results
```json
{
  "candidate_type": "fresher",
  "experience_years": 0,
  "aptitude_score": 48.5,      // Out of 60
  "communication_score": 32.0,  // Out of 40
  "total_score": 80.5,          // Out of 100
  "strengths": [
    "Strong analytical and problem-solving skills",
    "Excellent communication clarity and confidence"
  ],
  "improvement_areas": [
    "Continue developing all skills"
  ],
  "final_recommendation": "Strong Hire"
}
```

### Score Breakdown

**Aptitude (60 points)**
- Each question: 12 points (for 5 questions)
- Evaluated by LLM for correctness
- Considers numerical and semantic equivalence

**Communication (40 points)**
- Evaluated across ALL answers
- Criteria: Clarity, Fluency, Confidence, Structure, Relevance
- Each answer scored 0-10, then averaged and scaled

**Total Score (100 points)**
- Strong Hire: ≥ 80
- Hire: ≥ 65
- Borderline: ≥ 50
- Reject: < 50

## 🔐 Privacy & Security

✅ **Fully Offline**
- No data sent to external servers
- All processing happens locally
- Complete data privacy

✅ **Local Storage**
- SQLite database: `hr_assistant.db`
- Audio files: `data/audio_in/` and `data/audio_out/`
- No cloud storage

✅ **GDPR Compliant**
- Data stored locally
- Easy to delete candidate data
- Full control over information

## 📈 Performance Tips

### Faster Question Generation
1. Use a smaller model: `ollama pull mistral:7b`
2. Increase timeout if needed in `llm.py`
3. Pre-generate questions (advanced)

### Better Accuracy
1. Use larger model: `ollama pull mistral:latest`
2. Adjust temperature for evaluation (lower = more consistent)
3. Fine-tune prompts in `llm.py`

### Reduce Resource Usage
1. Use smaller model
2. Reduce number of questions
3. Disable communication scoring (use heuristics only)

## 🎓 Advanced Usage

### Custom Question Bank
Create `services/custom_questions.py`:
```python
CUSTOM_TOPICS = {
    "python_coding": {
        "fresher": [...],
        "experienced": [...]
    }
}
```

### Export Results to CSV
```python
import csv
from models.database import SessionLocal, FinalResult

db = SessionLocal()
results = db.query(FinalResult).all()

with open('results.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Candidate', 'Score', 'Recommendation'])
    for r in results:
        writer.writerow([r.candidate_id, r.total_score, r.status])
```

### Integrate with External Systems
```python
# POST results to your backend
import requests

@app.post("/interview/next")
async def next_step(...):
    # ... existing code ...
    if next_state["current_state"] == "CLOSING":
        # Send to external system
        requests.post('https://your-backend.com/api/results', 
                     json=final_output)
```

## 📞 Support

For issues or questions:
1. Check this guide first
2. Review `README_OFFLINE_AI_AGENT.md` for detailed documentation
3. Run test suite: `python test_enhanced_agent.py`
4. Contact development team

## 🎉 You're Ready!

Your offline AI HR Voice Interview Agent is now set up and ready to conduct interviews!

**Next Steps:**
1. Test with a sample interview
2. Customize questions for your needs
3. Adjust scoring thresholds
4. Deploy to production

**Happy Interviewing! 🚀**
