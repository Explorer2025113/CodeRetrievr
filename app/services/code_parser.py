"""
代码解析服务 - 使用tree-sitter提取代码片段
"""

import os
from typing import List, Dict, Optional
from pathlib import Path

try:
    import tree_sitter
    from tree_sitter import Language, Parser
    HAS_TREE_SITTER = True
except ImportError:
    tree_sitter = None
    Language = None
    Parser = None
    HAS_TREE_SITTER = False


class CodeParser:
    """代码解析器，用于提取函数、类等代码片段"""
    
    def __init__(self):
        """初始化代码解析器"""
        if not HAS_TREE_SITTER:
            raise ImportError("tree-sitter未安装，请运行: pip install tree-sitter")
        
        self.parsers = {}
        self._init_parsers()
    
    def _init_parsers(self):
        """初始化各语言的解析器"""
        # 注意：tree-sitter语言库需要先编译
        # 这里使用已安装的语言库
        try:
            # Python
            try:
                from tree_sitter_python import language as python_language_func
                # tree-sitter 0.25+ API: 需要将language函数的结果包装为Language对象
                python_lang = Language(python_language_func())
                parser = Parser(python_lang)
                self.parsers['python'] = parser
            except (ImportError, AttributeError, TypeError) as e:
                print(f"警告: tree-sitter-python初始化失败: {e}")
            
            # Java
            try:
                from tree_sitter_java import language as java_language_func
                java_lang = Language(java_language_func())
                parser = Parser(java_lang)
                self.parsers['java'] = parser
            except (ImportError, AttributeError, TypeError) as e:
                print(f"警告: tree-sitter-java初始化失败: {e}")
            
            # C++
            try:
                from tree_sitter_cpp import language as cpp_language_func
                cpp_lang = Language(cpp_language_func())
                parser = Parser(cpp_lang)
                self.parsers['cpp'] = parser
            except (ImportError, AttributeError, TypeError) as e:
                print(f"警告: tree-sitter-cpp初始化失败: {e}")
        
        except Exception as e:
            print(f"初始化解析器失败: {e}")
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """
        根据文件扩展名检测编程语言
        
        Args:
            file_path: 文件路径
        
        Returns:
            语言名称（python, java, cpp等）
        """
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c': 'cpp',
            '.h': 'cpp',
            '.hpp': 'cpp',
        }
        return language_map.get(ext)
    
    def extract_functions(self, code: str, language: str) -> List[Dict]:
        """
        提取函数定义
        
        Args:
            code: 代码文本
            language: 编程语言
        
        Returns:
            函数列表，每个函数包含：name, code, start_line, end_line
        """
        if language not in self.parsers:
            return []
        
        parser = self.parsers[language]
        tree = parser.parse(bytes(code, 'utf8'))
        
        functions = []
        
        if language == 'python':
            functions = self._extract_python_functions(tree, code)
        elif language == 'java':
            functions = self._extract_java_functions(tree, code)
        elif language == 'cpp':
            functions = self._extract_cpp_functions(tree, code)
        
        return functions
    
    def extract_classes(self, code: str, language: str) -> List[Dict]:
        """
        提取类定义
        
        Args:
            code: 代码文本
            language: 编程语言
        
        Returns:
            类列表，每个类包含：name, code, start_line, end_line
        """
        if language not in self.parsers:
            return []
        
        parser = self.parsers[language]
        tree = parser.parse(bytes(code, 'utf8'))
        
        classes = []
        
        if language == 'python':
            classes = self._extract_python_classes(tree, code)
        elif language == 'java':
            classes = self._extract_java_classes(tree, code)
        elif language == 'cpp':
            classes = self._extract_cpp_classes(tree, code)
        
        return classes
    
    def _extract_python_functions(self, tree, code: str) -> List[Dict]:
        """提取Python函数"""
        functions = []
        code_lines = code.split('\n')
        
        def traverse(node):
            if node.type == 'function_definition':
                name_node = None
                for child in node.children:
                    if child.type == 'identifier':
                        name_node = child
                        break
                
                if name_node:
                    start_line = node.start_point[0]
                    end_line = node.end_point[0]
                    func_code = '\n'.join(code_lines[start_line:end_line + 1])
                    
                    functions.append({
                        'name': name_node.text.decode('utf8'),
                        'code': func_code,
                        'start_line': start_line + 1,  # 1-based
                        'end_line': end_line + 1,
                    })
            
            for child in node.children:
                traverse(child)
        
        traverse(tree.root_node)
        return functions
    
    def _extract_python_classes(self, tree, code: str) -> List[Dict]:
        """提取Python类"""
        classes = []
        code_lines = code.split('\n')
        
        def traverse(node):
            if node.type == 'class_definition':
                name_node = None
                for child in node.children:
                    if child.type == 'identifier':
                        name_node = child
                        break
                
                if name_node:
                    start_line = node.start_point[0]
                    end_line = node.end_point[0]
                    class_code = '\n'.join(code_lines[start_line:end_line + 1])
                    
                    classes.append({
                        'name': name_node.text.decode('utf8'),
                        'code': class_code,
                        'start_line': start_line + 1,
                        'end_line': end_line + 1,
                    })
            
            for child in node.children:
                traverse(child)
        
        traverse(tree.root_node)
        return classes
    
    def _extract_java_functions(self, tree, code: str) -> List[Dict]:
        """提取Java方法"""
        functions = []
        code_lines = code.split('\n')
        
        def traverse(node):
            if node.type == 'method_declaration':
                name_node = None
                for child in node.children:
                    if child.type == 'identifier':
                        name_node = child
                        break
                
                if name_node:
                    start_line = node.start_point[0]
                    end_line = node.end_point[0]
                    func_code = '\n'.join(code_lines[start_line:end_line + 1])
                    
                    functions.append({
                        'name': name_node.text.decode('utf8'),
                        'code': func_code,
                        'start_line': start_line + 1,
                        'end_line': end_line + 1,
                    })
            
            for child in node.children:
                traverse(child)
        
        traverse(tree.root_node)
        return functions
    
    def _extract_java_classes(self, tree, code: str) -> List[Dict]:
        """提取Java类"""
        classes = []
        code_lines = code.split('\n')
        
        def traverse(node):
            if node.type == 'class_declaration':
                name_node = None
                for child in node.children:
                    if child.type == 'identifier':
                        name_node = child
                        break
                
                if name_node:
                    start_line = node.start_point[0]
                    end_line = node.end_point[0]
                    class_code = '\n'.join(code_lines[start_line:end_line + 1])
                    
                    classes.append({
                        'name': name_node.text.decode('utf8'),
                        'code': class_code,
                        'start_line': start_line + 1,
                        'end_line': end_line + 1,
                    })
            
            for child in node.children:
                traverse(child)
        
        traverse(tree.root_node)
        return classes
    
    def _extract_cpp_functions(self, tree, code: str) -> List[Dict]:
        """提取C++函数"""
        functions = []
        code_lines = code.split('\n')
        
        def traverse(node):
            if node.type == 'function_definition':
                name_node = None
                for child in node.children:
                    if child.type == 'function_declarator':
                        for grandchild in child.children:
                            if grandchild.type == 'identifier':
                                name_node = grandchild
                                break
                        break
                
                if name_node:
                    start_line = node.start_point[0]
                    end_line = node.end_point[0]
                    func_code = '\n'.join(code_lines[start_line:end_line + 1])
                    
                    functions.append({
                        'name': name_node.text.decode('utf8'),
                        'code': func_code,
                        'start_line': start_line + 1,
                        'end_line': end_line + 1,
                    })
            
            for child in node.children:
                traverse(child)
        
        traverse(tree.root_node)
        return functions
    
    def _extract_cpp_classes(self, tree, code: str) -> List[Dict]:
        """提取C++类"""
        classes = []
        code_lines = code.split('\n')
        
        def traverse(node):
            if node.type == 'class_specifier':
                name_node = None
                for child in node.children:
                    if child.type == 'type_identifier':
                        name_node = child
                        break
                
                if name_node:
                    start_line = node.start_point[0]
                    end_line = node.end_point[0]
                    class_code = '\n'.join(code_lines[start_line:end_line + 1])
                    
                    classes.append({
                        'name': name_node.text.decode('utf8'),
                        'code': class_code,
                        'start_line': start_line + 1,
                        'end_line': end_line + 1,
                    })
            
            for child in node.children:
                traverse(child)
        
        traverse(tree.root_node)
        return classes


# 全局实例
_code_parser: Optional[CodeParser] = None


def get_code_parser() -> CodeParser:
    """获取代码解析器实例（单例模式）"""
    global _code_parser
    if _code_parser is None:
        _code_parser = CodeParser()
    return _code_parser

