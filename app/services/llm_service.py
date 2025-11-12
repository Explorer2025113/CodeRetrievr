"""
大模型服务 - 支持DeepSeek和OpenAI
"""

import os
from typing import Optional
from app.core.config import settings

try:
    import openai
except ImportError:
    openai = None


class LLMService:
    """大模型服务类，支持DeepSeek和OpenAI"""
    
    def __init__(self):
        """初始化LLM服务"""
        if openai is None:
            raise ImportError("openai库未安装，请运行: pip install openai")
        
        # 确定使用的提供商
        self.provider = settings.LLM_PROVIDER.lower()
        self.api_key = settings.LLM_API_KEY or settings.OPENAI_API_KEY
        self.model = settings.LLM_MODEL or settings.OPENAI_MODEL
        self.max_tokens = settings.LLM_MAX_TOKENS or settings.OPENAI_MAX_TOKENS
        
        if not self.api_key:
            raise ValueError("未配置LLM_API_KEY或OPENAI_API_KEY")
        
        # 配置客户端
        if self.provider == "deepseek":
            # DeepSeek使用OpenAI兼容的API格式
            base_url = settings.LLM_BASE_URL or "https://api.deepseek.com"
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=base_url
            )
            # 默认使用deepseek-chat模型
            if not settings.LLM_MODEL:
                self.model = "deepseek-chat"
        else:
            # OpenAI使用默认配置
            self.client = openai.OpenAI(api_key=self.api_key)
            if not settings.LLM_MODEL:
                self.model = "gpt-3.5-turbo"
    
    async def generate_code_reuse_instruction(
        self,
        code_snippet: str,
        language: str,
        dependencies: list = None,
        user_query: str = ""
    ) -> str:
        """
        生成代码复用说明
        
        Args:
            code_snippet: 代码片段
            language: 编程语言
            dependencies: 依赖库列表
            user_query: 用户查询
        
        Returns:
            生成的复用说明文本
        """
        # 构建提示词
        prompt = self._build_prompt(
            code_snippet=code_snippet,
            language=language,
            dependencies=dependencies or [],
            user_query=user_query
        )
        
        try:
            # 调用API生成说明
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的代码助手，擅长解释代码的使用方法和注意事项。请使用清晰、结构化的 Markdown 格式输出，确保内容易于阅读和理解。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            # 格式化文本内容
            return self._format_explanation(content)
        
        except Exception as e:
            raise Exception(f"生成复用说明失败: {str(e)}")
    
    def _format_explanation(self, text: str) -> str:
        """
        格式化说明文本，确保格式清晰统一
        
        Args:
            text: 原始文本
            
        Returns:
            格式化后的文本
        """
        if not text:
            return text
        
        lines = text.split('\n')
        formatted_lines = []
        prev_empty = False
        
        for line in lines:
            stripped = line.strip()
            
            # 跳过连续的空行，只保留一个
            if not stripped:
                if not prev_empty:
                    formatted_lines.append('')
                    prev_empty = True
                continue
            
            prev_empty = False
            formatted_lines.append(line)
        
        # 去除开头和结尾的空行
        while formatted_lines and not formatted_lines[0].strip():
            formatted_lines.pop(0)
        while formatted_lines and not formatted_lines[-1].strip():
            formatted_lines.pop()
        
        return '\n'.join(formatted_lines)
    
    def _build_prompt(
        self,
        code_snippet: str,
        language: str,
        dependencies: list,
        user_query: str
    ) -> str:
        """构建提示词"""
        prompt = f"""请为以下{language}代码片段生成详细的复用说明。

代码片段：
```{language}
{code_snippet}
```

"""
        
        if dependencies:
            prompt += f"依赖库：{', '.join(dependencies)}\n\n"
        
        if user_query:
            prompt += f"用户需求：{user_query}\n\n"
        
        prompt += """请使用 Markdown 格式生成包含以下内容的复用说明，要求结构清晰、层次分明：

## 功能描述
简要说明这段代码的主要功能和用途。

## 使用步骤
按步骤说明如何在自己的项目中使用这段代码：
1. 安装依赖（如有）
2. 导入必要的模块
3. 复制代码或创建实例
4. 在项目中使用

## 参数说明
如果有函数、方法或类，详细说明各个参数的含义、类型和是否必填。

## 返回值说明
如果有返回值，说明返回值的类型、结构和含义。

## 注意事项
列出使用时需要注意的重要问题，如：
- 特殊要求
- 常见错误
- 性能考虑
- 兼容性问题

## 使用示例
提供一个完整、可直接运行的代码示例，展示如何使用这段代码。

**要求：**
- 使用中文回答
- 使用 Markdown 格式（标题使用 ##，列表使用 - 或 1.）
- 代码示例使用 ``` 代码块包裹
- 内容准确、简洁、实用
- 每个部分之间用空行分隔"""
        
        return prompt


# 全局实例
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """获取LLM服务实例（单例模式）"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

