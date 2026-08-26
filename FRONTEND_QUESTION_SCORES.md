# Frontend Integration Guide - Display Question Scores

## 📊 Question-Wise Scores Now Available!

Each question in the Interview Transcript now has an individual **score_out_of_5** field.

---

## 📝 Data Structure

### What You Get from `/result/{resultId}` API:

```json
{
  "details": {
    "transcript": [
      {
        "question": "Are you a fresher or do you have work experience?",
        "answer": "Take a yellow experience",
        "is_experience_detection": true,
        "score_out_of_5": 2.5,
        "rating": "Below Average",
        "weighted_score": 5.2
      },
      {
        "question": "Please introduce yourself and tell me about your background.",
        "answer": "I am a patent developer and I am an autonomous expert.",
        "is_hr_question": true,
        "score_out_of_5": 3.0,
        "rating": "Satisfactory",
        "weighted_score": 6.5
      },
      {
        "question": "What are your key strengths and skills?",
        "answer": "I am a group managing my time and project manager",
        "is_hr_question": true,
        "score_out_of_5": 2.5,
        "rating": "Below Average",
        "weighted_score": 5.8
      }
    ]
  }
}
```

---

## 🎨 Frontend Display Code

### Angular/TypeScript Example:

```typescript
// In your component.ts
export class CandidateDetailsComponent {
  transcript: any[] = [];
  
  loadCandidateDetails(resultId: number) {
    this.http.get(`/result/${resultId}`).subscribe((response: any) => {
      // Get the transcript with scores
      this.transcript = response.details.transcript || [];
    });
  }
  
  // Helper to get star display
  getStars(score: number): string {
    const fullStars = Math.floor(score);
    const hasHalfStar = (score - fullStars) >= 0.5;
    
    let stars = '⭐'.repeat(fullStars);
    if (hasHalfStar) stars += '✨';
    stars += '☆'.repeat(5 - fullStars - (hasHalfStar ? 1 : 0));
    
    return stars;
  }
  
  // Helper to get score color
  getScoreColor(score: number): string {
    if (score >= 4.0) return '#4CAF50'; // Green
    if (score >= 3.0) return '#2196F3'; // Blue  
    if (score >= 2.0) return '#FF9800'; // Orange
    return '#F44336'; // Red
  }
}
```

### HTML Template:

```html
<!-- Interview Transcript Section -->
<div class="interview-transcript">
  <h3>📝 Interview Transcript</h3>
  
  <div class="question-item" *ngFor="let item of transcript; let i = index">
    <!-- Only show HR questions (not aptitude) -->
    <div *ngIf="!item.is_aptitude">
      
      <!-- Question Header with Score -->
      <div class="question-header">
        <strong class="question-number">Q{{i}}:</strong>
        <strong class="question-text">{{item.question}}</strong>
        
        <!-- Score Badge -->
        <span class="score-badge" 
              *ngIf="item.score_out_of_5"
              [style.background]="getScoreColor(item.score_out_of_5)">
          {{item.score_out_of_5}}/5
        </span>
      </div>
      
      <!-- Answer -->
      <div class="answer-section">
        <span class="answer-label">A:</span>
        <span class="answer-text">{{item.answer}}</span>
      </div>
      
      <!-- Rating with Stars -->
      <div class="rating-section" *ngIf="item.rating">
        <span class="stars">{{getStars(item.score_out_of_5)}}</span>
        <span class="rating-label">({{item.rating}})</span>
      </div>
      
    </div>
  </div>
</div>
```

### CSS Styling:

```css
.interview-transcript {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
}

.question-item {
  background: #f8f9fa;
  border-left: 4px solid #007bff;
  padding: 15px;
  margin-bottom: 15px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.question-item:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transform: translateX(5px);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
  gap: 10px;
}

.question-number {
  color: #007bff;
  font-size: 14px;
  flex-shrink: 0;
}

.question-text {
  flex: 1;
  color: #333;
  font-size: 15px;
  line-height: 1.5;
}

.score-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-weight: bold;
  font-size: 13px;
  white-space: nowrap;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.answer-section {
  background: white;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 10px;
  line-height: 1.6;
}

.answer-label {
  font-weight: 600;
  color: #666;
  margin-right: 8px;
}

.answer-text {
  color: #333;
}

.rating-section {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.stars {
  font-size: 15px;
  letter-spacing: 2px;
}

.rating-label {
  color: #666;
  font-weight: 500;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .question-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .score-badge {
    align-self: flex-start;
    font-size: 12px;
    padding: 4px 10px;
  }
}
```

---

## 🔄 Plain JavaScript Example (No Framework):

