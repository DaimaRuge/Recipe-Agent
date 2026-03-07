"""测试：营养计算器"""

import pytest

from recipe_agent.models.recipe import Ingredient
from recipe_agent.services.nutrition_calculator import NutritionCalculator


def test_convert_to_grams():
    """测试单位转换"""
    calc = NutritionCalculator()
    
    assert calc._convert_to_grams(100, "克") == 100
    assert calc._convert_to_grams(1, "千克") == 1000
    assert calc._convert_to_grams(1, "斤") == 500


def test_calculate_ingredient_nutrition():
    """测试计算食材营养"""
    calc = NutritionCalculator()
    
    ingredient = Ingredient(name="西红柿", amount=200, unit="克")
    nutrition = calc.calculate_ingredient_nutrition(ingredient)
    
    assert nutrition is not None
    assert nutrition.calories == pytest.approx(36, rel=0.01)  # 18 * 2
    assert nutrition.protein == pytest.approx(1.8, rel=0.01)  # 0.9 * 2


def test_calculate_recipe_nutrition():
    """测试计算菜谱总营养"""
    calc = NutritionCalculator()
    
    ingredients = [
        Ingredient(name="西红柿", amount=200, unit="克"),
        Ingredient(name="鸡蛋", amount=100, unit="克"),
    ]
    
    nutrition = calc.calculate_recipe_nutrition(ingredients)
    
    assert nutrition.calories == pytest.approx(180, rel=0.01)  # 36 + 144
    assert nutrition.protein == pytest.approx(14.2, rel=0.01)  # 1.8 + 12.4


def test_unknown_ingredient():
    """测试未知食材"""
    calc = NutritionCalculator()
    
    ingredient = Ingredient(name="未知食材", amount=100, unit="克")
    nutrition = calc.calculate_ingredient_nutrition(ingredient)
    
    assert nutrition is None
