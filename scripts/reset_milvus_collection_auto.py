#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动重置Milvus集合（非交互式，直接执行）
注意：这会删除所有数据！
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from pymilvus import connections, utility

def reset_collection():
    """重置Milvus集合"""
    collection_name = settings.MILVUS_COLLECTION_NAME
    
    print("=" * 60)
    print("重置Milvus集合")
    print("=" * 60)
    
    try:
        # 连接到Milvus
        connections.connect(
            alias="default",
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT
        )
        print(f"✅ 已连接到Milvus: {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
    except Exception as e:
        print(f"❌ 连接Milvus失败: {e}")
        return False
    
    # 检查集合是否存在
    if utility.has_collection(collection_name):
        print(f"⚠️  集合 {collection_name} 已存在")
        
        try:
            from pymilvus import Collection
            collection = Collection(collection_name)
            collection.load()
            num_entities = collection.num_entities
            print(f"   当前数据量: {num_entities} 条")
        except Exception as e:
            print(f"   无法获取数据量: {e}")
        
        # 删除集合
        try:
            print(f"   正在删除集合...")
            utility.drop_collection(collection_name)
            print(f"   ✅ 集合已删除")
        except Exception as e:
            print(f"   ❌ 删除集合失败: {e}")
            return False
    else:
        print(f"✅ 集合 {collection_name} 不存在，无需删除")
    
    print(f"\n✅ 集合重置完成！")
    print(f"   现在可以重新运行向量化脚本插入数据")
    return True

if __name__ == '__main__':
    success = reset_collection()
    sys.exit(0 if success else 1)

