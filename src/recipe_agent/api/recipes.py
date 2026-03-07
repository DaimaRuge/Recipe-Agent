"""菜谱相关 API"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from recipe_agent.models.recipe import Recipe
from recipe_agent.models.user import UserPreference
from recipe_agent.services.recipe_generator import RecipeGenerator
from recipe_agent.services.recommendation import RecommendationService


router = APIRouter()


class GenerateRecipeRequest(BaseModel):
    """生成菜谱请求"""
    
    text: str = Field(..., description="自然语言输入")
    preference: Optional[UserPreference] = Field(None, description="用户偏好")


class GenerateRecipeResponse(BaseModel):
    """生成菜谱响应"""
    
    recipe: Recipe
    message: str = "生成成功"


@router.post("/generate", response_model=GenerateRecipeResponse)
async def generate_recipe(request: GenerateRecipeRequest):
    """从文本生成菜谱
    
    支持自然语言输入，如"番茄炒蛋"、"红烧肉"等
    """
    generator = RecipeGenerator()
    
    try:
        recipe = await generator.generate_from_text(
            text=request.text,
            preference=request.preference
        )
        
        return GenerateRecipeResponse(
            recipe=recipe,
            message=f"已为您生成菜谱：{recipe.title}"
        )
    
    except NotImplementedError:
        raise HTTPException(
            status_code=501,
            detail="功能开发中，敬请期待"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成失败：{str(e)}"
        )


@router.get("/recommendations", response_model=list[Recipe])
async def get_recommendations(
    user_id: str = Query(..., description="用户 ID"),
    count: int = Query(5, ge=1, le=10, description="推荐数量"),
    season: Optional[str] = Query(None, description="季节")
):
    """获取"今天吃什么"推荐
    
    基于用户偏好、季节、历史记录等因素推荐菜谱
    """
    service = RecommendationService()
    
    try:
        # TODO: 从数据库获取用户偏好
        preference = UserPreference()
        
        recipes = await service.get_daily_recommendations(
            preference=preference,
            count=count,
            season=season
        )
        
        return recipes
    
    except NotImplementedError:
        raise HTTPException(
            status_code=501,
            detail="功能开发中，敬请期待"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"推荐失败：{str(e)}"
        )


@router.get("/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: str):
    """获取菜谱详情
    
    根据菜谱 ID 获取详细信息
    """
    # TODO: 从数据库查询
    
    raise HTTPException(
        status_code=404,
        detail=f"菜谱 {recipe_id} 不存在"
    )


@router.post("/{recipe_id}/adjust", response_model=Recipe)
async def adjust_recipe(
    recipe_id: str,
    servings: Optional[int] = Query(None, ge=1, le=20, description="目标份数")
):
    """调整菜谱
    
    支持调整份数、替换食材等
    """
    # TODO: 实现调整逻辑
    
    raise HTTPException(
        status_code=501,
        detail="功能开发中，敬请期待"
    )
