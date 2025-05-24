import random
from typing import List

def mock_transcribe_audio(audio_file_path: str) -> str:
    """
    Mock function to simulate OpenAI's Whisper transcription.
    Returns a random sample transcription.
    """
    sample_transcriptions = [
        "Hello, this is a test recording. I'm speaking into the Brilliant Frame glasses.",
        "The weather is beautiful today. I can see the sun shining through the window.",
        "I need to remember to buy groceries later. Milk, eggs, and bread are on the list.",
        "This is an example of speech recognition. The Frame glasses are recording my voice.",
        "Testing one two three. Can you hear me clearly? This is a mock transcription."
    ]
    return random.choice(sample_transcriptions)

def mock_get_completion(prompt: str) -> str:
    """
    Mock function to simulate OpenAI's text completion.
    Returns a random sample response.
    """
    sample_responses = [
        "Based on your request, I would recommend trying the following approach...",
        "That's an interesting question. Let me break this down into three key points...",
        "I understand you're looking for guidance on this topic. Here's what I suggest...",
        "After analyzing your input, I think the best course of action would be...",
        "Let me provide some insights on this matter. First, consider the following..."
    ]
    return random.choice(sample_responses)

def mock_process_audio(audio_file_path: str) -> List[str]:
    """
    Mock function that combines transcription and completion.
    Returns a list of text blocks for display.
    """
    # Get mock transcription
    transcription = mock_transcribe_audio(audio_file_path)
    
    # Get mock completion based on transcription
    completion = mock_get_completion(transcription)
    
    # Return both as text blocks
    return [
        "Transcription:",
        transcription,
        "",
        "AI Response:",
        completion
    ] 