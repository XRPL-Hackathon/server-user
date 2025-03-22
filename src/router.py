from fastapi import APIRouter

from src.main.health.router import HealthAPIRouter
<<<<<<< HEAD
from src.main.nft import nft_controller as NftAPIRouter
=======
from src.main.users.router import UserAPIRouter

>>>>>>> a0655f32633b81938852724a40fe98e4df2ebfd7

router = APIRouter(
    prefix="",
)

router.include_router(HealthAPIRouter.router)
<<<<<<< HEAD
router.include_router(NftAPIRouter.router)
=======
router.include_router(UserAPIRouter.router)
>>>>>>> a0655f32633b81938852724a40fe98e4df2ebfd7
