# 📊 AI Interview Scoring Guide

This document explains the logic behind the **Empiric Infotech AI Interview Agent** scoring system.

## 🏆 Total Score Breakdown
The candidate is evaluated on a 100-point scale, split into two main components:

| Component | Weight | Max Score | Description |
|-----------|--------|-----------|-------------|
| **1. Aptitude** | **60%** | 60 pts | Technical accuracy and problem-solving skills. |
| **2. Communication** | **40%** | 40 pts | Clarity, fluency, and professional articulation. |

---

## 🧠 1. Aptitude Scoring (60%)
- **Number of Questions**: 5
- **Points per Question**: 12 points
- **How it works**:
  - The system compares the candidate's spoken answer to the stored correct answer.
  - **Exact Match**: If the answer matches exactly (e.g., "42"), full points are awarded immediately.
  - **Semantic Match**: If the answer is phrased differently (e.g., "The answer is 42"), the **Local LLM** analyzes the meaning. If the logic is correct, full points are awarded.
  - **Wrong/Skipped**: 0 points.

> **Example**:
> - Q: "What is 20 + 20?"
> - A: "It's forty." -> **Correct** (LLM understands "forty" == 40).

---

## 🗣️ 2. Interview & Communication Scoring (40%)
This score evaluates **HOW** the candidate speaks, not just **WHAT** they say.

### **What is Analyzed?**
Every single response (Introduction, Experience, HR answers, and even Aptitude explanations) is analyzed by the AI Engine.

### **Scoring Criteria (0-10 Scale per Answer)**
The LLM evaluates each response based on four key pillars:

1.  **Clarity 💎**
    - Is the answer easy to understand?
    - Is the speech coherent?
2.  **Fluency 🌊**
    - Does the candidate speak naturally without excessive pauses?
    - Is the sentence structure correct?
3.  **Relevance 🎯**
    - Does the answer directly address the question asked?
    - Does it stay on topic?
4.  **Conciseness ⏱️ (Context-Aware)**
    - **For Math/Logic**: Short answers are rewarded (e.g., "The answer is 5" = 10/10).
    - **For HR/Intro**: Detailed explanations are rewarded (e.g., "I have 3 years experience in..." = 10/10).
    - *One-word answers for HR questions result in low scores.*

### **Calculation Logic**
1.  The AI assigns a **Quality Score (0-10)** for every answer.
2.  The **Average Quality Score** is calculated across the entire interview.
3.  The Average is scaled to 40 points.
    - *Example: Average Quality = 8/10 -> Communication Score = 32/40.*

---

## 📈 Final Recommendation (Verdict)
Based on the **Total Score** (Aptitude + Communication), the system automatically classifies the candidate:

| Total Score | Verdict |
|-------------|---------|
| **80 - 100** | ✅ **Strong Hire** |
| **65 - 79** | 👍 **Hire** |
| **50 - 64** | ⚠️ **Borderline** |
| **0 - 49** | ❌ **Reject** |

---

## 🛠️ Technical Implementation
- **File**: `services/scoring.py`
- **Logic**:
  - `calculate_aptitude_score()` counts correct technical answers.
  - `calculate_communication_score()` sends every Q&A pair to the LLM with a specific prompt to evaluate soft skills.
