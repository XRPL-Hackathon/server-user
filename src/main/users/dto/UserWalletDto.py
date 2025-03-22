from pydantic import BaseModel

class WalletResponse(BaseModel):
    wallet_address: str
    user_id: str
    message: str