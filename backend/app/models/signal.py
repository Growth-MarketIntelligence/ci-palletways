from sqlalchemy import Column, String, ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Signal(BaseModel):
    __tablename__ = 'signals'

    competitor_id = Column(UUID(as_uuid=True), ForeignKey('competitors.id', ondelete='CASCADE'), nullable=False)
    topic_id = Column(UUID(as_uuid=True), ForeignKey('intelligence_topics.id', ondelete='CASCADE'), nullable=False)
    
    signal_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    detected_at = Column(DateTime(timezone=True), nullable=False)
    confidence = Column(Float, nullable=True)
    materiality = Column(String, nullable=True)
    competitive_relevance = Column(String, nullable=True)

    competitor = relationship("Competitor")
    topic = relationship("IntelligenceTopic")
    events = relationship("Event", secondary="signal_events")

class SignalEvent(BaseModel):
    __tablename__ = 'signal_events'
    
    signal_id = Column(UUID(as_uuid=True), ForeignKey('signals.id', ondelete='CASCADE'), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
