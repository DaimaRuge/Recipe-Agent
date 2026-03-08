"""向量数据库服务

基于 ChromaDB 的向量存储和检索
"""

import os
from typing import Optional

from pydantic import BaseModel


class VectorDBConfig(BaseModel):
    """向量数据库配置"""
    
    type: str = "chroma"
    persist_directory: str = "./data/vectors"
    collection_name: str = "recipes"
    embedding_model: str = "text-embedding-ada-002"


class VectorDocument(BaseModel):
    """向量文档"""
    
    id: str
    content: str
    metadata: dict


class VectorDBAdapter:
    """向量数据库适配器"""
    
    def __init__(self, config: VectorDBConfig):
        self.config = config
        self._client = None
        self._collection = None
    
    async def initialize(self):
        """初始化数据库连接"""
        # 延迟导入（避免强制依赖）
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError:
            raise ImportError(
                "chromadb 未安装。请运行: pip install chromadb"
            )
        
        # 确保目录存在
        os.makedirs(self.config.persist_directory, exist_ok=True)
        
        # 创建客户端
        self._client = chromadb.PersistentClient(
            path=self.config.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 获取或创建集合
        self._collection = self._client.get_or_create_collection(
            name=self.config.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    async def add_documents(
        self,
        documents: list[VectorDocument]
    ) -> int:
        """添加文档
        
        Args:
            documents: 文档列表
        
        Returns:
            添加的文档数量
        """
        if not self._collection:
            await self.initialize()
        
        ids = [doc.id for doc in documents]
        contents = [doc.content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        self._collection.add(
            ids=ids,
            documents=contents,
            metadatas=metadatas
        )
        
        return len(documents)
    
    async def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[dict] = None
    ) -> list[dict]:
        """搜索相似文档
        
        Args:
            query: 查询文本
            n_results: 返回结果数量
            where: 元数据过滤条件
        
        Returns:
            搜索结果列表
        """
        if not self._collection:
            await self.initialize()
        
        results = self._collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        
        # 格式化结果
        formatted = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                formatted.append({
                    "id": doc_id,
                    "content": results["documents"][0][i] if results["documents"] else None,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None
                })
        
        return formatted
    
    async def delete_document(self, doc_id: str):
        """删除文档
        
        Args:
            doc_id: 文档 ID
        """
        if not self._collection:
            await self.initialize()
        
        self._collection.delete(ids=[doc_id])
    
    async def get_document(self, doc_id: str) -> Optional[dict]:
        """获取单个文档
        
        Args:
            doc_id: 文档 ID
        
        Returns:
            文档数据
        """
        if not self._collection:
            await self.initialize()
        
        results = self._collection.get(
            ids=[doc_id],
            include=["documents", "metadatas"]
        )
        
        if results["ids"]:
            return {
                "id": results["ids"][0],
                "content": results["documents"][0] if results["documents"] else None,
                "metadata": results["metadatas"][0] if results["metadatas"] else {}
            }
        
        return None
    
    async def count(self) -> int:
        """获取文档总数"""
        if not self._collection:
            await self.initialize()
        
        return self._collection.count()
    
    async def clear(self):
        """清空集合"""
        if not self._client:
            await self.initialize()
        
        # 删除并重建集合
        self._client.delete_collection(self.config.collection_name)
        self._collection = self._client.create_collection(
            name=self.config.collection_name,
            metadata={"hnsw:space": "cosine"}
        )


class MockVectorDBAdapter(VectorDBAdapter):
    """Mock 向量数据库（用于测试）"""
    
    def __init__(self, config: VectorDBConfig):
        super().__init__(config)
        self._documents: dict[str, VectorDocument] = {}
    
    async def initialize(self):
        """初始化（无需操作）"""
        pass
    
    async def add_documents(self, documents: list[VectorDocument]) -> int:
        """添加文档"""
        for doc in documents:
            self._documents[doc.id] = doc
        return len(documents)
    
    async def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[dict] = None
    ) -> list[dict]:
        """搜索（简单匹配）"""
        results = []
        query_lower = query.lower()
        
        for doc_id, doc in self._documents.items():
            if query_lower in doc.content.lower():
                results.append({
                    "id": doc_id,
                    "content": doc.content,
                    "metadata": doc.metadata,
                    "distance": 0.0
                })
        
        return results[:n_results]
    
    async def delete_document(self, doc_id: str):
        """删除文档"""
        self._documents.pop(doc_id, None)
    
    async def get_document(self, doc_id: str) -> Optional[dict]:
        """获取文档"""
        doc = self._documents.get(doc_id)
        if doc:
            return {
                "id": doc.id,
                "content": doc.content,
                "metadata": doc.metadata
            }
        return None
    
    async def count(self) -> int:
        """计数"""
        return len(self._documents)
    
    async def clear(self):
        """清空"""
        self._documents.clear()


def create_vector_db(
    config: VectorDBConfig,
    use_mock: bool = False
) -> VectorDBAdapter:
    """创建向量数据库适配器
    
    Args:
        config: 配置
        use_mock: 是否使用 Mock
    
    Returns:
        适配器实例
    """
    if use_mock:
        return MockVectorDBAdapter(config)
    
    return VectorDBAdapter(config)
