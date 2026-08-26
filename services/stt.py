import os
from faster_whisper import WhisperModel

class STTService:
    def __init__(self, model_size="small", device="cpu", compute_type="int8"):
        # Use small model for better accuracy (base is faster but less accurate)
        print(f"Loading Whisper model: {model_size}...")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        print("Whisper model loaded successfully!")

    def transcribe(self, audio_path: str):
        if not os.path.exists(audio_path):
            return ""
        
        # Use language hint and better beam size for accuracy
        segments, info = self.model.transcribe(
            audio_path, 
            beam_size=5,
            language="en",
            condition_on_previous_text=False,
            vad_filter=True  # Voice activity detection to filter out silence
        )
        text = " ".join([segment.text for segment in segments])
        return text.strip()

stt_service = STTService()
