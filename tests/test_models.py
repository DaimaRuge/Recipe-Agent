"""测试：Recipe 模型"""

import pytest
from pydantic import ValidationError

from recipe_agent.models.recipe import (
    Ingredient,
    Step,
    Nutrition,
    Recipe,
)


def test_ingredient_creation():
    """测试创建食材"""
    ingredient = Ingredient(
        name="西红柿",
        amount=2,
        unit="个"
    )
    
    assert ingredient.name == "西红柿"
    assert ingredient.amount == 2
    assert ingredient.unit == "个"
    assert ingredient.optional is False
    assert ingredient.substitutes == []


def test_step_creation():
    """测试创建步骤"""
    step = Step(
        step_number=1,
        instruction="西红柿切块",
        duration_minutes=3
    )
    
    assert step.step_number == 1
    assert step.instruction == "西红柿切块"
    assert step.duration_minutes == 3
    assert step.tips == []


def test_nutrition_creation():
    """测试创建营养信息"""
    nutrition = Nutrition(
        calories=280,
        protein=12.5,
        carbohydrates=15.2,
        fat=18.3
    )
    
    assert nutrition.calories == 280
    assert nutrition.protein == 12.5
    assert nutrition.fiber is None


def test_recipe_creation():
    """测试创建菜谱"""
    recipe = Recipe(
        title="番茄炒蛋",
        description="经典家常菜",
        ingredients=[
            Ingredient(name="西红柿", amount=2, unit="个"),
            Ingredient(name="鸡蛋", amount=3, unit="个"),
        ],
        steps=[
            Step(step_number=1, instruction="准备食材"),
            Step(step_number=2, instruction="炒制"),
        ],
        nutrition=Nutrition(
            calories=280,
            protein=12.5,
            carbohydrates=15.2,
            fat=18.3
        )
    )
    
    assert recipe.title == "番茄炒蛋"
    assert recipe.difficulty == "medium"
    assert len(recipe.ingredients) == 2
    assert len(recipe.steps) == 2
    assert recipe.recipe_id is not None


def test_recipe_validation():
    """测试菜谱验证"""
    # 缺少必需字段
    with pytest.raises(ValidationError):
        Recipe(title="测试菜谱")
    
    # 空食材列表
    with pytest.raises(ValidationError):
        Recipe(
            title="测试",
            description="测试",
            ingredients=[],
            steps=[Step(step_number=1, instruction="test")],
            nutrition=Nutrition(calories=100, protein=10, carbohydrates=10, fat=5)
        )
