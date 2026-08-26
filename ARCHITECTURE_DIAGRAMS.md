# System Architecture Diagram

## Overall System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         CANDIDATE                               │
│                    (Voice Input/Output)                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (Browser)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Register   │  │   Interview  │  │  Dashboard   │          │
│  │     Page     │  │     Page     │  │     Page     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
└────────────────────────────┼─────────────────────────────────────┘
                             │ HTTP/REST API
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND (main.py)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  POST /interview/start                                    │  │
│  │  POST /interview/next                                     │  │
│  │  GET  /candidates                                         │  │
│  │  GET  /candidate/{id}                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────┬────────────────────────┬────────────────────────────┘
             │                        │
             ▼                        ▼
┌─────────────────────┐    ┌─────────────────────┐
│  Interview Manager  │    │   Scoring Engine    │
│  (State Machine)    │    │  (60/40 Evaluator)  │
└─────────┬───────────┘    └─────────┬───────────┘
          │                          │
          ▼                          ▼
┌─────────────────────────────────────────────────┐
│           LLM Service (Ollama Interface)        │
│  ┌──────────────────────────────────────────┐  │
│  │  • Generate Questions                    │  │
│  │  • Check Semantic Similarity             │  │
│  │  • Evaluate Aptitude Answers             │  │
│  │  • Score Communication Quality           │  │
│  └──────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────┘
                     │ HTTP (localhost:11434)
                     ▼
┌─────────────────────────────────────────────────┐
│              OLLAMA (Local AI)                  │
│  ┌──────────────────────────────────────────┐  │
│  │         Mistral LLM Model                │  │
│  │     (Fully Offline Processing)           │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Interview Flow State Machine

```
┌──────────────┐
│   GREETING   │
│              │
│ "Welcome to  │
│  your HR     │
│  interview"  │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│ EXPERIENCE_DETECTION │
│                      │
│ "Are you a fresher   │
│  or experienced?"    │
└──────┬───────────────┘
       │
       ├─────► Detect: fresher (<1 year)
       │       or experienced (≥1 year)
       │
       ▼
┌──────────────────────┐
│   APTITUDE_TEST      │
│                      │
│ Generate 5 unique    │
│ questions via LLM    │
│                      │
│ Q1 → Answer → Q2 →   │
│ Answer → ... → Q5    │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│      CLOSING         │
│                      │
│ Calculate scores     │
│ Generate results     │
│ Save to database     │
└──────────────────────┘
```

## Question Generation Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    START: Need Question                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Select Topic (Controlled Randomness)               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Fresher Topics:                                     │    │
│  │  • math                                             │    │
│  │  • logical_reasoning                                │    │
│  │  • pattern_recognition                              │    │
│  │  • basic_problem_solving                            │    │
│  │                                                     │    │
│  │ Experienced Topics:                                 │    │
│  │  • analytical_reasoning                             │    │
│  │  • decision_making                                  │    │
│  │  • logical_reasoning                                │    │
│  │  • math                                             │    │
│  └─────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Generate Question via LLM                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Prompt: "Generate a unique {topic} question         │    │
│  │          for {candidate_type} candidate"            │    │
│  │                                                     │    │
│  │ System: "You are an offline AI HR interview agent" │    │
│  │                                                     │    │
│  │ Temperature: 0.8 (controlled randomness)            │    │
│  └─────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Check Semantic Similarity                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Compare new question with asked_questions list      │    │
│  │                                                     │    │
│  │ LLM evaluates: "Is this semantically similar?"      │    │
│  │                                                     │    │
│  │ Temperature: 0.3 (more deterministic)               │    │
│  └─────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │
                    ┌────┴────┐
                    │         │
              Similar?   Not Similar?
                    │         │
                    ▼         ▼
            ┌──────────┐  ┌──────────────┐
            │ Attempt  │  │ Add to       │
            │ < 3?     │  │ asked_       │
            │          │  │ questions    │
            │ Yes: Goto│  │              │
            │ Step 1   │  │ RETURN       │
            │          │  │ Question     │
            │ No: Use  │  └──────────────┘
            │ Fallback │
            └──────────┘
```

## Scoring System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ALL ANSWERS COLLECTED                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                    ┌────┴────┐
                    │         │
                    ▼         ▼
        ┌──────────────┐  ┌──────────────┐
        │  Aptitude    │  │ All Answers  │
        │  Answers     │  │ (Including   │
        │  (60%)       │  │  Aptitude)   │
        │              │  │ (40%)        │
        └──────┬───────┘  └──────┬───────┘
               │                 │
               ▼                 ▼
    ┌──────────────────┐  ┌──────────────────┐
    │ For each answer: │  │ For each answer: │
    │                  │  │                  │
    │ 1. Get correct   │  │ 1. Evaluate with │
    │    answer from   │  │    LLM:          │
    │    stored data   │  │    • Clarity     │
    │                  │  │    • Fluency     │
    │ 2. Evaluate with │  │    • Confidence  │
    │    LLM:          │  │    • Structure   │
    │    • Numerical   │  │    • Relevance   │
    │      equivalence │  │                  │
    │    • Semantic    │  │ 2. Score 0-10    │
    │      equivalence │  │                  │
    │                  │  │ 3. Average all   │
    │ 3. Mark correct/ │  │    scores        │
    │    incorrect     │  │                  │
    └──────┬───────────┘  └──────┬───────────┘
           │                     │
           ▼                     ▼
    ┌──────────────────┐  ┌──────────────────┐
    │ Aptitude Score   │  │ Communication    │
    │                  │  │ Score            │
    │ (correct/total)  │  │                  │
    │     × 60         │  │ (avg/10) × 40    │
    │                  │  │                  │
    │ Max: 60 points   │  │ Max: 40 points   │
    └──────┬───────────┘  └──────┬───────────┘
           │                     │
           └──────────┬──────────┘
                      │
                      ▼
            ┌──────────────────┐
            │   TOTAL SCORE    │
            │                  │
            │ Aptitude +       │
            │ Communication    │
            │                  │
            │ Max: 100 points  │
            └──────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  RECOMMENDATION      │
        │                      │
        │ ≥80: Strong Hire     │
        │ ≥65: Hire            │
        │ ≥50: Borderline      │
        │ <50: Reject          │
        └──────────────────────┘
```

