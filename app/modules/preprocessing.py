import os
import re
from faster_whisper import WhisperModel, BatchedInferencePipeline

def clean_text(text: str) -> str:
    """
    Perform basic text preprocessing:
      - Remove redundant whitespaces between words.
      - Trim leading/trailing spaces.
    Can be extended with additional processing (e.g., punctuation normalization) if needed.
    """
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def preprocess_transcript(segments: list) -> list:
    """
    Preprocess each transcript segment, return a list of dictionaries containing:
      - start: segment start time
      - end: segment end time
      - text: cleaned content
    """
    processed_segments = []
    for segment in segments:
        processed_segments.append({
            'start': segment.start,
            'end': segment.end,
            'text': clean_text(segment.text)
        })
    return processed_segments

def transcribe_audio(input_audio: str = 'audio.mp3',
                     model_size: str = 'base',
                     device: str = 'cpu',
                     compute_type: str = 'int8',
                     beam_size: int = 5,
                     vad_filter: bool = True) -> tuple:
    """
    Transcribe audio file to text using Faster Whisper.

    Args:
        input_audio (str): Path to audio file (e.g., audio.mp3).
        model_size (str): Whisper model size.
        device (str): Device for inference.
        compute_type (str): Compute type (e.g., int8).
        beam_size (int): Beam size for decoding.
        vad_filter (bool): Apply VAD filter to remove non-speech.

    Returns:
        tuple: (processed_segments, info) where processed_segments is a list of cleaned segments,
               and info contains transcription metadata (e.g., language, probability).

    Raises:
        FileNotFoundError: If the audio file does not exist.
    """
    if not os.path.exists(input_audio):
        raise FileNotFoundError(f"File '{input_audio}' does not exist.")

    # Initialize Faster Whisper model
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    # Transcription configuration
    transcription_kwargs = {"beam_size": beam_size}
    if vad_filter:
        transcription_kwargs["vad_filter"] = True

    # Run transcription
    batched_model = BatchedInferencePipeline(model=model)
    segments, info = batched_model.transcribe(input_audio, **transcription_kwargs, batch_size=32)
    segments = list(segments)  # Convert generator to list
    processed_segments = preprocess_transcript(segments)
    return processed_segments, info

def save_transcript(segments: list, output_file: str) -> None:
    """
    Save the processed transcript to a text file.
    Each segment is saved in the format:
      transcript_text
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for seg in segments:
            f.write(f"{seg['text']}\n")
