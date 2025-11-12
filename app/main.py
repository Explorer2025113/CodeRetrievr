"""
FastAPI应用主入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from app.core.config import settings
from app.services.embedding_service import get_embedding_service
from app.services.milvus_service import get_milvus_service
from app.services.neo4j_service import get_neo4j_service
from app.services.llm_service import get_llm_service
from app.services.cache_service import get_cache_service

app = FastAPI(
    title="CodeRetrievr API",
    description="基于矢量数据库的代码检索与复用平台",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to CodeRetrievr API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


# ===== 检索 API =====
class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    language: Optional[str] = None      # 可选的语言过滤
    dependency: Optional[str] = None    # 可选的依赖库过滤
    repo_name: Optional[str] = None     # 可选的仓库过滤
    explain: bool = False               # 是否生成复用说明
    explain_top_n: int = 1              # 生成前N条的说明（其余只返回基础信息）


class SearchResultItem(BaseModel):
    id: Any
    score: float
    code_id: Optional[str] = None
    code: Optional[str] = None  # 代码内容
    name: Optional[str] = None
    type: Optional[str] = None
    language: Optional[str] = None
    file_path: Optional[str] = None
    repo_name: Optional[str] = None
    repo_url: Optional[str] = None
    # 关联信息
    dependencies: Optional[List[str]] = None
    related_codes: Optional[List[str]] = None
    explanation: Optional[str] = None  # 复用说明（可选）


class SearchResponse(BaseModel):
    query: str
    top_k: int
    results: List[SearchResultItem]


@app.post("/search", response_model=SearchResponse)
async def search_code(req: SearchRequest) -> SearchResponse:
    """
    自然语言检索代码片段：query -> 向量 -> Milvus搜索 -> Neo4j补充信息
    """
    # 1) 向量化查询
    embedding_service = get_embedding_service()
    query_vec = embedding_service.encode_code(req.query)

    # 2) Milvus 检索
    milvus_service = get_milvus_service()
    filter_expr = None
    if req.language:
        # 简单过滤表达式
        filter_expr = f"language == '{req.language}'"
    
    # 如果需要按仓库筛选，也添加到Milvus过滤条件
    if req.repo_name:
        if filter_expr:
            filter_expr = f"{filter_expr} && repo_name == '{req.repo_name}'"
        else:
            filter_expr = f"repo_name == '{req.repo_name}'"
    
    # 如果需要在Neo4j中筛选依赖库，增加搜索数量（因为依赖库筛选在Neo4j中进行）
    # 仓库筛选已经在Milvus中完成，所以不需要增加搜索数量
    search_k = req.top_k * 3 if req.dependency else req.top_k
    milvus_hits = milvus_service.search(query_vec, top_k=search_k, filter_expr=filter_expr)

    # 3) 用 Neo4j 补充关联信息并应用依赖库筛选
    neo4j_service = get_neo4j_service()
    enriched_results: List[SearchResultItem] = []
    filtered_count = 0
    
    for hit in milvus_hits:
        # 如果已经达到所需数量，停止处理
        if len(enriched_results) >= req.top_k:
            break
        # Milvus返回的是L2距离，越小越相似
        # 转换为相似度分数：similarity = 1 / (1 + distance)
        # 这样距离为0时相似度为1，距离越大相似度越小
        distance = float(hit.get("score", 0.0))
        similarity = 1.0 / (1.0 + distance)  # 转换为0-1之间的相似度
        
        item: Dict[str, Any] = {
            "id": hit.get("id"),
            "score": similarity,  # 使用转换后的相似度分数
            "distance": distance,  # 保留原始距离值（可选）
            "code_id": hit.get("code_id"),
            "code": hit.get("code"),  # 添加代码内容
            "name": hit.get("name"),
            "type": hit.get("type"),
            "language": hit.get("language"),
            "file_path": hit.get("file_path"),
            "repo_name": hit.get("repo_name"),
            "repo_url": hit.get("repo_url"),
        }
        code_id = hit.get("code_id")
        should_include = True
        
        # 如果指定了依赖库筛选，检查代码是否使用该依赖库
        if req.dependency and code_id:
            try:
                info = neo4j_service.get_code_snippet_info(code_id)
                if info:
                    item["dependencies"] = info.get("dependencies") or []
                    item["related_codes"] = info.get("similar_codes") or []
                    # 检查是否包含指定的依赖库
                    dependencies = item.get("dependencies", [])
                    if req.dependency not in dependencies:
                        should_include = False
                else:
                    # 如果Neo4j中没有信息，且要求依赖库筛选，则排除
                    should_include = False
            except Exception:
                # 如果查询失败，且要求依赖库筛选，则排除
                if req.dependency:
                    should_include = False
        elif code_id:
            # 没有依赖库筛选要求，但仍需要补充信息
            try:
                info = neo4j_service.get_code_snippet_info(code_id)
                if info:
                    item["dependencies"] = info.get("dependencies") or []
                    item["related_codes"] = info.get("similar_codes") or []
            except Exception:
                # 忽略单条补充失败，保证检索可用
                pass
        
        # 只有通过所有筛选条件才添加到结果中
        if should_include:
            enriched_results.append(SearchResultItem(**item))
            filtered_count += 1

    # 4) 生成复用说明（可选，仅对前N条）
    if req.explain and enriched_results:
        try:
            llm = get_llm_service()
            limit = min(req.explain_top_n, len(enriched_results))
            for i in range(limit):
                r = enriched_results[i]
                # 需要原始代码文本用于说明生成：从 Milvus 命中中取回的 code 字段
                # 为简洁，使用上面 milvus_hits 的 code 对应索引
                code_text = milvus_hits[i].get("code") or ""
                # 防止提示词过长导致模型拒绝或超限，截断到合理长度
                if code_text and len(code_text) > 2000:
                    code_text = code_text[:2000]
                try:
                    r.explanation = await llm.generate_code_reuse_instruction(
                        code_snippet=code_text,
                        language=r.language or "python",
                        dependencies=r.dependencies or [],
                        user_query=req.query
                    )
                except Exception:
                    # 单条失败不影响整体
                    r.explanation = None
        except Exception:
            # 忽略说明生成阶段的总失败
            pass

    return SearchResponse(query=req.query, top_k=req.top_k, results=enriched_results)


# ===== 统计 API =====
class StatisticsResponse(BaseModel):
    total_code_snippets: int
    total_libraries: int
    total_languages: int
    language_distribution: Dict[str, int]
    repo_distribution: Dict[str, int]
    top_dependencies: Dict[str, int]
    milvus_stats: Dict[str, Any]
    neo4j_stats: Dict[str, Any]


@app.get("/stats", response_model=StatisticsResponse)
async def get_statistics() -> StatisticsResponse:
    """
    获取代码库统计信息（带缓存，缓存5分钟）
    """
    cache_service = get_cache_service()
    cache_key = "statistics"
    
    # 尝试从缓存获取
    cached_stats = cache_service.get(cache_key)
    if cached_stats:
        return cached_stats
    
    try:
        # 获取Milvus统计（基本信息）
        milvus_service = get_milvus_service()
        milvus_stats = milvus_service.get_collection_stats()
        
        # 获取Neo4j统计（详细统计信息）
        neo4j_service = get_neo4j_service()
        neo4j_stats = neo4j_service.get_statistics()
        language_distribution = neo4j_service.get_language_distribution()
        repo_distribution = neo4j_service.get_repo_distribution(limit=20)
        top_deps = neo4j_service.get_top_dependencies(limit=20)
        
        stats = StatisticsResponse(
            total_code_snippets=milvus_stats.get("num_entities", 0),
            total_libraries=neo4j_stats.get("libraries", 0),
            total_languages=neo4j_stats.get("languages", 0),
            language_distribution=language_distribution,
            repo_distribution=repo_distribution,
            top_dependencies=top_deps,
            milvus_stats=milvus_stats,
            neo4j_stats=neo4j_stats,
        )
        
        # 缓存结果（5分钟）
        cache_service.set(cache_key, stats, ttl=300)
        
        return stats
    except Exception as e:
        # 如果某个服务失败，返回部分统计信息
        import traceback
        print(f"获取统计信息时出错: {str(e)}")
        print(traceback.format_exc())
        # 返回空统计，避免完全失败
        return StatisticsResponse(
            total_code_snippets=0,
            total_libraries=0,
            total_languages=0,
            language_distribution={},
            repo_distribution={},
            top_dependencies={},
            milvus_stats={},
            neo4j_stats={},
        )


# ===== 代码管理 API =====
class CodeSnippetRequest(BaseModel):
    code: str
    name: Optional[str] = None
    type: Optional[str] = None
    language: str
    file_path: Optional[str] = None
    repo_name: Optional[str] = None
    repo_url: Optional[str] = None
    dependencies: Optional[List[str]] = None


class CodeSnippetResponse(BaseModel):
    code_id: str
    code: str
    name: Optional[str] = None
    type: Optional[str] = None
    language: str
    file_path: Optional[str] = None
    repo_name: Optional[str] = None
    repo_url: Optional[str] = None
    dependencies: Optional[List[str]] = None


@app.get("/code", response_model=List[CodeSnippetResponse])
async def list_code_snippets(
    skip: int = 0,
    limit: int = 100,
    language: Optional[str] = None,
    repo_name: Optional[str] = None
) -> List[CodeSnippetResponse]:
    """
    获取代码片段列表
    """
    try:
        neo4j_service = get_neo4j_service()
        with neo4j_service.driver.session() as session:
            # 构建查询
            query = "MATCH (c:CodeSnippet)"
            conditions = []
            params = {}
            
            if language:
                conditions.append("c.language = $language")
                params["language"] = language
            if repo_name:
                conditions.append("c.repo_name = $repo_name")
                params["repo_name"] = repo_name
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " RETURN c.code_id as code_id, c.name as name, c.type as type, "
            query += "c.language as language, c.file_path as file_path, "
            query += "c.repo_name as repo_name, c.repo_url as repo_url "
            query += f"SKIP $skip LIMIT $limit"
            
            params["skip"] = skip
            params["limit"] = limit
            
            result = session.run(query, params)
            codes = []
            
            milvus_service = get_milvus_service()
            for record in result:
                code_id = record["code_id"]
                # 从Milvus获取代码内容
                milvus_data = milvus_service.get_by_code_id(code_id)
                # 获取依赖库
                info = neo4j_service.get_code_snippet_info(code_id)
                codes.append(CodeSnippetResponse(
                    code_id=code_id,
                    code=milvus_data.get("code", "") if milvus_data else "",
                    name=record.get("name") or (milvus_data.get("name") if milvus_data else None),
                    type=record.get("type") or (milvus_data.get("type") if milvus_data else None),
                    language=record.get("language", "python") or (milvus_data.get("language", "python") if milvus_data else "python"),
                    file_path=record.get("file_path") or (milvus_data.get("file_path") if milvus_data else None),
                    repo_name=record.get("repo_name") or (milvus_data.get("repo_name") if milvus_data else None),
                    repo_url=record.get("repo_url") or (milvus_data.get("repo_url") if milvus_data else None),
                    dependencies=info.get("dependencies", []) if info else [],
                ))
            
            return codes
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"获取代码列表失败: {str(e)}")


@app.get("/code/{code_id}", response_model=CodeSnippetResponse)
async def get_code_snippet(code_id: str) -> CodeSnippetResponse:
    """
    获取代码片段详情
    """
    try:
        neo4j_service = get_neo4j_service()
        info = neo4j_service.get_code_snippet_info(code_id)
        
        if not info:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="代码片段不存在")
        
        # 从Milvus获取代码内容
        milvus_service = get_milvus_service()
        milvus_data = milvus_service.get_by_code_id(code_id)
        
        return CodeSnippetResponse(
            code_id=info.get("code_id", code_id),
            code=milvus_data.get("code", "") if milvus_data else "",
            name=info.get("name") or (milvus_data.get("name") if milvus_data else None),
            type=info.get("type") or (milvus_data.get("type") if milvus_data else None),
            language=info.get("language", "python") or (milvus_data.get("language", "python") if milvus_data else "python"),
            file_path=info.get("file_path") or (milvus_data.get("file_path") if milvus_data else None),
            repo_name=info.get("repo_name") or (milvus_data.get("repo_name") if milvus_data else None),
            repo_url=info.get("repo_url") or (milvus_data.get("repo_url") if milvus_data else None),
            dependencies=info.get("dependencies", []),
        )
    except Exception as e:
        from fastapi import HTTPException
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"获取代码片段失败: {str(e)}")


@app.post("/code", response_model=CodeSnippetResponse)
async def add_code_snippet(snippet: CodeSnippetRequest) -> CodeSnippetResponse:
    """
    添加代码片段
    """
    import uuid
    
    try:
        # 生成唯一ID
        code_id = str(uuid.uuid4())
        
        # 向量化代码
        embedding_service = get_embedding_service()
        code_vec = embedding_service.encode_code(snippet.code)
        
        # 插入到Milvus
        milvus_service = get_milvus_service()
        milvus_ids = milvus_service.insert_code_snippets(
            code_snippets=[{
                "code_id": code_id,
                "code": snippet.code,
                "name": snippet.name or "",
                "type": snippet.type or "function",
                "language": snippet.language,
                "file_path": snippet.file_path or "",
                "repo_name": snippet.repo_name or "",
                "repo_url": snippet.repo_url or "",
            }],
            vectors=[code_vec]
        )
        milvus_id = milvus_ids[0] if milvus_ids else None
        
        # 插入到Neo4j
        neo4j_service = get_neo4j_service()
        neo4j_service.create_code_snippet_node(
            code_id=code_id,
            name=snippet.name or "",
            code_type=snippet.type or "function",
            language=snippet.language,
            file_path=snippet.file_path or "",
            repo_name=snippet.repo_name or "",
            repo_url=snippet.repo_url or "",
            milvus_id=milvus_id
        )
        
        # 创建依赖关系
        if snippet.dependencies:
            neo4j_service.create_dependency_relationships(code_id, snippet.dependencies)
        
        # 创建语言关系
        neo4j_service.create_language_relationship(code_id, snippet.language)
        
        # 清除统计信息缓存（因为数据已更新）
        cache_service = get_cache_service()
        cache_service.delete("statistics")
        
        return CodeSnippetResponse(
            code_id=code_id,
            code=snippet.code,
            name=snippet.name,
            type=snippet.type,
            language=snippet.language,
            file_path=snippet.file_path,
            repo_name=snippet.repo_name,
            repo_url=snippet.repo_url,
            dependencies=snippet.dependencies,
        )
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"添加代码片段失败: {str(e)}")


@app.put("/code/{code_id}", response_model=CodeSnippetResponse)
async def update_code_snippet(
    code_id: str,
    snippet: CodeSnippetRequest
) -> CodeSnippetResponse:
    """
    更新代码片段
    """
    try:
        # 检查代码片段是否存在
        neo4j_service = get_neo4j_service()
        info = neo4j_service.get_code_snippet_info(code_id)
        
        if not info:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="代码片段不存在")
        
        # 更新Milvus中的数据（需要删除旧数据并插入新数据）
        milvus_service = get_milvus_service()
        # 删除旧数据
        milvus_service.delete_by_code_id(code_id)
        # 向量化新代码
        embedding_service = get_embedding_service()
        code_vec = embedding_service.encode_code(snippet.code)
        # 插入新数据
        milvus_ids = milvus_service.insert_code_snippets(
            code_snippets=[{
                "code_id": code_id,
                "code": snippet.code,
                "name": snippet.name or "",
                "type": snippet.type or "function",
                "language": snippet.language,
                "file_path": snippet.file_path or "",
                "repo_name": snippet.repo_name or "",
                "repo_url": snippet.repo_url or "",
            }],
            vectors=[code_vec]
        )
        milvus_id = milvus_ids[0] if milvus_ids else None
        
        # 更新Neo4j中的节点
        neo4j_service.create_code_snippet_node(
            code_id=code_id,
            name=snippet.name or "",
            code_type=snippet.type or "function",
            language=snippet.language,
            file_path=snippet.file_path or "",
            repo_name=snippet.repo_name or "",
            repo_url=snippet.repo_url or "",
            milvus_id=milvus_id
        )
        
        # 删除旧依赖关系，创建新依赖关系
        with neo4j_service.driver.session() as session:
            # 删除旧依赖关系
            delete_query = """
            MATCH (c:CodeSnippet {code_id: $code_id})-[r:DEPENDS_ON]->()
            DELETE r
            """
            session.run(delete_query, code_id=code_id)
        
        # 创建新依赖关系
        if snippet.dependencies:
            neo4j_service.create_dependency_relationships(code_id, snippet.dependencies)
        
        # 清除统计信息缓存（因为数据已更新）
        cache_service = get_cache_service()
        cache_service.delete("statistics")
        
        return CodeSnippetResponse(
            code_id=code_id,
            code=snippet.code,
            name=snippet.name,
            type=snippet.type,
            language=snippet.language,
            file_path=snippet.file_path,
            repo_name=snippet.repo_name,
            repo_url=snippet.repo_url,
            dependencies=snippet.dependencies,
        )
    except Exception as e:
        from fastapi import HTTPException
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"更新代码片段失败: {str(e)}")


@app.delete("/code/{code_id}")
async def delete_code_snippet(code_id: str):
    """
    删除代码片段
    """
    try:
        # 检查代码片段是否存在
        neo4j_service = get_neo4j_service()
        info = neo4j_service.get_code_snippet_info(code_id)
        
        if not info:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="代码片段不存在")
        
        # 从Milvus删除
        milvus_service = get_milvus_service()
        milvus_deleted = milvus_service.delete_by_code_id(code_id)
        
        # 从Neo4j删除节点和关系
        with neo4j_service.driver.session() as session:
            # 删除节点及其所有关系
            query = """
            MATCH (c:CodeSnippet {code_id: $code_id})
            DETACH DELETE c
            """
            session.run(query, code_id=code_id)
        
        if not milvus_deleted:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Milvus中未找到该代码片段")
        
        # 清除统计信息缓存（因为数据已更新）
        cache_service = get_cache_service()
        cache_service.delete("statistics")
        
        return {"message": "代码片段已删除", "code_id": code_id}
    except Exception as e:
        from fastapi import HTTPException
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"删除代码片段失败: {str(e)}")

