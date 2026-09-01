from sqlalchemy import Column, String
from app.models.base import BaseModel

class Market(BaseModel):
    __tablename__ = 'markets'

    name = Column(String, nullable=False)
    country_code = Column(String, nullable=False)
    status = Column(String, default="active", nullable=False)
