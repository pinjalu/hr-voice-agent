import os
from faster_whisper import WhisperModel

class STTService:
    def __init__(self, model_size="small.en", device="cpu", compute_type="int8"):
        # Use small.en model for better accuracy
        print(f"Loading Whisper model: {model_size}...")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        print("Whisper model loaded successfully!")

    def transcribe(self, audio_path: str):
        if not os.path.exists(audio_path):
            return ""
            
        # Check if file is too small (e.g., less than 1KB) to be a valid recording
        if os.path.getsize(audio_path) < 100:
            return ""
        
        try:
            # Use language hint "en" and reduced beam size for speed
            segments, info = self.model.transcribe(
                audio_path, 
                beam_size=2,  # Reduced from 5 to 2 for 2-3x speedup
                language="en",
                condition_on_previous_text=False,
                vad_filter=True  # Voice activity detection to filter out silence
            )
            text = " ".join([segment.text for segment in segments])
            return text.strip()
        except Exception as e:
            print(f"STT Error processing {audio_path}: {e}")
            return ""

stt_service = STTService()
