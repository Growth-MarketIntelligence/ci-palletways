from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Evidence(BaseModel):
    __tablename__ = 'evidence'

    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    claim = Column(String, nullable=True)
    text_excerpt = Column(String, nullable=True)
    location_reference = Column(String, nullable=True)
    
    document = relationship("Document")
