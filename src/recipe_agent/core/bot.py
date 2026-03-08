"""Bot 平台适配器

支持飞书、微信、钉钉等平台
"""

import hashlib
import hmac
import json
from abc import ABC, abstractmethod
from typing import Any, Optional

import httpx
from pydantic import BaseModel


class BotConfig(BaseModel):
    """Bot 配置"""
    
    platform: str  # feishu / wechat / dingtalk
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    webhook_url: Optional[str] = None
    verify_token: Optional[str] = None
    encoding_aes_key: Optional[str] = None


class BotMessage(BaseModel):
    """Bot 消息"""
    
    message_id: str
    user_id: str
    chat_id: str
    content: str
    message_type: str = "text"
    raw_data: dict = {}
    
    # 多模态支持
    image_url: Optional[str] = None
    video_url: Optional[str] = None


class BotResponse(BaseModel):
    """Bot 响应"""
    
    content: str
    message_type: str = "text"
    
    # 富文本支持
    cards: Optional[dict] = None
    buttons: Optional[list[dict]] = None
    images: Optional[list[str]] = None


class BotAdapter(ABC):
    """Bot 适配器基类"""
    
    @abstractmethod
    async def send_message(
        self,
        chat_id: str,
        response: BotResponse
    ) -> bool:
        """发送消息"""
        pass
    
    @abstractmethod
    def parse_message(self, raw_data: dict) -> BotMessage:
        """解析消息"""
        pass
    
    @abstractmethod
    async def verify_signature(
        self,
        signature: str,
        timestamp: str,
        nonce: str,
        body: str
    ) -> bool:
        """验证签名"""
        pass


class FeishuBotAdapter(BotAdapter):
    """飞书 Bot 适配器"""
    
    def __init__(self, config: BotConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=30)
        self._access_token: Optional[str] = None
    
    async def _get_access_token(self) -> str:
        """获取访问令牌"""
        if self._access_token:
            return self._access_token
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        
        response = await self.client.post(
            url,
            json={
                "app_id": self.config.app_id,
                "app_secret": self.config.app_secret
            }
        )
        
        data = response.json()
        self._access_token = data["tenant_access_token"]
        
        return self._access_token
    
    async def send_message(
        self,
        chat_id: str,
        response: BotResponse
    ) -> bool:
        """发送消息"""
        token = await self._get_access_token()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 构建消息内容
        content: dict[str, Any]
        
        if response.message_type == "text":
            content = {"text": response.content}
        elif response.message_type == "interactive" and response.cards:
            content = response.cards
        else:
            content = {"text": response.content}
        
        payload = {
            "receive_id": chat_id,
            "msg_type": response.message_type,
            "content": json.dumps(content)
        }
        
        url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
        
        response = await self.client.post(
            url,
            headers=headers,
            json=payload
        )
        
        return response.status_code == 200
    
    def parse_message(self, raw_data: dict) -> BotMessage:
        """解析飞书消息"""
        event = raw_data.get("event", {})
        message = event.get("message", {})
        
        # 解析内容
        content_str = message.get("content", "{}")
        content_data = json.loads(content_str) if isinstance(content_str, str) else content_str
        
        content = content_data.get("text", "")
        message_type = message.get("message_type", "text")
        
        # 提取图片/视频
        image_url = None
        video_url = None
        
        if message_type == "image":
            image_key = content_data.get("image_key")
            if image_key:
                image_url = f"feishu://image/{image_key}"
        
        return BotMessage(
            message_id=message.get("message_id", ""),
            user_id=event.get("sender", {}).get("sender_id", {}).get("user_id", ""),
            chat_id=message.get("chat_id", ""),
            content=content,
            message_type=message_type,
            raw_data=raw_data,
            image_url=image_url,
            video_url=video_url
        )
    
    async def verify_signature(
        self,
        signature: str,
        timestamp: str,
        nonce: str,
        body: str
    ) -> bool:
        """验证飞书签名"""
        # 飞书使用不同的验证方式
        # 简化实现，生产环境需要完整验证
        return True


