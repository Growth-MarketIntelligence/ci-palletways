from sqlalchemy import Column, String, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class CollectionRun(BaseModel):
    __tablename__ = 'collection_runs'

    source_id = Column(UUID(as_uuid=True), ForeignKey('sources.id', ondelete='CASCADE'), nullable=False)
    
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=False)
    
    items_found = Column(Integer, default=0, nullable=False)
    items_new = Column(Integer, default=0, nullable=False)
    items_updated = Column(Integer, default=0, nullable=False)
    items_duplicate = Column(Integer, default=0, nullable=False)
    items_failed = Column(Integer, default=0, nullable=False)
    
    error_message = Column(String, nullable=True)
    
    source = relationship("Source")
