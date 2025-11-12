# CodeRetrievr 前端

基于 React + TypeScript + Vite + Ant Design 的代码检索前端应用。

## 功能特性

- 🔍 自然语言代码检索
- 📝 代码高亮显示
- 📋 一键复制代码
- 📖 AI生成复用说明（Markdown渲染）
- 🎨 现代化UI设计
- 📱 响应式布局

## 技术栈

- **React 18** - UI框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Ant Design 5** - UI组件库
- **React Router** - 路由管理
- **Axios** - HTTP客户端
- **React Syntax Highlighter** - 代码高亮
- **React Markdown** - Markdown渲染

## 快速开始

### 安装依赖

```bash
cd frontend
npm install
# 或
yarn install
# 或
pnpm install
```

### 开发模式

```bash
npm run dev
```

前端将在 http://localhost:3000 启动

### 构建生产版本

```bash
npm run build
```

构建产物将在 `dist` 目录中

### 预览生产版本

```bash
npm run preview
```

## 环境变量

创建 `.env` 文件（可选）：

```env
VITE_API_BASE_URL=http://localhost:8000
```

如果不设置，默认使用 `http://localhost:8000`

## 项目结构

```
frontend/
├── src/
│   ├── components/       # 组件
│   │   ├── Header.tsx
│   │   ├── SearchResults.tsx
│   │   ├── CodeDisplay.tsx
│   │   └── ExplanationDisplay.tsx
│   ├── pages/           # 页面
│   │   └── SearchPage.tsx
│   ├── services/        # API服务
│   │   └── api.ts
│   ├── App.tsx          # 主应用
│   └── main.tsx         # 入口文件
├── public/              # 静态资源
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 功能说明

### 搜索功能

- 支持自然语言查询
- 支持按编程语言筛选
- 支持设置返回数量
- 支持生成AI复用说明

### 代码展示

- 语法高亮
- 行号显示
- 代码复制
- 代码折叠/展开

### 复用说明

- Markdown渲染
- 代码示例高亮
- 可折叠展示

## 开发说明

### API接口

前端通过 `/api` 代理访问后端API，代理配置在 `vite.config.ts` 中：

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ''),
    },
  },
}
```

### 组件说明

- **SearchPage**: 搜索页面，包含搜索表单和结果展示
- **SearchResults**: 搜索结果列表组件
- **CodeDisplay**: 代码展示组件，支持高亮和复制
- **ExplanationDisplay**: 复用说明展示组件，支持Markdown渲染

## 注意事项

1. 确保后端API服务已启动（默认端口8000）
2. 后端需要启用CORS，允许前端域名访问
3. 代码高亮使用Prism，支持多种编程语言
4. Markdown渲染支持GitHub Flavored Markdown (GFM)

## 故障排除

### 无法连接到后端API

- 检查后端服务是否启动
- 检查 `VITE_API_BASE_URL` 配置
- 检查后端CORS配置

### 代码高亮不显示

- 检查 `react-syntax-highlighter` 是否正确安装
- 检查语言名称是否正确

### Markdown渲染异常

- 检查 `react-markdown` 和 `remark-gfm` 是否正确安装
- 检查Markdown内容格式

## 许可证

MIT License

