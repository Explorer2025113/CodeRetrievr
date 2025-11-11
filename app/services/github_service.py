"""
GitHub API服务 - 用于采集开源代码
"""

import os
import time
from typing import List, Dict, Optional
from github import Github
from github.Repository import Repository
from github.ContentFile import ContentFile
from app.core.config import settings


class GitHubService:
    """GitHub API服务类"""
    
    def __init__(self):
        """初始化GitHub服务"""
        token = settings.GITHUB_TOKEN
        if not token:
            raise ValueError("未配置GITHUB_TOKEN，请在.env文件中设置")
        
        self.github = Github(token)
        self.rate_limit = settings.GITHUB_RATE_LIMIT
    
    def search_repositories(
        self,
        query: str,
        language: Optional[str] = None,
        sort: str = "stars",
        order: str = "desc",
        per_page: int = 30
    ) -> List[Repository]:
        """
        搜索GitHub仓库
        
        Args:
            query: 搜索关键词
            language: 编程语言（如python, java, cpp）
            sort: 排序方式（stars, forks, updated）
            order: 排序顺序（desc, asc）
            per_page: 每页数量（最多100）
        
        Returns:
            仓库列表
        """
        # 构建搜索查询
        search_query = query
        if language:
            search_query += f" language:{language}"
        
        try:
            repositories = self.github.search_repositories(
                search_query,
                sort=sort,
                order=order
            )
            
            # 获取前per_page个结果
            repos = []
            for i, repo in enumerate(repositories):
                if i >= per_page:
                    break
                repos.append(repo)
                # 检查速率限制
                self._check_rate_limit()
            
            return repos
        
        except Exception as e:
            raise Exception(f"搜索仓库失败: {str(e)}")
    
    def get_repository_files(
        self,
        repo: Repository,
        path: str = "",
        file_extensions: Optional[List[str]] = None
    ) -> List[ContentFile]:
        """
        获取仓库中的文件列表
        
        Args:
            repo: GitHub仓库对象
            path: 目录路径（默认为根目录）
            file_extensions: 文件扩展名过滤（如['.py', '.java']）
        
        Returns:
            文件列表
        """
        try:
            contents = repo.get_contents(path)
            files = []
            
            if isinstance(contents, list):
                # 目录
                for content in contents:
                    if content.type == "file":
                        # 检查文件扩展名
                        if file_extensions:
                            if any(content.name.endswith(ext) for ext in file_extensions):
                                files.append(content)
                        else:
                            files.append(content)
                    elif content.type == "dir":
                        # 递归获取子目录文件
                        sub_files = self.get_repository_files(
                            repo, content.path, file_extensions
                        )
                        files.extend(sub_files)
            else:
                # 单个文件
                if file_extensions:
                    if any(contents.name.endswith(ext) for ext in file_extensions):
                        files.append(contents)
                else:
                    files.append(contents)
            
            return files
        
        except Exception as e:
            print(f"获取文件列表失败 {path}: {str(e)}")
            return []
    
    def get_file_content(self, content_file: ContentFile) -> Optional[str]:
        """
        获取文件内容
        
        Args:
            content_file: GitHub文件对象
        
        Returns:
            文件内容（文本）
        """
        try:
            # 检查文件大小（GitHub API限制，大文件需要特殊处理）
            if content_file.size > 1_000_000:  # 1MB
                print(f"文件过大，跳过: {content_file.path} ({content_file.size} bytes)")
                return None
            
            content = content_file.decoded_content.decode('utf-8')
            return content
        
        except UnicodeDecodeError:
            print(f"无法解码文件: {content_file.path}")
            return None
        except Exception as e:
            print(f"获取文件内容失败 {content_file.path}: {str(e)}")
            return None
    
    def get_repository_info(self, repo: Repository) -> Dict:
        """
        获取仓库信息
        
        Args:
            repo: GitHub仓库对象
        
        Returns:
            仓库信息字典
        """
        # 安全获取license信息
        license_name = None
        try:
            if hasattr(repo, 'license') and repo.license:
                license_name = repo.license.name if hasattr(repo.license, 'name') else str(repo.license)
        except Exception:
            pass
        
        return {
            "name": repo.name,
            "full_name": repo.full_name,
            "url": repo.html_url,
            "description": repo.description or "",
            "language": repo.language or "",
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "created_at": repo.created_at.isoformat() if repo.created_at else None,
            "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
            "license": license_name,
        }
    
    def _check_rate_limit(self):
        """检查并等待速率限制"""
        rate_limit = self.github.get_rate_limit()
        remaining = rate_limit.core.remaining
        
        if remaining < 10:
            reset_time = rate_limit.core.reset
            wait_time = (reset_time - time.time()) + 1
            if wait_time > 0:
                print(f"速率限制接近，等待 {wait_time:.0f} 秒...")
                time.sleep(wait_time)


# 全局实例
_github_service: Optional[GitHubService] = None


def get_github_service() -> GitHubService:
    """获取GitHub服务实例（单例模式）"""
    global _github_service
    if _github_service is None:
        _github_service = GitHubService()
    return _github_service

