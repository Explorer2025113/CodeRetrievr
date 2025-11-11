#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码采集脚本
从GitHub采集开源代码并提取代码片段
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.github_service import get_github_service
from app.services.code_parser import get_code_parser
from app.services.code_cleaner import get_code_cleaner
from app.core.config import settings


def collect_code_from_repo(
    repo_name: str,
    language: str = "python",
    output_dir: Optional[str] = None
) -> List[Dict]:
    """
    从指定仓库采集代码
    
    Args:
        repo_name: 仓库名称（格式：owner/repo）
        language: 编程语言
        output_dir: 输出目录
    
    Returns:
        代码片段列表
    """
    github_service = get_github_service()
    code_parser = get_code_parser()
    code_cleaner = get_code_cleaner()
    
    # 获取仓库
    try:
        repo = github_service.github.get_repo(repo_name)
        repo_info = github_service.get_repository_info(repo)
        print(f"采集仓库: {repo_info['full_name']}")
        print(f"描述: {repo_info['description']}")
        print(f"Stars: {repo_info['stars']}")
    except Exception as e:
        print(f"获取仓库失败: {e}")
        return []
    
    # 确定文件扩展名
    file_extensions = {
        'python': ['.py'],
        'java': ['.java'],
        'cpp': ['.cpp', '.cc', '.cxx', '.h', '.hpp'],
    }.get(language.lower(), ['.py'])
    
    # 获取文件列表
    print("获取文件列表...")
    files = github_service.get_repository_files(
        repo,
        file_extensions=file_extensions
    )
    print(f"找到 {len(files)} 个文件")
    
    # 提取代码片段
    all_snippets = []
    
    for i, file in enumerate(files, 1):
        print(f"处理文件 {i}/{len(files)}: {file.path}")
        
        # 获取文件内容
        content = github_service.get_file_content(file)
        if not content:
            continue
        
        # 解析代码
        functions = code_parser.extract_functions(content, language)
        classes = code_parser.extract_classes(content, language)
        
        # 清洗代码
        for func in functions:
            cleaned = code_cleaner.clean_code_snippet(func['code'])
            if cleaned:
                func['code'] = cleaned
                func['type'] = 'function'
                func['file_path'] = file.path
                func['repo_url'] = repo_info['url']
                func['repo_name'] = repo_info['full_name']
                func['language'] = language
                func['dependencies'] = code_cleaner.extract_dependencies(
                    cleaned, language
                )
                all_snippets.append(func)
        
        for cls in classes:
            cleaned = code_cleaner.clean_code_snippet(cls['code'])
            if cleaned:
                cls['code'] = cleaned
                cls['type'] = 'class'
                cls['file_path'] = file.path
                cls['repo_url'] = repo_info['url']
                cls['repo_name'] = repo_info['full_name']
                cls['language'] = language
                cls['dependencies'] = code_cleaner.extract_dependencies(
                    cleaned, language
                )
                all_snippets.append(cls)
    
    # 去重
    print(f"去重前: {len(all_snippets)} 个片段")
    all_snippets = code_cleaner.remove_duplicates(all_snippets)
    print(f"去重后: {len(all_snippets)} 个片段")
    
    # 保存结果
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_path / f"code_snippets_{repo_name.replace('/', '_')}_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_snippets, f, ensure_ascii=False, indent=2)
        
        print(f"结果已保存到: {output_file}")
    
    return all_snippets


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='从GitHub采集代码')
    parser.add_argument('repo', help='仓库名称（格式：owner/repo）')
    parser.add_argument('--language', '-l', default='python',
                       choices=['python', 'java', 'cpp'],
                       help='编程语言')
    parser.add_argument('--output', '-o',
                       default=settings.CODE_SNIPPETS_DIR,
                       help='输出目录')
    
    args = parser.parse_args()
    
    try:
        snippets = collect_code_from_repo(
            args.repo,
            args.language,
            args.output
        )
        
        print(f"\n采集完成！共获得 {len(snippets)} 个代码片段")
        
    except Exception as e:
        print(f"采集失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