```javascript
// Fetch and display results
async function displayCandidateTranscript(resultId) {
  const response = await fetch(`/result/${resultId}`);
  const data = await response.json();
  
  const transcript = data.details.transcript;
  const container = document.getElementById('transcript-container');
  
  container.innerHTML = '<h3>📝 Interview Transcript</h3>';
  
  transcript.forEach((item, index) => {
    // Skip aptitude questions
    if (item.is_aptitude) return;
    
    const stars = getStars(item.score_out_of_5 || 0);
    const scoreColor = getScoreColor(item.score_out_of_5 || 0);
    
    const questionHtml = `
      <div class="question-item">
        <div class="question-header">
          <strong>Q${index}:</strong>
          <strong>${item.question}</strong>
          ${item.score_out_of_5 ? 
            `<span class="score-badge" style="background: ${scoreColor}">
              ${item.score_out_of_5}/5
            </span>` : ''}
        </div>
        
        <div class="answer-section">
          <span class="answer-label">A:</span>
          <span>${item.answer}</span>
        </div>
        
        ${item.rating ?
          `<div class="rating-section">
            <span class="stars">${stars}</span>
            <span class="rating-label">(${item.rating})</span>
          </div>` : ''}
      </div>
    `;
    
    container.innerHTML += questionHtml;
  });
}

function getStars(score) {
  const fullStars = Math.floor(score);
  const hasHalfStar = (score - fullStars) >= 0.5;
  
  let stars = '⭐'.repeat(fullStars);
  if (hasHalfStar) stars += '✨';
  stars += '☆'.repeat(5 - fullStars - (hasHalfStar ? 1 : 0));
  
  return stars;
}

function getScoreColor(score) {
  if (score >= 4.0) return '#4CAF50';
  if (score >= 3.0) return '#2196F3';
  if (score >= 2.0) return '#FF9800';
  return '#F44336';
}

// Call when page loads
displayCandidateTranscript(1);
```

---

## 📱 Example Output:

Based on your screenshot, it will now look like:

```
📝 Interview Transcript

┌─────────────────────────────────────────────────────────┐
│ Q1: Are you a fresher or do you have work experience?  │
│                                            2.5/5        │
│ A: Take a yellow experience                            │
│ ⭐⭐✨☆☆ (Below Average)                                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Q2: Please introduce yourself and tell me about your   │
│     background.                             3.0/5      │
│ A: I am a patent developer and I am an autonomous      │
│    expert.                                             │
│ ⭐⭐⭐☆☆ (Satisfactory)                                 │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Q3: What are your key strengths and skills?  2.5/5    │
│ A: I am a group managing my time and project manager  │
│ ⭐⭐✨☆☆ (Below Average)                                │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ What's Available in Each Question:

```typescript
interface QuestionItem {
  question: string;           // The question text
  answer: string;             // Candidate's answer
  score_out_of_5?: number;    // ⭐ NEW! Score 0-5
  rating?: string;            // ⭐ NEW! "Excellent", "Good", etc.
  weighted_score?: number;    // ⭐ NEW! Detailed 0-10 score
  is_aptitude?: boolean;      // true for aptitude questions
  is_hr_question?: boolean;   // true for HR questions
  is_experience_detection?: boolean; // true for experience question
}
```

---

## 🚀 Quick Implementation Checklist:

- [ ] Update your frontend component to fetch from `/result/{resultId}`
- [ ] Access `response.details.transcript` array
- [ ] For each item, display `item.score_out_of_5` if it exists
- [ ] Show star rating using `getStars()` helper
- [ ] Color-code score badge using `getScoreColor()` helper
- [ ] Display `item.rating` text (Excellent, Good, etc.)

---

## 💡 Tips:

1. **Filter Questions**: Use `!item.is_aptitude` to show only HR questions
2. **Show All**: Remove filter to show all questions including aptitude
3. **Sort by Score**: `transcript.sort((a, b) => (b.score_out_of_5 || 0) - (a.score_out_of_5 || 0))`
4. **Highlight Low Scores**: Add special styling for scores < 3.0
5. **Average Score**: Calculate average: `transcript.reduce((sum, item) => sum + (item.score_out_of_5 || 0), 0) / transcript.length`

---

## 🎯 Example: Show Only Low-Scoring Questions

```typescript
// In your component
getLowScoringQuestions() {
  return this.transcript.filter(item => 
    !item.is_aptitude && 
    item.score_out_of_5 && 
    item.score_out_of_5 < 3.0
  );
}
```

```html
<div class="alert alert-warning" *ngIf="getLowScoringQuestions().length > 0">
  <h4>⚠️ Areas Needing Improvement</h4>
  <p>The following questions scored below 3.0/5:</p>
  <ul>
    <li *ngFor="let item of getLowScoringQuestions()">
      {{item.question}} - {{item.score_out_of_5}}/5
    </li>
  </ul>
</div>
```

---

**Now each question in your Interview Transcript has a score! 🎉**

Simply access `item.score_out_of_5`, `item.rating`, and `item.weighted_score` from the transcript array.
