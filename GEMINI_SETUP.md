,m # Gemini API Setup Guide

## Why Use Gemini API for Scoring?

Using Google's Gemini API for scoring provides several advantages:

✅ **More Reliable**: Better at following instructions and generating consistent scores  
✅ **Faster**: Typically responds in 2-5 seconds (vs 10-30 seconds for local LLM)  
✅ **More Accurate**: Better grammar detection and communication evaluation  
✅ **No Timeouts**: More stable than local LLM, especially for complex evaluations  
✅ **Better JSON Parsing**: More consistent JSON output for structured scoring  
✅ **Free Tier Available**: Generous free tier for testing and small-scale use

## Setup Instructions

### Step 1: Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### Step 2: Set Environment Variable

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

**Permanent Setup (Windows):**
1. Open System Properties → Environment Variables
2. Add new variable: `GEMINI_API_KEY` = `your_api_key_here`

**Permanent Setup (Linux/Mac):**
Add to `~/.bashrc` or `~/.zshrc`:
```bash
export GEMINI_API_KEY="your_api_key_here"
```

### Step 3: Restart Your Application

After setting the environment variable, restart your FastAPI server:

```bash
# Stop the current server (Ctrl+C)
# Then restart
python main.py
# or
uvicorn main:app --reload
```

## How It Works

- **With Gemini API Key**: The system automatically uses Gemini for all evaluation/scoring tasks
- **Without Gemini API Key**: The system falls back to local Ollama (requires Ollama running)

### Automatic Detection

The system automatically detects when to use Gemini:
- ✅ **Evaluation/Scoring tasks** → Uses Gemini (if API key is set)
- ✅ **Question generation** → Uses Ollama (local, faster for simple tasks)
- ✅ **Other tasks** → Uses Ollama (local, no API costs)

## Testing

To verify Gemini is working:

1. Set your API key
2. Start the interview
3. Check console output - you should see:
   - `"Using Gemini API for evaluation"` (if working)
   - `"Gemini API failed, falling back to Ollama"` (if API key is invalid)

## Cost Information

**Gemini 1.5 Flash (Free Tier):**
- 15 requests per minute
- 1 million tokens per day
- Perfect for HR interview scoring (each evaluation uses ~500-1000 tokens)

**Pricing (if you exceed free tier):**
- $0.075 per 1M input tokens
- $0.30 per 1M output tokens
- Very affordable for interview scoring

## Troubleshooting

### Issue: "Gemini API Error: Request timed out"
**Solution**: Check your internet connection. Gemini requires internet access.

### Issue: "Gemini API Error: Invalid API key"
**Solution**: 
1. Verify your API key is correct
2. Make sure environment variable is set correctly
3. Restart your application after setting the variable

### Issue: Still using Ollama instead of Gemini
**Solution**:
1. Check if `GEMINI_API_KEY` environment variable is set: `echo $GEMINI_API_KEY` (Linux/Mac) or `echo %GEMINI_API_KEY%` (Windows)
2. Restart your application
3. Check console logs for error messages

## Benefits for Your Use Case

For HR interview scoring, Gemini provides:
- **Stricter grammar detection**: Better at catching "For now I have worked" type errors
- **More consistent scoring**: Less variation between similar answers
- **Better JSON parsing**: More reliable structured output
- **Faster evaluation**: 2-5 seconds vs 10-30 seconds

## Fallback Behavior

If Gemini API fails or times out, the system automatically falls back to:
1. Local Ollama (if running)
2. Rule-based fallback evaluation (if Ollama also fails)

This ensures your interview system always works, even without internet or API access.

