# Offline AI HR Voice Interview Agent

## Overview

This is a **fully offline AI-powered HR Voice Interview Agent** that conducts voice-based interviews, generates aptitude questions dynamically using a local LLM, and evaluates candidates objectively.

## Core Features

### ✅ Fully Offline Operation
- All AI reasoning happens locally via **Ollama**
- No internet connection required
- No external API calls
- Complete data privacy

### ✅ Dynamic Question Generation
- Questions generated in real-time by local LLM
- Unique questions for each interview
- Difficulty adjusted based on candidate experience
- Anti-repetition with semantic similarity checking

### ✅ Experience-Based Differentiation
- Automatically detects fresher vs experienced candidates
- Adjusts question difficulty accordingly
- **Fresher**: Basic math, logical reasoning, pattern recognition
- **Experienced**: Analytical reasoning, decision making, complex scenarios

### ✅ Intelligent Scoring (60/40 Split)
- **Aptitude Score (60%)**: Evaluates problem-solving and analytical skills
- **Communication Score (40%)**: Assesses clarity, fluency, confidence, structure
- AI-powered answer evaluation
- Objective, consistent scoring

### ✅ Structured Output
```json
{
  "candidate_type": "fresher | experienced",
  "experience_years": 0,
  "aptitude_score": 48.5,
  "communication_score": 32.0,
  "total_score": 80.5,
  "strengths": [
    "Strong analytical and problem-solving skills",
    "Clear and structured communication"
  ],
  "improvement_areas": [
    "Continue developing all skills"
  ],
  "final_recommendation": "Strong Hire | Hire | Borderline | Reject"
}
```

## Architecture

### Components

1. **Interview Manager** (`services/interview_manager.py`)
   - Controls interview flow
   - Generates unique questions
   - Prevents repetition
   - Detects candidate experience level

2. **LLM Service** (`services/llm.py`)
   - Interfaces with Ollama
   - Generates aptitude questions
   - Checks semantic similarity
   - Evaluates communication quality
   - Scores aptitude answers

3. **Scoring Engine** (`services/scoring.py`)
   - Calculates aptitude score (60%)
   - Calculates communication score (40%)
   - Generates final verdict
   - Provides strengths and improvement areas

4. **STT Service** (`services/stt.py`)
   - Converts speech to text
   - Uses faster-whisper (offline)

5. **TTS Service** (`services/tts.py`)
   - Converts text to speech
   - Uses pyttsx3 (offline)

## Interview Flow

```
1. GREETING
   ↓
2. EXPERIENCE DETECTION
   - "Are you a fresher or experienced?"
   - Detects: fresher (<1 year) or experienced (≥1 year)
   ↓
3. APTITUDE TEST
   - Generates 5 unique questions
   - Topics selected with controlled randomness
   - Each question checked for semantic uniqueness
   - Difficulty adjusted based on candidate type
   ↓
4. CLOSING
   - Calculate scores
   - Generate structured output
   - Save to database
```

## Question Generation Process

### 1. Topic Selection
- **Fresher Topics**: math, logical_reasoning, pattern_recognition, basic_problem_solving
- **Experienced Topics**: analytical_reasoning, decision_making, logical_reasoning, math

### 2. Generation with LLM
```python
llm_service.generate_aptitude_question(
    candidate_type="fresher",  # or "experienced"
    topic="math",
    asked_questions=[...]  # Previously asked questions
)
```

### 3. Anti-Repetition Check
```python
is_similar = llm_service.check_semantic_similarity(
    new_question="What is 2+2?",
    asked_questions=["What is 1+1?", "Calculate 3+3"]
)
# Returns True if semantically similar
```

### 4. Controlled Randomness
- Uses `random.choice()` for topic selection
- Temperature: 0.8 for question generation
- Temperature: 0.3 for similarity checking
- Temperature: 0.2 for answer evaluation

## Scoring System

### Aptitude Score (60 points)
- Each question evaluated by LLM
- Considers:
  - Numerical equivalence (e.g., "60" = "sixty" = "6-0")
  - Semantic equivalence (e.g., "not necessarily" = "cannot be determined")
  - Partial correctness
- Formula: `(correct_count / total_questions) * 60`

### Communication Score (40 points)
- Evaluates ALL answers (including aptitude)
- Criteria:
  - **Clarity**: Easy to understand?
  - **Fluency**: Natural flow?
  - **Confidence**: Sounds assured?
  - **Structure**: Well-organized?
  - **Relevance**: Stays on topic?
- Each answer scored 0-10 by LLM
- Formula: `(average_score / 10) * 40`

### Final Recommendation
- **Strong Hire**: Total ≥ 80
- **Hire**: Total ≥ 65
- **Borderline**: Total ≥ 50
- **Reject**: Total < 50

## API Endpoints

### POST `/interview/start`
Start a new interview session.

**Request:**
```json
{
  "candidate_id": 1
}
```

**Response:**
```json
{
  "text": "Welcome to your HR interview...",
  "audio_url": "/audio/out/greeting.wav",
  "state": {
    "current_state": "EXPERIENCE_DETECTION",
    "candidate_type": null,
    "experience_years": 0,
    "apt_idx": 0,
    "asked_questions": [],
    "generated_questions": [],
    "history": []
  }
}
```

