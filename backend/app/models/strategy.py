from sqlalchemy import Column, String, ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class StrategyInsight(BaseModel):
    __tablename__ = 'strategy_insights'

    competitor_id = Column(UUID(as_uuid=True), ForeignKey('competitors.id', ondelete='CASCADE'), nullable=False)
    
    strategy_category = Column(String, nullable=False)
    strategy_theme = Column(String, nullable=False)
    assessment = Column(String, nullable=False)
    interpretation = Column(String, nullable=False)
    confidence = Column(Float, nullable=True)
    
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)

    competitor = relationship("Competitor")
    events = relationship("StrategyInsightEvent", back_populates="insight", cascade="all, delete-orphan")


class StrategyInsightEvent(BaseModel):
    __tablename__ = 'strategy_insight_events'

    strategy_insight_id = Column(UUID(as_uuid=True), ForeignKey('strategy_insights.id', ondelete='CASCADE'), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey('events.id', ondelete='CASCADE'), nullable=False)

    insight = relationship("StrategyInsight", back_populates="events")
    event = relationship("Event")
