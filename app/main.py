from dotenv import load_dotenv
load_dotenv()  # <-- loads your .env file immediately

import os
import uvicorn
from fastapi import FastAPI, Query, File, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel
import chromadb
import pandas as pd
from openai import OpenAI
from threading import Lock
from faster_whisper import WhisperModel
from elevenlabs import ElevenLabs
import tempfile

from app.prompts import JAPANAUT_PROMPT

app = FastAPI()

# --- Global variables ---
CSV_FILE = "./temples_kamakura_v1.csv"  # ✅ Updated filename
COLLECTION_NAME = "temples_kamakura"     # ✅ Updated collection name
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = None
collection_lock = Lock()

# Whisper model (lazy load)
whisper_model = None
whisper_lock = Lock()

# Choose model via env var
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# --- Response model for GPT-4 endpoint ---
class LLMResponse(BaseModel):
    query: str
    response: str

# --- Helper function to get GPT response ---
def get_gpt_response(query_text: str) -> str:
    """Shared function to get GPT response from query text"""
    global collection

    try:
        # Check API key
        OPENAI_KEY = os.getenv("OPENAI_API_KEY")
        if not OPENAI_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is missing!")
        client = OpenAI(api_key=OPENAI_KEY)

        # Lazy Chroma initialization
        with collection_lock:
            if collection is None:
                try:
                    collection = chroma_client.get_collection(COLLECTION_NAME)
                    print(f"✅ Loaded existing Chroma collection '{COLLECTION_NAME}'")
                except chromadb.errors.InvalidCollectionException:
                    # Collection doesn't exist, create it from CSV
                    print(f"📝 Creating new collection '{COLLECTION_NAME}' from CSV...")
                    df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
                    df.columns = df.columns.str.strip()
                    collection = chroma_client.create_collection(COLLECTION_NAME)
                    
                    # ✅ CRITICAL FIX: Combine ALL searchable fields
                    for _, row in df.iterrows():
                        doc_id = str(row.get("id", _))
                        
                        # Get all fields
                        title = str(row.get("title", ""))
                        content = str(row.get("content", ""))
                        alt_names = str(row.get("alt-names", ""))
                        context_triggers = str(row.get("context triggers", ""))
                        sustainability_nudge = str(row.get("sustainability nudge", ""))
                        
                        # Create combined searchable document
                        combined_document = f"""
Title: {title}
Content: {content}
Alternative Names: {alt_names}
Context: {context_triggers}
Sustainability: {sustainability_nudge}
                        """.strip()
                        
                        # Keep metadata separate
                        metadata = {
                            "title": title,
                            "alt-names": alt_names,
                            "category": str(row.get("category", "")),
                            "context_triggers": context_triggers,
                            "sustainability_nudge": sustainability_nudge
                        }
                        
                        collection.add(
                            ids=[doc_id],
                            documents=[combined_document],
                            metadatas=[metadata]
                        )
                    
                    print(f"✅ {CSV_FILE} loaded into Chroma collection '{COLLECTION_NAME}' ({len(df)} entries)")

        # Retrieve top Chroma chunks
        results = collection.query(query_texts=[query_text], n_results=3)
        chunks = results.get('documents', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]
        
        if not chunks:
            chunks = ["Sorry, I don't have information on that topic yet."]
            metadatas = [{}]

        # ✅ IMPROVED: Extract sustainability nudges from results
        context_parts = []
        sustainability_nudges = []
        
        for i, (chunk, metadata) in enumerate(zip(chunks, metadatas)):
            # Add the main content
            context_parts.append(f"Source {i+1}:\n{chunk}")
            
            # Extract sustainability nudge if present
            nudge = metadata.get('sustainability_nudge', '').strip()
            if nudge and nudge.lower() != 'nan':
                sustainability_nudges.append(nudge)
        
        context_text = "\n\n".join(context_parts)
        
        # Add sustainability section if we found nudges
        if sustainability_nudges:
            sustainability_text = "\n".join([f"• {nudge}" for nudge in sustainability_nudges])
            context_text += f"\n\n🌱 Sustainability Tips:\n{sustainability_text}"

        # Prepare user message with enhanced context
        user_message = f"{context_text}\n\nUser question: {query_text}"

        # Call OpenAI Chat API
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": JAPANAUT_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=200
        )

        answer = response.choices[0].message.content.strip()
        return answer

    except Exception as e:
        return f"An error occurred: {str(e)}"

# --- Text query endpoint (existing) ---
@app.get("/query", response_model=LLMResponse)
def query_chroma_llm(q: str = Query(..., description="Query text")):
    answer = get_gpt_response(q)
    return LLMResponse(query=q, response=answer)

# --- NEW: Voice query endpoint ---
@app.post("/voice-query")
async def voice_query(audio: UploadFile = File(...)):
    """
    Accepts audio file, transcribes it, gets GPT response, 
    converts to speech, and returns audio
    """
    global whisper_model
    
    try:
        # Get API keys
        ELEVENLABS_KEY = os.getenv("ELEVENLABS_API_KEY")
        ELEVENLABS_VOICE = os.getenv("ELEVENLABS_VOICE_ID")
        
        # Debug logging
        print(f"🔑 ELEVENLABS_API_KEY present: {bool(ELEVENLABS_KEY)}")
        print(f"🔑 ELEVENLABS_VOICE_ID present: {bool(ELEVENLABS_VOICE)}")
        if ELEVENLABS_KEY:
            print(f"🔑 API Key length: {len(ELEVENLABS_KEY)}")

        if not ELEVENLABS_KEY or not ELEVENLABS_VOICE:
            return Response(
                content="ElevenLabs credentials not configured",
                status_code=500
            )
        
        
        # Initialize Whisper model (lazy load)
        with whisper_lock:
            if whisper_model is None:
                # Use 'base' model for speed, or 'small'/'medium' for better accuracy
                whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
        
        # Save uploaded audio to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            content = await audio.read()
            temp_audio.write(content)
            temp_audio_path = temp_audio.name
        
        # Transcribe audio with Whisper
        segments, info = whisper_model.transcribe(temp_audio_path, beam_size=5)
        transcribed_text = " ".join([segment.text for segment in segments])
        
        # Clean up temp audio file
        os.unlink(temp_audio_path)
        
        if not transcribed_text.strip():
            return Response(
                content="No speech detected in audio",
                status_code=400
            )
        
        # Get GPT response
        gpt_response = get_gpt_response(transcribed_text)
        
        # Convert response to speech with ElevenLabs
        elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_KEY)
        
        audio_response = elevenlabs_client.text_to_speech.convert(
            voice_id=ELEVENLABS_VOICE,
            text=gpt_response,
            model_id="eleven_multilingual_v2"
        )
        
        # Collect audio bytes
        audio_bytes = b"".join(audio_response)
        
        # Return audio file
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=response.mp3"
            }
        )
        
    except Exception as e:
        return Response(
            content=f"Error processing voice query: {str(e)}",
            status_code=500
        )

# --- Root route for Railway health checks ---
@app.get("/")
def root():
    return {"status": "ok"}

# --- Ping route ---
@app.get("/ping")
def ping():
    return {"message": "pong"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)