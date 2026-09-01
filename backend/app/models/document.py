from sqlalchemy import Column, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Document(BaseModel):
    __tablename__ = 'documents'

    source_id = Column(UUID(as_uuid=True), ForeignKey('sources.id', ondelete='CASCADE'), nullable=False)
    url = Column(String, nullable=True)
    title = Column(String, nullable=True)
    content_type = Column(String, nullable=True)
    content_hash = Column(String, nullable=False)
    
    source_published_at = Column(DateTime(timezone=True), nullable=True)
    source_updated_at = Column(DateTime(timezone=True), nullable=True)
    collected_at = Column(DateTime(timezone=True), nullable=False)
    
    raw_storage_ref = Column(String, nullable=True)
    text_content = Column(String, nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)  # Using metadata_ to avoid conflict with SQLAlchemy's internal metadata attribute

    __table_args__ = (
        UniqueConstraint('source_id', 'content_hash', name='uq_source_content_hash'),
    )

    source = relationship("Source")
