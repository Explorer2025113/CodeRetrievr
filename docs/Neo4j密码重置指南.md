# Neo4j 密码重置指南

## 问题描述

如果遇到 `Neo.ClientError.Security.Unauthorized` 错误，说明Neo4j的密码配置不正确。

## 原因

Neo4j容器在首次启动时会初始化数据库，如果：
1. 容器已经存在并使用旧密码初始化
2. `.env`文件中的密码与`docker-compose.yml`中的密码不一致
3. 容器启动时密码设置失败

就会导致认证失败。

## 解决方案

### 方案1：重置Neo4j容器（推荐）

```bash
# 1. 停止并删除Neo4j容器
docker-compose stop neo4j
docker-compose rm -f neo4j

# 2. 删除Neo4j数据卷（注意：这会删除所有数据）
docker volume rm code-retrievr_neo4j_data
docker volume rm code-retrievr_neo4j_logs

# 3. 确保.env文件中的密码与docker-compose.yml一致
# .env: NEO4J_PASSWORD=your_actual_password_123
# docker-compose.yml: NEO4J_AUTH=neo4j/your_actual_password_123

# 4. 重新启动容器
docker-compose up -d neo4j
```

### 方案2：通过Web界面重置密码

1. 访问Neo4j Web界面：http://localhost:7474
2. 使用默认用户名：`neo4j`
3. 如果提示需要重置密码，输入新密码：`your_actual_password_123`
4. 更新`.env`文件中的`NEO4J_PASSWORD`

### 方案3：在容器内重置密码

```bash
# 进入Neo4j容器
docker exec -it code-retrievr-neo4j bash

# 使用cypher-shell重置密码
cypher-shell -u neo4j -p <旧密码>
# 然后执行：
# CALL dbms.security.changePassword('your_actual_password_123');
```

## 验证

```bash
# 测试连接
docker exec code-retrievr-neo4j cypher-shell -u neo4j -p your_actual_password_123 "RETURN 1"
```

如果返回 `1`，说明密码正确。

## 注意事项

1. **首次启动**：Neo4j首次启动时会要求设置密码，如果使用`NEO4J_AUTH`环境变量，会自动设置
2. **数据持久化**：Neo4j数据存储在Docker卷中，删除卷会丢失所有数据
3. **密码一致性**：确保`.env`和`docker-compose.yml`中的密码一致

## 推荐配置

在`.env`文件中：
```
NEO4J_PASSWORD=your_actual_password_123
```

在`docker-compose.yml`中：
```yaml
environment:
  - NEO4J_AUTH=neo4j/your_actual_password_123
```

两者必须完全一致！

