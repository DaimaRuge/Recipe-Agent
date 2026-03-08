"""LLM 适配层

支持 deepseek、seed 等多种 LLM 提供商
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Optional

import httpx
from pydantic import BaseModel


class LLMConfig(BaseModel):
    """LLM 配置"""
    
    provider: str = "deepseek"
    model: str = "deepseek-chat"
    api_key: str
    api_base: str = "https://api.deepseek.com"
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 60


class LLMAdapter(ABC):
    """LLM 适配器基类"""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """生成文本"""
        pass
    
    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> dict[str, Any]:
        """生成 JSON"""
        pass


class DeepSeekAdapter(LLMAdapter):
    """DeepSeek 适配器
    
    兼容 OpenAI API 格式
    """
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=config.timeout)
    
    async def _call_api(
        self,
        messages: list[dict],
        **kwargs
    ) -> str:
        """调用 API"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }
        
        response = await self.client.post(
            f"{self.config.api_base}/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        response.raise_for_status()
        data = response.json()
        
        return data["choices"][0]["message"]["content"]
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """生成文本"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        return await self._call_api(messages, **kwargs)
    
    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> dict[str, Any]:
        """生成 JSON"""
        # 强制要求 JSON 输出
        enhanced_prompt = f"""{prompt}

请直接返回 JSON 格式，不要包含任何其他文字或说明。"""
        
        enhanced_system = system_prompt or "你是一个专业的菜谱生成助手，必须返回有效的 JSON 格式。"
        enhanced_system += "\n\n重要：只返回 JSON，不要包含任何其他内容。"
        
        result = await self.generate(enhanced_prompt, enhanced_system, **kwargs)
        
        # 清理可能的前后缀
        result = result.strip()
        if result.startswith("```json"):
            result = result[7:]
        if result.startswith("```"):
            result = result[3:]
        if result.endswith("```"):
            result = result[:-3]
        result = result.strip()
        
        try:
            return json.loads(result)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM 返回的不是有效 JSON: {e}\n\n原始输出:\n{result}")


class SeedAdapter(LLMAdapter):
    """Seed (字节跳动) 适配器
    
    使用 OpenAI 兼容接口
    """
    
    def __init__(self, config: LLMConfig):
        # Seed 使用不同的 API base
        if "seed" in config.model.lower():
            config.api_base = "https://ark.cn-beijing.volces.com/api/v3"
        
        # 复用 DeepSeek 的实现（OpenAI 兼容）
        self._impl = DeepSeekAdapter(config)
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        return await self._impl.generate(prompt, system_prompt, **kwargs)
    
    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> dict[str, Any]:
        return await self._impl.generate_json(prompt, system_prompt, **kwargs)


class MockLLMAdapter(LLMAdapter):
    """Mock LLM 适配器（用于测试）"""
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        return "这是一条模拟响应"
    
    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> dict[str, Any]:
        return {
            "title": "番茄炒蛋",
            "description": "经典家常菜，酸甜可口",
            "difficulty": "easy",
            "prep_time": 5,
            "cook_time": 10,
            "total_time": 15,
            "servings": 2,
            "tags": ["家常菜", "快手菜"],
            "cuisine": "中式",
            "ingredients": [
                {"name": "西红柿", "amount": 2, "unit": "个", "optional": False},
                {"name": "鸡蛋", "amount": 3, "unit": "个", "optional": False},
                {"name": "葱花", "amount": 1, "unit": "勺", "optional": True}
            ],
            "steps": [
                {"step_number": 1, "instruction": "西红柿切块，鸡蛋打散", "duration_minutes": 3},
                {"step_number": 2, "instruction": "热锅倒油，倒入蛋液炒至凝固", "duration_minutes": 2, "temperature": "中火"},
                {"step_number": 3, "instruction": "加入西红柿翻炒至出汁", "duration_minutes": 3, "temperature": "中火"},
                {"step_number": 4, "instruction": "调味出锅，撒上葱花", "duration_minutes": 1}
            ],
            "nutrition": {
                "calories": 280,
                "protein": 12.5,
                "carbohydrates": 15.2,
                "fat": 18.3
            }
        }


def create_llm_adapter(config: LLMConfig) -> LLMAdapter:
    """创建 LLM 适配器
    
    Args:
        config: LLM 配置
    
    Returns:
        对应的适配器实例
    """
    if not config.api_key or config.api_key == "mock":
        return MockLLMAdapter()
    
    provider = config.provider.lower()
    
    if provider == "deepseek":
        return DeepSeekAdapter(config)
    elif provider == "seed":
        return SeedAdapter(config)
    else:
        # 默认使用 DeepSeek 实现（OpenAI 兼容）
        return DeepSeekAdapter(config)
