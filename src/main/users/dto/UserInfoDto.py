from pydantic import BaseModel

class UserInfoResponse(BaseModel):
    user_id: str
    nickname: str
    level_title: str
    point: float
    total_revenue: float
    xrp_balance: float
    rlusd_balance: float