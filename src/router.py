from fastapi import APIRouter

from src.main.health.router import HealthAPIRouter
from src.main.nft import nft_controller as NftAPIRouter

router = APIRouter(
    prefix="",
)

router.include_router(HealthAPIRouter.router)
router.include_router(NftAPIRouter.router)