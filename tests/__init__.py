"""测试：User 模型"""

import pytest
from pydantic import ValidationError

from recipe_agent.models.user import (
    UserPreference,
    UserProfile,
    DietaryRestriction,
    TastePreference,
    CookingSkillLevel,
)


def test_user_preference_creation():
    """测试创建用户偏好"""
    preference = UserPreference(
        favorite_cuisines=["川菜", "粤菜"],
        taste_preferences=[TastePreference.SPICY],
        cooking_skill=CookingSkillLevel.INTERMEDIATE
    )
    
    assert preference.favorite_cuisines == ["川菜", "粤菜"]
    assert preference.taste_preferences == [TastePreference.SPICY]
    assert preference.cooking_skill == CookingSkillLevel.INTERMEDIATE


def test_dietary_restrictions():
    """测试饮食限制"""
    preference = UserPreference(
        dietary_restrictions=[
            DietaryRestriction.VEGETARIAN,
            DietaryRestriction.GLUTEN_FREE
        ]
    )
    
    assert len(preference.dietary_restrictions) == 2
    assert DietaryRestriction.VEGETARIAN in preference.dietary_restrictions


def test_user_profile_creation():
    """测试创建用户档案"""
    profile = UserProfile(
        username="测试用户",
        email="test@example.com"
    )
    
    assert profile.username == "测试用户"
    assert profile.email == "test@example.com"
    assert profile.data_encrypted is True
    assert profile.user_id is not None


def test_user_validation():
    """测试用户验证"""
    # 用户名太短
    with pytest.raises(ValidationError):
        UserProfile(username="a")
    
    # 用户名太长
    with pytest.raises(ValidationError):
        UserProfile(username="a" * 100)
