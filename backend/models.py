import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID

from backend.database import Base


class Property(Base):
    __tablename__ = "properties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))


class PropertyZone(Base):
    __tablename__ = "property_zones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    floor_type = Column(String(100), nullable=False)
    square_footage = Column(Integer, nullable=False)
    qr_code_token = Column(String(100), unique=True, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))


class SlangDictionary(Base):
    __tablename__ = "slang_dictionary"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phrase = Column(String(255), unique=True, nullable=False)
    canonical_english = Column(String(255), nullable=False)
    action_trigger = Column(String(100), nullable=True)


class ShiftEvent(Base):
    __tablename__ = "shift_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=True)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("property_zones.id", ondelete="CASCADE"), nullable=True)
    worker_phone = Column(String(50), nullable=False)
    event_type = Column(String(50), nullable=False)
    scanned_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    gps_lat = Column(Float, nullable=True)
    gps_lon = Column(Float, nullable=True)
    voice_note_url = Column(Text, nullable=True)
    transcription = Column(Text, nullable=True)
