from xrpl.clients import JsonRpcClient
from xrpl.asyncio.wallet import generate_faucet_wallet
from src.main.users.repository.UserRepository import UserRepository

TESTNET_URL = "https://s.altnet.rippletest.net:51234"
client = JsonRpcClient(TESTNET_URL)
class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
    
    def get_wallets(self, user_id: str):
        wallets = self.user_repository.find_wallets_by_user_id(user_id)
        if not wallets:
            return {"message": "No wallets found for this user"}
        return wallets
    
    async def generate_wallet(self, user_id: str):
        wallet = await generate_faucet_wallet(client=client, debug=True)
        wallet_address = wallet.classic_address
        result = self.user_repository.save_wallet(user_id, wallet_address)
        return result