"""推荐服务

"今天吃什么"快速候选推荐
"""

from datetime import datetime
from typing import Optional

from recipe_agent.core.llm import LLMConfig, LLMAdapter, create_llm_adapter
from recipe_agent.core.prompts import RecipePrompts
from recipe_agent.models.recipe import Recipe
from recipe_agent.models.user import UserPreference


class RecommendationService:
    """推荐服务
    
    负责根据用户偏好推荐菜谱
    """
    
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        """初始化推荐服务
        
        Args:
            llm_config: LLM 配置（可选）
        """
        if llm_config:
            self.llm: LLMAdapter = create_llm_adapter(llm_config)
        else:
            # 使用 Mock 适配器
            mock_config = LLMConfig(
                provider="mock",
                model="deepseek-chat",
                api_key="mock"
            )
            self.llm = create_llm_adapter(mock_config)
        
        self.prompts = RecipePrompts()
    
    async def get_daily_recommendations(
        self,
        preference: UserPreference,
        count: int = 5,
        season: Optional[str] = None
    ) -> list[Recipe]:
        """获取"今天吃什么"推荐
        
        Args:
            preference: 用户偏好
            count: 推荐数量（默认 5 个）
            season: 季节（可选，如"春季"）
        
        Returns:
            推荐菜谱列表
        """
        # 使用 LLM 生成推荐
        system_prompt = self.prompts.get_system_prompt()
        user_prompt = self.prompts.get_recommendation_prompt(preference, season, count)
        
        try:
            result = await self.llm.generate_json(
                prompt=user_prompt,
                system_prompt=system_prompt
            )
            
            # 解析返回的菜谱列表
            if isinstance(result, list):
                recipes_data = result
            elif isinstance(result, dict) and "recipes" in result:
                recipes_data = result["recipes"]
            else:
                recipes_data = [result]
            
            # 构建简化的 Recipe 对象
            recipes = []
            for data in recipes_data[:count]:
                recipe = Recipe(
                    title=data.get("title", "未知菜谱"),
                    description=data.get("description", ""),
                    tags=data.get("tags", []),
                    total_time=data.get("total_time"),
                    # 使用默认值填充必需字段
                    ingredients=[],
                    steps=[],
                    nutrition=Recipe.__fields__["nutrition"].default_factory()
                )
                recipes.append(recipe)
            
            return recipes
        
        except Exception as e:
            # Fallback: 返回空列表或使用基于规则的推荐
            print(f"LLM 推荐失败: {e}")
            return []
    
    def _get_current_season(self) -> str:
        """获取当前季节
        
        Returns:
            季节名称（春季/夏季/秋季/冬季）
        """
        month = datetime.now().month
        
        if month in [3, 4, 5]:
            return "春季"
        elif month in [6, 7, 8]:
            return "夏季"
        elif month in [9, 10, 11]:
            return "秋季"
        else:
            return "冬季"
    
    def _filter_by_preference(
        self,
        recipes: list[Recipe],
        preference: UserPreference
    ) -> list[Recipe]:
        """根据用户偏好过滤菜谱
        
        Args:
            recipes: 候选菜谱列表
            preference: 用户偏好
        
        Returns:
            过滤后的菜谱列表
        """
        filtered = []
        
        for recipe in recipes:
            # 检查是否包含不喜欢的食材
            has_disliked = any(
                ing.name in preference.disliked_ingredients
                for ing in recipe.ingredients
            )
            
            if has_disliked:
                continue
            
            # 检查烹饪时间
            if preference.max_cooking_time:
                total_time = recipe.total_time or 0
                if total_time > preference.max_cooking_time:
                    continue
            
            # 检查难度是否符合技能水平
            # TODO: 实现更细致的难度匹配
            
            filtered.append(recipe)
        
        return filtered
    
    def _ensure_diversity(
        self,
        recipes: list[Recipe],
        count: int
    ) -> list[Recipe]:
        """确保推荐多样性
        
        Args:
            recipes: 候选菜谱列表
            count: 需要的数量
        
        Returns:
            多样化后的菜谱列表
        """
        # TODO: 实现多样性算法
        # 1. 不同菜系
        # 2. 不同口味
        # 3. 不同烹饪方式
        
        return recipes[:count]
    
    async def get_similar_recipes(
        self,
        recipe: Recipe,
        count: int = 3
    ) -> list[Recipe]:
        """获取相似菜谱
        
        Args:
            recipe: 参考菜谱
            count: 需要的数量
        
        Returns:
            相似菜谱列表
        """
        # TODO: 使用向量相似度搜索
        # 1. 将菜谱向量化
        # 2. 在向量数据库中搜索
        # 3. 返回最相似的结果
        
        raise NotImplementedError("待实现相似度搜索")
