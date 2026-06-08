from backend.services.voice_processor import translate_field_audio

def test_spanish_slang_mapping():
    # Test local context mapping of common commercial janitorial slang
    translation = translate_field_audio(transcription_text="La pulidora de pisos está dañada")
    assert "[FLOOR BUFFER / BURNISHER]" in translation
