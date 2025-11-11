#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境配置检查脚本
用于验证开发环境是否正确配置
"""

import os
import sys
import subprocess
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    try:
        # 尝试设置UTF-8编码
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        # 如果失败，使用ASCII替代emoji
        pass

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  警告: python-dotenv 未安装，将使用系统环境变量")


def safe_print(text):
    """安全打印，处理编码问题"""
    try:
        # 尝试直接打印
        print(text, flush=True)
    except (UnicodeEncodeError, UnicodeError):
        # 如果无法打印emoji，替换为ASCII字符
        text = (text.replace('✅', '[OK]')
                   .replace('❌', '[X]')
                   .replace('⚠️', '[!]')
                   .replace('⚪', '[ ]')
                   .replace('🎉', '[SUCCESS]')
                   .replace('💡', '[TIP]'))
        print(text, flush=True)

def print_header(text):
    """打印分隔线"""
    safe_print("\n" + "=" * 60)
    safe_print(f"  {text}")
    safe_print("=" * 60)


def check_python():
    """检查Python版本"""
    print_header("Python环境检查")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 9:
        safe_print(f"✅ Python版本: {version_str}")
        
        # 检查是否在conda环境中
        conda_env = os.getenv('CONDA_DEFAULT_ENV')
        if conda_env:
            safe_print(f"✅ Conda环境: {conda_env}")
        else:
            # 检查是否在venv中
            venv = os.getenv('VIRTUAL_ENV')
            if venv:
                safe_print(f"✅ 虚拟环境: {venv}")
            else:
                safe_print("⚠️  未检测到虚拟环境，建议使用conda或venv")
        
        return True
    else:
        print(f"❌ Python版本过低: {version_str}")
        print("   需要 Python 3.9 或更高版本")
        print("   建议使用: conda create -n coderetrievr python=3.9")
        return False


def check_dependencies():
    """检查关键依赖包"""
    print_header("依赖包检查")
    required_packages = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'pymilvus': 'PyMilvus',
        'neo4j': 'Neo4j',
        'sentence_transformers': 'sentence-transformers',
        'openai': 'OpenAI',
        'dotenv': 'python-dotenv',
    }
    
    missing = []
    errors = []
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} 未安装")
            missing.append(name)
        except Exception as e:
            # 某些包导入时可能有警告或错误，但不影响使用
            error_msg = str(e)
            if '__version_info__' in error_msg or 'marshmallow' in error_msg.lower():
                # marshmallow版本检查问题，不影响使用
                print(f"✅ {name} (已安装，但有版本检查警告)")
            else:
                print(f"⚠️  {name}: {error_msg}")
                errors.append(f"{name}: {error_msg}")
    
    if missing:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing)}")
        print("   运行: pip install -r requirements.txt")
        return False
    
    if errors:
        print(f"\n⚠️  部分包有警告，但不影响使用")
    
    return True


def check_env_vars():
    """检查环境变量"""
    print_header("环境变量检查")
    
    required_vars = {
        'LLM_API_KEY': '大模型API密钥（DeepSeek/OpenAI，必需）',
        'GITHUB_TOKEN': 'GitHub Token（必需）',
        'NEO4J_PASSWORD': 'Neo4j密码（必需）',
    }
    
    # 兼容旧配置
    legacy_vars = {
        'OPENAI_API_KEY': 'OpenAI API密钥（已废弃，请使用LLM_API_KEY）',
    }
    
    optional_vars = {
        'PINECONE_API_KEY': 'Pinecone API密钥（云端版）',
        'MILVUS_HOST': 'Milvus主机地址',
        'NEO4J_URI': 'Neo4j连接URI',
        'LLM_PROVIDER': '大模型提供商（deepseek/openai）',
        'LLM_BASE_URL': 'DeepSeek API地址',
    }
    
    missing_required = []
    missing_optional = []
    
    # 检查必需变量（支持LLM_API_KEY或OPENAI_API_KEY）
    llm_key_set = bool(os.getenv('LLM_API_KEY') or os.getenv('OPENAI_API_KEY'))
    if llm_key_set:
        key_var = 'LLM_API_KEY' if os.getenv('LLM_API_KEY') else 'OPENAI_API_KEY'
        value = os.getenv(key_var)
        masked = value[:10] + '...' if len(value) > 10 else '***'
        print(f"✅ 大模型API密钥: {masked} ({key_var})")
    else:
        print(f"❌ 大模型API密钥: 未设置 - {required_vars['LLM_API_KEY']}")
        missing_required.append('LLM_API_KEY')
    
    # 检查其他必需变量
    for var, desc in required_vars.items():
        if var == 'LLM_API_KEY':  # 已单独处理
            continue
        value = os.getenv(var)
        if value:
            masked = value[:10] + '...' if len(value) > 10 else '***'
            print(f"✅ {var}: {masked}")
        else:
            print(f"❌ {var}: 未设置 - {desc}")
            missing_required.append(var)
    
    # 检查旧配置（兼容性）
    print("\n兼容性检查:")
    for var, desc in legacy_vars.items():
        value = os.getenv(var)
        if value:
            print(f"⚠️  {var}: 已设置但已废弃 - {desc}")
            print(f"   建议迁移到 LLM_API_KEY")
    
    print("\n可选环境变量:")
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: 已设置")
        else:
            print(f"⚪ {var}: 未设置 - {desc}")
            missing_optional.append(var)
    
    if missing_required:
        print(f"\n❌ 缺少必需的环境变量: {', '.join(missing_required)}")
        print("   请检查 .env 文件或设置系统环境变量")
        return False
    
    return True


def check_docker():
    """检查Docker"""
    print_header("Docker检查")
    
    try:
        # 检查Docker是否安装
        result = subprocess.run(
            ['docker', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Docker已安装: {version}")
            
            # 检查Docker服务是否运行（使用docker info更可靠）
            try:
                info_result = subprocess.run(
                    ['docker', 'info'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if info_result.returncode == 0:
                    print("✅ Docker服务正在运行")
                    return True
                else:
                    error_msg = info_result.stderr.strip()
                    if "Cannot connect to the Docker daemon" in error_msg or "Is the docker daemon running" in error_msg:
                        print("⚠️  Docker服务未运行")
                        print("   请启动 Docker Desktop")
                        print("   或运行: docker-compose up -d")
                    else:
                        print("⚠️  Docker服务状态未知")
                    return False
            except subprocess.TimeoutExpired:
                print("⚠️  Docker服务响应超时")
                return False
            except FileNotFoundError:
                print("⚠️  无法检查Docker服务状态")
                return False
        else:
            print("❌ Docker未正确安装")
            return False
    except FileNotFoundError:
        print("❌ Docker未安装或未在PATH中")
        print("   请安装 Docker Desktop: https://www.docker.com/products/docker-desktop")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  Docker命令执行超时")
        return False


def check_docker_services():
    """检查Docker服务状态"""
    print_header("Docker服务检查")
    
    # 先检查Docker是否可用
    try:
        subprocess.run(
            ['docker', 'info'],
            capture_output=True,
            timeout=5
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("⚠️  Docker服务未运行，无法检查容器状态")
        print("   请先启动 Docker Desktop")
        return False
    
    services = {
        'code-retrievr-milvus': 'Milvus矢量数据库',
        'code-retrievr-neo4j': 'Neo4j知识图谱',
    }
    
    try:
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print("⚠️  无法获取Docker容器列表")
            return False
        
        running_containers = result.stdout.strip().split('\n') if result.stdout else []
        # 过滤空字符串
        running_containers = [c for c in running_containers if c]
        
        all_running = True
        for service, desc in services.items():
            if service in running_containers:
                print(f"✅ {desc} ({service})")
            else:
                print(f"⚪ {desc} ({service}) 未运行")
                print(f"   启动命令: docker-compose up -d")
                all_running = False
        
        if not all_running:
            print("\n💡 提示: 这些服务是可选的，仅在需要本地数据库时启动")
            print("   如果使用云端服务（Pinecone），可以跳过此步骤")
        
        return all_running
    except subprocess.TimeoutExpired:
        print("⚠️  检查Docker服务状态超时")
        return False
    except Exception as e:
        print(f"⚠️  检查Docker服务时出错: {e}")
        return False


def check_directories():
    """检查项目目录结构"""
    print_header("项目目录检查")
    
    required_dirs = [
        'app',
        'data',
        'docs',
        'scripts',
    ]
    
    all_exist = True
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ 目录不存在")
            all_exist = False
    
    # 检查.env文件（也检查env文件作为兼容）
    env_file = project_root / '.env'
    env_file_alt = project_root / 'env'
    
    if env_file.exists():
        print("✅ .env 文件存在")
    elif env_file_alt.exists():
        print("⚠️  检测到 env 文件（无点），建议重命名为 .env")
        print("   运行: Copy-Item env .env (Windows) 或 mv env .env (Linux/macOS)")
        # 尝试自动创建
        try:
            import shutil
            shutil.copy(env_file_alt, env_file)
            print("   ✅ 已自动创建 .env 文件")
        except:
            pass
    else:
        print("⚠️  .env 文件不存在")
        print("   运行: cp env.example .env 或 Copy-Item env.example .env")
    
    return all_exist


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  CodeRetrievr 环境配置检查")
    print("=" * 60)
    
    checks = [
        ("Python版本", check_python),
        ("依赖包", check_dependencies),
        ("环境变量", check_env_vars),
        ("Docker", check_docker),
        ("Docker服务", check_docker_services),
        ("项目目录", check_directories),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ 检查 {name} 时出错: {e}")
            results.append((name, False))
    
    # 总结
    print_header("检查总结")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {name}")
    
    print(f"\n总计: {passed}/{total} 项检查通过")
    
    # Docker服务是可选的（仅本地部署需要）
    # 如果其他必需项都通过，即使Docker服务未运行也可以继续
    required_passed = sum(1 for name, result in results 
                         if result and name not in ["Docker", "Docker服务"])
    required_total = sum(1 for name, _ in results 
                        if name not in ["Docker", "Docker服务"])
    
    if passed == total:
        print("\n🎉 环境配置检查全部通过！可以开始开发了。")
        return 0
    elif required_passed == required_total:
        print("\n✅ 必需配置检查通过！")
        print("💡 Docker服务未运行（可选，仅本地部署需要）")
        print("   如需本地部署数据库，请运行: docker-compose up -d")
        return 0
    else:
        print("\n⚠️  部分必需检查未通过，请修复上述问题后重试。")
        return 1


if __name__ == '__main__':
    sys.exit(main())

