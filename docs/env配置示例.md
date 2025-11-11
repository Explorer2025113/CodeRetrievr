# .env 配置文件示例和说明

## 快速开始

1. **复制示例文件**：
```bash
cp .env.example .env
```

2. **编辑 .env 文件**，填入必需的配置项

3. **验证配置**：
```bash
python scripts/check_environment.py
```

## 完整配置示例

### 最小配置（必需项）

```env
# 大模型API密钥（DeepSeek推荐）
LLM_PROVIDER=deepseek
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat

# GitHub Token
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Neo4j密码
NEO4J_PASSWORD=your_secure_password_123
```

### 完整配置示例

```env
# ==================== 应用配置 ====================
APP_NAME=CodeRetrievr
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development

# ==================== API配置 ====================
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# ==================== 矢量数据库（本地Milvus） ====================
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=code_snippets
MILVUS_DIMENSION=768

# ==================== 知识图谱（Neo4j） ====================
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=MySecurePassword123!

# ==================== 大模型API（DeepSeek） ====================
LLM_PROVIDER=deepseek
LLM_API_KEY=sk-1234567890abcdef1234567890abcdef
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
LLM_MAX_TOKENS=1000

# ==================== GitHub API ====================
GITHUB_TOKEN=ghp_1234567890abcdef1234567890abcdef12345678
GITHUB_RATE_LIMIT=5000

# ==================== 代码嵌入模型 ====================
EMBEDDING_MODEL=microsoft/codebert-base
EMBEDDING_DEVICE=cpu

# ==================== 数据存储 ====================
DATA_DIR=./data
CODE_SNIPPETS_DIR=./data/code_snippets
METADATA_DIR=./data/metadata

# ==================== 日志 ====================
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log

# ==================== 安全 ====================
SECRET_KEY=my-super-secret-key-change-in-production-12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ==================== 部署模式 ====================
DEPLOYMENT_MODE=local
```

## 配置项说明

### 必需配置（必须填写）

| 配置项 | 说明 | 示例值 | 获取方式 |
|--------|------|--------|----------|
| `LLM_API_KEY` | DeepSeek或OpenAI API密钥 | `sk-xxx...` | [DeepSeek](https://platform.deepseek.com/api_keys) |
| `GITHUB_TOKEN` | GitHub Personal Access Token | `ghp_xxx...` | [GitHub Settings](https://github.com/settings/tokens) |
| `NEO4J_PASSWORD` | Neo4j数据库密码 | `your_password` | 在docker-compose.yml中设置 |

### 推荐配置（建议填写）

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `LLM_PROVIDER` | 大模型提供商 | `deepseek` |
| `LLM_MODEL` | 使用的模型 | `deepseek-chat` |
| `MILVUS_HOST` | Milvus主机地址 | `localhost` |
| `MILVUS_PORT` | Milvus端口 | `19530` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

### 可选配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `PINECONE_API_KEY` | Pinecone API密钥（云端部署） | - |
| `REDIS_HOST` | Redis主机（缓存） | - |
| `SECRET_KEY` | JWT密钥（用户认证） | - |

## 不同场景的配置

### 场景1：本地开发（推荐）

```env
DEPLOYMENT_MODE=local
LLM_PROVIDER=deepseek
LLM_API_KEY=sk-your-deepseek-key
MILVUS_HOST=localhost
NEO4J_PASSWORD=local_dev_password
GITHUB_TOKEN=ghp_your_token
```

### 场景2：云端部署

```env
DEPLOYMENT_MODE=cloud
LLM_PROVIDER=deepseek
LLM_API_KEY=sk-your-deepseek-key
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=us-west1-gcp
NEO4J_PASSWORD=cloud_secure_password
GITHUB_TOKEN=ghp_your_token
```

### 场景3：使用OpenAI（需要科学上网）

```env
LLM_PROVIDER=openai
LLM_API_KEY=sk-your-openai-key
LLM_MODEL=gpt-3.5-turbo
# LLM_BASE_URL 留空，使用OpenAI默认地址
```

## 安全注意事项

⚠️ **重要**：

1. **不要提交 .env 文件到Git**
   - `.env` 已在 `.gitignore` 中
   - 只提交 `.env.example` 作为模板

2. **生产环境必须修改**：
   - `SECRET_KEY` - 使用随机生成的强密码
   - `NEO4J_PASSWORD` - 使用强密码
   - 所有API密钥 - 定期轮换

3. **密钥管理**：
   - 不要在代码中硬编码密钥
   - 使用环境变量或密钥管理服务
   - 定期检查密钥权限

## 验证配置

运行环境检查脚本：

```bash
python scripts/check_environment.py
```

应该看到：
- ✅ 大模型API密钥: 已设置
- ✅ GitHub Token: 已设置
- ✅ Neo4j密码: 已设置

## 常见问题

### Q1: 如何生成强密码？

```bash
# Linux/macOS
openssl rand -base64 32

# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Q2: 如何测试API密钥是否有效？

```python
# 测试DeepSeek API
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.choices[0].message.content)
```

### Q3: 配置不生效？

1. 确认 `.env` 文件在项目根目录
2. 确认环境变量名称正确（区分大小写）
3. 重启应用服务
4. 检查是否有语法错误（如缺少引号）

---

**文档版本**：v1.0  
**创建日期**：2024年  
**最后更新**：2024年

