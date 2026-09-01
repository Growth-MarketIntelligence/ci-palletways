from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import BaseModel

class IntelligenceTopic(BaseModel):
    __tablename__ = 'intelligence_topics'

    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="active", nullable=False)
    topic_vocabulary = Column(JSONB, nullable=True)
