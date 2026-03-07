"""用户数据模型"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DietaryRestriction(str, Enum):
    """饮食限制类型"""
    
    VEGETARIAN = "vegetarian"  # 素食
    VEGAN = "vegan"  # 纯素
    HALAL = "halal"  # 清真
    KOSHER = "kosher"  # 犹太洁食
    GLUTEN_FREE = "gluten_free"  # 无麸质
    LACTOSE_FREE = "lactose_free"  # 无乳糖
    NUT_ALLERGY = "nut_allergy"  # 坚果过敏
    SEAFOOD_ALLERGY = "seafood_allergy"  # 海鲜过敏
    DIABETES = "diabetes"  # 糖尿病
    HYPERTENSION = "hypertension"  # 高血压
    LOW_SODIUM = "low_sodium"  # 低钠


class TastePreference(str, Enum):
    """口味偏好"""
    
    SWEET = "sweet"  # 甜
    SOUR = "sour"  # 酸
    SPICY = "spicy"  # 辣
    SALTY = "salty"  # 咸
    BITTER = "bitter"  # 苦
    UMAMI = "umami"  # 鲜


class CookingSkillLevel(str, Enum):
    """烹饪技能等级"""
    
    BEGINNER = "beginner"  # 新手
    INTERMEDIATE = "intermediate"  # 中级
    ADVANCED = "advanced"  # 高级
    EXPERT = "expert"  # 专家


class UserPreference(BaseModel):
    """用户偏好设置"""
    
    dietary_restrictions: list[DietaryRestriction] = Field(
        default_factory=list,
        description="饮食限制"
    )
    favorite_cuisines: list[str] = Field(
        default_factory=list,
        description="喜欢的菜系"
    )
    disliked_ingredients: list[str] = Field(
        default_factory=list,
        description="不喜欢的食材"
    )
    taste_preferences: list[TastePreference] = Field(
        default_factory=list,
        description="口味偏好"
    )
    cooking_skill: CookingSkillLevel = Field(
        default=CookingSkillLevel.INTERMEDIATE,
        description="烹饪技能等级"
    )
    max_cooking_time: Optional[int] = Field(
        None,
        ge=5,
        le=300,
        description="最大烹饪时间（分钟）"
    )
    serving_size: int = Field(
        default=2,
        ge=1,
        le=10,
        description="常用份数"
    )
    
    # 健康目标
    daily_calorie_goal: Optional[int] = Field(
        None,
        ge=1000,
        le=5000,
        description="每日热量目标"
    )
    health_goals: list[str] = Field(
        default_factory=list,
        description="健康目标（如：减脂、增肌、控制血糖）"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "dietary_restrictions": ["vegetarian"],
                "favorite_cuisines": ["中式", "意式"],
                "disliked_ingredients": ["香菜", "洋葱"],
                "taste_preferences": ["spicy", "umami"],
                "cooking_skill": "intermediate",
                "max_cooking_time": 30,
                "serving_size": 2,
                "daily_calorie_goal": 2000,
                "health_goals": ["减脂"]
            }
        }


class UserProfile(BaseModel):
    """用户档案"""
    
    user_id: UUID = Field(default_factory=uuid4, description="用户唯一标识")
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    
    preference: UserPreference = Field(
        default_factory=UserPreference,
        description="用户偏好"
    )
    
    # 隐私设置
    data_encrypted: bool = Field(default=True, description="数据是否加密")
    share_data: bool = Field(default=False, description="是否共享数据用于改进")
    
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "美食家小王",
                "email": "wang@example.com",
                "preference": {
                    "favorite_cuisines": ["川菜", "粤菜"],
                    "taste_preferences": ["spicy"],
                    "cooking_skill": "intermediate"
                }
            }
        }
