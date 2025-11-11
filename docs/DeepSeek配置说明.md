# DeepSeek API 配置说明

## 简介

DeepSeek 是一个高性能的AI大模型服务，提供与OpenAI兼容的API接口。本项目已集成DeepSeek支持，可以作为OpenAI的替代方案。

## 为什么选择DeepSeek？

1. **国内可用**：无需科学上网，访问速度快
2. **价格优惠**：相比OpenAI更经济实惠
3. **代码能力强**：在代码理解和生成方面表现优秀
4. **API兼容**：完全兼容OpenAI API格式，易于集成

## 获取API密钥

### 步骤1：注册账号

1. 访问 https://platform.deepseek.com/
2. 使用手机号或邮箱注册账号
3. 完成邮箱验证

### 步骤2：获取API密钥

1. 登录后进入控制台
2. 点击左侧菜单 "API Keys"
3. 点击 "创建新的API密钥"
4. 复制生成的密钥（格式：`sk-...`）

⚠️ **注意**：API密钥只显示一次，请妥善保存

### 步骤3：充值（如需要）

- DeepSeek提供一定的免费额度
- 超出免费额度后需要充值使用
- 价格：约 ¥0.0014/1K tokens（输入），¥0.0028/1K tokens（输出）

## 配置方法

### 方法1：使用环境变量（推荐）

在 `.env` 文件中添加以下配置：

```env
# DeepSeek配置
LLM_PROVIDER=deepseek
LLM_API_KEY=sk-your-deepseek-api-key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
LLM_MAX_TOKENS=1000
```

### 方法2：在代码中配置

如果需要在代码中直接配置：

```python
from app.core.config import settings

# 修改配置
settings.LLM_PROVIDER = "deepseek"
settings.LLM_API_KEY = "sk-your-api-key"
settings.LLM_BASE_URL = "https://api.deepseek.com"
settings.LLM_MODEL = "deepseek-chat"
```

## 使用示例

### 基本使用

```python
from app.services.llm_service import get_llm_service

# 获取服务实例
llm_service = get_llm_service()

# 生成代码复用说明
instruction = await llm_service.generate_code_reuse_instruction(
    code_snippet="""
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
    """,
    language="python",
    dependencies=[],
    user_query="如何实现快速排序"
)

print(instruction)
```

## 模型说明

### deepseek-chat

- **用途**：通用对话和代码生成
- **特点**：代码理解能力强，适合生成代码说明
- **推荐场景**：代码复用说明生成

### 其他可用模型

DeepSeek可能提供其他模型，可在API文档中查看最新可用模型列表。

## 与OpenAI的对比

| 特性 | DeepSeek | OpenAI |
|------|----------|--------|
| 国内访问 | ✅ 可直接访问 | ❌ 需要科学上网 |
| API格式 | ✅ 兼容OpenAI | ✅ 标准格式 |
| 代码能力 | ✅ 优秀 | ✅ 优秀 |
| 价格 | 💰 更优惠 | 💰 较贵 |
| 响应速度 | ⚡ 快（国内） | ⚡ 中等 |

## 故障排查

### 问题1：API调用失败

**错误信息**：`401 Unauthorized`

**解决方案**：
1. 检查API密钥是否正确
2. 确认API密钥未过期
3. 检查账户余额是否充足

### 问题2：连接超时

**错误信息**：`Connection timeout`

**解决方案**：
1. 检查网络连接
2. 确认 `LLM_BASE_URL` 配置正确
3. 尝试使用代理（如需要）

### 问题3：模型不存在

**错误信息**：`Model not found`

**解决方案**：
1. 确认 `LLM_MODEL` 配置正确（应为 `deepseek-chat`）
2. 查看DeepSeek文档确认最新可用模型

## 成本控制

### 实现缓存机制

为避免重复生成相同代码的说明，建议实现缓存：

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def get_cached_instruction(code_hash: str):
    # 从缓存获取
    pass
```

### 设置使用限额

在DeepSeek控制台可以设置：
- 每日使用限额
- 每月使用限额
- 单次请求token限制

## 迁移指南

### 从OpenAI迁移到DeepSeek

1. **更新环境变量**：
   ```env
   # 旧配置
   OPENAI_API_KEY=sk-...
   
   # 新配置
   LLM_PROVIDER=deepseek
   LLM_API_KEY=sk-...
   LLM_BASE_URL=https://api.deepseek.com
   ```

2. **代码无需修改**：
   - 由于使用兼容的API格式，代码无需修改
   - 只需更新配置即可

3. **测试验证**：
   ```bash
   python scripts/check_environment.py
   ```

## 更多资源

- **DeepSeek官网**：https://www.deepseek.com/
- **API文档**：https://platform.deepseek.com/docs
- **定价信息**：https://platform.deepseek.com/pricing

---

**文档版本**：v1.0  
**创建日期**：2024年  
**最后更新**：2024年

