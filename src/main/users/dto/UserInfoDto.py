from pydantic import BaseModel

class UserInfoResponse(BaseModel):
    user_id: str
    nickname: str
    level_title: str
    point: float
    total_revenue: float
