##entity 같은 역할입니다.
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class NFTRecord(Base):
    __tablename__ = "nft_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_wallet = Column(String, index=True, nullable=False)
    nft_id = Column(String, unique=True, nullable=False)
    nft_grade = Column(String, nullable=False)
    transaction_hash = Column(String, unique=True, nullable=False)
    nft_metadata_uri = Column(String, nullable=True)
    issued_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
