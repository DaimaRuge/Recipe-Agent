"""Prompt 模板

用于菜谱生成的提示词模板
"""

from typing import Optional

from recipe_agent.models.user import UserPreference


class RecipePrompts:
    """菜谱生成 Prompt 模板"""
    
    @staticmethod
    def get_system_prompt() -> str:
        """获取系统提示"""
        return """你是一个专业的菜谱生成助手，能够根据用户输入生成详细、可执行的菜谱。

你的职责：
1. 理解用户的菜谱需求（菜名、食材、口味等）
2. 生成结构化、可执行的菜谱
3. 确保营养信息准确
4. 考虑用户偏好和饮食限制

输出要求：
- 必须返回有效的 JSON 格式
- 食材用量要具体（如：2个、100克）
- 步骤要清晰、可执行
- 营养信息要基于标准食材计算"""

    @staticmethod
    def get_generation_prompt(
        text: str,
        preference: Optional[UserPreference] = None
    ) -> str:
        """获取生成 Prompt
        
        Args:
            text: 用户输入
            preference: 用户偏好
        
        Returns:
            完整的 prompt
        """
        prompt = f"请为以下需求生成菜谱：{text}\n\n"
        
        # 添加用户偏好
        if preference:
            pref_parts = []
            
            if preference.favorite_cuisines:
                pref_parts.append(f"喜欢的菜系：{', '.join(preference.favorite_cuisines)}")
            
            if preference.disliked_ingredients:
                pref_parts.append(f"不喜欢的食材：{', '.join(preference.disliked_ingredients)}")
            
            if preference.taste_preferences:
                tastes = [t.value for t in preference.taste_preferences]
                pref_parts.append(f"口味偏好：{', '.join(tastes)}")
            
            if preference.dietary_restrictions:
                restrictions = [r.value for r in preference.dietary_restrictions]
                pref_parts.append(f"饮食限制：{', '.join(restrictions)}")
            
            if preference.max_cooking_time:
                pref_parts.append(f"最大烹饪时间：{preference.max_cooking_time} 分钟")
            
            if preference.cooking_skill:
                pref_parts.append(f"烹饪技能：{preference.cooking_skill.value}")
            
            if pref_parts:
                prompt += "用户偏好：\n" + "\n".join(f"- {p}" for p in pref_parts) + "\n\n"
        
        # 添加输出格式要求
        prompt += """请返回以下 JSON 格式：
{
  "title": "菜谱名称",
  "description": "菜谱描述（50-100字）",
  "difficulty": "easy/medium/hard",
  "prep_time": 准备时间（分钟）,
  "cook_time": 烹饪时间（分钟）,
  "total_time": 总时间（分钟）,
  "servings": 份数,
  "tags": ["标签1", "标签2"],
  "cuisine": "菜系",
  "ingredients": [
    {
      "name": "食材名称",
      "amount": 数量,
      "unit": "单位（克/个/勺等）",
      "optional": false,
      "substitutes": ["替代食材"]
    }
  ],
  "steps": [
    {
      "step_number": 1,
      "instruction": "步骤说明",
      "duration_minutes": 预计时长,
      "temperature": "温度说明（可选）",
      "tips": ["小贴士"]
    }
  ],
  "nutrition": {
    "calories": 热量（每份，kcal）,
    "protein": 蛋白质（g）,
    "carbohydrates": 碳水化合物（g）,
    "fat": 脂肪（g）,
    "fiber": 膳食纤维（g，可选）,
    "sodium": 钠（mg，可选）,
    "sugar": 糖（g，可选）
  },
  "equipment": ["所需设备"],
  "tips": ["整体贴士"]
}"""
        
        return prompt
    
    @staticmethod
    def get_adjustment_prompt(
        recipe_title: str,
        adjustment_type: str,
        details: dict
    ) -> str:
        """获取调整 Prompt
        
        Args:
            recipe_title: 原菜谱名称
            adjustment_type: 调整类型（servings/ingredient/health）
            details: 调整详情
        
        Returns:
            调整 prompt
        """
        if adjustment_type == "servings":
            return f"""请将菜谱"{recipe_title}"的份数从 {details.get('from', 2)} 调整为 {details.get('to', 4)}。

要求：
1. 按比例调整所有食材用量
2. 重新计算营养信息（每份）
3. 步骤说明保持不变

返回完整的调整后菜谱 JSON。"""
        
        elif adjustment_type == "ingredient":
            return f"""请将菜谱"{recipe_title}"中的 {details.get('original')} 替换为 {details.get('substitute')}。

要求：
1. 调整食材列表
2. 更新相关步骤说明
3. 重新计算营养信息

返回完整的调整后菜谱 JSON。"""
        
        elif adjustment_type == "health":
            return f"""请根据健康需求调整菜谱"{recipe_title}"。

健康需求：{details.get('requirement')}

要求：
1. 选择更健康的食材替代
2. 减少油盐用量
3. 保留菜谱核心风味

返回完整的调整后菜谱 JSON。"""
        
        return ""
    
    @staticmethod
    def get_recommendation_prompt(
        preference: UserPreference,
        season: Optional[str] = None,
        count: int = 5
    ) -> str:
        """获取推荐 Prompt
        
        Args:
            preference: 用户偏好
            season: 季节
            count: 推荐数量
        
        Returns:
            推荐 prompt
        """
        prompt = f"请推荐 {count} 道适合今天的菜谱。\n\n"
        
        if season:
            prompt += f"当前季节：{season}\n"
        
        if preference.favorite_cuisines:
            prompt += f"喜欢的菜系：{', '.join(preference.favorite_cuisines)}\n"
        
        if preference.taste_preferences:
            tastes = [t.value for t in preference.taste_preferences]
            prompt += f"口味偏好：{', '.join(tastes)}\n"
        
        if preference.max_cooking_time:
            prompt += f"最大烹饪时间：{preference.max_cooking_time} 分钟\n"
        
        prompt += "\n请返回一个 JSON 数组，包含简化的菜谱信息（title, description, tags, total_time）。"
        
        return prompt
