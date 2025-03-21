from typing import Optional
from src.main.config.mongodb import get_mongo_client
# from src.main.nft.nft_user_info import User

class UserRepository:
    def __init__(self):
        client = get_mongo_client()
        self.db = client["xrpedia-data"]
        self.wallets_collection = self.db["wallets"]

    def find_wallets_by_user_id(self, user_id: str) -> list:
        wallets = list(self.wallets_collection.find({"user_id": user_id}, {"_id": 0}))
        return wallets if wallets else []
    
    def save_wallet(self, user_id: str, wallet_address: str, seed: str, point: int = 0, nft_grade: str = "bronze"):
        wallet_data ={
            "address": wallet_address,
            "seed": seed,
            "point": point,
            "nft_grade": nft_grade
        }
        existing = self.wallets_collection.find_one({"user_id": user_id})
        if existing:
            self.wallets_collection.update_one(
                {"user_id": user_id}, 
                {"$set": wallet_data}
            )
            return {"message": "Wallet updated", 
                    "user_id": user_id, 
                    **wallet_data}
        else:
            self.wallets_collection.insert_one({"user_id": user_id, 
                                                **wallet_data})
            return {"message": "Wallet created", 
                    "user_id": user_id, 
                    **wallet_data}
        
    
    # def get_all_user(self) -> list[User]:
    #     docs = self.wallets_collection.find({}, {"_id": 0, "address":1, "point": 1})
    #     users = [User(wallet=doc["address"], point=doc.get("point", 0)) for doc in docs]
    #     return users
