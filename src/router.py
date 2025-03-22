from fastapi import APIRouter

from src.main.health.router import HealthAPIRouter
from src.main.users.router import UserAPIRouter


router = APIRouter(
    prefix="",
)

router.include_router(HealthAPIRouter.router)
router.include_router(UserAPIRouter.router)