## Data Flow Diagram

```
┌──────────────┐
│  Candidate   │
│  Registers   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Database: candidates table          │
│  • id, name, email, created_at       │
└──────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│  Interview   │
│   Starts     │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│  State: In-Memory (Client-Side)      │
│  • current_state                     │
│  • candidate_type                    │
│  • experience_years                  │
│  • asked_questions []                │
│  • generated_questions []            │
│  • history []                        │
└──────┬───────────────────────────────┘
       │
       │ (Each answer)
       ▼
┌──────────────────────────────────────┐
│  State.history.append({              │
│    question: "...",                  │
│    answer: "...",                    │
│    correct_answer: "...",            │
│    is_aptitude: true/false           │
│  })                                  │
└──────┬───────────────────────────────┘
       │
       │ (Interview complete)
       ▼
┌──────────────────────────────────────┐
│  Calculate Scores                    │
│  • aptitude_score (60)               │
│  • communication_score (40)          │
│  • total_score (100)                 │
│  • strengths []                      │
│  • improvement_areas []              │
│  • recommendation                    │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  Database: Save Results              │
│                                      │
│  interview_answers:                  │
│  • question_text, answer             │
│                                      │
│  aptitude_results:                   │
│  • question, given, correct,         │
│    is_correct                        │
│                                      │
│  final_results:                      │
│  • interview_score (comm)            │
│  • aptitude_score                    │
│  • total_score                       │
│  • status (recommendation)           │
│  • transcript (full JSON)            │
└──────────────────────────────────────┘
```

## Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      USER REQUEST                           │
│              "Start Interview" Button Click                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Frontend (app.js)                                          │
│  • Capture audio from microphone                            │
│  • Send to /interview/next with state                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend (main.py)                                          │
│  • Receive audio + state                                    │
│  • Call interview_manager.process_answer()                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  STT Service (stt.py)                                       │
│  • Transcribe audio to text                                 │
│  • Return transcription                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Interview Manager (interview_manager.py)                   │
│  • Update state with answer                                 │
│  • Detect experience (if EXPERIENCE_DETECTION)              │
│  • Store in history                                         │
│  • Call get_next_step()                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Interview Manager (get_next_step)                          │
│  • Check current state                                      │
│  • If APTITUDE_TEST: Generate question                      │
│  • Call _generate_unique_aptitude_question()                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  LLM Service (llm.py)                                       │
│  • generate_aptitude_question()                             │
│  • Select topic with random.choice()                        │
│  • Query Ollama with prompt                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Ollama (localhost:11434)                                   │
│  • Process prompt with Mistral model                        │
│  • Generate question + answer                               │
│  • Return JSON                                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  LLM Service (llm.py)                                       │
│  • check_semantic_similarity()                              │
│  • Compare with asked_questions                             │
│  • Return True/False                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Interview Manager                                          │
│  • If similar: Regenerate (max 3 attempts)                  │
│  • If unique: Add to asked_questions                        │
│  • Store in generated_questions                             │
│  • Return question text                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  TTS Service (tts.py)                                       │
│  • Convert text to speech                                   │
│  • Save audio file                                          │
│  • Return audio path                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend (main.py)                                          │
│  • Return JSON response:                                    │
│    - text (question)                                        │
│    - audio_url                                              │
│    - state (updated)                                        │
│    - transcription                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Frontend (app.js)                                          │
│  • Display question text                                    │
│  • Play audio                                               │
│  • Update state                                             │
│  • Wait for user response                                   │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

```
┌─────────────────────────────────────┐
│         candidates                  │
├─────────────────────────────────────┤
│ id (PK)          INTEGER            │
│ name             VARCHAR             │
│ email            VARCHAR (UNIQUE)    │
│ created_at       TIMESTAMP           │
└─────────────────────────────────────┘
              │
              │ 1:N
              ▼
┌─────────────────────────────────────┐
│      interview_answers              │
├─────────────────────────────────────┤
│ id (PK)          INTEGER            │
│ candidate_id (FK) INTEGER           │
│ question_index   INTEGER            │
│ question_text    TEXT               │
│ transcribed_answer TEXT             │
│ created_at       TIMESTAMP          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│      aptitude_results               │
├─────────────────────────────────────┤
│ id (PK)          INTEGER            │
│ candidate_id (FK) INTEGER           │
│ question_index   INTEGER            │
│ question_text    TEXT               │
│ given_answer     TEXT               │
│ correct_answer   TEXT               │
│ is_correct       BOOLEAN            │
│ created_at       TIMESTAMP          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│        final_results                │
├─────────────────────────────────────┤
│ id (PK)          INTEGER            │
│ candidate_id (FK) INTEGER (UNIQUE)  │
│ interview_score  FLOAT (comm 40)    │
│ aptitude_score   FLOAT (apt 60)     │
│ total_score      FLOAT (100)        │
│ status           VARCHAR            │
│ transcript       TEXT (JSON)        │
│ created_at       TIMESTAMP          │
└─────────────────────────────────────┘
```
