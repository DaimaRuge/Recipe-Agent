"""营养计算服务

基于食材数据库的营养成分计算
"""

from typing import Optional

from recipe_agent.models.recipe import Ingredient, Nutrition


class NutritionCalculator:
    """营养计算器
    
    负责计算菜谱的营养成分
    """
    
    # TODO: 接入真实的营养数据库（如 USDA、中国食品成分表）
    # 当前使用示例数据
    
    # 示例：每 100g 的营养数据
    NUTRITION_DB: dict[str, Nutrition] = {
        "西红柿": Nutrition(
            calories=18,
            protein=0.9,
            carbohydrates=3.9,
            fat=0.2,
            fiber=1.2,
            sodium=5,
            sugar=2.6
        ),
        "鸡蛋": Nutrition(
            calories=144,
            protein=13.3,
            carbohydrates=2.8,
            fat=8.8,
            fiber=0,
            sodium=140,
            sugar=1.1
        ),
        "猪肉": Nutrition(
            calories=143,
            protein=20.3,
            carbohydrates=0,
            fat=6.2,
            fiber=0,
            sodium=60,
            sugar=0
        ),
    }
    
    # 单位转换到克的系数
    UNIT_TO_GRAMS: dict[str, float] = {
        "克": 1.0,
        "g": 1.0,
        "千克": 1000.0,
        "kg": 1000.0,
        "斤": 500.0,
        "两": 50.0,
        "个": 150.0,  # 平均值
        "勺": 15.0,
        "茶匙": 5.0,
        "汤匙": 15.0,
        "毫升": 1.0,
        "ml": 1.0,
        "升": 1000.0,
    }
    
    def _convert_to_grams(self, amount: float, unit: str) -> float:
        """将食材量转换为克
        
        Args:
            amount: 数量
            unit: 单位
        
        Returns:
            克数
        """
        coefficient = self.UNIT_TO_GRAMS.get(unit.lower(), 100.0)  # 默认 100g
        return amount * coefficient
    
    def calculate_ingredient_nutrition(
        self,
        ingredient: Ingredient
    ) -> Optional[Nutrition]:
        """计算单个食材的营养成分
        
        Args:
            ingredient: 食材对象
        
        Returns:
            营养信息，如果食材不在数据库中则返回 None
        """
        base_nutrition = self.NUTRITION_DB.get(ingredient.name)
        if not base_nutrition:
            return None
        
        # 转换为克
        grams = self._convert_to_grams(ingredient.amount, ingredient.unit)
        ratio = grams / 100.0  # 数据库以 100g 为基准
        
        return Nutrition(
            calories=base_nutrition.calories * ratio,
            protein=base_nutrition.protein * ratio,
            carbohydrates=base_nutrition.carbohydrates * ratio,
            fat=base_nutrition.fat * ratio,
            fiber=(base_nutrition.fiber or 0) * ratio,
            sodium=(base_nutrition.sodium or 0) * ratio,
            sugar=(base_nutrition.sugar or 0) * ratio,
        )
    
    def calculate_recipe_nutrition(
        self,
        ingredients: list[Ingredient]
    ) -> Nutrition:
        """计算整个菜谱的营养成分
        
        Args:
            ingredients: 食材列表
        
        Returns:
            总营养信息
        """
        total = Nutrition(
            calories=0,
            protein=0,
            carbohydrates=0,
            fat=0,
            fiber=0,
            sodium=0,
            sugar=0,
        )
        
        for ingredient in ingredients:
            nutrition = self.calculate_ingredient_nutrition(ingredient)
            if nutrition:
                total.calories += nutrition.calories
                total.protein += nutrition.protein
                total.carbohydrates += nutrition.carbohydrates
                total.fat += nutrition.fat
                total.fiber = (total.fiber or 0) + (nutrition.fiber or 0)
                total.sodium = (total.sodium or 0) + (nutrition.sodium or 0)
                total.sugar = (total.sugar or 0) + (nutrition.sugar or 0)
        
        return total
    
    def validate_nutrition(
        self,
        nutrition: Nutrition,
        preference: Optional[dict] = None
    ) -> dict[str, bool]:
        """验证营养是否符合用户需求
        
        Args:
            nutrition: 营养信息
            preference: 用户偏好（如低钠、低糖等）
        
        Returns:
            验证结果字典
        """
        results = {
            "low_sodium": nutrition.sodium is not None and nutrition.sodium < 600,
            "low_sugar": nutrition.sugar is not None and nutrition.sugar < 10,
            "high_protein": nutrition.protein > 20,
            "low_calorie": nutrition.calories < 300,
        }
        
        return results
