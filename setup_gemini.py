"""
Quick setup script to configure Gemini API key
Run this once to set your API key
"""
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    print("⚠️  GEMINI_API_KEY is not set.")
    print("")
    print("Set it as an environment variable before running this script:")
    print("  Windows PowerShell: $env:GEMINI_API_KEY='your-key-here'")
    print("  Windows CMD: set GEMINI_API_KEY=your-key-here")
    print("  Linux/Mac: export GEMINI_API_KEY='your-key-here'")
else:
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
    print("✅ Gemini API key loaded from environment successfully!")

