# Anaconda 快速开始指南

本指南提供使用 Anaconda 部署 CodeRetrievr 项目的快速步骤。

## 📋 前提条件

- 已安装 Anaconda 或 Miniconda
- 已安装 Docker Desktop
- 已安装 Git

## 🚀 快速部署步骤

### 1. 安装 Anaconda（如果还未安装）

1. 访问 [Anaconda官网](https://www.anaconda.com/download)
2. 下载并安装 Anaconda（推荐）或 Miniconda（更轻量）
3. **Windows用户**：
   - 如果无法添加到 PATH，**不用担心**！请使用 **Anaconda Prompt**（见下方说明）
   - 如果可以，安装时勾选 "Add Anaconda to PATH"
4. 验证安装：
   ```bash
   # 如果 conda 在 PATH 中
   conda --version
   
   # 如果 conda 不在 PATH 中，使用 Anaconda Prompt（见下方）
   ```

> 💡 **重要提示**：如果 conda 不在 PATH 环境变量中，请查看 [Conda不在PATH的解决方案](./Conda不在PATH的解决方案.md)

### 2. 克隆项目

```bash
git clone https://github.com/yourusername/CodeRetrievr.git
cd CodeRetrievr
```

### 3. 创建 Conda 环境

**如果 conda 在 PATH 中：**
```bash
# 创建名为 coderetrievr 的 Python 3.9 环境
conda create -n coderetrievr python=3.9 -y

# 激活环境
conda activate coderetrievr
```

**如果 conda 不在 PATH 中（Windows用户）：**
1. 打开 **Anaconda Prompt**（从开始菜单）
2. 导航到项目目录：`cd E:\Github\CodeRetrievr`
3. 运行上述命令

**如果 conda 不在 PATH 中（Linux/macOS用户）：**
```bash
# 初始化 conda（替换 ~/anaconda3 为您的实际路径）
source ~/anaconda3/etc/profile.d/conda.sh

# 然后运行上述命令
conda create -n coderetrievr python=3.9 -y
conda activate coderetrievr
```

> 📖 **详细说明**：请查看 [Conda不在PATH的解决方案](./Conda不在PATH的解决方案.md)

### 4. 安装依赖

#### 方法1：使用 pip（简单）

```bash
# 确保已激活环境
conda activate coderetrievr

# 升级 pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

#### 方法2：使用 conda 安装 PyTorch（推荐，更稳定）

```bash
# 确保已激活环境
conda activate coderetrievr

# 使用 conda 安装 PyTorch（CPU版本）
conda install pytorch cpuonly -c pytorch -y

# 安装其他依赖
pip install -r requirements.txt
```

#### 方法3：使用国内镜像源（如果网络较慢）

```bash
# 配置 conda 镜像
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --set show_channel_urls yes

# 配置 pip 镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装依赖
pip install -r requirements.txt
```

### 5. 配置环境变量

```bash
# 创建 .env 文件
# Windows:
copy env .env
# macOS/Linux:
cp env .env

# 编辑 .env 文件，填入必需的配置：
# - LLM_API_KEY (DeepSeek/OpenAI API密钥)
# - GITHUB_TOKEN (GitHub Token)
# - NEO4J_PASSWORD (需与docker-compose.yml中的密码一致)
```

### 6. 启动 Docker 服务

```bash
# 启动所有服务
docker-compose up -d

# 等待服务启动（约1-2分钟）
docker-compose ps
```

### 7. 验证环境

```bash
# 确保已激活环境
conda activate coderetrievr

# 运行环境检查
python scripts/check_environment.py
```

### 8. 启动后端服务

```bash
# 确保已激活环境
conda activate coderetrievr

# 启动服务
python -m uvicorn app.main:app --reload
```

访问 http://localhost:8000/docs 查看 API 文档。

## 🔧 日常使用

### 激活环境

```bash
conda activate coderetrievr
```

### 运行脚本

```bash
# 环境检查
python scripts/check_environment.py

# 代码采集
python scripts/collect_code.py tiangolo/fastapi --language python

# 向量化代码
python scripts/vectorize_code.py data/code_snippets/your_file.json
```

### 退出环境

```bash
conda deactivate
```

## ⚠️ 常见问题

### 问题1：conda 命令未找到

**这是最常见的问题！如果 conda 不在 PATH 中，请使用以下方法：**

**Windows用户（推荐）：**
- ✅ 使用 **Anaconda Prompt**（从开始菜单打开）
- ✅ 这是最简单可靠的方法，无需配置 PATH

**Windows用户（备选）：**
- 使用完整路径：`C:\Users\YourName\anaconda3\Scripts\conda.exe`
- 或在 PowerShell 中运行：`conda init powershell`，然后重启

**Linux/macOS用户：**
- 运行：`source ~/anaconda3/etc/profile.d/conda.sh`（替换为您的实际路径）
- 或使用完整路径：`~/anaconda3/bin/conda`

> 📖 **详细解决方案**：请查看 [Conda不在PATH的解决方案](./Conda不在PATH的解决方案.md)

### 问题2：PyTorch 安装失败

**解决方案**：
```bash
# 使用 conda 安装（推荐）
conda install pytorch cpuonly -c pytorch -y

# 或使用国内镜像源
pip install torch -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题3：依赖冲突

**解决方案**：
```bash
# 创建全新的环境
conda env remove -n coderetrievr
conda create -n coderetrievr python=3.9 -y
conda activate coderetrievr
pip install -r requirements.txt
```

## 📚 相关文档

- [Anaconda环境配置指南](./Anaconda环境配置指南.md) - 详细配置说明
- [新机器部署指南](./新机器部署指南.md) - 完整部署步骤
- [快速启动检查清单](./快速启动检查清单.md) - 快速验证部署

## 🎯 快速参考

```bash
# 创建环境
conda create -n coderetrievr python=3.9 -y

# 激活环境
conda activate coderetrievr

# 安装依赖
pip install -r requirements.txt

# 或使用 conda 安装 PyTorch
conda install pytorch cpuonly -c pytorch -y
pip install -r requirements.txt

# 验证环境
python scripts/check_environment.py

# 启动服务
python -m uvicorn app.main:app --reload
```

---

**文档版本**：v1.0  
**创建日期**：2024年11月

