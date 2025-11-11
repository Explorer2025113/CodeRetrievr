# Neo4j连接问题解决方案

## 问题症状

运行向量化脚本时出现错误：
```
Exception: 连接Neo4j失败: {code: Neo.ClientError.Security.Unauthorized} {message: The client is unauthorized due to authentication failure.}
```

## 原因分析

1. Neo4j容器在首次启动时使用的密码与配置不同
2. 容器已经用旧密码初始化，即使修改了配置也不会生效
3. `.env`文件和`docker-compose.yml`中的密码不一致

## 解决方案

### 方案1：重置Neo4j容器（推荐，彻底解决）

```powershell
# 1. 停止Neo4j容器
docker-compose stop neo4j

# 2. 删除Neo4j容器
docker-compose rm -f neo4j

# 3. 删除Neo4j数据卷（注意：这会删除所有数据）
docker volume rm code-retrievr_neo4j_data
docker volume rm code-retrievr_neo4j_logs

# 4. 确保.env文件中的密码与docker-compose.yml一致
# .env: NEO4J_PASSWORD=your_actual_password_123
# docker-compose.yml: NEO4J_AUTH=neo4j/your_actual_password_123

# 5. 重新启动容器
docker-compose up -d neo4j

# 6. 等待容器启动（约30-60秒）
docker logs -f code-retrievr-neo4j
```

### 方案2：通过Web界面重置密码

1. 访问Neo4j Web界面：http://localhost:7474
2. 使用默认用户名：`neo4j`
3. 尝试以下密码：
   - `neo4j` (默认初始密码)
   - `your_actual_password_123` (配置的密码)
4. 如果登录成功，可以修改密码
5. 更新`.env`文件中的`NEO4J_PASSWORD`为实际密码

### 方案3：在容器内重置密码

```powershell
# 进入Neo4j容器
docker exec -it code-retrievr-neo4j bash

# 使用cypher-shell重置密码
cypher-shell -u neo4j -p neo4j
# 如果上面的密码不对，尝试：
# cypher-shell -u neo4j -p your_actual_password_123

# 在cypher-shell中执行：
CALL dbms.security.changePassword('your_actual_password_123');
# 然后退出：:exit

# 更新.env文件
# NEO4J_PASSWORD=your_actual_password_123
```

### 方案4：临时跳过Neo4j（仅使用Milvus）

如果暂时不需要Neo4j，可以修改脚本，让Neo4j变成可选的。

## 验证连接

```powershell
# 测试连接
docker exec code-retrievr-neo4j cypher-shell -u neo4j -p your_actual_password_123 "RETURN 1"
```

如果返回 `1`，说明密码正确。

## 检查配置一致性

确保以下配置完全一致：

1. **.env文件**:
   ```
   NEO4J_PASSWORD=your_actual_password_123
   ```

2. **docker-compose.yml**:
   ```yaml
   environment:
     - NEO4J_AUTH=neo4j/your_actual_password_123
   ```

3. **健康检查**:
   ```yaml
   test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "your_actual_password_123", "RETURN 1"]
   ```

## 常见问题

### Q: 为什么容器内测试密码通过，但Python连接失败？

A: 可能是：
1. Python使用的连接字符串不正确
2. Neo4j的Bolt协议版本问题
3. 密码中有特殊字符或空格

### Q: 重置容器会丢失数据吗？

A: 是的，删除数据卷会丢失所有Neo4j数据。如果已有重要数据，请先备份。

### Q: 如何备份Neo4j数据？

A: 
```powershell
# 导出数据
docker exec code-retrievr-neo4j neo4j-admin database dump --database=neo4j --to-path=/data/backup

# 或者直接备份数据卷
docker run --rm -v code-retrievr_neo4j_data:/data -v ${PWD}:/backup alpine tar czf /backup/neo4j_backup.tar.gz /data
```

