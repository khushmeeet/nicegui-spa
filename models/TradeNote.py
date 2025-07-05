from enum import Enum
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.base import Base


class TradeNote(Base):
    __tablename__ = "trade_notes"

    id = Column(Integer, primary_key=True)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=False)
    note = Column(String, nullable=False)

    trade = relationship("Trade", backref="note")
