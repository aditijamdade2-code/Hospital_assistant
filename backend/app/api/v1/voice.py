from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
from backend.app.services.voice.factory import get_stt_provider, get_tts_provider

router = APIRouter(prefix="/voice", tags=["Voice"])

class SynthesizeRequest(BaseModel):
    text: str
    language: Optional[str] = "en"
    voice: Optional[str] = None

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = Form("en")
):
    """
    Transcribes uploaded audio into structured text in the given language (en, hi, mr).
    """
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty audio file provided")
        
        provider = get_stt_provider()
        text = await provider.transcribe(content, language=language, filename=file.filename or "audio.wav")
        return {
            "transcription": text,
            "language": language,
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")

@router.post("/synthesize")
async def synthesize_speech(req: SynthesizeRequest):
    """
    Synthesizes assistant text into audio.
    """
    try:
        provider = get_tts_provider()
        audio_bytes = await provider.synthesize(req.text, language=req.language, voice=req.voice)
        return Response(content=audio_bytes, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {e}")
