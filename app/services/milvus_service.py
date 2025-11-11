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
            
            # 先加载集合才能获取实体数量
            try:
                collection.load()
            except:
                pass
            
            # 检查集合中是否已有数据
            try:
                num_entities = collection.num_entities
                if num_entities > 0:
                    print(f"⚠️  警告：集合中已有 {num_entities} 条数据")
                    print(f"⚠️  如果数据类型不匹配，可能会导致插入失败")
                    print(f"⚠️  建议：运行 'python scripts/reset_milvus_collection.py' 重置集合")
                    print(f"⚠️  或者：手动删除集合并重新运行脚本")
            except Exception as e:
                print(f"⚠️  警告：无法获取集合实体数量: {e}")
            
            # 验证schema是否匹配（简化检查，避免复杂的属性访问）
            try:
                schema = collection.schema
                # 检查是否有vector字段
                has_vector_field = any(field.name == "vector" for field in schema.fields)
                if not has_vector_field:
                    print(f"⚠️  警告：集合中未找到vector字段，schema可能不匹配")
                    print(f"⚠️  建议：删除集合并重新创建")
            except Exception as e:
                print(f"⚠️  警告：无法验证schema: {e}")
            
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
        
        # 辅助函数：确保值为字符串且不超过长度限制
        def ensure_string(value, default="", max_length=None):
            """确保值为字符串类型，处理None值，并限制长度"""
            # 处理None值
            if value is None:
                value = default
            
            # 处理其他非字符串类型（包括int, float, bool, list, dict等）
            if not isinstance(value, str):
                # 如果是bytes，先解码
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-8')
                    except:
                        value = str(value)
                # 如果是其他类型，转换为字符串
                else:
                    value = str(value)
            
            # 确保是字符串类型
            if not isinstance(value, str):
                value = str(value)
            
            # 如果超过最大长度，截断
            if max_length and len(value) > max_length:
                value = value[:max_length]
            
            return value
        
        # 辅助函数：确保向量转换为float类型的列表
        def ensure_float_vector(vector):
            """确保向量是float类型的列表（扁平化处理）"""
            # 先转换为numpy数组以便统一处理
            if isinstance(vector, np.ndarray):
                # 如果是多维数组，先展平
                if vector.ndim > 1:
                    vector = vector.flatten()
                # 确保是float32类型
                vector = vector.astype(np.float32)
            elif isinstance(vector, list):
                # 如果是列表，先转换为numpy数组
                vector = np.array(vector, dtype=np.float32)
                # 如果是多维，展平
                if vector.ndim > 1:
                    vector = vector.flatten()
            else:
                # 其他类型，尝试转换
                vector = np.array(list(vector), dtype=np.float32)
                if vector.ndim > 1:
                    vector = vector.flatten()
            
            # 转换为Python列表（确保是float类型，不是numpy类型）
            result = vector.tolist()
            
            # 双重检查：确保所有元素都是Python float类型
            return [float(x) for x in result]
        
        # 准备数据（确保所有值都是字符串类型，None转换为空字符串）
        # 先转换所有向量，确保格式一致
        converted_vectors = []
        for i, vector in enumerate(vectors):
            try:
                converted_vec = ensure_float_vector(vector)
                # 验证维度
                if len(converted_vec) != self.dimension:
                    raise ValueError(f"向量 {i} 维度不匹配: 期望 {self.dimension}, 实际 {len(converted_vec)}")
                converted_vectors.append(converted_vec)
            except Exception as e:
                raise ValueError(f"转换向量 {i} 失败: {str(e)}")
        
        data = {
            "code_id": [ensure_string(snippet.get("code_id"), f"snippet_{i}", 255) for i, snippet in enumerate(code_snippets)],
            "code": [ensure_string(snippet.get("code"), "", 65535) for snippet in code_snippets],
            "name": [ensure_string(snippet.get("name"), "", 255) for snippet in code_snippets],
            "type": [ensure_string(snippet.get("type"), "", 50) for snippet in code_snippets],
            "language": [ensure_string(snippet.get("language"), "", 50) for snippet in code_snippets],
            "file_path": [ensure_string(snippet.get("file_path"), "", 512) for snippet in code_snippets],
            "repo_name": [ensure_string(snippet.get("repo_name"), "", 255) for snippet in code_snippets],
            "repo_url": [ensure_string(snippet.get("repo_url"), "", 512) for snippet in code_snippets],
            "vector": converted_vectors,
        }
        
        # 验证数据一致性
        try:
            # 检查向量格式一致性
            if len(converted_vectors) > 0:
                first_vec_len = len(converted_vectors[0])
                first_vec_type = type(converted_vectors[0][0]) if len(converted_vectors[0]) > 0 else None
                for i, vec in enumerate(converted_vectors):
                    if len(vec) != first_vec_len:
                        raise ValueError(f"向量 {i} 长度不一致: 第一个向量长度 {first_vec_len}, 当前向量长度 {len(vec)}")
                    if len(vec) > 0:
                        vec_type = type(vec[0])
                        if vec_type != first_vec_type:
                            raise ValueError(f"向量 {i} 元素类型不一致: 第一个向量元素类型 {first_vec_type}, 当前向量元素类型 {vec_type}")
            
            # 检查数据长度一致性
            expected_len = len(code_snippets)
            for field_name, field_data in data.items():
                if len(field_data) != expected_len:
                    raise ValueError(f"字段 {field_name} 数据长度不匹配: 期望 {expected_len}, 实际 {len(field_data)}")
            
            # 检查字符串字段的类型一致性
            string_fields = ["code_id", "code", "name", "type", "language", "file_path", "repo_name", "repo_url"]
            for field_name in string_fields:
                if field_name in data:
                    field_data = data[field_name]
                    # 检查前10条数据的类型
                    for i, value in enumerate(field_data[:10]):
                        if not isinstance(value, str):
                            raise ValueError(f"字段 {field_name} 索引 {i} 的类型不是字符串: {type(value).__name__} = {repr(value)[:50]}")
        except Exception as e:
            raise Exception(f"数据验证失败: {str(e)}")
        
        # 插入数据
        try:
            # 进一步校验：检查向量中是否包含 NaN / Inf
            for i, vec in enumerate(converted_vectors):
                for j, x in enumerate(vec):
                    if x != x:  # NaN 检查
                        raise ValueError(f"向量 {i} 的第 {j} 个元素为 NaN")
                    if x == float("inf") or x == float("-inf"):
                        raise ValueError(f"向量 {i} 的第 {j} 个元素为 Inf")

            # 使用“行模式”插入，避免列模式与 row_insert 的解析不一致
            rows = []
            for i, snippet in enumerate(code_snippets):
                rows.append({
                    "code_id": data["code_id"][i],
                    "code": data["code"][i],
                    "name": data["name"][i],
                    "type": data["type"][i],
                    "language": data["language"][i],
                    "file_path": data["file_path"][i],
                    "repo_name": data["repo_name"][i],
                    "repo_url": data["repo_url"][i],
                    "vector": converted_vectors[i],
                })

            insert_result = self.collection.insert(rows)
            # 刷新集合
            self.collection.flush()
            print(f"✅ 成功插入 {len(code_snippets)} 个代码片段")
            return insert_result.primary_keys
        except Exception as e:
            # 提供更详细的错误信息
            error_msg = str(e)
            error_str = str(e).lower()
            
            # 检查是否是数据类型不匹配错误
            if "datatype" in error_str or "type" in error_str or "not match" in error_str:
                # 检查集合中是否已有数据
                try:
                    num_entities = self.collection.num_entities
                    if num_entities > 0:
                        error_msg += f"\n\n⚠️  问题诊断："
                        error_msg += f"\n   - 集合中已有 {num_entities} 条数据"
                        error_msg += f"\n   - 新数据与已有数据的类型可能不匹配"
                        error_msg += f"\n   - 这通常是因为集合中存在旧版本代码插入的数据"
                        error_msg += f"\n\n💡 解决方案："
                        error_msg += f"\n   1. 重置集合（删除所有数据）："
                        error_msg += f"\n      python scripts/reset_milvus_collection.py"
                        error_msg += f"\n   2. 然后重新运行向量化脚本"
                except:
                    pass
            
            # 尝试获取更多调试信息
            try:
                # 检查转换后的向量
                if len(converted_vectors) > 0:
                    converted_dims = [len(v) for v in converted_vectors[:5]]
                    if len(converted_vectors[0]) > 0:
                        converted_elem_types = [type(v[0]).__name__ for v in converted_vectors[:5]]
                        # 检查所有向量的元素类型是否一致
                        all_same_type = all(type(v[0]).__name__ == converted_elem_types[0] for v in converted_vectors if len(v) > 0)
                    else:
                        converted_elem_types = ['N/A'] * min(5, len(converted_vectors))
                        all_same_type = True
                    
                    error_msg += f"\n\n调试信息（转换后向量）："
                    error_msg += f"\n   - 向量数量: {len(converted_vectors)}"
                    error_msg += f"\n   - 前5个向量维度: {converted_dims}"
                    error_msg += f"\n   - 前5个向量元素类型: {converted_elem_types}"
                    error_msg += f"\n   - 所有向量元素类型一致: {all_same_type}"
                    error_msg += f"\n   - 期望维度: {self.dimension}"
                
                # 检查原始向量
                vector_dims = [len(v) if hasattr(v, '__len__') else 'N/A' for v in vectors[:5]]
                vector_types = [type(v).__name__ for v in vectors[:5]]
                
                if len(vectors) > 0 and hasattr(vectors[0], '__len__'):
                    first_vec = vectors[0]
                    if isinstance(first_vec, np.ndarray):
                        elem_type = str(first_vec.dtype)
                        shape = first_vec.shape
                    elif isinstance(first_vec, list) and len(first_vec) > 0:
                        elem_type = type(first_vec[0]).__name__
                        shape = (len(first_vec),)
                    else:
                        elem_type = 'unknown'
                        shape = 'unknown'
                    
                    error_msg += f"\n\n调试信息（原始向量）："
                    error_msg += f"\n   - 前5个向量维度: {vector_dims}"
                    error_msg += f"\n   - 前5个向量类型: {vector_types}"
                    error_msg += f"\n   - 第一个向量元素类型: {elem_type}"
                    error_msg += f"\n   - 第一个向量形状: {shape}"
                
                # 检查字符串字段的类型（重点检查）
                error_msg += f"\n\n字符串字段类型检查（前5条）："
                for field_name in ["code_id", "code", "name", "type", "language", "file_path", "repo_name", "repo_url"]:
                    if field_name in data:
                        field_data = data[field_name]
                        # 检查是否有非字符串类型
                        non_str_indices = [i for i, v in enumerate(field_data[:5]) if not isinstance(v, str)]
                        if non_str_indices:
                            error_msg += f"\n   ⚠️  {field_name}: 发现非字符串类型 (索引: {non_str_indices})"
                            for idx in non_str_indices:
                                error_msg += f"\n      索引 {idx}: {type(field_data[idx]).__name__} = {repr(field_data[idx])[:50]}"
                        else:
                            error_msg += f"\n   ✅ {field_name}: 所有值都是字符串类型"
            except Exception as debug_error:
                error_msg += f"\n   调试信息获取失败: {debug_error}"
            
            raise Exception(f"插入数据失败: {error_msg}")
    
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


# 全局实例
_milvus_service: Optional[MilvusService] = None


def get_milvus_service() -> MilvusService:
    """获取Milvus服务实例（单例模式）"""
    global _milvus_service
    if _milvus_service is None:
        _milvus_service = MilvusService()
    return _milvus_service

