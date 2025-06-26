import os
import shutil
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

from app.modules.preprocessing import transcribe_audio, save_transcript, preprocess_transcript, clean_text
from app.modules.summarizer import generate_meeting_minutes, process_transcript_file
from app.modules.exporter import export_meeting_minutes_to_docx
from app.modules.schema import MeetingMinutes
from app import config

app = FastAPI(
    title="Meeting Minutes Generator API",
    description="API for an application that generates meeting minutes from transcripts.",
    version="1.0"
)

# ---------------------
# Endpoint: Convert audio to transcript
# ---------------------
@app.post("/transcribe", summary="Convert audio to transcript")
async def transcribe_endpoint(audio: UploadFile = File(...)):
    """
    Receive an audio file, save it temporarily, call the transcribe_audio function,
    and return the transcript along with metadata.
    """
    temp_audio_path = f"temp_{audio.filename}"
    try:
        with open(temp_audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        segments, info = transcribe_audio(
            input_audio=temp_audio_path,
            model_size=config.WHISPER_MODEL_SIZE,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE,
            beam_size=config.WHISPER_BEAM_SIZE,
            vad_filter=config.WHISPER_USE_VAD
        )
        result = {
            "transcript": segments,
            "info": {
                "language": info.language,
                "language_probability": info.language_probability
            }
        }
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)


# ---------------------
# Endpoint: Convert audio to transcript and return as TXT file
# ---------------------

def remove_file(path: str):
    if os.path.exists(path):
        os.remove(path)

@app.post("/transcribe-txt", summary="Convert audio to transcript and return as TXT file")
async def transcribe_txt_endpoint(audio: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    Receive an audio file, save it temporarily, transcribe it, save the result to a TXT file,
    and return the TXT file for download.
    """
    temp_audio_path = f"temp_{audio.filename}"
    temp_txt_path = f"transcript_{audio.filename}.txt"
    try:
        with open(temp_audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        segments, info = transcribe_audio(
            input_audio=temp_audio_path,
            model_size=config.WHISPER_MODEL_SIZE,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE,
            beam_size=config.WHISPER_BEAM_SIZE,
            vad_filter=config.WHISPER_USE_VAD
        )

        save_transcript(segments, temp_txt_path)

        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

        if background_tasks:
            background_tasks.add_task(remove_file, temp_txt_path)

        return FileResponse(
            path=temp_txt_path,
            media_type="text/plain",
            filename="transcript.txt"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------
# Endpoint: Generate meeting minutes from uploaded transcript file
# ---------------------
@app.post("/summarize-file", summary="Generate meeting minutes from transcript file")
async def summarize_file_endpoint(
        file: UploadFile = File(...),
        chunk_size: int = Form(7),
        chunk_overlap: int = Form(2)
):
    """
    Receive a transcript file, save it temporarily, process it using process_transcript_file,
    and return the combined meeting minutes.
    """
    temp_file_path = f"temp_{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        merged_minutes = process_transcript_file(temp_file_path, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return JSONResponse(content=merged_minutes.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


# ---------------------
# Endpoint: Generate meeting minutes from raw transcript text
# ---------------------
class TranscriptInput(BaseModel):
    transcript: str


@app.post("/summarize", summary="Generate meeting minutes from text transcript")
async def summarize_endpoint(input_data: TranscriptInput):
    """
    Receive transcript text and return generated meeting minutes in JSON format.
    """
    try:
        meeting_minutes = generate_meeting_minutes(input_data.transcript)
        return JSONResponse(content=meeting_minutes.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------
# Endpoint: Export meeting minutes to a DOCX file
# ---------------------
@app.post("/export-docx", summary="Export meeting minutes as DOCX")
async def export_docx_endpoint(meeting_minutes: MeetingMinutes, background_tasks: BackgroundTasks):
    """
    Receive meeting minutes in JSON format and export to a DOCX file.
    Automatically deletes the file after sending it to the client.
    """
    try:
        temp_docx = "temp_meeting_minutes.docx"
        export_meeting_minutes_to_docx(meeting_minutes, temp_docx)
        background_tasks.add_task(remove_file, temp_docx)
        return FileResponse(
            path=temp_docx,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename="meeting_minutes.docx"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
