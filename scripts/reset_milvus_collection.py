#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重置Milvus集合（删除并重新创建）
注意：这会删除所有数据！
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from pymilvus import connections, utility, Collection

def reset_collection():
    """重置Milvus集合"""
    collection_name = settings.MILVUS_COLLECTION_NAME
    
    # 连接到Milvus
    connections.connect(
        alias="default",
        host=settings.MILVUS_HOST,
        port=settings.MILVUS_PORT
    )
    
    # 检查集合是否存在
    if utility.has_collection(collection_name):
        print(f"⚠️  集合 {collection_name} 已存在")
        
        # 获取集合信息
        collection = Collection(collection_name)
        num_entities = collection.num_entities
        print(f"   当前数据量: {num_entities} 条")
        
        # 删除集合
        print(f"   正在删除集合...")
        utility.drop_collection(collection_name)
        print(f"   ✅ 集合已删除")
    else:
        print(f"✅ 集合 {collection_name} 不存在，无需删除")
    
    print(f"\n✅ 集合重置完成！")
    print(f"   现在可以重新运行向量化脚本插入数据")

if __name__ == '__main__':
    print("=" * 60)
    print("重置Milvus集合")
    print("=" * 60)
    print("⚠️  警告：这将删除集合中的所有数据！")
    
    # 确认
    response = input("\n是否继续？(yes/no): ")
    if response.lower() in ['yes', 'y']:
        reset_collection()
    else:
        print("操作已取消")

