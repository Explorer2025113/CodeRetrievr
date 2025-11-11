#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试代码采集功能 - 只采集少量文件用于验证
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.github_service import get_github_service
from app.services.code_parser import get_code_parser
from app.services.code_cleaner import get_code_cleaner


def test_collect():
    """测试采集功能"""
    print("=" * 60)
    print("测试代码采集功能")
    print("=" * 60)
    
    # 初始化服务
    print("\n1. 初始化服务...")
    try:
        github = get_github_service()
        print("✅ GitHub服务初始化成功")
    except Exception as e:
        print(f"❌ GitHub服务初始化失败: {e}")
        return
    
    try:
        parser = get_code_parser()
        print("✅ 代码解析器初始化成功")
        print(f"   支持的语言: {list(parser.parsers.keys())}")
    except Exception as e:
        print(f"❌ 代码解析器初始化失败: {e}")
        return
    
    try:
        cleaner = get_code_cleaner()
        print("✅ 代码清洗器初始化成功")
    except Exception as e:
        print(f"❌ 代码清洗器初始化失败: {e}")
        return
    
    # 测试获取仓库
    print("\n2. 测试获取仓库...")
    try:
        repo = github.github.get_repo("tiangolo/fastapi")
        repo_info = github.get_repository_info(repo)
        print(f"✅ 获取仓库成功: {repo_info['full_name']}")
        print(f"   描述: {repo_info['description']}")
        print(f"   Stars: {repo_info['stars']}")
    except Exception as e:
        print(f"❌ 获取仓库失败: {e}")
        return
    
    # 测试获取文件（只获取前5个）
    print("\n3. 测试获取文件（限制5个）...")
    try:
        files = github.get_repository_files(
            repo,
            file_extensions=['.py']
        )
        print(f"✅ 找到 {len(files)} 个Python文件")
        
        # 只处理前5个文件
        test_files = files[:5]
        print(f"   测试处理前 {len(test_files)} 个文件...")
        
        total_snippets = 0
        for i, file in enumerate(test_files, 1):
            print(f"\n   文件 {i}/{len(test_files)}: {file.path}")
            
            # 获取文件内容
            content = github.get_file_content(file)
            if not content:
                print("     ⚠️  无法获取内容，跳过")
                continue
            
            # 解析代码
            functions = parser.extract_functions(content, "python")
            classes = parser.extract_classes(content, "python")
            
            print(f"     找到 {len(functions)} 个函数, {len(classes)} 个类")
            
            # 清洗代码
            cleaned_count = 0
            for func in functions:
                cleaned = cleaner.clean_code_snippet(func['code'])
                if cleaned:
                    cleaned_count += 1
                    total_snippets += 1
            
            for cls in classes:
                cleaned = cleaner.clean_code_snippet(cls['code'])
                if cleaned:
                    cleaned_count += 1
                    total_snippets += 1
            
            print(f"     通过清洗: {cleaned_count} 个片段")
        
        print(f"\n✅ 测试完成！共获得 {total_snippets} 个代码片段")
        print("\n💡 提示: 完整采集请使用 scripts/collect_code.py")
        
    except Exception as e:
        print(f"❌ 处理文件失败: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == '__main__':
    test_collect()

