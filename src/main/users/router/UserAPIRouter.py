import uuid
from fastapi import APIRouter, Depends
from src.main.auth.dependencies import get_current_user
from src.main.users.service.UserService import UserService
from src.main.users.dto.UserWalletDto import WalletRequest

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
async def create_or_update_wallet(
    wallet_data: WalletRequest,
    user_id: uuid.UUID = Depends(get_current_user),
    user_service: UserService = Depends()
):
    return user_service.add_wallet(str(user_id), wallet_data.wallet_address)