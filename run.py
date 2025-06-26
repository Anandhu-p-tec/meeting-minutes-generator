import gradio as gr
import os
from app.modules.preprocessing import transcribe_audio
from app.modules.summarizer import process_transcript_file, generate_meeting_minutes
from app.modules.exporter import export_meeting_minutes_to_docx, refine_meeting_minutes
from app import config

def process_audio_to_docx(audio_file: str, api_key_text: str) -> str:
    """
    Takes an audio file and API key, converts it to transcript, processes it into MeetingMinutes,
    refines the result, and exports it to a DOCX file.

    Args:
        audio_file (str): Path to the uploaded audio file.
        api_key_text (str): OpenAI API key.

    Returns:
        str: Path to the generated DOCX file.
    """
    if not audio_file:
        raise ValueError("No audio file uploaded.")
    if not api_key_text:
        raise ValueError("Please provide an OpenAI API Key.")

    os.environ["OPENAI_API_KEY"] = api_key_text

    temp_transcript = "temp_transcript.txt"
    try:
        # Step 1: Transcribe the audio into text
        segments, info = transcribe_audio(
            input_audio=audio_file,
            model_size=config.WHISPER_MODEL_SIZE,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE,
            beam_size=config.WHISPER_BEAM_SIZE,
            vad_filter=config.WHISPER_USE_VAD
        )

        # Step 2: Combine the transcript segments into full text
        transcript_text = "\n".join(seg['text'] for seg in segments)
        with open(temp_transcript, "w", encoding="utf-8") as f:
            f.write(transcript_text)

        # Step 3: Process the transcript into MeetingMinutes format
        meeting_minutes = process_transcript_file(temp_transcript, chunk_size=10, chunk_overlap=2)

        # Step 4: Refine the MeetingMinutes object
        refined_minutes = refine_meeting_minutes(meeting_minutes)

        # Step 5: Export to DOCX
        output_docx = "generated_meeting_minutes.docx"
        export_meeting_minutes_to_docx(refined_minutes, output_docx)

        return output_docx

    except Exception as e:
        raise Exception(f"An error occurred: {str(e)}")
    finally:
        if os.path.exists(temp_transcript):
            os.remove(temp_transcript)

# Gradio web interface
iface = gr.Interface(
    fn=process_audio_to_docx,
    inputs=[
        gr.Audio(type="filepath", label="Upload Audio File"),
        gr.Textbox(lines=1, placeholder="Enter your OpenAI API Key", label="OpenAI API Key", type="text")
    ],
    outputs=gr.File(label="Download Meeting Minutes (.docx)"),
    title="Meeting Minutes Generator",
    description="Upload an audio file and provide your OpenAI API Key to generate structured meeting minutes as a Word document."
)

if __name__ == "__main__":
    iface.launch()
