import { useState, useEffect } from 'react'
import { Card, Input, Button, Select, Space, Spin, message, Checkbox, Tabs } from 'antd'
import { SearchOutlined, ReloadOutlined, BarChartOutlined, SettingOutlined } from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import { api, SearchResultItem } from '../services/api'
import SearchResults from '../components/SearchResults'
import StatisticsDisplay from '../components/StatisticsDisplay'
import CodeManagementPage from './CodeManagementPage'
import './SearchPage.css'

const { TextArea } = Input
const { Option } = Select
const { TabPane } = Tabs

const SearchPage = () => {
  const { t } = useTranslation()
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
      message.warning(t('search.enterKeywords'))
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
        message.info(t('search.noResults'))
      }
    } catch (error: any) {
      console.error('Search error:', error)
      const errorMessage = error?.response?.data?.detail || error?.message || t('search.searchFailed')
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
        <TabPane tab={<span><SearchOutlined />{t('tabs.search')}</span>} key="search">
          <Card className="search-card" title={t('search.title')}>
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>
              {t('search.query')}
            </label>
            <TextArea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={t('search.queryPlaceholder')}
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
                {t('search.language')}
              </label>
              <Select
                value={language}
                onChange={setLanguage}
                placeholder={t('search.allLanguages')}
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
                {t('search.dependency')}
              </label>
              <Select
                value={dependency}
                onChange={setDependency}
                placeholder={t('search.allDependencies')}
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
                {t('search.repo')}
              </label>
              <Select
                value={repoName}
                onChange={setRepoName}
                placeholder={t('search.allRepos')}
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
                {t('search.topK')}
              </label>
              <Select
                value={topK}
                onChange={setTopK}
                style={{ width: 120 }}
              >
                <Option value={5}>5</Option>
                <Option value={10}>10</Option>
                <Option value={20}>20</Option>
                <Option value={50}>50</Option>
              </Select>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>
                {t('search.explain')}
              </label>
              <Checkbox
                checked={explain}
                onChange={(e) => setExplain(e.target.checked)}
              >
                {t('search.explainLabel')}
              </Checkbox>
            </div>

            {explain && (
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>
                  {t('search.explainCount')}
                </label>
                <Select
                  value={explainTopN}
                  onChange={setExplainTopN}
                  style={{ width: 120 }}
                >
                  <Option value={1}>1</Option>
                  <Option value={3}>3</Option>
                  <Option value={5}>5</Option>
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
              {t('search.search')}
            </Button>
            <Button
              icon={<ReloadOutlined />}
              onClick={handleReset}
              size="large"
            >
              {t('search.reset')}
            </Button>
          </Space>

              <div style={{ fontSize: '12px', color: '#666' }}>
                {t('search.tip')}
              </div>
            </Space>
          </Card>

          {loading && (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <Spin size="large" tip={t('search.searching')} />
            </div>
          )}

          {!loading && results.length > 0 && (
            <SearchResults results={results} />
          )}
        </TabPane>
        <TabPane tab={<span><BarChartOutlined />{t('tabs.stats')}</span>} key="stats">
          <StatisticsDisplay />
        </TabPane>
        <TabPane tab={<span><SettingOutlined />{t('tabs.manage')}</span>} key="manage">
          <CodeManagementPage />
        </TabPane>
      </Tabs>
    </div>
  )
}

export default SearchPage

