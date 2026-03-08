"""Bot Webhook API"""

from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel

from recipe_agent.core.bot import BotConfig
from recipe_agent.core.llm import LLMConfig
from recipe_agent.core.vision import VisionConfig
from recipe_agent.services.bot_handler import BotHandler


router = APIRouter()


# TODO: 从配置读取
def get_bot_config(platform: str) -> BotConfig:
    """获取 Bot 配置"""
    import os
    
    return BotConfig(
        platform=platform,
        app_id=os.getenv(f"{platform.upper()}_APP_ID"),
        app_secret=os.getenv(f"{platform.upper()}_APP_SECRET"),
        verify_token=os.getenv(f"{platform.upper()}_VERIFY_TOKEN")
    )


def get_handler(platform: str) -> BotHandler:
    """获取处理器"""
    import os
    
    llm_config = None
    api_key = os.getenv("LLM_API_KEY")
    if api_key:
        llm_config = LLMConfig(
            provider=os.getenv("LLM_PROVIDER", "deepseek"),
            model=os.getenv("LLM_MODEL", "deepseek-chat"),
            api_key=api_key,
            api_base=os.getenv("LLM_API_BASE", "https://api.deepseek.com")
        )
    
    vision_config = None
    vision_key = os.getenv("VISION_API_KEY")
    if vision_key:
        vision_config = VisionConfig(
            provider=os.getenv("VISION_PROVIDER", "openai"),
            model=os.getenv("VISION_MODEL", "gpt-4-vision-preview"),
            api_key=vision_key
        )
    
    return BotHandler(
        bot_config=get_bot_config(platform),
        llm_config=llm_config,
        vision_config=vision_config
    )


@router.post("/feishu")
async def feishu_webhook(
    request: Request,
    x_lark_signature: str = Header(None, alias="X-Lark-Signature")
):
    """飞书 Webhook"""
    try:
        # 读取请求体
        body = await request.json()
        
        # 验证签名（可选）
        # TODO: 实现签名验证
        
        # 处理消息
        handler = get_handler("feishu")
        response = await handler.handle_message(body)
        
        # 返回响应
        return {"status": "ok", "message": response.content}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/wechat")
async def wechat_webhook(
    request: Request,
    signature: str = "",
    timestamp: str = "",
    nonce: str = ""
):
    """微信 Webhook"""
    try:
        # 验证签名
        handler = get_handler("wechat")
        
        body = await request.body()
        is_valid = await handler.bot.verify_signature(
            signature, timestamp, nonce, body.decode()
        )
        
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # 处理消息
        data = await request.json()
        response = await handler.handle_message(data)
        
        return {"status": "ok", "message": response.content}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dingtalk")
async def dingtalk_webhook(
    request: Request,
    signature: str = "",
    timestamp: str = ""
):
    """钉钉 Webhook"""
    try:
        handler = get_handler("dingtalk")
        
        # 验证签名
        body = await request.body()
        is_valid = await handler.bot.verify_signature(
            signature, timestamp, "", body.decode()
        )
        
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # 处理消息
        data = await request.json()
        response = await handler.handle_message(data)
        
        return {"status": "ok", "message": response.content}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
