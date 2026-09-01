from sqlalchemy import Column, String, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel

class Source(BaseModel):
    __tablename__ = 'sources'

    competitor_id = Column(UUID(as_uuid=True), ForeignKey('competitors.id', ondelete='SET NULL'), nullable=True)
    market_id = Column(UUID(as_uuid=True), ForeignKey('markets.id', ondelete='SET NULL'), nullable=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey('intelligence_topics.id', ondelete='SET NULL'), nullable=True)
    
    source_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=True)
    domain = Column(String, nullable=True)
    collection_method = Column(String, nullable=True)
    compliance_status = Column(String, nullable=True)
    robots_status = Column(String, nullable=True)
    collection_enabled = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=0, nullable=False)
    reliability = Column(String, nullable=True)
