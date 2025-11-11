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
            if device == "cuda":
                if torch.cuda.is_available():
                    gpu_name = torch.cuda.get_device_name(0)
                    print(f"[OK] CUDA可用，使用GPU加速 (设备: {gpu_name})")
                else:
                    print("[WARNING] CUDA不可用，自动切换到CPU")
                    print("[INFO] 提示：如果您有NVIDIA GPU，请安装CUDA版本的PyTorch：")
                    print("[INFO]   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
                    device = "cpu"
        except ImportError:
            print("[WARNING] PyTorch未安装，使用CPU模式")
            device = "cpu"
        
        print(f"加载嵌入模型: {model_name} (设备: {device})")
        try:
            self.model = SentenceTransformer(model_name, device=device)
            self.dimension = self.model.get_sentence_embedding_dimension()
            print(f"[OK] 模型加载成功，向量维度: {self.dimension}")
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
            # 确保返回的是numpy数组的列表
            # model.encode返回的是2D numpy数组 (shape: [batch_size, dimension])
            if isinstance(vectors, np.ndarray):
                # 如果是2D数组，转换为列表，每个元素是一个1D numpy数组
                # 统一转换为float32类型以确保类型一致
                vectors = vectors.astype(np.float32)
                return [vectors[i] for i in range(len(vectors))]
            elif isinstance(vectors, list):
                # 如果已经是列表，确保每个元素是numpy数组
                return [np.array(v, dtype=np.float32) if not isinstance(v, np.ndarray) else v.astype(np.float32) for v in vectors]
            else:
                # 其他情况，尝试转换
                vectors_array = np.array(vectors, dtype=np.float32)
                return [vectors_array[i] for i in range(len(vectors_array))]
        except RuntimeError as e:
            # 如果CUDA相关错误，尝试切换到CPU
            if "cuda" in str(e).lower() or "CUDA" in str(e):
                import torch
                if torch.cuda.is_available():
                    # CUDA可用但出错，可能是内存不足等问题
                    raise Exception(f"CUDA错误: {str(e)}。请尝试减小batch_size或使用CPU模式")
                else:
                    # CUDA不可用，应该已经在初始化时切换到CPU了
                    raise Exception(f"批量编码失败（CUDA不可用）: {str(e)}")
            raise Exception(f"批量编码失败: {str(e)}")
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

