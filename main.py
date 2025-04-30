from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
import torch
import pytesseract
from PIL import Image
import os
import shutil
import logging
from tempfile import NamedTemporaryFile
import traceback
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tesseract setup
tesseract_path = os.getenv("TESSERACT_PATH") or shutil.which("tesseract")
if not tesseract_path or not os.path.exists(tesseract_path):
    raise FileNotFoundError(f"Tesseract not found at {tesseract_path}")
pytesseract.pytesseract.tesseract_cmd = tesseract_path

# Serve frontend
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend")

# Load AI models
whisper_model = pipeline("automatic-speech-recognition", model="openai/whisper-small")
trocr_model = pipeline("image-to-text", model="microsoft/trocr-base-printed")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
grammar_corrector = pipeline("text2text-generation", model="grammarly/coedit-large")

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_AUDIO_TYPES = ["audio/wav", "audio/x-wav"]
ALLOWED_IMAGE_TYPES = ["image/png", "image/jpeg", "image/jpg"]

class TextRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/voice")
async def voice_to_text(audio: UploadFile = File(...)):
    try:
        validate_file(audio, 'audio')
        with NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            content = await audio.read()
            temp_audio.write(content)
            temp_audio_path = temp_audio.name
        try:
            result = whisper_model(temp_audio_path)
            return {"text": result["text"]}
        finally:
            os.unlink(temp_audio_path)
    except Exception as e:
        logger.error(f"Error in voice_to_text: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

@app.post("/text")
async def image_to_text(file: UploadFile = File(...)):
    try:
        validate_file(file, 'image')
        image = Image.open(file.file)
        result = trocr_model(image)
        return {"text": result[0]["generated_text"]}
    except Exception as e:
        logger.error(f"Error in image_to_text: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/summarize")
async def summarize_text(data: TextRequest):
    try:
        summary = summarizer(data.text, max_length=150, min_length=30, do_sample=False)
        return {"summary": summary[0]["summary_text"]}
    except Exception as e:
        logger.error(f"Error in summarize_text: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error summarizing text: {str(e)}")

@app.post("/correct-grammar")
async def correct_grammar(data: TextRequest):
    try:
        corrected = grammar_corrector(data.text)
        return {"corrected": corrected[0]["generated_text"]}
    except Exception as e:
        logger.error(f"Error in correct_grammar: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error correcting grammar: {str(e)}")

def validate_file(file: UploadFile, file_type: str):
    logger.info(f"Validating file: {file.filename}, Type: {file.content_type}")
    if (file_type == 'audio' and file.content_type not in ALLOWED_AUDIO_TYPES) or (file_type == 'image' and file.content_type not in ALLOWED_IMAGE_TYPES):
        raise HTTPException(status_code=400, detail=f"Invalid {file_type} file type")
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File size exceeds {MAX_FILE_SIZE//1024//1024}MB limit")
