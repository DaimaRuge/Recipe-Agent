"""API 路由"""

from fastapi import APIRouter

from recipe_agent.api.recipes import router as recipes_router
from recipe_agent.api.users import router as users_router
from recipe_agent.api.bot import router as bot_router

api_router = APIRouter()

api_router.include_router(
    recipes_router,
    prefix="/recipes",
    tags=["recipes"]
)

api_router.include_router(
    users_router,
    prefix="/users",
    tags=["users"]
)

api_router.include_router(
    bot_router,
    prefix="/bot",
    tags=["bot"]
)
