from src.main.users.repository.UserRepository import UserRepository

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
    
    def get_wallets(self, user_id: str):
        wallets = self.user_repository.find_wallets_by_user_id(user_id)

        if not wallets:
            return {"message": "No wallets found for this user"}
        
        return wallets
    
    def add_wallet(self, user_id: str, wallet_address: str):
        return self.user_repository.create_or_update_wallet(user_id, wallet_address, point=0)