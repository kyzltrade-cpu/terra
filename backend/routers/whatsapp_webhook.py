import math

from fastapi import APIRouter, Depends, Form, Response
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import PropertyZone, ShiftEvent
from backend.services.voice_processor import transcribe_whatsapp_media, translate_field_audio
from backend.services.agent_triage import triage_field_anomaly

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])


def verify_geofence(
    user_lat: float,
    user_lon: float,
    target_lat: float,
    target_lon: float,
    threshold_meters: float = 100.0,
) -> bool:
    R = 6371000.0
    phi1 = math.radians(user_lat)
    phi2 = math.radians(target_lat)
    delta_phi = math.radians(target_lat - user_lat)
    delta_lambda = math.radians(target_lon - user_lon)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    distance = R * c
    return distance <= threshold_meters


@router.post("/webhook")
async def whatsapp_webhook(
    Body: str = Form(None),
    From: str = Form(...),
    Latitude: str = Form(None),
    Longitude: str = Form(None),
    MediaUrl0: str = Form(None),
    db: Session = Depends(get_db),
):
    # Handle incoming voice note
    if MediaUrl0:
        raw_text = transcribe_whatsapp_media(MediaUrl0)
        triage_data = triage_field_anomaly(raw_text)
        
        severity_emoji = "🚨" if triage_data.get("severity") == "high" else "⚠️" if triage_data.get("severity") == "medium" else "ℹ️"
        gh_status = f"Created! 🔗 {triage_data['github_issue_url']}" if triage_data.get("github_issue_created") else "Not Required (SLA safe)"
        
        transcription_formatted = (
            f"Voice Transcription: \"{raw_text}\"\n"
            f"Agent Triage Issue: {triage_data.get('detected_issue')}\n"
            f"Assigned Agent: {triage_data.get('assigned_agent')}\n"
            f"Severity: {triage_data.get('severity')}\n"
            f"Reasoning: {triage_data.get('reasoning')}\n"
            f"GitHub Ticket: {gh_status}"
        )

        # Save anomaly/maintenance report in DB with rich agent triage metadata
        event = ShiftEvent(
            worker_phone=From,
            event_type="anomaly_report",
            gps_lat=float(Latitude) if Latitude else None,
            gps_lon=float(Longitude) if Longitude else None,
            voice_note_url=MediaUrl0,
            transcription=transcription_formatted
        )
        db.add(event)
        db.commit()
        
        twiml_response = (
            f"<Response><Message>🎙️ Voice Log Received!\n"
            f"\"_{raw_text}_\"\n\n"
            f"🤖 *The Concierge (Agent Triage):*\n"
            f"• *Issue:* {triage_data.get('detected_issue')}\n"
            f"• *Dept:* {triage_data.get('assigned_agent')}\n"
            f"• *Severity:* {severity_emoji} {(triage_data.get('severity') or '').upper()}\n"
            f"• *Reasoning:* \"{triage_data.get('reasoning')}\"\n\n"
            f"🛠️ *GitHub Ticket:* {gh_status}</Message></Response>"
        )
        return Response(content=twiml_response, media_type="application/xml")

    text_body = Body.strip() if Body else ""

    if text_body.startswith("QR_ZONE_"):
        token = text_body.replace("QR_ZONE_", "")
        zone = db.query(PropertyZone).filter_by(qr_code_token=token).first()

        if not zone:
            twiml_response = (
                "<Response><Message>Error: Invalid QR code scanned.</Message></Response>"
            )
            return Response(content=twiml_response, media_type="application/xml")

        if Latitude and Longitude and zone.latitude and zone.longitude:
            is_valid = verify_geofence(
                float(Latitude), float(Longitude), zone.latitude, zone.longitude
            )
            if not is_valid:
                twiml_response = f"<Response><Message>Warning: Check-in blocked. You must be physically on-site at {zone.name} to complete this scan.</Message></Response>"
                return Response(content=twiml_response, media_type="application/xml")

        event = ShiftEvent(
            property_id=zone.property_id,
            zone_id=zone.id,
            worker_phone=From,
            event_type="check_in",
            gps_lat=float(Latitude) if Latitude else None,
            gps_lon=float(Longitude) if Longitude else None,
        )
        db.add(event)
        db.commit()

        twiml_response = f"<Response><Message>Check-In Confirmed! Zone: {zone.name} successfully registered.</Message></Response>"
        return Response(content=twiml_response, media_type="application/xml")

    if text_body:
        triage_data = triage_field_anomaly(text_body)
        
        severity_emoji = "🚨" if triage_data.get("severity") == "high" else "⚠️" if triage_data.get("severity") == "medium" else "ℹ️"
        gh_status = f"Created! 🔗 {triage_data['github_issue_url']}" if triage_data.get("github_issue_created") else "Not Required (SLA safe)"
        
        transcription_formatted = (
            f"Text Message Input: \"{text_body}\"\n"
            f"Agent Triage Issue: {triage_data.get('detected_issue')}\n"
            f"Assigned Agent: {triage_data.get('assigned_agent')}\n"
            f"Severity: {triage_data.get('severity')}\n"
            f"Reasoning: {triage_data.get('reasoning')}\n"
            f"GitHub Ticket: {gh_status}"
        )

        # Save typed anomaly report in DB with rich agent triage metadata
        event = ShiftEvent(
            worker_phone=From,
            event_type="text_anomaly_report",
            gps_lat=float(Latitude) if Latitude else None,
            gps_lon=float(Longitude) if Longitude else None,
            transcription=transcription_formatted
        )
        db.add(event)
        db.commit()
        
        twiml_response = (
            f"<Response><Message>✍️ Text Log Received!\n"
            f"\"_{text_body}_\"\n\n"
            f"🤖 *The Concierge (Agent Triage):*\n"
            f"• *Issue:* {triage_data.get('detected_issue')}\n"
            f"• *Dept:* {triage_data.get('assigned_agent')}\n"
            f"• *Severity:* {severity_emoji} {(triage_data.get('severity') or '').upper()}\n"
            f"• *Reasoning:* \"{triage_data.get('reasoning')}\"\n\n"
            f"🛠️ *GitHub Ticket:* {gh_status}</Message></Response>"
        )
        return Response(content=twiml_response, media_type="application/xml")

    twiml_response = "<Response><Message>TerraClean.OS active. Please scan a physical QR code to register your check-in, or send a voice memo for anomaly reporting.</Message></Response>"
    return Response(content=twiml_response, media_type="application/xml")
