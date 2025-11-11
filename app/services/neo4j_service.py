"""
Neo4j知识图谱服务
"""

from typing import List, Dict, Optional
from neo4j import GraphDatabase
from app.core.config import settings


class Neo4jService:
    """Neo4j知识图谱服务"""
    
    def __init__(self):
        """初始化Neo4j服务"""
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        
        if not self.password:
            raise ValueError("未配置NEO4J_PASSWORD，请在.env文件中设置")
        
        # 创建驱动
        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password)
        )
        
        # 验证连接
        try:
            self.driver.verify_connectivity()
            print(f"✅ 已连接到Neo4j: {self.uri}")
        except Exception as e:
            raise Exception(f"连接Neo4j失败: {str(e)}")
    
    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.close()
    
    def create_code_snippet_node(
        self,
        code_id: str,
        name: str,
        code_type: str,
        language: str,
        file_path: str,
        repo_name: str,
        repo_url: str,
        milvus_id: Optional[int] = None
    ) -> bool:
        """
        创建代码片段节点
        
        Args:
            code_id: 代码片段唯一ID
            name: 函数/类名称
            code_type: 类型（function/class）
            language: 编程语言
            file_path: 文件路径
            repo_name: 仓库名称
            repo_url: 仓库URL
            milvus_id: Milvus中的ID（用于关联）
        
        Returns:
            是否成功
        """
        with self.driver.session() as session:
            query = """
            MERGE (c:CodeSnippet {code_id: $code_id})
            SET c.name = $name,
                c.type = $code_type,
                c.language = $language,
                c.file_path = $file_path,
                c.repo_name = $repo_name,
                c.repo_url = $repo_url,
                c.milvus_id = $milvus_id
            RETURN c
            """
            
            result = session.run(
                query,
                code_id=code_id,
                name=name,
                code_type=code_type,
                language=language,
                file_path=file_path,
                repo_name=repo_name,
                repo_url=repo_url,
                milvus_id=milvus_id
            )
            
            return result.single() is not None
    
    def create_dependency_relationships(
        self,
        code_id: str,
        dependencies: List[str]
    ) -> bool:
        """
        创建依赖关系
        
        Args:
            code_id: 代码片段ID
            dependencies: 依赖库列表
        
        Returns:
            是否成功
        """
        if not dependencies:
            return True
        
        with self.driver.session() as session:
            for dep in dependencies:
                # 创建或获取依赖库节点
                query1 = """
                MERGE (d:Library {name: $dep_name})
                RETURN d
                """
                session.run(query1, dep_name=dep)
                
                # 创建依赖关系
                query2 = """
                MATCH (c:CodeSnippet {code_id: $code_id})
                MATCH (d:Library {name: $dep_name})
                MERGE (c)-[:DEPENDS_ON]->(d)
                RETURN c, d
                """
                session.run(query2, code_id=code_id, dep_name=dep)
            
            return True
    
    def create_language_relationship(
        self,
        code_id: str,
        language: str
    ) -> bool:
        """
        创建语言关系
        
        Args:
            code_id: 代码片段ID
            language: 编程语言
        
        Returns:
            是否成功
        """
        with self.driver.session() as session:
            # 创建或获取语言节点
            query1 = """
            MERGE (l:Language {name: $lang_name})
            RETURN l
            """
            session.run(query1, lang_name=language)
            
            # 创建关系
            query2 = """
            MATCH (c:CodeSnippet {code_id: $code_id})
            MATCH (l:Language {name: $lang_name})
            MERGE (c)-[:WRITTEN_IN]->(l)
            RETURN c, l
            """
            session.run(query2, code_id=code_id, lang_name=language)
            
            return True
    
    def get_code_snippet_info(self, code_id: str) -> Optional[Dict]:
        """
        获取代码片段信息及其关联
        
        Args:
            code_id: 代码片段ID
        
        Returns:
            代码片段信息及关联数据
        """
        with self.driver.session() as session:
            query = """
            MATCH (c:CodeSnippet {code_id: $code_id})
            OPTIONAL MATCH (c)-[:DEPENDS_ON]->(d:Library)
            OPTIONAL MATCH (c)-[:WRITTEN_IN]->(l:Language)
            OPTIONAL MATCH (c)-[:SIMILAR_TO]->(similar:CodeSnippet)
            RETURN c,
                   collect(DISTINCT d.name) as dependencies,
                   collect(DISTINCT l.name) as languages,
                   collect(DISTINCT similar.code_id) as similar_codes
            """
            
            result = session.run(query, code_id=code_id)
            record = result.single()
            
            if not record:
                return None
            
            node = record["c"]
            return {
                "code_id": node["code_id"],
                "name": node.get("name"),
                "type": node.get("type"),
                "language": node.get("language"),
                "file_path": node.get("file_path"),
                "repo_name": node.get("repo_name"),
                "repo_url": node.get("repo_url"),
                "dependencies": record["dependencies"],
                "languages": record["languages"],
                "similar_codes": record["similar_codes"],
            }
    
    def search_by_dependency(self, library_name: str, limit: int = 10) -> List[Dict]:
        """
        根据依赖库搜索代码片段
        
        Args:
            library_name: 依赖库名称
            limit: 返回数量限制
        
        Returns:
            代码片段列表
        """
        with self.driver.session() as session:
            query = """
            MATCH (c:CodeSnippet)-[:DEPENDS_ON]->(d:Library {name: $lib_name})
            RETURN c.code_id as code_id,
                   c.name as name,
                   c.type as type,
                   c.language as language,
                   c.repo_name as repo_name
            LIMIT $limit
            """
            
            result = session.run(query, lib_name=library_name, limit=limit)
            return [dict(record) for record in result]
    
    def get_statistics(self) -> Dict:
        """获取知识图谱统计信息"""
        with self.driver.session() as session:
            queries = {
                "code_snippets": "MATCH (c:CodeSnippet) RETURN count(c) as count",
                "libraries": "MATCH (l:Library) RETURN count(l) as count",
                "languages": "MATCH (lang:Language) RETURN count(lang) as count",
                "dependencies": "MATCH ()-[r:DEPENDS_ON]->() RETURN count(r) as count",
            }
            
            stats = {}
            for key, query in queries.items():
                result = session.run(query)
                stats[key] = result.single()["count"]
            
            return stats


# 全局实例
_neo4j_service: Optional[Neo4jService] = None


def get_neo4j_service() -> Neo4jService:
    """获取Neo4j服务实例（单例模式）"""
    global _neo4j_service
    if _neo4j_service is None:
        _neo4j_service = Neo4jService()
    return _neo4j_service

