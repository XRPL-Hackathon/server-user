from typing import Optional
from src.main.config.mongodb import get_mongo_client

class UserRepository:
    def __init__(self):
        client = get_mongo_client()
        self.db = client["xrpedia-data"]
        self.wallets_collection = self.db["wallets"]

    def find_wallets_by_user_id(self, user_id: str) -> list:
        wallets = list(self.wallets_collection.find({"user_id": user_id}, {"_id": 0}))
        return wallets if wallets else []
    
    def create_or_update_wallet(self, user_id: str, wallet_address: str) -> dict:
        existing_wallet = self.wallets_collection.find_one({"user_id": user_id})

        if existing_wallet:
            self.wallets_collection.update_one({"user_id": user_id}, 
                                               {"$set": {"address": wallet_address}})
            return {"message": "Wallet updated", "user_id": user_id, "wallet_address": wallet_address}
        
        else:
            self.wallets_collection.insert_one({"user_id": user_id, "address": wallet_address})
            return {"message": "Wallet created", "user_id": user_id, "wallet_address": wallet_address}