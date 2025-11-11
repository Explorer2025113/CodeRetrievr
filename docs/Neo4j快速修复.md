# Neo4j 认证问题快速修复

## 问题
`Neo.ClientError.Security.Unauthorized` - Neo4j认证失败

## 快速解决方案

### 方法1：通过Web界面设置密码（最简单）

1. **访问Neo4j Web界面**：
   ```
   http://localhost:7474
   ```

2. **首次登录**：
   - 用户名：`neo4j`
   - 初始密码：`neo4j`（首次登录会要求修改）

3. **设置新密码**：
   - 输入新密码：`your_actual_password_123`
   - 确认密码：`your_actual_password_123`

4. **验证**：
   ```bash
   docker exec code-retrievr-neo4j cypher-shell -u neo4j -p your_actual_password_123 "RETURN 1"
   ```

### 方法2：等待容器完全启动

Neo4j容器需要30-60秒完全初始化，请等待后再测试：

```bash
# 等待60秒
Start-Sleep -Seconds 60

# 测试连接
docker exec code-retrievr-neo4j cypher-shell -u neo4j -p your_actual_password_123 "RETURN 1"
```

### 方法3：检查容器状态

```bash
# 查看容器日志
docker logs code-retrievr-neo4j --tail 50

# 查看容器状态
docker ps | Select-String neo4j
```

## 验证修复

运行向量化脚本：
```bash
conda activate coderetrievr
python scripts/vectorize_code.py data/code_snippets/code_snippets_tiangolo_fastapi_20251110_231137.json
```

如果Neo4j连接成功，会看到：
```
✅ 已连接到Neo4j: bolt://localhost:7687
```

