import uuid
from fastapi import APIRouter, Depends
from src.main.auth.dependencies import get_current_user
from src.main.users.dto.UserInfoDto import UserInfoResponse
from src.main.users.service.UserService import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# 유저의 XPRL 지갑 목록 조회
@router.get("/wallets")
async def get_user_wallets(
    user_id: uuid.UUID = Depends(get_current_user),
    user_service: UserService = Depends()
):
    return user_service.get_wallets(str(user_id))

# 유저의 XPRL 지갑 주소 저장 또는 업데이트 하는 API
@router.post("/wallets")
async def create_wallet(
    user_id: uuid.UUID = Depends(get_current_user),
    user_service: UserService = Depends()
):
    return await user_service.generate_wallet(str(user_id))

@router.get("", response_model=UserInfoResponse)
async def get_user_info(
    user_id: uuid.UUID = Depends(get_current_user),
    user_service: UserService = Depends()
):
    return user_service.get_user_info(str(user_id))
