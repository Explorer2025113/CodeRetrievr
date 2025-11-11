#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查Milvus集合的Schema和数据
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.milvus_service import get_milvus_service
from pymilvus import utility

def main():
    """检查Milvus集合状态"""
    service = get_milvus_service()
    collection = service.collection
    
    print("=" * 60)
    print("Milvus集合信息")
    print("=" * 60)
    
    # 集合基本信息
    print(f"\n集合名称: {service.collection_name}")
    print(f"实体数量: {collection.num_entities}")
    print(f"向量维度: {service.dimension}")
    
    # Schema信息
    print("\n字段Schema:")
    for field in collection.schema.fields:
        print(f"  - {field.name}: {field.dtype} (max_length: {getattr(field, 'max_length', 'N/A')})")
    
    # 检查是否有数据
    if collection.num_entities > 0:
        print(f"\n⚠️  集合中已有 {collection.num_entities} 条数据")
        print("如果数据类型不匹配，可能需要删除集合重新创建")
        
        # 查询一条数据检查类型
        try:
            results = collection.query(
                expr="id >= 0",
                limit=1,
                output_fields=["code_id", "code", "name", "type", "language"]
            )
            if results:
                print("\n示例数据:")
                for key, value in results[0].items():
                    if key != "vector":
                        print(f"  {key}: {type(value).__name__} = {str(value)[:50]}")
        except Exception as e:
            print(f"\n查询数据失败: {e}")
    else:
        print("\n✅ 集合为空，可以开始插入数据")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()

