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
                        "content": "你是一个专业的代码助手，擅长解释代码的使用方法和注意事项。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            raise Exception(f"生成复用说明失败: {str(e)}")
    
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
        
        prompt += """请生成包含以下内容的复用说明：
1. 功能描述：这段代码的主要功能是什么
2. 使用步骤：如何在自己的项目中使用这段代码
3. 参数说明：如果有函数/方法，说明各个参数的含义
4. 返回值说明：如果有返回值，说明返回值的含义
5. 注意事项：使用时需要注意的问题
6. 使用示例：提供一个简单的使用示例

请用中文回答，格式清晰，分点列出。"""
        
        return prompt


# 全局实例
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """获取LLM服务实例（单例模式）"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

