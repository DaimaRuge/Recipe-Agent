"""多模态处理服务

图片和视频识别
"""

import base64
from abc import ABC, abstractmethod
from typing import Optional

import httpx
from pydantic import BaseModel


class VisionConfig(BaseModel):
    """视觉模型配置"""
    
    provider: str = "openai"  # openai / deepseek / local
    model: str = "gpt-4-vision-preview"
    api_key: Optional[str] = None
    api_base: str = "https://api.openai.com"
    max_tokens: int = 1000
    timeout: int = 120


class IngredientRecognitionResult(BaseModel):
    """食材识别结果"""
    
    ingredients: list[str]
    confidence: float
    suggestions: list[str]


class VisionAdapter(ABC):
    """视觉模型适配器"""
    
    @abstractmethod
    async def analyze_image(
        self,
        image_data: str,
        prompt: str
    ) -> str:
        """分析图片
        
        Args:
            image_data: 图片数据（base64 或 URL）
            prompt: 分析提示
        
        Returns:
            分析结果
        """
        pass
    
    @abstractmethod
    async def recognize_ingredients(
        self,
        image_data: str
    ) -> IngredientRecognitionResult:
        """识别食材
        
        Args:
            image_data: 图片数据
        
        Returns:
            识别结果
        """
        pass


class OpenAIVisionAdapter(VisionAdapter):
    """OpenAI Vision 适配器"""
    
    def __init__(self, config: VisionConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=config.timeout)
    
    async def _call_vision_api(
        self,
        image_url: str,
        prompt: str
    ) -> str:
        """调用视觉 API"""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            "max_tokens": self.config.max_tokens
        }
        
        response = await self.client.post(
            f"{self.config.api_base}/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        response.raise_for_status()
        data = response.json()
        
        return data["choices"][0]["message"]["content"]
    
    async def analyze_image(self, image_data: str, prompt: str) -> str:
        """分析图片"""
        # 判断是 URL 还是 base64
        if image_data.startswith("http"):
            image_url = image_data
        else:
            # 假设是 base64
            if not image_data.startswith("data:"):
                image_url = f"data:image/jpeg;base64,{image_data}"
            else:
                image_url = image_data
        
        return await self._call_vision_api(image_url, prompt)
    
    async def recognize_ingredients(
        self,
        image_data: str
    ) -> IngredientRecognitionResult:
        """识别食材"""
        prompt = """请分析这张图片中的食材。

要求：
1. 列出所有可见的食材
2. 评估识别的可信度（0-1）
3. 推测可能制作的菜品

请以 JSON 格式返回：
{
  "ingredients": ["食材1", "食材2"],
  "confidence": 0.85,
  "suggestions": ["建议菜品1", "建议菜品2"]
}"""
        
        result = await self.analyze_image(image_data, prompt)
        
        # 解析 JSON
        import json
        try:
            # 清理可能的格式
            result = result.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            
            data = json.loads(result)
            return IngredientRecognitionResult(**data)
        except:
            # 解析失败，返回简单结果
            return IngredientRecognitionResult(
                ingredients=[],
                confidence=0.0,
                suggestions=[result]
            )


class MockVisionAdapter(VisionAdapter):
    """Mock 视觉适配器（用于测试）"""
    
    async def analyze_image(self, image_data: str, prompt: str) -> str:
        """模拟分析"""
        return "这是一张食材图片，包含西红柿、鸡蛋等常见食材。"
    
    async def recognize_ingredients(
        self,
        image_data: str
    ) -> IngredientRecognitionResult:
        """模拟识别"""
        return IngredientRecognitionResult(
            ingredients=["西红柿", "鸡蛋", "葱"],
            confidence=0.9,
            suggestions=["番茄炒蛋", "西红柿鸡蛋汤"]
        )


def create_vision_adapter(config: VisionConfig) -> VisionAdapter:
    """创建视觉适配器
    
    Args:
        config: 配置
    
    Returns:
        适配器实例
    """
    if not config.api_key or config.api_key == "mock":
        return MockVisionAdapter()
    
    return OpenAIVisionAdapter(config)


class VideoProcessor:
    """视频处理器
    
    负责视频关键帧提取和分析
    """
    
    async def extract_key_frames(
        self,
        video_path: str,
        n_frames: int = 5
    ) -> list[str]:
        """提取关键帧
        
        Args:
            video_path: 视频路径
            n_frames: 提取帧数
        
        Returns:
            base64 编码的帧列表
        """
        # TODO: 使用 OpenCV 或 FFmpeg 实现
        # 当前返回 Mock 数据
        
        return ["mock_frame_1", "mock_frame_2", "mock_frame_3"]
    
    async def analyze_cooking_video(
        self,
        video_path: str,
        vision_adapter: VisionAdapter
    ) -> dict:
        """分析烹饪视频
        
        Args:
            video_path: 视频路径
            vision_adapter: 视觉适配器
        
        Returns:
            分析结果
        """
        # 1. 提取关键帧
        frames = await self.extract_key_frames(video_path)
        
        # 2. 分析每一帧
        results = []
        for frame in frames:
            analysis = await vision_adapter.analyze_image(
                frame,
                "描述这个烹饪步骤"
            )
            results.append(analysis)
        
        # 3. 合并结果
        return {
            "frames": len(frames),
            "analyses": results,
            "summary": "视频分析完成"
        }
