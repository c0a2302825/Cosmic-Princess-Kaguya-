from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Date, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Goods(Base):
    __tablename__ = "goods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    image_url = Column(String(255))
    release_date = Column(Date, nullable=True, index=True)  # グッズの発売日
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # リレーションシップ
    possessions = relationship("Possession", back_populates="goods")

class Possession(Base):
    __tablename__ = "possessions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    goods_id = Column(Integer, ForeignKey("goods.id"), nullable=False)
    quantity = Column(Integer, default=1)
    status = Column(String(20), default="current")  # "current" or "planned"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # リレーションシップ
    goods = relationship("Goods", back_populates="possessions")