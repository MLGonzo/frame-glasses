import openai
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

async def transcribe_audio(audio_file_path: str | Path) -> str:
    """
    Transcribe an audio file using OpenAI's Whisper model.
    
    Args:
        audio_file_path: Path to the audio file to transcribe
        
    Returns:
        str: The transcribed text from the audio file
        
    Raises:
        FileNotFoundError: If the audio file doesn't exist
        Exception: For other errors during transcription
    """
    try:
        # Ensure the file exists
        audio_path = Path(audio_file_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
            
        # Open and transcribe the audio file
        with open(audio_path, 'rb') as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1"
            )
            
        return transcription.text
        
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        raise