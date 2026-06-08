import os
import requests

SLANG_MAPPINGS = {
    "pulidora de pisos": "floor buffer / burnisher",
    "poda de jardin": "turf lawn trimming",
    "bano sucio": "restroom sanitation alert",
    "manguera rota": "broken pressure washing hose",
    "quimicos terminados": "chemical supply depletion",
    # Single-word robust keywords
    "manguera": "broken pressure washing hose",
    "pulidora": "floor buffer / burnisher",
    "baño": "restroom sanitation alert",
    "bano": "restroom sanitation alert",
    "poda": "turf lawn trimming",
    "químicos": "chemical supply depletion",
    "quimicos": "chemical supply depletion",
    "espejo": "broken mirror"
}

def translate_field_audio(transcription_text: str) -> str:
    cleaned = transcription_text.lower().strip()
    
    # Map raw translated text to standard B2B canonical entities
    for slang, canonical in SLANG_MAPPINGS.items():
        if slang in cleaned:
            cleaned = cleaned.replace(slang, f"[{canonical.upper()}]")
            
    return cleaned

def transcribe_whatsapp_media(media_url: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return "La pulidora de pisos tiene un problema" # Return mock slang string for sandbox fallback
        
    try:
        # Download the audio file from Twilio CDN
        audio_data = requests.get(media_url).content
        # Call standard Whisper transcriptions endpoint
        files = {"file": ("audio.ogg", audio_data, "audio/ogg")}
        headers = {"Authorization": f"Bearer {api_key}"}
        resp = requests.post("https://api.openai.com/v1/audio/transcriptions", files=files, headers=headers, data={"model": "whisper-1"})
        return resp.json().get("text", "")
    except Exception as e:
        return f"Error transcribing media file: {str(e)}"
