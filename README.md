# 1. 创建conda环境
conda create -n coderetrievr python=3.9 -y

# 2. 激活环境
conda activate coderetrievr

# 3. 安装依赖
pip install -r requirements.txt

# 4. 验证环境
python scripts/check_environment.py# CodeRetrievr - 基于矢量数据库的代码检索与复用平台

## 项目简介

CodeRetrievr 是一个基于矢量数据库和知识图谱的智能代码检索与复用平台，支持通过自然语言查询检索相关代码片段，并提供AI生成的复用说明。

## 核心功能

- 🔍 **自然语言代码检索**：使用自然语言描述需求，快速找到相关代码片段
- 📊 **知识图谱关联**：展示代码的依赖关系、使用场景等关联信息
- 🤖 **AI复用说明生成**：自动生成代码使用说明、参数解释和注意事项
- 🌐 **多语言支持**：支持 Python、C++、Java 等多种编程语言
- 🏠 **双模式部署**：支持本地离线部署和云端多用户部署

## 技术栈

### 后端
- **语言**：Python 3.9+
- **框架**：FastAPI
- **矢量数据库**：Milvus（本地）/ Pinecone（云端）
- **知识图谱**：Neo4j
- **代码嵌入模型**：CodeBERT / StarCoder

### 前端
- **框架**：React + TypeScript
- **UI组件**：Ant Design

## 快速开始

### 环境要求

- Python 3.9+
- Docker & Docker Compose（用于本地部署数据库）
- Node.js 16+（前端开发）

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/yourusername/CodeRetrievr.git
cd CodeRetrievr
```

2. **创建Python环境**

**使用Anaconda（推荐）：**
```bash
# 创建conda环境
conda create -n coderetrievr python=3.9 -y

# 激活环境
conda activate coderetrievr
```

**或使用venv：**
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

3. **安装Python依赖**
```bash
# 升级pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 如果torch安装失败，可以尝试：
# conda install pytorch cpuonly -c pytorch
# 或
# pip install torch --index-url https://download.pytorch.org/whl/cpu
```

4. **配置环境变量**
```bash
# 创建.env文件（如果.env.example存在）
cp .env.example .env

# 编辑 .env 文件，填入API密钥等配置
# 必需配置：
# - LLM_API_KEY (DeepSeek API密钥)
# - GITHUB_TOKEN
# - NEO4J_PASSWORD
```

4. **启动数据库服务（本地部署）**
```bash
docker-compose up -d
```

5. **启动后端服务**
```bash
python -m uvicorn app.main:app --reload
```

6. **启动前端服务**
```bash
cd frontend
npm install
npm start
```

## 项目结构

```
CodeRetrievr/
├── app/                    # 后端应用
│   ├── api/               # API路由
│   ├── core/              # 核心功能模块
│   ├── models/            # 数据模型
│   ├── services/          # 业务逻辑
│   └── utils/             # 工具函数
├── frontend/              # 前端应用
├── data/                  # 数据存储
├── scripts/               # 脚本工具
├── docs/                  # 文档
├── tests/                 # 测试
├── docker-compose.yml     # Docker编排
├── requirements.txt       # Python依赖
└── README.md             # 项目说明
```

## 开发计划

详细的项目步骤表请参考 [项目步骤表.md](./项目步骤表.md)

## 快速开始 - 代码采集

### 采集单个仓库

```bash
# 激活环境
conda activate coderetrievr

# 采集代码（示例：FastAPI项目）
python scripts/collect_code.py tiangolo/fastapi --language python

# 查看结果
ls data/code_snippets/
```

### 采集多个仓库

编辑 `scripts/batch_collect.py`，添加要采集的仓库列表，然后运行：

```bash
python scripts/batch_collect.py
```

详细说明请参考 [阶段2代码采集指南.md](./docs/阶段2代码采集指南.md)

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

