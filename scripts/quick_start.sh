#!/bin/bash
# CodeRetrievr 快速启动脚本 (Linux/macOS)

set -e

echo "=========================================="
echo "  CodeRetrievr 快速启动脚本"
echo "=========================================="
echo ""

# 检查是否在项目根目录
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查 Conda 环境
echo "1. 检查 Conda 环境..."
if ! command -v conda &> /dev/null; then
    echo "⚠️  Conda 未在 PATH 中（这是正常的）"
    echo ""
    echo "💡 解决方案："
    echo "   1. 初始化 conda（推荐）："
    echo "      source ~/anaconda3/etc/profile.d/conda.sh"
    echo "      # 替换 ~/anaconda3 为您的实际 Anaconda 安装路径"
    echo ""
    echo "   2. 使用完整路径："
    echo "      ~/anaconda3/bin/conda create -n coderetrievr python=3.9 -y"
    echo ""
    echo "   3. 查看详细解决方案："
    echo "      docs/Conda不在PATH的解决方案.md"
    echo ""
    
    # 检查 Python
    if ! command -v python &> /dev/null; then
        echo "❌ Python 未安装，请先安装 Python 3.9+"
        echo "   或安装 Anaconda: https://www.anaconda.com/download"
        exit 1
    fi
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    echo "⚠️  检测到 Python: $PYTHON_VERSION"
    echo "   可以使用 venv，但建议使用 Conda（见上方解决方案）"
else
    CONDA_VERSION=$(conda --version 2>&1)
    echo "✅ Conda 已安装: $CONDA_VERSION"
    
    # 检查是否在 conda 环境中
    if [ -n "$CONDA_DEFAULT_ENV" ]; then
        echo "✅ 当前 Conda 环境: $CONDA_DEFAULT_ENV"
        
        # 检查是否是 coderetrievr 环境
        if [ "$CONDA_DEFAULT_ENV" = "coderetrievr" ]; then
            echo "✅ 已激活 coderetrievr 环境"
        else
            echo "⚠️  当前环境不是 coderetrievr，建议激活: conda activate coderetrievr"
        fi
    else
        echo "⚠️  未检测到 Conda 环境，建议创建并激活:"
        echo "   conda create -n coderetrievr python=3.9 -y"
        echo "   conda activate coderetrievr"
    fi
    
    # 检查 Python 版本
    if command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
        echo "✅ Python 版本: $PYTHON_VERSION"
    fi
fi
echo ""

# 检查 Docker
echo "2. 检查 Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi
if ! docker info &> /dev/null; then
    echo "❌ Docker 服务未运行，请启动 Docker Desktop"
    exit 1
fi
echo "✅ Docker 已安装并运行"
echo ""

# 检查 .env 文件
echo "3. 检查环境变量配置..."
if [ ! -f ".env" ]; then
    if [ -f "env" ]; then
        echo "⚠️  .env 文件不存在，从 env 模板创建..."
        cp env .env
        echo "✅ 已创建 .env 文件"
        echo "⚠️  请编辑 .env 文件，填入必需的配置（LLM_API_KEY, GITHUB_TOKEN, NEO4J_PASSWORD）"
        echo "   然后重新运行此脚本"
        exit 1
    else
        echo "❌ .env 文件不存在，且 env 模板也不存在"
        exit 1
    fi
fi
echo "✅ .env 文件存在"
echo ""

# 检查 Docker 服务
echo "4. 检查 Docker 服务状态..."
if ! docker-compose ps | grep -q "code-retrievr-milvus"; then
    echo "⚠️  Docker 服务未启动，正在启动..."
    docker-compose up -d
    echo "⏳ 等待服务启动（约1-2分钟）..."
    sleep 30
    echo "✅ Docker 服务已启动"
else
    echo "✅ Docker 服务已运行"
fi
echo ""

# 运行环境检查
echo "5. 运行环境检查..."
python scripts/check_environment.py
CHECK_RESULT=$?
echo ""

if [ $CHECK_RESULT -eq 0 ]; then
    echo "=========================================="
    echo "  ✅ 环境配置完成！"
    echo "=========================================="
    echo ""
    echo "下一步："
    echo "1. 启动后端服务: python -m uvicorn app.main:app --reload"
    echo "2. 访问 API 文档: http://localhost:8000/docs"
    echo "3. 开始采集代码: python scripts/collect_code.py tiangolo/fastapi --language python"
    echo ""
else
    echo "=========================================="
    echo "  ⚠️  环境检查未完全通过"
    echo "=========================================="
    echo ""
    echo "请根据上述检查结果修复问题，然后重新运行此脚本"
    echo ""
    exit 1
fi

