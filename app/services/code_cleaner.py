"""
代码清洗服务 - 过滤和优化代码片段
"""

import re
from typing import List, Dict, Optional


class CodeCleaner:
    """代码清洗器，用于过滤和优化代码片段"""
    
    def __init__(
        self,
        min_lines: int = 5,
        max_lines: int = 200,
        min_comment_ratio: float = 0.5
    ):
        """
        初始化代码清洗器
        
        Args:
            min_lines: 最小代码行数
            max_lines: 最大代码行数
            min_comment_ratio: 最大注释比例（超过此比例的代码将被过滤）
        """
        self.min_lines = min_lines
        self.max_lines = max_lines
        self.min_comment_ratio = min_comment_ratio
    
    def clean_code_snippet(self, code: str) -> Optional[str]:
        """
        清洗单个代码片段
        
        Args:
            code: 原始代码
        
        Returns:
            清洗后的代码，如果不符合要求则返回None
        """
        if not code or not code.strip():
            return None
        
        # 移除前后空白
        code = code.strip()
        
        # 检查代码行数
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        if len(non_empty_lines) < self.min_lines:
            return None
        
        if len(lines) > self.max_lines:
            return None
        
        # 检查注释比例
        comment_count = sum(1 for line in lines if self._is_comment_line(line))
        comment_ratio = comment_count / len(lines) if lines else 0
        
        if comment_ratio > self.min_comment_ratio:
            return None
        
        # 检查代码完整性（简单检查：是否有语法错误标记）
        if self._has_syntax_errors(code):
            return None
        
        return code
    
    def _is_comment_line(self, line: str) -> bool:
        """判断是否为注释行"""
        stripped = line.strip()
        # Python注释
        if stripped.startswith('#'):
            return True
        # Java/C++单行注释
        if stripped.startswith('//'):
            return True
        # Java/C++多行注释开始/结束
        if stripped.startswith('/*') or stripped.endswith('*/'):
            return True
        # 空行不算注释
        if not stripped:
            return False
        return False
    
    def _has_syntax_errors(self, code: str) -> bool:
        """简单检查是否有明显的语法错误"""
        # 检查括号是否匹配
        if not self._check_brackets(code):
            return True
        
        # 检查是否有明显的错误标记
        error_patterns = [
            r'\.\.\.',  # Python省略号（可能表示未完成）
            r'TODO.*FIXME',  # TODO/FIXME标记
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return True
        
        return False
    
    def _check_brackets(self, code: str) -> bool:
        """检查括号是否匹配"""
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []
        
        in_string = False
        string_char = None
        
        for char in code:
            # 处理字符串
            if char in ('"', "'") and (not stack or stack[-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
                continue
            
            if in_string:
                continue
            
            # 处理括号
            if char in brackets:
                stack.append(char)
            elif char in brackets.values():
                if not stack:
                    return False
                opening = stack.pop()
                if brackets[opening] != char:
                    return False
        
        return len(stack) == 0
    
    def remove_duplicates(self, code_snippets: List[Dict]) -> List[Dict]:
        """
        去除重复的代码片段
        
        Args:
            code_snippets: 代码片段列表
        
        Returns:
            去重后的代码片段列表
        """
        seen = set()
        unique_snippets = []
        
        for snippet in code_snippets:
            code = snippet.get('code', '')
            # 使用代码的hash作为唯一标识
            code_hash = hash(code.strip())
            
            if code_hash not in seen:
                seen.add(code_hash)
                unique_snippets.append(snippet)
        
        return unique_snippets
    
    def extract_dependencies(self, code: str, language: str) -> List[str]:
        """
        提取代码依赖
        
        Args:
            code: 代码文本
            language: 编程语言
        
        Returns:
            依赖库列表
        """
        dependencies = []
        
        if language == 'python':
            # Python import语句
            import_pattern = r'^(?:from\s+(\S+)\s+)?import\s+(\S+)'
            for line in code.split('\n'):
                match = re.match(import_pattern, line.strip())
                if match:
                    if match.group(1):  # from ... import
                        dependencies.append(match.group(1))
                    else:  # import ...
                        dependencies.append(match.group(2).split('.')[0])
        
        elif language == 'java':
            # Java import语句
            import_pattern = r'^import\s+(?:static\s+)?([\w.]+)'
            for line in code.split('\n'):
                match = re.match(import_pattern, line.strip())
                if match:
                    dependencies.append(match.group(1))
        
        elif language == 'cpp':
            # C++ include语句
            include_pattern = r'^#include\s+[<"]([\w/]+)[>"]'
            for line in code.split('\n'):
                match = re.match(include_pattern, line.strip())
                if match:
                    dependencies.append(match.group(1))
        
        # 去重并排序
        return sorted(list(set(dependencies)))


# 全局实例
_code_cleaner: Optional[CodeCleaner] = None


def get_code_cleaner() -> CodeCleaner:
    """获取代码清洗器实例（单例模式）"""
    global _code_cleaner
    if _code_cleaner is None:
        _code_cleaner = CodeCleaner()
    return _code_cleaner

