import pytest
from unittest.mock import MagicMock
from backend.models import PropertyZone

def test_whatsapp_qr_webhook_check_in(client, mock_db):
    # Mocking the zone lookup
    mock_zone = PropertyZone(
        id="98739861-777c-4bad-a81f-b22e12861642",
        property_id="3d183980-ff6d-4952-b883-7c3852d7e5b6",
        name="Lobby Restroom",
        floor_type="tile",
        square_footage=1500,
        qr_code_token="987654",
        latitude=22.2855,
        longitude=114.1577
    )
    
    # Mocking query chain
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = mock_zone
    mock_query.filter_by.return_value = mock_filter
    mock_db.query.return_value = mock_query
    
    payload = {
        "Body": "QR_ZONE_987654",
        "From": "whatsapp:+155****4567",
        "Latitude": "22.2855",
        "Longitude": "114.1577"
    }
    
    response = client.post("/api/whatsapp/webhook", data=payload)
    assert response.status_code == 200
    assert "Check-In Confirmed" in response.text

def test_whatsapp_voice_webhook_analysis(client, mock_db):
    # Simulate a voice note URL payload
    payload = {
        "From": "whatsapp:+155****4567",
        "MediaUrl0": "https://api.twilio.com/2010-04-01/Accounts/AC123/Messages/MM123/Media/ME123"
    }
    
    response = client.post("/api/whatsapp/webhook", data=payload)
    assert response.status_code == 200
    # Whisper mock will output: "La pulidora de pisos tiene un problema"
    # Slang dictionary maps "pulidora de pisos" -> "[FLOOR BUFFER / BURNISHER]"
    assert "La pulidora de pisos" in response.text
    assert "[FLOOR BUFFER / BURNISHER]" in response.text

def test_whatsapp_text_anomaly_webhook(client, mock_db):
    # Simulate a typed text message anomaly report
    payload = {
        "From": "whatsapp:+155****4567",
        "Body": "La manguera está rota"
    }
    
    response = client.post("/api/whatsapp/webhook", data=payload)
    assert response.status_code == 200
    assert "Text Log Received!" in response.text
    assert "[BROKEN PRESSURE WASHING HOSE]" in response.text

