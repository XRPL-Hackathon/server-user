from sqlalchemy.orm import Session
from src.main.nft.nft_model import NFTRecord
from datetime import datetime

# repository/user_repository.py
def get_users_with_point_over(session, min_point: int):
    return session.query(User).filter(User.point >= min_point).all()

# repository/nft_repository.py
def save_nfts_bulk(session, nft_records: list):
    session.bulk_save_objects(nft_records)
    session.commit()
