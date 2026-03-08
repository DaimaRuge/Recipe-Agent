"""Bot 消息处理服务

处理来自不同平台的消息并返回菜谱
"""

from typing import Optional

from recipe_agent.core.bot import (
    BotAdapter,
    BotConfig,
    BotMessage,
    BotResponse,
    create_bot_adapter
)
from recipe_agent.core.llm import LLMConfig
from recipe_agent.core.vision import VisionConfig
from recipe_agent.models.recipe import Recipe
from recipe_agent.models.user import UserPreference
from recipe_agent.services.multimodal import MultimodalRecipeGenerator
from recipe_agent.services.recipe_generator import RecipeGenerator
from recipe_agent.services.recommendation import RecommendationService


class BotHandler:
    """Bot 消息处理器
    
    负责处理来自不同平台的消息
    """
    
    def __init__(
        self,
        bot_config: BotConfig,
        llm_config: Optional[LLMConfig] = None,
        vision_config: Optional[VisionConfig] = None
    ):
        """初始化处理器
        
        Args:
            bot_config: Bot 配置
            llm_config: LLM 配置
            vision_config: 视觉配置
        """
        self.bot: BotAdapter = create_bot_adapter(bot_config)
        self.llm_config = llm_config
        self.vision_config = vision_config
        
        # 初始化服务
        self.recipe_generator = RecipeGenerator(llm_config=llm_config)
        self.multimodal_generator = MultimodalRecipeGenerator(
            llm_config=llm_config,
            vision_config=vision_config
        )
        self.recommendation_service = RecommendationService(llm_config=llm_config)
    
    async def handle_message(
        self,
        raw_data: dict
    ) -> BotResponse:
        """处理消息
        
        Args:
            raw_data: 原始消息数据
        
        Returns:
            响应消息
        """
        # 1. 解析消息
        message = self.bot.parse_message(raw_data)
        
        # 2. 根据消息类型处理
        try:
            if message.message_type == "text":
                return await self._handle_text(message)
            
            elif message.message_type == "image":
                return await self._handle_image(message)
            
            elif message.message_type == "video":
                return await self._handle_video(message)
            
            else:
                return BotResponse(
                    content="抱歉，暂不支持这种消息类型。请发送文字或图片。"
                )
        
        except Exception as e:
            return BotResponse(
                content=f"处理消息时出错：{str(e)}"
            )
    
    async def _handle_text(self, message: BotMessage) -> BotResponse:
        """处理文本消息"""
        text = message.content.strip()
        
        # 判断意图
        if "吃什么" in text or "推荐" in text:
            # 推荐菜谱
            preference = await self._get_user_preference(message.user_id)
            recipes = await self.recommendation_service.get_daily_recommendations(
                preference=preference,
                count=3
            )
            
            if recipes:
                content = "为您推荐以下菜谱：\n\n"
                for i, recipe in enumerate(recipes, 1):
                    content += f"{i}. {recipe.title}\n"
                    content += f"   {recipe.description}\n\n"
                
                return BotResponse(content=content)
            else:
                return BotResponse(
                    content="暂时没有合适的推荐，请稍后再试。"
                )
        
        else:
            # 生成菜谱
            preference = await self._get_user_preference(message.user_id)
            recipe = await self.recipe_generator.generate_from_text(
                text=text,
                preference=preference
            )
            
            # 格式化响应
            content = self._format_recipe(recipe)
            
            return BotResponse(content=content)
    
    async def _handle_image(self, message: BotMessage) -> BotResponse:
        """处理图片消息"""
        if not message.image_url:
            return BotResponse(
                content="无法获取图片，请重新发送。"
            )
        
        # 识别食材并生成菜谱
        preference = await self._get_user_preference(message.user_id)
        recipe = await self.multimodal_generator.generate_from_image(
            image_data=message.image_url,
            preference=preference
        )
        
        content = f"识别到图片中的食材，为您生成菜谱：\n\n"
        content += self._format_recipe(recipe)
        
        return BotResponse(content=content)
    
    async def _handle_video(self, message: BotMessage) -> BotResponse:
        """处理视频消息"""
        if not message.video_url:
            return BotResponse(
                content="无法获取视频，请重新发送。"
            )
        
        # TODO: 实现视频处理
        return BotResponse(
            content="视频分析功能开发中，敬请期待！"
        )
    
    def _format_recipe(self, recipe: Recipe) -> str:
        """格式化菜谱为文本
        
        Args:
            recipe: 菜谱对象
        
        Returns:
            格式化的文本
        """
        lines = [
            f"🍳 {recipe.title}",
            "",
            f"📝 {recipe.description}",
            "",
            f"⏱️ 用时：{recipe.total_time or '?'} 分钟",
            f"👥 份数：{recipe.servings} 人份",
            f"📊 难度：{recipe.difficulty}",
            "",
            "🥘 食材："
        ]
        
        for ing in recipe.ingredients:
            optional = "（可选）" if ing.optional else ""
            lines.append(f"  • {ing.name} {ing.amount}{ing.unit}{optional}")
        
        lines.append("")
        lines.append("👨‍🍳 步骤：")
        
        for step in recipe.steps:
            lines.append(f"  {step.step_number}. {step.instruction}")
            if step.duration_minutes:
                lines.append(f"     ⏰ {step.duration_minutes} 分钟")
        
        lines.append("")
        lines.append("💪 营养（每份）：")
        lines.append(f"  • 热量：{recipe.nutrition.calories} kcal")
        lines.append(f"  • 蛋白质：{recipe.nutrition.protein} g")
        lines.append(f"  • 碳水：{recipe.nutrition.carbohydrates} g")
        lines.append(f"  • 脂肪：{recipe.nutrition.fat} g")
        
        return "\n".join(lines)
    
    async def _get_user_preference(
        self,
        user_id: str
    ) -> UserPreference:
        """获取用户偏好
        
        Args:
            user_id: 用户 ID
        
        Returns:
            用户偏好
        """
        # TODO: 从数据库查询用户偏好
        return UserPreference()
    
    async def send_message(
        self,
        chat_id: str,
        content: str
    ) -> bool:
        """发送消息
        
        Args:
            chat_id: 聊天 ID
            content: 消息内容
        
        Returns:
            是否成功
        """
        response = BotResponse(content=content)
        return await self.bot.send_message(chat_id, response)
