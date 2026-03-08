"""多模态菜谱生成服务

从图片/视频生成菜谱
"""

from typing import Optional

from recipe_agent.core.llm import LLMAdapter, LLMConfig, create_llm_adapter
from recipe_agent.core.vision import (
    VisionAdapter,
    VisionConfig,
    create_vision_adapter,
    IngredientRecognitionResult
)
from recipe_agent.models.recipe import Recipe
from recipe_agent.models.user import UserPreference
from recipe_agent.services.recipe_generator import RecipeGenerator


class MultimodalRecipeGenerator:
    """多模态菜谱生成器
    
    负责从图片/视频生成菜谱
    """
    
    def __init__(
        self,
        llm_config: Optional[LLMConfig] = None,
        vision_config: Optional[VisionConfig] = None
    ):
        """初始化
        
        Args:
            llm_config: LLM 配置
            vision_config: 视觉模型配置
        """
        # 创建适配器
        if llm_config:
            self.llm: LLMAdapter = create_llm_adapter(llm_config)
        else:
            mock_llm = LLMConfig(provider="mock", model="mock", api_key="mock")
            self.llm = create_llm_adapter(mock_llm)
        
        if vision_config:
            self.vision: VisionAdapter = create_vision_adapter(vision_config)
        else:
            mock_vision = VisionConfig(provider="mock", api_key="mock")
            self.vision = create_vision_adapter(mock_vision)
        
        self.recipe_generator = RecipeGenerator(llm_config=llm_config)
    
    async def generate_from_image(
        self,
        image_data: str,
        preference: Optional[UserPreference] = None
    ) -> Recipe:
        """从图片生成菜谱
        
        Args:
            image_data: 图片数据（URL 或 base64）
            preference: 用户偏好
        
        Returns:
            生成的菜谱
        """
        # 1. 识别食材
        recognition = await self.vision.recognize_ingredients(image_data)
        
        # 2. 构建生成提示
        ingredients_str = "、".join(recognition.ingredients)
        suggestions_str = "、".join(recognition.suggestions)
        
        prompt = f"""识别到的食材：{ingredients_str}
识别可信度：{recognition.confidence:.0%}
推荐菜品：{suggestions_str}

请根据这些食材生成一道详细的菜谱。"""
        
        # 3. 生成菜谱
        recipe = await self.recipe_generator.generate_from_text(
            text=prompt,
            preference=preference
        )
        
        return recipe
    
    async def generate_from_video(
        self,
        video_path: str,
        preference: Optional[UserPreference] = None
    ) -> Recipe:
        """从视频生成菜谱
        
        Args:
            video_path: 视频路径
            preference: 用户偏好
        
        Returns:
            生成的菜谱
        """
        from recipe_agent.core.vision import VideoProcessor
        
        # 1. 分析视频
        processor = VideoProcessor()
        analysis = await processor.analyze_cooking_video(video_path, self.vision)
        
        # 2. 构建生成提示
        prompt = f"""这是一个烹饪视频，共 {analysis['frames']} 个关键帧。

分析摘要：
{chr(10).join(f'- {a}' for a in analysis['analyses'])}

请根据视频内容生成详细的菜谱。"""
        
        # 3. 生成菜谱
        recipe = await self.recipe_generator.generate_from_text(
            text=prompt,
            preference=preference
        )
        
        return recipe
    
    async def analyze_food_image(
        self,
        image_data: str
    ) -> dict:
        """分析食物图片
        
        Args:
            image_data: 图片数据
        
        Returns:
            分析结果
        """
        # 详细分析
        prompt = """请详细分析这张食物图片，包括：

1. 菜品名称（推测）
2. 主要食材
3. 烹饪方法
4. 口味特点
5. 营养估算
6. 制作难度

请以 JSON 格式返回。"""
        
        analysis = await self.vision.analyze_image(image_data, prompt)
        
        # 尝试解析 JSON
        import json
        try:
            return json.loads(analysis)
        except:
            return {"raw_analysis": analysis}
    
    async def suggest_recipes_by_ingredients(
        self,
        ingredients: list[str],
        preference: Optional[UserPreference] = None,
        count: int = 3
    ) -> list[Recipe]:
        """根据食材推荐菜谱
        
        Args:
            ingredients: 食材列表
            preference: 用户偏好
            count: 推荐数量
        
        Returns:
            菜谱列表
        """
        ingredients_str = "、".join(ingredients)
        prompt = f"请推荐 {count} 道可以用以下食材制作的菜谱：{ingredients_str}"
        
        # 使用 LLM 生成多个菜谱
        system_prompt = self.recipe_generator.prompts.get_system_prompt()
        user_prompt = self.recipe_generator.prompts.get_generation_prompt(prompt, preference)
        
        # 修改 prompt 要求返回多个菜谱
        user_prompt += f"\n\n请返回 {count} 道不同的菜谱，以 JSON 数组格式返回。"
        
        result = await self.llm.generate_json(
            prompt=user_prompt,
            system_prompt=system_prompt
        )
        
        # 解析结果
        recipes_data = result if isinstance(result, list) else [result]
        
        recipes = []
        for data in recipes_data[:count]:
            try:
                recipe = self.recipe_generator._parse_recipe(data)
                recipes.append(recipe)
            except Exception as e:
                print(f"解析菜谱失败: {e}")
                continue
        
        return recipes
