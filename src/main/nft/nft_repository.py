from src.main.config.mongodb import get_mongo_client
from src.main.nft.nft_model import NFTRecord
from datetime import datetime

# repository/nft_repository.py
def save_nfts_bulk(nft_records: list):
    client = get_mongo_client()
    db = client['xrpedia-data']
    nft_collection = db['nft_records']

    docs = [
        {
            "nft_id": r.nft_id,
            "user_wallet": r.user_wallet,
            "nft_grade": r.nft_grade,
            "transaction_hash": r.transaction_hash,
            "metadata_uri": r.metadata_uri,
            "issued_at": r.issued_at,
            "expires_at": r.expires_at,
        }
        for r in nft_records
    ]
    
    if docs: 
        nft_collection.insert_many(docs)