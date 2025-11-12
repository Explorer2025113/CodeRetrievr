import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error)
    
    // 统一错误处理
    if (error.response) {
      // 服务器返回了错误响应
      const status = error.response.status
      const message = error.response.data?.detail || error.response.data?.message || '请求失败'
      
      // 可以根据状态码进行不同的处理
      if (status === 401) {
        // 未授权，可能需要登录
        console.error('未授权访问')
      } else if (status === 404) {
        // 资源不存在
        console.error('资源不存在')
      } else if (status >= 500) {
        // 服务器错误
        console.error('服务器错误')
      }
    } else if (error.request) {
      // 请求已发出，但没有收到响应
      console.error('网络错误，请检查网络连接')
    } else {
      // 请求配置错误
      console.error('请求配置错误:', error.message)
    }
    
    return Promise.reject(error)
  }
)

// API 类型定义
export interface SearchRequest {
  query: string
  top_k?: number
  language?: string
  dependency?: string
  repo_name?: string
  explain?: boolean
  explain_top_n?: number
}

export interface SearchResultItem {
  id: number | string
  score: number
  code_id?: string
  code?: string
  name?: string
  type?: string
  language?: string
  file_path?: string
  repo_name?: string
  repo_url?: string
  dependencies?: string[]
  related_codes?: string[]
  explanation?: string
}

export interface SearchResponse {
  query: string
  top_k: number
  results: SearchResultItem[]
}

export interface StatisticsResponse {
  total_code_snippets: number
  total_libraries: number
  total_languages: number
  language_distribution: Record<string, number>
  repo_distribution: Record<string, number>
  top_dependencies: Record<string, number>
  milvus_stats: Record<string, any>
  neo4j_stats: Record<string, any>
}

export interface CodeSnippet {
  code_id?: string
  code: string
  name?: string
  type?: string
  language: string
  file_path?: string
  repo_name?: string
  repo_url?: string
  dependencies?: string[]
}

export interface CodeSnippetWithId extends CodeSnippet {
  code_id: string
}

// API 方法
export const api = {
  // 搜索代码
  searchCode: async (params: SearchRequest): Promise<SearchResponse> => {
    const response = await apiClient.post<SearchResponse>('/search', params)
    return response.data
  },

  // 健康检查
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await apiClient.get<{ status: string }>('/health')
    return response.data
  },

  // 获取统计信息
  getStatistics: async (): Promise<StatisticsResponse> => {
    const response = await apiClient.get<StatisticsResponse>('/stats')
    return response.data
  },

  // 获取代码列表
  getCodeSnippets: async (params?: {
    skip?: number
    limit?: number
    language?: string
    repo_name?: string
  }): Promise<CodeSnippet[]> => {
    const response = await apiClient.get<CodeSnippet[]>('/code', { params })
    return response.data
  },

  // 获取代码详情
  getCodeSnippet: async (codeId: string): Promise<CodeSnippet> => {
    const response = await apiClient.get<CodeSnippet>(`/code/${codeId}`)
    return response.data
  },

  // 添加代码片段
  addCodeSnippet: async (snippet: CodeSnippet): Promise<CodeSnippet> => {
    const response = await apiClient.post<CodeSnippet>('/code', snippet)
    return response.data
  },

  // 更新代码片段
  updateCodeSnippet: async (codeId: string, snippet: Partial<CodeSnippet>): Promise<CodeSnippet> => {
    const response = await apiClient.put<CodeSnippet>(`/code/${codeId}`, snippet)
    return response.data
  },

  // 删除代码片段
  deleteCodeSnippet: async (codeId: string): Promise<void> => {
    await apiClient.delete(`/code/${codeId}`)
  },
}

export default api