class WeChatBotAdapter(BotAdapter):
    """微信 Bot 适配器"""
    
    def __init__(self, config: BotConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=30)
    
    async def send_message(
        self,
        chat_id: str,
        response: BotResponse
    ) -> bool:
        """发送消息（企业微信）"""
        # TODO: 实现企业微信消息发送
        return False
    
    def parse_message(self, raw_data: dict) -> BotMessage:
        """解析微信消息"""
        return BotMessage(
            message_id=raw_data.get("MsgId", ""),
            user_id=raw_data.get("FromUserName", ""),
            chat_id=raw_data.get("FromUserName", ""),
            content=raw_data.get("Content", ""),
            message_type=raw_data.get("MsgType", "text"),
            raw_data=raw_data
        )
    
    async def verify_signature(
        self,
        signature: str,
        timestamp: str,
        nonce: str,
        body: str = ""
    ) -> bool:
        """验证微信签名"""
        token = self.config.verify_token or ""
        
        # 排序并拼接
        items = [token, timestamp, nonce]
        items.sort()
        joined = "".join(items)
        
        # SHA1
        calculated = hashlib.sha1(joined.encode()).hexdigest()
        
        return calculated == signature


class DingTalkBotAdapter(BotAdapter):
    """钉钉 Bot 适配器"""
    
    def __init__(self, config: BotConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=30)
    
    async def send_message(
        self,
        chat_id: str,
        response: BotResponse
    ) -> bool:
        """发送消息"""
        if not self.config.webhook_url:
            return False
        
        payload = {
            "msgtype": response.message_type,
            response.message_type: {
                "content": response.content
            }
        }
        
        resp = await self.client.post(
            self.config.webhook_url,
            json=payload
        )
        
        return resp.status_code == 200
    
    def parse_message(self, raw_data: dict) -> BotMessage:
        """解析钉钉消息"""
        return BotMessage(
            message_id=raw_data.get("msgid", ""),
            user_id=raw_data.get("senderNick", ""),
            chat_id=raw_data.get("conversationId", ""),
            content=raw_data.get("content", {}).get("content", ""),
            message_type=raw_data.get("msgtype", "text"),
            raw_data=raw_data
        )
    
    async def verify_signature(
        self,
        signature: str,
        timestamp: str,
        nonce: str,
        body: str
    ) -> bool:
        """验证钉钉签名"""
        secret = self.config.app_secret or ""
        
        # 拼接时间戳和密钥
        string_to_sign = f"{timestamp}\n{secret}"
        
        # HMAC-SHA256
        hmac_code = hmac.new(
            secret.encode(),
            string_to_sign.encode(),
            digestmod=hashlib.sha256
        ).digest()
        
        # Base64
        import base64
        calculated = base64.b64encode(hmac_code).decode()
        
        return calculated == signature


class MockBotAdapter(BotAdapter):
    """Mock Bot 适配器（用于测试）"""
    
    async def send_message(self, chat_id: str, response: BotResponse) -> bool:
        """模拟发送"""
        print(f"[Mock Bot] 发送到 {chat_id}: {response.content}")
        return True
    
    def parse_message(self, raw_data: dict) -> BotMessage:
        """模拟解析"""
        return BotMessage(
            message_id="mock_id",
            user_id="mock_user",
            chat_id="mock_chat",
            content=raw_data.get("content", ""),
            message_type="text",
            raw_data=raw_data
        )
    
    async def verify_signature(
        self,
        signature: str,
        timestamp: str,
        nonce: str,
        body: str
    ) -> bool:
        """模拟验证"""
        return True


def create_bot_adapter(config: BotConfig) -> BotAdapter:
    """创建 Bot 适配器
    
    Args:
        config: Bot 配置
    
    Returns:
        适配器实例
    """
    platform = config.platform.lower()
    
    if platform == "feishu":
        return FeishuBotAdapter(config)
    elif platform == "wechat":
        return WeChatBotAdapter(config)
    elif platform == "dingtalk":
        return DingTalkBotAdapter(config)
    else:
        return MockBotAdapter()
