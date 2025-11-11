# CodeRetrievr 快速启动脚本 (Windows PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  CodeRetrievr 快速启动脚本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否在项目根目录
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ 错误: 请在项目根目录运行此脚本" -ForegroundColor Red
    exit 1
}

# 检查 Conda 环境
Write-Host "1. 检查 Conda 环境..." -ForegroundColor Yellow
try {
    $condaVersion = conda --version 2>&1
    Write-Host "✅ Conda 已安装: $condaVersion" -ForegroundColor Green
    
    # 检查是否在 conda 环境中
    $condaEnv = $env:CONDA_DEFAULT_ENV
    if ($condaEnv) {
        Write-Host "✅ 当前 Conda 环境: $condaEnv" -ForegroundColor Green
        
        # 检查是否是 coderetrievr 环境
        if ($condaEnv -eq "coderetrievr") {
            Write-Host "✅ 已激活 coderetrievr 环境" -ForegroundColor Green
        } else {
            Write-Host "⚠️  当前环境不是 coderetrievr，建议激活: conda activate coderetrievr" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️  未检测到 Conda 环境，建议创建并激活:" -ForegroundColor Yellow
        Write-Host "   conda create -n coderetrievr python=3.9 -y" -ForegroundColor White
        Write-Host "   conda activate coderetrievr" -ForegroundColor White
    }
    
    # 检查 Python 版本
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✅ Python 版本: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  无法获取 Python 版本" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Conda 未在 PATH 中（这是正常的）" -ForegroundColor Yellow
    Write-Host "" -ForegroundColor Yellow
    Write-Host "💡 解决方案：" -ForegroundColor Cyan
    Write-Host "   1. 使用 Anaconda Prompt（推荐）：" -ForegroundColor White
    Write-Host "      - 从开始菜单打开 'Anaconda Prompt'" -ForegroundColor White
    Write-Host "      - 导航到项目目录：cd $PWD" -ForegroundColor White
    Write-Host "      - 在 Anaconda Prompt 中运行此脚本" -ForegroundColor White
    Write-Host "" -ForegroundColor White
    Write-Host "   2. 查看详细解决方案：" -ForegroundColor White
    Write-Host "      docs/Conda不在PATH的解决方案.md" -ForegroundColor White
    Write-Host "" -ForegroundColor White
    
    # 尝试检查 Python（可能使用 venv）
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "⚠️  检测到 Python: $pythonVersion" -ForegroundColor Yellow
        Write-Host "   可以使用 venv，但建议使用 Anaconda Prompt + Conda" -ForegroundColor Yellow
    } catch {
        Write-Host "❌ Python 未安装，请先安装 Python 3.9+" -ForegroundColor Red
        Write-Host "   或安装 Anaconda: https://www.anaconda.com/download" -ForegroundColor Yellow
        exit 1
    }
}
Write-Host ""

# 检查 Docker
Write-Host "2. 检查 Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "✅ Docker 已安装: $dockerVersion" -ForegroundColor Green
    
    # 检查 Docker 服务是否运行
    try {
        docker info | Out-Null
        Write-Host "✅ Docker 服务正在运行" -ForegroundColor Green
    } catch {
        Write-Host "❌ Docker 服务未运行，请启动 Docker Desktop" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Docker 未安装，请先安装 Docker Desktop" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 检查 .env 文件
Write-Host "3. 检查环境变量配置..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    if (Test-Path "env") {
        Write-Host "⚠️  .env 文件不存在，从 env 模板创建..." -ForegroundColor Yellow
        Copy-Item env .env
        Write-Host "✅ 已创建 .env 文件" -ForegroundColor Green
        Write-Host "⚠️  请编辑 .env 文件，填入必需的配置（LLM_API_KEY, GITHUB_TOKEN, NEO4J_PASSWORD）" -ForegroundColor Yellow
        Write-Host "   然后重新运行此脚本" -ForegroundColor Yellow
        exit 1
    } else {
        Write-Host "❌ .env 文件不存在，且 env 模板也不存在" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ .env 文件存在" -ForegroundColor Green
Write-Host ""

# 检查 Docker 服务
Write-Host "4. 检查 Docker 服务状态..." -ForegroundColor Yellow
$containers = docker ps --format "{{.Names}}" 2>&1
if ($containers -notmatch "code-retrievr-milvus") {
    Write-Host "⚠️  Docker 服务未启动，正在启动..." -ForegroundColor Yellow
    docker-compose up -d
    Write-Host "⏳ 等待服务启动（约1-2分钟）..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    Write-Host "✅ Docker 服务已启动" -ForegroundColor Green
} else {
    Write-Host "✅ Docker 服务已运行" -ForegroundColor Green
}
Write-Host ""

# 运行环境检查
Write-Host "5. 运行环境检查..." -ForegroundColor Yellow
python scripts/check_environment.py
$checkResult = $LASTEXITCODE
Write-Host ""

if ($checkResult -eq 0) {
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "  ✅ 环境配置完成！" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "下一步：" -ForegroundColor Cyan
    Write-Host "1. 启动后端服务: python -m uvicorn app.main:app --reload" -ForegroundColor White
    Write-Host "2. 访问 API 文档: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "3. 开始采集代码: python scripts/collect_code.py tiangolo/fastapi --language python" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "==========================================" -ForegroundColor Yellow
    Write-Host "  ⚠️  环境检查未完全通过" -ForegroundColor Yellow
    Write-Host "==========================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "请根据上述检查结果修复问题，然后重新运行此脚本" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

