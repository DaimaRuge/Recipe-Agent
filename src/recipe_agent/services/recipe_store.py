"""菜谱存储服务

将菜谱向量化并存储到向量数据库
"""

from typing import Optional
from uuid import UUID

from recipe_agent.core.vectordb import (
    VectorDBAdapter,
    VectorDBConfig,
    VectorDocument,
    create_vector_db
)
from recipe_agent.models.recipe import Recipe


class RecipeStore:
    """菜谱存储服务
    
    负责将菜谱向量化并存储到向量数据库
    """
    
    def __init__(
        self,
        config: Optional[VectorDBConfig] = None,
        use_mock: bool = False
    ):
        """初始化存储服务
        
        Args:
            config: 向量数据库配置
            use_mock: 是否使用 Mock
        """
        self.config = config or VectorDBConfig()
        self.db: VectorDBAdapter = create_vector_db(self.config, use_mock)
    
    async def initialize(self):
        """初始化数据库"""
        await self.db.initialize()
    
    def _recipe_to_document(self, recipe: Recipe) -> VectorDocument:
        """将菜谱转换为向量文档
        
        Args:
            recipe: 菜谱对象
        
        Returns:
            向量文档
        """
        # 构建用于向量化的文本内容
        content_parts = [
            f"菜名：{recipe.title}",
            f"描述：{recipe.description}",
            f"菜系：{recipe.cuisine or '未分类'}",
            f"难度：{recipe.difficulty}",
            f"标签：{', '.join(recipe.tags)}",
            f"食材：{', '.join(ing.name for ing in recipe.ingredients)}",
            f"总时间：{recipe.total_time or 0} 分钟",
        ]
        
        content = "\n".join(content_parts)
        
        # 元数据
        metadata = {
            "title": recipe.title,
            "cuisine": recipe.cuisine or "",
            "difficulty": recipe.difficulty,
            "total_time": recipe.total_time or 0,
            "tags": recipe.tags,
            "servings": recipe.servings,
            "calories": recipe.nutrition.calories
        }
        
        return VectorDocument(
            id=str(recipe.recipe_id),
            content=content,
            metadata=metadata
        )
    
    async def add_recipe(self, recipe: Recipe) -> str:
        """添加菜谱到向量数据库
        
        Args:
            recipe: 菜谱对象
        
        Returns:
            文档 ID
        """
        document = self._recipe_to_document(recipe)
        await self.db.add_documents([document])
        return document.id
    
    async def add_recipes(self, recipes: list[Recipe]) -> list[str]:
        """批量添加菜谱
        
        Args:
            recipes: 菜谱列表
        
        Returns:
            文档 ID 列表
        """
        documents = [self._recipe_to_document(r) for r in recipes]
        await self.db.add_documents(documents)
        return [doc.id for doc in documents]
    
    async def search_recipes(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[dict] = None
    ) -> list[dict]:
        """搜索相似菜谱
        
        Args:
            query: 查询文本
            n_results: 返回数量
            filters: 过滤条件（如 {"cuisine": "中式"}）
        
        Returns:
            搜索结果
        """
        return await self.db.search(
            query=query,
            n_results=n_results,
            where=filters
        )
    
    async def get_recipe(self, recipe_id: UUID) -> Optional[dict]:
        """获取单个菜谱
        
        Args:
            recipe_id: 菜谱 ID
        
        Returns:
            菜谱数据
        """
        return await self.db.get_document(str(recipe_id))
    
    async def delete_recipe(self, recipe_id: UUID):
        """删除菜谱
        
        Args:
            recipe_id: 菜谱 ID
        """
        await self.db.delete_document(str(recipe_id))
    
    async def count(self) -> int:
        """获取菜谱总数"""
        return await self.db.count()
    
    async def clear(self):
        """清空所有菜谱"""
        await self.db.clear()
    
    async def find_by_ingredients(
        self,
        ingredients: list[str],
        n_results: int = 5
    ) -> list[dict]:
        """根据食材查找菜谱
        
        Args:
            ingredients: 食材列表
            n_results: 返回数量
        
        Returns:
            匹配的菜谱
        """
        query = f"包含食材：{', '.join(ingredients)}"
        return await self.search_recipes(query, n_results)
    
    async def find_by_cuisine(
        self,
        cuisine: str,
        n_results: int = 5
    ) -> list[dict]:
        """根据菜系查找
        
        Args:
            cuisine: 菜系名称
            n_results: 返回数量
        
        Returns:
            匹配的菜谱
        """
        return await self.search_recipes(
            query=cuisine,
            n_results=n_results,
            filters={"cuisine": cuisine}
        )
    
    async def find_by_difficulty(
        self,
        difficulty: str,
        n_results: int = 5
    ) -> list[dict]:
        """根据难度查找
        
        Args:
            difficulty: 难度等级
            n_results: 返回数量
        
        Returns:
            匹配的菜谱
        """
        return await self.search_recipes(
            query=f"难度 {difficulty}",
            n_results=n_results,
            filters={"difficulty": difficulty}
        )
