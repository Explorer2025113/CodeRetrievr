# Anaconda环境配置指南

## 简介

本指南专门针对使用Anaconda/Miniconda的用户，提供详细的conda环境配置步骤。

## 前置要求

- 已安装Anaconda或Miniconda
- 确保conda命令可用

验证安装：
```bash
conda --version
```

## 创建Conda环境

### 步骤1：创建新环境

```bash
# 创建名为coderetrievr的Python 3.9环境
conda create -n coderetrievr python=3.9 -y
```

**参数说明**：
- `-n coderetrievr`: 环境名称，可以自定义
- `python=3.9`: 指定Python版本（必须3.9+）
- `-y`: 自动确认，跳过提示

### 步骤2：激活环境

```bash
conda activate coderetrievr
```

激活成功后，命令行提示符前会显示 `(coderetrievr)`。

### 步骤3：验证环境

```bash
# 查看当前环境
conda info --envs

# 确认Python版本
python --version  # 应显示 Python 3.9.x

# 查看当前环境的包
conda list
```

## 安装项目依赖

### 方法1：使用pip安装（推荐）

```bash
# 确保已激活环境
conda activate coderetrievr

# 升级pip
python -m pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

### 方法2：使用conda安装部分包

某些包（如PyTorch）可以通过conda安装，可能更稳定：

```bash
# 安装PyTorch（CPU版本）
conda install pytorch cpuonly -c pytorch -y

# 安装其他依赖
pip install -r requirements.txt
```

### 方法3：混合安装

```bash
# 先安装conda可用的包
conda install numpy pandas -y

# 再安装其他依赖
pip install -r requirements.txt
```

## 常见问题解决

### 问题1：torch安装失败

**错误信息**：`ERROR: Could not find a version that satisfies the requirement torch`

**解决方案A：使用conda安装**
```bash
conda install pytorch cpuonly -c pytorch -y
```

**解决方案B：使用PyTorch官方源**
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

**解决方案C：如果有GPU**
```bash
# CUDA 11.8
conda install pytorch pytorch-cuda=11.8 -c pytorch -c nvidia -y

# CUDA 12.1
conda install pytorch pytorch-cuda=12.1 -c pytorch -c nvidia -y
```

### 问题2：依赖冲突

**错误信息**：`ERROR: pip's dependency resolver does not currently take into account all the packages that are already installed`

**解决方案**：
```bash
# 创建全新的环境
conda create -n coderetrievr python=3.9 -y
conda activate coderetrievr

# 先安装可能冲突的包
conda install numpy pandas -y

# 再安装其他依赖
pip install -r requirements.txt
```

### 问题3：conda环境激活失败

**Windows PowerShell错误**：`conda : 无法将"conda"项识别为 cmdlet、函数、脚本文件或可运行程序的名称`

**解决方案**：
1. 打开Anaconda Prompt（不是普通PowerShell）
2. 或手动初始化conda：
```powershell
# 在PowerShell中执行
conda init powershell
# 重启PowerShell
```

### 问题4：网络问题导致安装慢

**解决方案：使用国内镜像源**

```bash
# 配置conda镜像（清华大学源）
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --set show_channel_urls yes

# 配置pip镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

## 环境管理

### 查看所有环境

```bash
conda env list
# 或
conda info --envs
```

### 导出环境配置

```bash
# 导出当前环境的包列表
conda list --export > environment.txt

# 或导出为yaml格式（推荐）
conda env export > environment.yml
```

### 从配置文件创建环境

```bash
# 从yaml文件创建
conda env create -f environment.yml

# 从requirements.txt创建（需要先创建环境）
conda create -n coderetrievr python=3.9 -y
conda activate coderetrievr
pip install -r requirements.txt
```

### 删除环境

```bash
# 先停用当前环境
conda deactivate

# 删除环境
conda env remove -n coderetrievr
```

### 更新环境中的包

```bash
conda activate coderetrievr

# 更新conda包
conda update --all

# 更新pip包
pip install --upgrade -r requirements.txt
```

## 验证安装

运行环境检查脚本：

```bash
conda activate coderetrievr
python scripts/check_environment.py
```

应该看到：
- ✅ Python版本检查通过
- ✅ Conda环境检测到
- ✅ 所有依赖包已安装

## 开发工作流

### 日常使用

```bash
# 1. 激活环境
conda activate coderetrievr

# 2. 运行项目
python -m uvicorn app.main:app --reload

# 3. 运行脚本
python scripts/check_environment.py

# 4. 退出环境（可选）
conda deactivate
```

### 在IDE中配置

**VS Code:**
1. 打开命令面板（Ctrl+Shift+P）
2. 输入 "Python: Select Interpreter"
3. 选择 `coderetrievr` 环境的Python解释器
   - 路径通常为：`C:\Users\YourName\anaconda3\envs\coderetrievr\python.exe`

**PyCharm:**
1. File > Settings > Project > Python Interpreter
2. 点击齿轮图标 > Add
3. 选择Conda Environment
4. 选择Existing environment
5. 选择 `coderetrievr` 环境

## Conda vs venv对比

| 特性 | Conda | venv |
|------|-------|------|
| 包管理 | conda + pip | 仅pip |
| 二进制包 | ✅ 支持 | ❌ 不支持 |
| 非Python包 | ✅ 可安装 | ❌ 不支持 |
| 环境隔离 | ✅ 完全隔离 | ✅ 完全隔离 |
| 跨平台 | ✅ 优秀 | ✅ 良好 |
| 推荐场景 | 科学计算、ML项目 | 纯Python项目 |

**本项目推荐使用Conda**，因为：
- 需要安装PyTorch等科学计算包
- Conda可以更好地处理二进制依赖
- 环境管理更简单

## 快速参考

```bash
# 创建环境
conda create -n coderetrievr python=3.9 -y

# 激活环境
conda activate coderetrievr

# 安装依赖
pip install -r requirements.txt

# 验证安装
python scripts/check_environment.py

# 运行项目
python -m uvicorn app.main:app --reload
```

---

**文档版本**：v1.0  
**创建日期**：2024年  
**最后更新**：2024年

