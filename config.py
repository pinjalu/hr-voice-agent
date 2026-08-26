"""
Configuration file for API keys and settings
"""
import os

# Gemini API Key for better scoring accuracy
# Get your free API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

