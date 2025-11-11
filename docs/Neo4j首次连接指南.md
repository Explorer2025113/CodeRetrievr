# Neo4j 首次连接指南

## 重要说明

Neo4j **不需要注册**，只需要设置初始密码即可。

## 连接步骤

### 步骤1：使用默认密码连接

在Neo4j连接界面：

1. **Connect URL**: `neo4j://localhost:7687` 或 `bolt://localhost:7687`
2. **Username**: `neo4j`
3. **Password**: `neo4j`（这是默认初始密码）

点击 **Connect** 按钮

### 步骤2：设置新密码

首次连接成功后，Neo4j会要求你设置新密码：

1. **Current password**: `neo4j`（当前密码）
2. **New password**: `your_actual_password_123`（新密码）
3. **Confirm password**: `your_actual_password_123`（确认新密码）

点击 **Change Password** 或 **Set Password**

### 步骤3：使用新密码重新连接

设置新密码后，使用新密码重新连接：

1. **Username**: `neo4j`
2. **Password**: `your_actual_password_123`（刚设置的新密码）

## 验证配置

确保 `.env` 文件中的密码与新设置的密码一致：

```env
NEO4J_PASSWORD=your_actual_password_123
```

## 常见问题

### Q: 如果忘记密码怎么办？

A: 重置Neo4j容器：
```bash
docker-compose stop neo4j
docker-compose rm -f neo4j
docker-compose up -d neo4j
```
然后重新设置密码。

### Q: 连接URL应该填什么？

A: 
- 如果使用Neo4j Browser（Web界面）：`neo4j://localhost:7687`
- 如果使用代码连接：`bolt://localhost:7687`

### Q: 为什么一直提示认证失败？

A: 可能的原因：
1. 密码输入错误（注意大小写）
2. 容器还未完全启动（等待30-60秒）
3. 密码与`.env`文件不一致

## 连接成功后

连接成功后，你就可以：
1. 在Neo4j Browser中执行Cypher查询
2. 运行向量化脚本存储代码片段
3. 查看知识图谱数据

