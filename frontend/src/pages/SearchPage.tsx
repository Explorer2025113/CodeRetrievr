import { useState, useEffect } from 'react'
import { Card, Input, Button, Select, Space, Spin, message, Checkbox, Tabs } from 'antd'
import { SearchOutlined, ReloadOutlined, BarChartOutlined, SettingOutlined } from '@ant-design/icons'
import { api, SearchResultItem } from '../services/api'
import SearchResults from '../components/SearchResults'
import StatisticsDisplay from '../components/StatisticsDisplay'
import CodeManagementPage from './CodeManagementPage'
import './SearchPage.css'

const { TextArea } = Input
const { Option } = Select
const { TabPane } = Tabs

const SearchPage = () => {
  const [activeTab, setActiveTab] = useState('search')
  const [query, setQuery] = useState('')
  const [language, setLanguage] = useState<string | undefined>(undefined)
  const [dependency, setDependency] = useState<string | undefined>(undefined)
  const [repoName, setRepoName] = useState<string | undefined>(undefined)
  const [topK, setTopK] = useState(10)
  const [explain, setExplain] = useState(false)
  const [explainTopN, setExplainTopN] = useState(1)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<SearchResultItem[]>([])
  const [availableDependencies, setAvailableDependencies] = useState<string[]>([])
  const [availableRepos, setAvailableRepos] = useState<string[]>([])

  // 加载可用筛选选项
  useEffect(() => {
    loadFilterOptions()
  }, [])

  const loadFilterOptions = async () => {
    try {
      const stats = await api.getStatistics()
      setAvailableDependencies(Object.keys(stats.top_dependencies))
      setAvailableRepos(Object.keys(stats.repo_distribution))
    } catch (error) {
      console.error('Failed to load filter options:', error)
    }
  }

  const handleSearch = async () => {
    if (!query.trim()) {
      message.warning('请输入搜索关键词')
      return
    }

    setLoading(true)
    try {
      const response = await api.searchCode({
        query: query.trim(),
        top_k: topK,
        language: language || undefined,
        dependency: dependency || undefined,
        repo_name: repoName || undefined,
        explain,
        explain_top_n: explainTopN,
      })
      setResults(response.results)
      if (response.results.length === 0) {
        message.info('未找到相关代码片段')
      }
    } catch (error: any) {
      console.error('Search error:', error)
      const errorMessage = error?.response?.data?.detail || error?.message || '搜索失败，请稍后重试'
      message.error({
        content: errorMessage,
        duration: 5,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setQuery('')
    setLanguage(undefined)
    setDependency(undefined)
    setRepoName(undefined)
    setTopK(10)
    setExplain(false)
    setExplainTopN(1)
    setResults([])
  }

  return (
    <div className="search-page">
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane tab={<span><SearchOutlined />代码检索</span>} key="search">
          <Card className="search-card" title="代码检索">
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>
              搜索查询
            </label>
            <TextArea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="请输入自然语言描述，例如：如何实现快速排序、FastAPI路由处理、Python异步函数等"
              rows={3}
              onPressEnter={(e) => {
                if (e.ctrlKey || e.metaKey) {
                  handleSearch()
                }
              }}
            />
          </div>

          <Space wrap>
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>
                编程语言
              </label>
              <Select
                value={language}
                onChange={setLanguage}
                placeholder="全部语言"
                allowClear
                style={{ width: 150 }}
              >
                <Option value="python">Python</Option>
                <Option value="java">Java</Option>
                <Option value="cpp">C++</Option>
                <Option value="javascript">JavaScript</Option>
                <Option value="typescript">TypeScript</Option>
              </Select>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>
                依赖库
              </label>
              <Select
                value={dependency}
                onChange={setDependency}
                placeholder="全部依赖库"
                allowClear
                showSearch
                filterOption={(input, option) =>
                  (option?.children as unknown as string)?.toLowerCase().includes(input.toLowerCase())
                }
                style={{ width: 200 }}
              >
                {availableDependencies.map((dep) => (
                  <Option key={dep} value={dep}>
                    {dep}
                  </Option>
                ))}
              </Select>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>
                仓库
              </label>
              <Select
                value={repoName}
                onChange={setRepoName}
                placeholder="全部仓库"
                allowClear
                showSearch
                filterOption={(input, option) =>
                  (option?.children as unknown as string)?.toLowerCase().includes(input.toLowerCase())
                }
                style={{ width: 250 }}
              >
                {availableRepos.map((repo) => (
                  <Option key={repo} value={repo}>
                    {repo}
                  </Option>
                ))}
              </Select>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>
                返回数量
              </label>
              <Select
                value={topK}
                onChange={setTopK}
                style={{ width: 120 }}
              >
                <Option value={5}>5 条</Option>
                <Option value={10}>10 条</Option>
                <Option value={20}>20 条</Option>
                <Option value={50}>50 条</Option>
              </Select>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>
                生成说明
              </label>
              <Checkbox
                checked={explain}
                onChange={(e) => setExplain(e.target.checked)}
              >
                生成复用说明
              </Checkbox>
            </div>

            {explain && (
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>
                  说明数量
                </label>
                <Select
                  value={explainTopN}
                  onChange={setExplainTopN}
                  style={{ width: 120 }}
                >
                  <Option value={1}>1 条</Option>
                  <Option value={3}>3 条</Option>
                  <Option value={5}>5 条</Option>
                </Select>
              </div>
            )}
          </Space>

          <Space>
            <Button
              type="primary"
              icon={<SearchOutlined />}
              onClick={handleSearch}
              loading={loading}
              size="large"
            >
              搜索
            </Button>
            <Button
              icon={<ReloadOutlined />}
              onClick={handleReset}
              size="large"
            >
              重置
            </Button>
          </Space>

              <div style={{ fontSize: '12px', color: '#666' }}>
                💡 提示：按 Ctrl+Enter (Windows) 或 Cmd+Enter (Mac) 快速搜索
              </div>
            </Space>
          </Card>

          {loading && (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <Spin size="large" tip="正在搜索..." />
            </div>
          )}

          {!loading && results.length > 0 && (
            <SearchResults results={results} />
          )}
        </TabPane>
        <TabPane tab={<span><BarChartOutlined />统计信息</span>} key="stats">
          <StatisticsDisplay />
        </TabPane>
        <TabPane tab={<span><SettingOutlined />代码管理</span>} key="manage">
          <CodeManagementPage />
        </TabPane>
      </Tabs>
    </div>
  )
}

export default SearchPage

