
# Standard library imports
import asyncio
import io
import json
import os
import queue
import threading

# Third-party imports
import fastapi
import librosa
import numpy as np
import requests
import soundfile as sf
import uvicorn
import websockets
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sounddevice as sd
from scipy.io.wavfile import write


def record_audio(seconds: float = 5.0) -> str:
    fs = 16000  # Sample rate
    channels = 2 # Channels
    filename = "output.wav"

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=channels)
    sd.wait()  # Wait until recording is finished
    write(filename, fs, myrecording)  # Save as WAV file
    return filename


# Configuration
ws_uri_base_stt = 'wss://luminous-stt.hypercliq.com'
ws_uri_base_tts = "https://luminous-tts.hypercliq.com"
token = os.environ.get("LUMINOUS_STT_API_TOKEN", "EMPTY")

app = FastAPI(
    title="Speech/TTS API",
    description="API for Speech-to-Text (ASR) and Text-to-Speech (TTS) services provided by Hypercliq in Luminous project and deployed by Vicomtech",
    version="1.0.0"
)

# TTS Functions
def synthesize_speech(text):
    """
    Synthesize speech from text using TTS service.
    Returns audio content in MP3 format.
    """
    url = f"{ws_uri_base_tts}/v1/speech"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": token
    }
    payload = {
        "text": text,
        "format": "text",
        "voice": "Joanna",
        "language": "en-US",
        "output": "mp3"
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        return response.content
    else:
        print("Error response:", response.text)
        return None

# ASR Functions
async def process_audio_file(audio_bytes: bytes, sample_rate: int) -> str:
    """
    Process audio file bytes through the WebSocket ASR service.
    Returns the transcribed text.
    """
    ws_uri = f"{ws_uri_base_stt}?sampleRate={sample_rate}&token={token}" # &sendPartials=true
    transcripts = []
    
    try:
        async with websockets.connect(ws_uri) as websocket:
            # Send audio data in chunks
            chunk_size = 2048
            for i in range(0, len(audio_bytes), chunk_size):
                chunk = audio_bytes[i: i + chunk_size]
                await websocket.send(chunk)

            await websocket.send("END_OF_STREAM")

            # Receive transcription
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if "transcript" in data:
                        # print(f"Final: {data['transcript']}")
                        transcripts.append(data["transcript"])
                except json.JSONDecodeError:
                    print("Received non-JSON message:", message)
                    
    except Exception as e:
        print(f"Error during WebSocket communication: {e}")
        raise

    final_transcript = " ".join(transcripts)
    
    return final_transcript

# Add this class for the request schema
class TTSRequest(BaseModel):
    text: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Hi! I love Python"
                }
            ]
        }
    }

# API Endpoints
@app.post("/asr/file")
async def asr_from_file(file: UploadFile = File(...)):
    """
    Convert uploaded audio file to text using ASR.
    """
    try:
        content = file.read()
        audio_array, sample_rate = librosa.load(io.BytesIO(content), sr=None)
        audio_array = (audio_array * 32767).astype(np.int16)
        pcm_bytes = audio_array.tobytes()
        
        transcript = await process_audio_file(pcm_bytes, sample_rate=sample_rate)
        
        return JSONResponse({
            "status": "success",
            "transcript": transcript
        })
    except Exception as e:  
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)
    

@app.post("/asr/bytes")
async def asr_from_bytes(bytes: bytes, sample_rate: int):
    """
    Convert uploaded audio bytes to text using ASR.
    """
    try:
        transcript = await process_audio_file(bytes, sample_rate=sample_rate)
        
        return JSONResponse({
            "status": "success",
            "transcript": transcript
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech (POST endpoint).
    Accepts JSON with "text" field and returns MP3 audio file.
    """
    try:
        audio_content = synthesize_speech(request.text)
        
        if audio_content is None:
            return JSONResponse({
                "status": "error",
                "message": "Failed to synthesize speech"
            }, status_code=500)
            
        return fastapi.Response(
            content=audio_content,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f'attachment; filename="speech.mp3"'
            }
        )
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@app.get("/tts/{text}")
async def text_to_speech_get(text: str):
    """
    Convert text to speech (GET endpoint).
    Text is passed as URL parameter and returns MP3 audio file.
    """
    try:
        audio_content = synthesize_speech(text)
        
        if audio_content is None:
            return JSONResponse({
                "status": "error",
                "message": "Failed to synthesize speech"
            }, status_code=500)
            
        return fastapi.Response(
            content=audio_content,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f'attachment; filename="speech.mp3"'
            }
        )
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=8000)