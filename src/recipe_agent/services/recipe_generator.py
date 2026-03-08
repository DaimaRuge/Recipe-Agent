"""菜谱生成服务

基于 LLM 的菜谱生成核心逻辑
"""

from typing import Optional
from uuid import UUID

from recipe_agent.core.llm import LLMConfig, LLMAdapter, create_llm_adapter
from recipe_agent.core.prompts import RecipePrompts
from recipe_agent.models.recipe import Recipe, Ingredient, Step, Nutrition
from recipe_agent.models.user import UserPreference


class RecipeGenerator:
    """菜谱生成器
    
    负责根据用户输入和偏好生成结构化菜谱
    """
    
    def __init__(
        self,
        llm_config: Optional[LLMConfig] = None,
        model_name: str = "deepseek-chat"
    ):
        """初始化生成器
        
        Args:
            llm_config: LLM 配置（可选）
            model_name: 使用的 LLM 模型名称
        """
        if llm_config:
            self.llm: LLMAdapter = create_llm_adapter(llm_config)
        else:
            # 使用 Mock 适配器
            mock_config = LLMConfig(
                provider="mock",
                model=model_name,
                api_key="mock"
            )
            self.llm = create_llm_adapter(mock_config)
        
        self.prompts = RecipePrompts()
    
    async def generate_from_text(
        self,
        text: str,
        preference: Optional[UserPreference] = None
    ) -> Recipe:
        """从文本生成菜谱
        
        Args:
            text: 自然语言输入（如"番茄炒蛋"）
            preference: 用户偏好（可选）
        
        Returns:
            生成的菜谱对象
        """
        # 1. 构建 prompt
        system_prompt = self.prompts.get_system_prompt()
        user_prompt = self.prompts.get_generation_prompt(text, preference)
        
        # 2. 调用 LLM
        result = await self.llm.generate_json(
            prompt=user_prompt,
            system_prompt=system_prompt
        )
        
        # 3. 解析并构建 Recipe 对象
        recipe = self._parse_recipe(result)
        
        return recipe
    
    def _parse_recipe(self, data: dict) -> Recipe:
        """解析 LLM 返回的数据为 Recipe 对象
        
        Args:
            data: LLM 返回的 JSON 数据
        
        Returns:
            Recipe 对象
        """
        # 解析食材
        ingredients = [
            Ingredient(
                name=ing.get("name", ""),
                amount=ing.get("amount", 1),
                unit=ing.get("unit", "克"),
                optional=ing.get("optional", False),
                substitutes=ing.get("substitutes", [])
            )
            for ing in data.get("ingredients", [])
        ]
        
        # 解析步骤
        steps = [
            Step(
                step_number=step.get("step_number", idx + 1),
                instruction=step.get("instruction", ""),
                duration_minutes=step.get("duration_minutes"),
                temperature=step.get("temperature"),
                tips=step.get("tips", [])
            )
            for idx, step in enumerate(data.get("steps", []))
        ]
        
        # 解析营养信息
        nutrition_data = data.get("nutrition", {})
        nutrition = Nutrition(
            calories=nutrition_data.get("calories", 0),
            protein=nutrition_data.get("protein", 0),
            carbohydrates=nutrition_data.get("carbohydrates", 0),
            fat=nutrition_data.get("fat", 0),
            fiber=nutrition_data.get("fiber"),
            sodium=nutrition_data.get("sodium"),
            sugar=nutrition_data.get("sugar")
        )
        
        # 构建 Recipe
        recipe = Recipe(
            title=data.get("title", ""),
            description=data.get("description", ""),
            difficulty=data.get("difficulty", "medium"),
            prep_time=data.get("prep_time"),
            cook_time=data.get("cook_time"),
            total_time=data.get("total_time"),
            servings=data.get("servings", 4),
            tags=data.get("tags", []),
            cuisine=data.get("cuisine"),
            ingredients=ingredients,
            steps=steps,
            nutrition=nutrition,
            equipment=data.get("equipment", []),
            tips=data.get("tips", [])
        )
        
        return recipe
    
    async def generate_from_image(
        self,
        image_url: str,
        preference: Optional[UserPreference] = None
    ) -> Recipe:
        """从图片生成菜谱
        
        Args:
            image_url: 图片 URL
            preference: 用户偏好（可选）
        
        Returns:
            生成的菜谱对象
        """
        # TODO: 实现多模态 LLM 调用
        # 1. 图片预处理
        # 2. 食材识别
        # 3. 调用视觉 LLM
        # 4. 生成菜谱
        
        raise NotImplementedError("待实现多模态集成")
    
    async def adjust_for_servings(
        self,
        recipe: Recipe,
        target_servings: int
    ) -> Recipe:
        """调整菜谱份数
        
        Args:
            recipe: 原菜谱
            target_servings: 目标份数
        
        Returns:
            调整后的菜谱
        """
        if recipe.servings == target_servings:
            return recipe
        
        ratio = target_servings / recipe.servings
        
        # 调整食材用量
        adjusted_ingredients = [
            ingredient.model_copy(update={
                "amount": ingredient.amount * ratio
            })
            for ingredient in recipe.ingredients
        ]
        
        # 调整营养信息
        adjusted_nutrition = recipe.nutrition.model_copy(update={
            "calories": recipe.nutrition.calories * ratio,
            "protein": recipe.nutrition.protein * ratio,
            "carbohydrates": recipe.nutrition.carbohydrates * ratio,
            "fat": recipe.nutrition.fat * ratio,
        })
        
        return recipe.model_copy(update={
            "servings": target_servings,
            "ingredients": adjusted_ingredients,
            "nutrition": adjusted_nutrition
        })
    
    async def substitute_ingredient(
        self,
        recipe: Recipe,
        ingredient_name: str,
        substitute: str
    ) -> Recipe:
        """替换食材
        
        Args:
            recipe: 原菜谱
            ingredient_name: 要替换的食材名称
            substitute: 替代食材
        
        Returns:
            调整后的菜谱
        """
        # TODO: 实现智能食材替换
        # 1. 查找食材
        # 2. 调用 LLM 生成调整建议
        # 3. 更新步骤说明
        # 4. 重新计算营养
        
        raise NotImplementedError("待实现智能食材替换")
