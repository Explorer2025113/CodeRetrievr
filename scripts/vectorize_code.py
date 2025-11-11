#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码向量化脚本
将采集的代码片段转换为向量并存储到Milvus和Neo4j
"""

import sys
import json
import uuid
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.embedding_service import get_embedding_service
from app.services.milvus_service import get_milvus_service
from app.services.neo4j_service import get_neo4j_service
from app.core.config import settings


def load_code_snippets(json_file: str) -> List[Dict]:
    """加载代码片段JSON文件"""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def vectorize_and_store(
    code_snippets: List[Dict],
    batch_size: int = 100
) -> Dict:
    """
    向量化并存储代码片段
    
    Args:
        code_snippets: 代码片段列表
        batch_size: 批处理大小
    
    Returns:
        处理统计信息
    """
    embedding_service = get_embedding_service()
    milvus_service = get_milvus_service()
    neo4j_service = get_neo4j_service()
    
    stats = {
        "total": len(code_snippets),
        "processed": 0,
        "milvus_inserted": 0,
        "neo4j_inserted": 0,
        "errors": 0
    }
    
    # 分批处理
    for i in range(0, len(code_snippets), batch_size):
        batch = code_snippets[i:i + batch_size]
        print(f"\n处理批次 {i//batch_size + 1}/{(len(code_snippets) + batch_size - 1)//batch_size}")
        
        try:
            # 准备代码文本
            code_texts = []
            processed_snippets = []
            
            for snippet in batch:
                # 生成唯一ID
                if "code_id" not in snippet:
                    snippet["code_id"] = str(uuid.uuid4())
                
                # 准备向量化的文本（代码 + 名称 + 类型）
                text = f"{snippet.get('name', '')} {snippet.get('type', '')} {snippet.get('code', '')}"
                code_texts.append(text)
                processed_snippets.append(snippet)
            
            # 批量编码为向量
            print("  编码向量...")
            vectors = embedding_service.encode_batch(code_texts, batch_size=batch_size)
            
            # 插入Milvus
            print("  插入Milvus...")
            milvus_ids = milvus_service.insert_code_snippets(processed_snippets, vectors)
            stats["milvus_inserted"] += len(milvus_ids)
            
            # 插入Neo4j
            print("  插入Neo4j...")
            for j, snippet in enumerate(processed_snippets):
                try:
                    # 创建代码片段节点
                    neo4j_service.create_code_snippet_node(
                        code_id=snippet["code_id"],
                        name=snippet.get("name", ""),
                        code_type=snippet.get("type", ""),
                        language=snippet.get("language", ""),
                        file_path=snippet.get("file_path", ""),
                        repo_name=snippet.get("repo_name", ""),
                        repo_url=snippet.get("repo_url", ""),
                        milvus_id=milvus_ids[j] if j < len(milvus_ids) else None
                    )
                    
                    # 创建语言关系
                    if snippet.get("language"):
                        neo4j_service.create_language_relationship(
                            snippet["code_id"],
                            snippet["language"]
                        )
                    
                    # 创建依赖关系
                    if snippet.get("dependencies"):
                        neo4j_service.create_dependency_relationships(
                            snippet["code_id"],
                            snippet["dependencies"]
                        )
                    
                    stats["neo4j_inserted"] += 1
                
                except Exception as e:
                    print(f"  ⚠️  插入Neo4j失败 {snippet.get('name', 'unknown')}: {e}")
                    stats["errors"] += 1
            
            stats["processed"] += len(batch)
            print(f"  ✅ 批次完成: {len(batch)} 个片段")
        
        except Exception as e:
            print(f"  ❌ 批次处理失败: {e}")
            stats["errors"] += len(batch)
            import traceback
            traceback.print_exc()
    
    return stats


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='向量化代码片段并存储')
    parser.add_argument('json_file', help='代码片段JSON文件路径')
    parser.add_argument('--batch-size', '-b', type=int, default=100,
                       help='批处理大小（默认：100）')
    
    args = parser.parse_args()
    
    # 加载代码片段
    print(f"加载代码片段: {args.json_file}")
    code_snippets = load_code_snippets(args.json_file)
    print(f"共 {len(code_snippets)} 个代码片段")
    
    # 向量化并存储
    try:
        stats = vectorize_and_store(code_snippets, batch_size=args.batch_size)
        
        print("\n" + "=" * 60)
        print("处理完成！")
        print("=" * 60)
        print(f"总计: {stats['total']} 个片段")
        print(f"已处理: {stats['processed']} 个片段")
        print(f"Milvus插入: {stats['milvus_inserted']} 个")
        print(f"Neo4j插入: {stats['neo4j_inserted']} 个")
        print(f"错误: {stats['errors']} 个")
        
        # 显示统计信息
        print("\nMilvus统计:")
        milvus_stats = get_milvus_service().get_collection_stats()
        for key, value in milvus_stats.items():
            print(f"  {key}: {value}")
        
        print("\nNeo4j统计:")
        neo4j_stats = get_neo4j_service().get_statistics()
        for key, value in neo4j_stats.items():
            print(f"  {key}: {value}")
    
    except Exception as e:
        print(f"处理失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

