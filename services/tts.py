import subprocess
import os
import uuid

class TTSService:
    def __init__(self, model_path="en_US-lessac-medium.onnx", piper_path="piper"):
        self.model_path = model_path
        self.piper_path = piper_path
        self.output_dir = "data/audio_out"
        os.makedirs(self.output_dir, exist_ok=True)

    def text_to_speech(self, text: str):
        """
        Converts text to speech using Piper TTS CLI.
        Returns the path to the generated wav file.
        """
        filename = f"{uuid.uuid4()}.wav"
        output_path = os.path.join(self.output_dir, filename)
        
        # Command for Piper: echo text | piper --model model.onnx --output_file out.wav
        try:
            # Check if piper exists
            import shutil
            if not shutil.which(self.piper_path) and not os.path.exists(self.piper_path):
                print(f"Warning: Piper executable not found at {self.piper_path}. Skipping TTS.")
                return None

            process = subprocess.Popen(
                [self.piper_path, "--model", self.model_path, "--output_file", output_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            process.communicate(input=text)
            if os.path.exists(output_path):
                return output_path
            return None
        except Exception as e:
            print(f"TTS Error: {e}")
            return None

tts_service = TTSService()