### POST `/interview/next`
Process answer and get next question.

**Request:**
```
candidate_id: 1
state_json: {...}
audio: <audio file>
```

**Response (during interview):**
```json
{
  "text": "What is 25 + 17?",
  "audio_url": "/audio/out/question.wav",
  "state": {...},
  "transcription": "I am a fresher"
}
```

**Response (at completion):**
```json
{
  "text": "Thank you for your time...",
  "audio_url": "/audio/out/closing.wav",
  "state": {...},
  "transcription": "42",
  "final_results": {
    "candidate_type": "fresher",
    "experience_years": 0,
    "aptitude_score": 48.5,
    "communication_score": 32.0,
    "total_score": 80.5,
    "strengths": [...],
    "improvement_areas": [...],
    "final_recommendation": "Strong Hire"
  }
}
```

## Setup Instructions

### Prerequisites
1. **Python 3.8+**
2. **Ollama** installed and running
3. **Mistral model** downloaded in Ollama

### Installation

```bash
# 1. Install Ollama
# Visit: https://ollama.ai

# 2. Download Mistral model
ollama pull mistral

# 3. Install Python dependencies
pip install fastapi uvicorn sqlalchemy faster-whisper pyttsx3 requests

# 4. Run the application
python main.py
```

### Verify Ollama is Running
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "Hello",
  "stream": false
}'
```

## Testing

### Run Test Suite
```bash
python test_enhanced_agent.py
```

This tests:
- ✓ Experience detection
- ✓ Dynamic question generation
- ✓ Anti-repetition logic
- ✓ Interview flow
- ✓ Scoring system (60/40)
- ✓ Structured JSON output

### Manual Testing
```bash
# 1. Start the server
python main.py

# 2. Open browser
http://localhost:8000

# 3. Register and start interview
```

## Configuration

### Adjust Number of Questions
Edit `services/interview_manager.py`:
```python
self.num_aptitude_questions = 5  # Change to desired number
```

### Change LLM Model
Edit `services/llm.py`:
```python
def __init__(self, model="mistral", ...):  # Change model name
```

### Adjust Scoring Thresholds
Edit `services/scoring.py`:
```python
def get_final_verdict(self, aptitude_score, communication_score):
    if total_score >= 80:  # Adjust thresholds
        recommendation = "Strong Hire"
    # ...
```

## Important Constraints

### ⚠️ Offline Operation
- **MUST** have Ollama running locally
- **NO** internet access required
- **NO** external API calls

### ⚠️ Question Uniqueness
- Maximum 3 attempts to generate unique question
- Uses semantic similarity checking
- Falls back to simple question if all attempts fail

### ⚠️ LLM Response Handling
- Timeouts set to 30 seconds
- Fallback logic for failed generations
- Graceful degradation

### ⚠️ Scoring Accuracy
- Depends on LLM quality (Mistral recommended)
- Fallback to heuristic scoring if LLM fails
- Correct answers must be stored during generation

## Troubleshooting

### Issue: Questions are repetitive
**Solution**: Check semantic similarity is working:
```python
# Test in Python console
from services.llm import llm_service
result = llm_service.check_semantic_similarity(
    "What is 2+2?",
    ["What is 1+1?"]
)
print(result)  # Should return True
```

### Issue: Scoring seems incorrect
**Solution**: Verify LLM is evaluating answers:
```python
from services.llm import llm_service
result = llm_service.evaluate_aptitude_answer(
    question="What is 2+2?",
    given_answer="4",
    correct_answer="4"
)
print(result)  # Should return True
```

### Issue: Ollama connection errors
**Solution**: 
1. Check Ollama is running: `ollama list`
2. Verify model is downloaded: `ollama pull mistral`
3. Test connection: `curl http://localhost:11434/api/tags`

## Database Schema

### Candidates Table
- `id`: Primary key
- `name`: Candidate name
- `email`: Candidate email
- `created_at`: Timestamp

### Interview Answers Table
- `id`: Primary key
- `candidate_id`: Foreign key
- `question_index`: Question number
- `question_text`: The question asked
- `transcribed_answer`: Candidate's answer

### Aptitude Results Table
- `id`: Primary key
- `candidate_id`: Foreign key
- `question_index`: Question number
- `question_text`: The question asked
- `given_answer`: Candidate's answer
- `correct_answer`: Expected answer
- `is_correct`: Boolean

### Final Results Table
- `id`: Primary key
- `candidate_id`: Foreign key
- `interview_score`: Communication score (40)
- `aptitude_score`: Aptitude score (60)
- `total_score`: Total score (100)
- `status`: Recommendation
- `transcript`: Full structured JSON output
- `created_at`: Timestamp

## Future Enhancements

### Potential Improvements
1. **Multi-language support** for international candidates
2. **Custom question banks** per job role
3. **Video recording** for non-verbal communication analysis
4. **Resume parsing** for context-aware questions
5. **Follow-up questions** based on answers
6. **Adaptive difficulty** during the interview
7. **Export to PDF/CSV** for reports

## License

This project is for internal use only.

## Support

For issues or questions, contact the development team.
