from sqlalchemy import Column, String, ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Event(BaseModel):
    __tablename__ = 'events'

    competitor_id = Column(UUID(as_uuid=True), ForeignKey('competitors.id', ondelete='CASCADE'), nullable=False)
    topic_id = Column(UUID(as_uuid=True), ForeignKey('intelligence_topics.id', ondelete='CASCADE'), nullable=False)
    evidence_id = Column(UUID(as_uuid=True), ForeignKey('evidence.id', ondelete='SET NULL'), nullable=True)
    
    event_type = Column(String, nullable=False)
    event_subtype = Column(String, nullable=True)
    signal_type = Column(String, nullable=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    event_metadata = Column(JSONB, nullable=True)
    event_date = Column(DateTime(timezone=True), nullable=True)
    location = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    
    extraction_model = Column(String, nullable=True)
    extraction_prompt_version = Column(String, nullable=True)

    evidence = relationship("Evidence")
    competitor = relationship("Competitor")
    topic = relationship("IntelligenceTopic")
