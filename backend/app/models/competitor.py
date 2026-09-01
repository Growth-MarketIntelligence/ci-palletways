import uuid
from sqlalchemy import Column, String, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.base import BaseModel

def get_utc_now():
    return datetime.now(timezone.utc)

class Competitor(BaseModel):
    __tablename__ = 'competitors'

    name = Column(String, nullable=False)
    canonical_name = Column(String, nullable=False)
    website = Column(String, nullable=True)
    description = Column(String, nullable=True)
    status = Column(String, default="active", nullable=False)

    aliases = relationship("CompetitorAlias", back_populates="competitor")
    markets = relationship("CompetitorMarket", back_populates="competitor")


class CompetitorAlias(BaseModel):
    __tablename__ = 'competitor_aliases'

    competitor_id = Column(UUID(as_uuid=True), ForeignKey('competitors.id', ondelete='CASCADE'), nullable=False)
    alias = Column(String, nullable=False)
    alias_type = Column(String, nullable=True)
    
    # Exclude updated_at for Alias based on requirements if you prefer, but BaseModel includes it.
    # We will let BaseModel handle it.

    __table_args__ = (
        UniqueConstraint('competitor_id', 'alias', name='uq_competitor_alias'),
    )

    competitor = relationship("Competitor", back_populates="aliases")


class CompetitorMarket(BaseModel):
    __tablename__ = 'competitor_markets'

    competitor_id = Column(UUID(as_uuid=True), ForeignKey('competitors.id', ondelete='CASCADE'), nullable=False)
    market_id = Column(UUID(as_uuid=True), ForeignKey('markets.id', ondelete='CASCADE'), nullable=False)
    status = Column(String, default="active", nullable=False)

    __table_args__ = (
        UniqueConstraint('competitor_id', 'market_id', name='uq_competitor_market'),
    )

    competitor = relationship("Competitor", back_populates="markets")
