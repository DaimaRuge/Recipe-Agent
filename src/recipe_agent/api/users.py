"""用户相关 API"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from recipe_agent.models.user import UserProfile, UserPreference


router = APIRouter()


class CreateUserRequest(BaseModel):
    """创建用户请求"""
    
    username: str
    email: str | None = None


class UpdatePreferenceRequest(BaseModel):
    """更新偏好请求"""
    
    preference: UserPreference


@router.post("/", response_model=UserProfile)
async def create_user(request: CreateUserRequest):
    """创建新用户"""
    # TODO: 实现用户创建逻辑
    
    profile = UserProfile(
        username=request.username,
        email=request.email
    )
    
    return profile


@router.get("/{user_id}", response_model=UserProfile)
async def get_user(user_id: str):
    """获取用户信息"""
    # TODO: 从数据库查询
    
    raise HTTPException(
        status_code=404,
        detail=f"用户 {user_id} 不存在"
    )


@router.get("/{user_id}/preference", response_model=UserPreference)
async def get_user_preference(user_id: str):
    """获取用户偏好"""
    # TODO: 从数据库查询
    
    raise HTTPException(
        status_code=404,
        detail=f"用户 {user_id} 不存在"
    )


@router.put("/{user_id}/preference", response_model=UserPreference)
async def update_user_preference(
    user_id: str,
    request: UpdatePreferenceRequest
):
    """更新用户偏好"""
    # TODO: 实现更新逻辑
    
    return request.preference
