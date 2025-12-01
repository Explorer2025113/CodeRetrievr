"""
Milvus矢量数据库服务
"""

from typing import List, Dict, Optional
import numpy as np
from pymilvus import (
    connections,
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    utility,
)
from app.core.config import settings


class MilvusService:
    """Milvus矢量数据库服务"""
    
    def __init__(self):
        """初始化Milvus服务"""
        self.host = settings.MILVUS_HOST
        self.port = settings.MILVUS_PORT
        self.collection_name = settings.MILVUS_COLLECTION_NAME
        self.dimension = settings.MILVUS_DIMENSION
        
        # 连接到Milvus
        self._connect()
        
        # 获取或创建集合
        self.collection = self._get_or_create_collection()
    
    def _connect(self):
        """连接到Milvus服务器"""
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )
            print(f"✅ 已连接到Milvus: {self.host}:{self.port}")
        except Exception as e:
            raise Exception(f"连接Milvus失败: {str(e)}")
    
    def _get_or_create_collection(self) -> Collection:
        """获取或创建集合"""
        # 检查集合是否存在
        if utility.has_collection(self.collection_name):
            print(f"集合 {self.collection_name} 已存在")
            collection = Collection(self.collection_name)
            # 加载集合到内存
            collection.load()
            return collection
        
        # 创建新集合
        print(f"创建新集合: {self.collection_name}")
        
        # 定义字段
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="code_id", dtype=DataType.VARCHAR, max_length=255),
            FieldSchema(name="code", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=255),
            FieldSchema(name="type", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="language", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="file_path", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="repo_name", dtype=DataType.VARCHAR, max_length=255),
            FieldSchema(name="repo_url", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
        ]
        
        # 创建Schema
        schema = CollectionSchema(
            fields=fields,
            description="代码片段矢量数据库"
        )
        
        # 创建集合
        collection = Collection(
            name=self.collection_name,
            schema=schema
        )
        
        # 创建索引
        index_params = {
            "metric_type": "L2",  # 使用L2距离
            "index_type": "HNSW",  # 使用HNSW索引
            "params": {"M": 16, "efConstruction": 200}
        }
        
        collection.create_index(
            field_name="vector",
            index_params=index_params
        )
        
        # 加载集合
        collection.load()
        
        print(f"✅ 集合创建成功: {self.collection_name}")
        return collection
    
    def insert_code_snippets(
        self,
        code_snippets: List[Dict],
        vectors: List[np.ndarray]
    ) -> List[int]:
        """
        插入代码片段和向量
        
        Args:
            code_snippets: 代码片段列表（包含元数据）
            vectors: 对应的向量列表
        
        Returns:
            插入的ID列表
        """
        if len(code_snippets) != len(vectors):
            raise ValueError("代码片段数量与向量数量不匹配")
        
        # 准备数据
        data = {
            "code_id": [snippet.get("code_id", f"snippet_{i}") for i, snippet in enumerate(code_snippets)],
            "code": [snippet.get("code", "") for snippet in code_snippets],
            "name": [snippet.get("name", "") for snippet in code_snippets],
            "type": [snippet.get("type", "") for snippet in code_snippets],
            "language": [snippet.get("language", "") for snippet in code_snippets],
            "file_path": [snippet.get("file_path", "") for snippet in code_snippets],
            "repo_name": [snippet.get("repo_name", "") for snippet in code_snippets],
            "repo_url": [snippet.get("repo_url", "") for snippet in code_snippets],
            "vector": [vector.tolist() for vector in vectors],
        }
        
        # 插入数据
        try:
            insert_result = self.collection.insert(data)
            # 刷新集合
            self.collection.flush()
            print(f"✅ 成功插入 {len(code_snippets)} 个代码片段")
            return insert_result.primary_keys
        except Exception as e:
            raise Exception(f"插入数据失败: {str(e)}")
    
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        filter_expr: Optional[str] = None
    ) -> List[Dict]:
        """
        搜索相似代码片段
        
        Args:
            query_vector: 查询向量
            top_k: 返回前k个结果
            filter_expr: 过滤表达式（如 "language == 'python'"）
        
        Returns:
            搜索结果列表
        """
        search_params = {
            "metric_type": "L2",
            "params": {"ef": 64}  # HNSW搜索参数
        }
        
        try:
            results = self.collection.search(
                data=[query_vector.tolist()],
                anns_field="vector",
                param=search_params,
                limit=top_k,
                expr=filter_expr,
                output_fields=["code_id", "code", "name", "type", "language", "file_path", "repo_name", "repo_url"]
            )
            
            # 格式化结果
            search_results = []
            for hits in results:
                for hit in hits:
                    search_results.append({
                        "id": hit.id,
                        "score": hit.score,
                        "code_id": hit.entity.get("code_id"),
                        "code": hit.entity.get("code"),
                        "name": hit.entity.get("name"),
                        "type": hit.entity.get("type"),
                        "language": hit.entity.get("language"),
                        "file_path": hit.entity.get("file_path"),
                        "repo_name": hit.entity.get("repo_name"),
                        "repo_url": hit.entity.get("repo_url"),
                    })
            
            return search_results
        
        except Exception as e:
            raise Exception(f"搜索失败: {str(e)}")
    
    def get_collection_stats(self) -> Dict:
        """获取集合统计信息"""
        try:
            stats = {
                "collection_name": self.collection_name,
                "num_entities": self.collection.num_entities,
                "dimension": self.dimension,
            }
            return stats
        except Exception as e:
            raise Exception(f"获取统计信息失败: {str(e)}")

    def get_language_stats(self) -> Dict[str, int]:
        """
        获取按语言分类的统计
        注意：由于Milvus查询性能考虑，此方法返回空字典
        实际统计信息应从Neo4j获取
        """
        # Milvus的query操作对大量数据性能较差，统计信息主要从Neo4j获取
        # 这里返回空字典，让调用方使用Neo4j的统计
        return {}
    
    def get_repo_stats(self) -> Dict[str, int]:
        """
        获取按仓库分类的统计
        注意：由于Milvus查询性能考虑，此方法返回空字典
        实际统计信息应从Neo4j获取
        """
        # Milvus的query操作对大量数据性能较差，统计信息主要从Neo4j获取
        # 这里返回空字典，让调用方使用Neo4j的统计
        return {}
    
    def get_by_code_id(self, code_id: str) -> Optional[Dict]:
        """
        根据code_id获取代码片段
        
        Args:
            code_id: 代码片段ID
            
        Returns:
            代码片段信息，如果不存在返回None
        """
        try:
            results = self.collection.query(
                expr=f"code_id == '{code_id}'",
                output_fields=["code_id", "code", "name", "type", "language", "file_path", "repo_name", "repo_url"],
                limit=1
            )
            
            if results and len(results) > 0:
                result = results[0]
                return {
                    "id": result.get("id"),
                    "code_id": result.get("code_id"),
                    "code": result.get("code"),
                    "name": result.get("name"),
                    "type": result.get("type"),
                    "language": result.get("language"),
                    "file_path": result.get("file_path"),
                    "repo_name": result.get("repo_name"),
                    "repo_url": result.get("repo_url"),
                }
            return None
        except Exception as e:
            print(f"根据code_id查询失败: {str(e)}")
            return None
    
    def delete_by_code_id(self, code_id: str) -> bool:
        """
        根据code_id删除代码片段
        
        Args:
            code_id: 代码片段ID
            
        Returns:
            是否成功删除
        """
        try:
            # 先查询获取id
            results = self.collection.query(
                expr=f"code_id == '{code_id}'",
                output_fields=["id"],
                limit=1
            )
            
            if results and len(results) > 0:
                entity_id = results[0].get("id")
                # 删除
                self.collection.delete(expr=f"id == {entity_id}")
                self.collection.flush()
                return True
            return False
        except Exception as e:
            print(f"删除代码片段失败: {str(e)}")
            return False


# 全局实例
_milvus_service: Optional[MilvusService] = None


def get_milvus_service() -> MilvusService:
    """获取Milvus服务实例（单例模式）"""
    global _milvus_service
    if _milvus_service is None:
        _milvus_service = MilvusService()
    return _milvus_service

