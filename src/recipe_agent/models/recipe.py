"""Recipe 数据模型

基于 schemas/recipe_v0.1.json 的 Pydantic 模型
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Ingredient(BaseModel):
    """食材"""
    
    name: str = Field(..., description="食材名称")
    amount: float = Field(..., ge=0, description="数量")
    unit: str = Field(..., description="单位 (克/毫升/个/勺等)")
    optional: bool = Field(default=False, description="是否可选")
    substitutes: list[str] = Field(default_factory=list, description="替代食材")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "西红柿",
                "amount": 2,
                "unit": "个",
                "optional": False,
                "substitutes": ["圣女果"]
            }
        }


class Step(BaseModel):
    """烹饪步骤"""
    
    step_number: int = Field(..., ge=1, description="步骤序号")
    instruction: str = Field(..., min_length=1, description="步骤说明")
    duration_minutes: Optional[int] = Field(None, ge=0, description="预计时长（分钟）")
    temperature: Optional[str] = Field(None, description="温度说明（如：中火、180°C）")
    tips: list[str] = Field(default_factory=list, description="步骤小贴士")
    
    class Config:
        json_schema_extra = {
            "example": {
                "step_number": 1,
                "instruction": "西红柿切块，鸡蛋打散",
                "duration_minutes": 3,
                "temperature": None,
                "tips": ["西红柿可以用开水烫一下去皮"]
            }
        }


class Nutrition(BaseModel):
    """营养信息（每份）"""
    
    calories: float = Field(..., ge=0, description="热量 (kcal)")
    protein: float = Field(..., ge=0, description="蛋白质 (g)")
    carbohydrates: float = Field(..., ge=0, description="碳水化合物 (g)")
    fat: float = Field(..., ge=0, description="脂肪 (g)")
    fiber: Optional[float] = Field(None, ge=0, description="膳食纤维 (g)")
    sodium: Optional[float] = Field(None, ge=0, description="钠 (mg)")
    sugar: Optional[float] = Field(None, ge=0, description="糖 (g)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "calories": 280,
                "protein": 12.5,
                "carbohydrates": 15.2,
                "fat": 18.3,
                "fiber": 2.1,
                "sodium": 520,
                "sugar": 8.5
            }
        }


class Recipe(BaseModel):
    """菜谱"""
    
    recipe_id: UUID = Field(default_factory=uuid4, description="唯一标识符")
    title: str = Field(..., min_length=1, max_length=200, description="菜谱名称")
    description: str = Field(..., min_length=1, max_length=2000, description="菜谱描述")
    
    difficulty: str = Field(default="medium", description="难度等级")
    prep_time: Optional[int] = Field(None, ge=0, description="准备时间（分钟）")
    cook_time: Optional[int] = Field(None, ge=0, description="烹饪时间（分钟）")
    total_time: Optional[int] = Field(None, ge=0, description="总时间（分钟）")
    servings: int = Field(default=4, ge=1, le=20, description="份数")
    
    tags: list[str] = Field(default_factory=list, description="标签")
    cuisine: Optional[str] = Field(None, description="菜系（如：中式、意式）")
    
    ingredients: list[Ingredient] = Field(..., min_length=1, description="食材列表")
    steps: list[Step] = Field(..., min_length=1, description="步骤列表")
    nutrition: Nutrition = Field(..., description="营养信息")
    
    equipment: list[str] = Field(default_factory=list, description="所需设备")
    tips: list[str] = Field(default_factory=list, description="整体贴士")
    
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "番茄炒蛋",
                "description": "经典家常菜，酸甜可口，营养丰富",
                "difficulty": "easy",
                "prep_time": 5,
                "cook_time": 10,
                "total_time": 15,
                "servings": 2,
                "tags": ["家常菜", "快手菜", "下饭菜"],
                "cuisine": "中式",
                "ingredients": [
                    {
                        "name": "西红柿",
                        "amount": 2,
                        "unit": "个",
                        "optional": False
                    },
                    {
                        "name": "鸡蛋",
                        "amount": 3,
                        "unit": "个",
                        "optional": False
                    }
                ],
                "steps": [
                    {
                        "step_number": 1,
                        "instruction": "西红柿切块，鸡蛋打散",
                        "duration_minutes": 3
                    },
                    {
                        "step_number": 2,
                        "instruction": "热锅倒油，倒入蛋液炒至凝固",
                        "duration_minutes": 2,
                        "temperature": "中火"
                    }
                ],
                "nutrition": {
                    "calories": 280,
                    "protein": 12.5,
                    "carbohydrates": 15.2,
                    "fat": 18.3
                }
            }
        }
