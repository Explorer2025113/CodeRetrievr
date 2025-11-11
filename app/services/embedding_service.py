"""
代码嵌入服务 - 将代码片段转为向量
"""

import os
from typing import List, Optional
import numpy as np
from app.core.config import settings

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False
    SentenceTransformer = None


class EmbeddingService:
    """代码嵌入服务，用于将代码文本转换为向量"""
    
    def __init__(self):
        """初始化嵌入服务"""
        if not HAS_SENTENCE_TRANSFORMERS:
            raise ImportError("sentence-transformers未安装，请运行: pip install sentence-transformers")
        
        model_name = settings.EMBEDDING_MODEL
        device = settings.EMBEDDING_DEVICE
        
        # 检查CUDA是否可用，如果不可用则使用CPU
        try:
            import torch
            if device == "cuda" and not torch.cuda.is_available():
                print("[!] CUDA不可用，自动切换到CPU")
                device = "cpu"
        except ImportError:
            device = "cpu"
        
        print(f"加载嵌入模型: {model_name} (设备: {device})")
        try:
            self.model = SentenceTransformer(model_name, device=device)
            self.dimension = self.model.get_sentence_embedding_dimension()
            print(f"✅ 模型加载成功，向量维度: {self.dimension}")
        except Exception as e:
            raise Exception(f"加载嵌入模型失败: {str(e)}")
    
    def encode_code(self, code: str) -> np.ndarray:
        """
        将代码文本编码为向量
        
        Args:
            code: 代码文本
        
        Returns:
            向量（numpy数组）
        """
        try:
            # 使用模型编码
            vector = self.model.encode(code, convert_to_numpy=True)
            return vector
        except Exception as e:
            raise Exception(f"编码代码失败: {str(e)}")
    
    def encode_batch(self, codes: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """
        批量编码代码
        
        Args:
            codes: 代码文本列表
            batch_size: 批处理大小
        
        Returns:
            向量列表
        """
        try:
            vectors = self.model.encode(
                codes,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=True
            )
            return [vector for vector in vectors]
        except Exception as e:
            raise Exception(f"批量编码失败: {str(e)}")
    
    def get_dimension(self) -> int:
        """获取向量维度"""
        return self.dimension


# 全局实例
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """获取嵌入服务实例（单例模式）"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

