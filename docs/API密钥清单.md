# CodeRetrievr API密钥清单

## 密钥管理说明

⚠️ **安全提示**：
- 所有API密钥应存储在 `.env` 文件中，**不要**提交到Git仓库
- 定期轮换密钥
- 使用环境变量而非硬编码
- 生产环境使用密钥管理服务（如AWS Secrets Manager）

## 必需密钥清单

### 1. 大模型API密钥（DeepSeek / OpenAI）

**用途**：生成代码复用说明

#### 方案A：DeepSeek API（推荐，国内可用）

**获取方式**：
1. 访问 https://platform.deepseek.com/
2. 登录/注册账号
3. 进入 API Keys 页面
4. 创建新的API密钥
5. 复制密钥

**配置位置**：`.env` 文件
```env
LLM_PROVIDER=deepseek
LLM_API_KEY=sk-...
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

**成本参考**：
- DeepSeek Chat: ¥0.0014/1K tokens (输入), ¥0.0028/1K tokens (输出)
- 价格相对OpenAI更优惠

**状态**：☐ 已申请 ☐ 已配置

#### 方案B：OpenAI API（备选）

**获取方式**：
1. 访问 https://platform.openai.com/api-keys
2. 登录/注册账号
3. 点击 "Create new secret key"
4. 复制密钥（只显示一次）

**配置位置**：`.env` 文件
```env
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
LLM_MODEL=gpt-3.5-turbo
```

**成本参考**：
- GPT-3.5-turbo: $0.002/1K tokens (输入), $0.002/1K tokens (输出)
- 建议设置使用限额：$50-200/月

**状态**：☐ 已申请 ☐ 已配置

---

### 2. GitHub Personal Access Token

**用途**：通过GitHub API采集开源代码

**获取方式**：
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 设置权限：
   - ✅ `public_repo` (读取公开仓库)
   - ✅ `read:org` (如果需要访问组织仓库)
4. 设置过期时间（建议90天）
5. 生成并复制token

**配置位置**：`.env` 文件
```env
GITHUB_TOKEN=ghp_...
```

**限制说明**：
- 未认证：60请求/小时
- 认证后：5,000请求/小时

**状态**：☐ 已申请 ☐ 已配置

---

## 可选密钥清单

### 3. Pinecone API Key（云端部署）

**用途**：使用云端矢量数据库服务

**获取方式**：
1. 访问 https://www.pinecone.io/
2. 注册免费账号
3. 创建项目
4. 在API Keys页面获取密钥

**配置位置**：`.env` 文件
```env
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=code-retrievr
```

**免费额度**：
- 1个索引
- 100K向量
- 适合初期使用

**状态**：☐ 已申请 ☐ 已配置（仅云端版需要）

---

### 4. Anthropic Claude API Key（可选）

**用途**：作为OpenAI的备选方案，生成代码复用说明

**获取方式**：
1. 访问 https://console.anthropic.com/
2. 注册账号
3. 在API Keys页面创建密钥

**配置位置**：`.env` 文件
```env
ANTHROPIC_API_KEY=sk-ant-...
```

**状态**：☐ 已申请 ☐ 已配置（可选）

---

### 5. 云服务账号（云端部署）

#### AWS
- **用途**：EC2、RDS、S3等服务
- **配置**：AWS CLI配置或环境变量
- **状态**：☐ 已申请 ☐ 已配置

#### Azure
- **用途**：App Service、Cosmos DB等
- **配置**：Azure CLI配置
- **状态**：☐ 已申请 ☐ 已配置

#### Google Cloud
- **用途**：Cloud Run、Cloud SQL等
- **配置**：gcloud CLI配置
- **状态**：☐ 已申请 ☐ 已配置

---

## 密钥检查清单

在开始开发前，确认以下密钥已配置：

- [ ] OpenAI API Key（必需）
- [ ] GitHub Token（必需）
- [ ] Pinecone API Key（仅云端版需要）
- [ ] 云服务账号（仅云端部署需要）

## 验证密钥配置

运行环境检查脚本：

```bash
python scripts/check_environment.py
```

或手动检查：

```bash
# 检查环境变量
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"
```

## 密钥轮换计划

| 密钥类型 | 轮换周期 | 上次更新 | 下次更新 |
|---------|---------|---------|---------|
| GitHub Token | 90天 | - | - |
| OpenAI API Key | 不轮换（可撤销） | - | - |
| Pinecone API Key | 不轮换（可撤销） | - | - |

## 紧急情况处理

如果密钥泄露：

1. **立即撤销密钥**
   - GitHub: https://github.com/settings/tokens
   - OpenAI: https://platform.openai.com/api-keys
   - Pinecone: https://app.pinecone.io/

2. **生成新密钥**

3. **更新 `.env` 文件**

4. **重新部署服务**

---

**文档版本**：v1.0  
**创建日期**：2024年  
**最后更新**：2024年

