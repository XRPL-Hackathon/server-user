from pydantic import BaseModel

class WalletRequest(BaseModel):
    wallet_address: str