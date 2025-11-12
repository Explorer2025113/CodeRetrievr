import { useEffect, useState } from 'react'
import { Card, Row, Col, Statistic, Table, Tag, Spin, message } from 'antd'
import { CodeOutlined, DatabaseOutlined, FileTextOutlined, LinkOutlined } from '@ant-design/icons'
import { api, StatisticsResponse } from '../services/api'
import './StatisticsDisplay.css'

const StatisticsDisplay = () => {
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<StatisticsResponse | null>(null)

  useEffect(() => {
    loadStatistics()
  }, [])

  const loadStatistics = async () => {
    try {
      setLoading(true)
      const data = await api.getStatistics()
      setStats(data)
    } catch (error: any) {
      console.error('Failed to load statistics:', error)
      const errorMessage = error?.response?.data?.detail || error?.message || '加载统计信息失败'
      message.error({
        content: errorMessage,
        duration: 5,
      })
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <Spin size="large" tip="加载统计信息..." />
      </div>
    )
  }

  if (!stats) {
    return null
  }

  // 语言分布表格数据
  const languageData = Object.entries(stats.language_distribution)
    .map(([language, count]) => ({
      key: language,
      language,
      count,
      percentage: ((count / stats.total_code_snippets) * 100).toFixed(1),
    }))
    .sort((a, b) => b.count - a.count)

  // 仓库分布表格数据
  const repoData = Object.entries(stats.repo_distribution)
    .map(([repo, count]) => ({
      key: repo,
      repo,
      count,
      percentage: ((count / stats.total_code_snippets) * 100).toFixed(1),
    }))
    .sort((a, b) => b.count - a.count)

  // 依赖库表格数据
  const dependencyData = Object.entries(stats.top_dependencies)
    .map(([library, count]) => ({
      key: library,
      library,
      count,
    }))
    .sort((a, b) => b.count - a.count)

  const languageColumns = [
    {
      title: '编程语言',
      dataIndex: 'language',
      key: 'language',
      render: (text: string) => <Tag color="green">{text}</Tag>,
    },
    {
      title: '代码片段数',
      dataIndex: 'count',
      key: 'count',
      sorter: (a: any, b: any) => a.count - b.count,
    },
    {
      title: '占比',
      dataIndex: 'percentage',
      key: 'percentage',
      render: (text: string) => `${text}%`,
    },
  ]

  const repoColumns = [
    {
      title: '仓库名称',
      dataIndex: 'repo',
      key: 'repo',
      render: (text: string) => (
        <Tag color="blue" icon={<LinkOutlined />}>
          {text}
        </Tag>
      ),
    },
    {
      title: '代码片段数',
      dataIndex: 'count',
      key: 'count',
      sorter: (a: any, b: any) => a.count - b.count,
    },
    {
      title: '占比',
      dataIndex: 'percentage',
      key: 'percentage',
      render: (text: string) => `${text}%`,
    },
  ]

  const dependencyColumns = [
    {
      title: '依赖库',
      dataIndex: 'library',
      key: 'library',
      render: (text: string) => <Tag color="purple">{text}</Tag>,
    },
    {
      title: '使用次数',
      dataIndex: 'count',
      key: 'count',
      sorter: (a: any, b: any) => a.count - b.count,
    },
  ]

  return (
    <div className="statistics-display">
      <Card title="代码库统计" extra={<DatabaseOutlined />}>
        {/* 基础统计 */}
        <Row gutter={16} style={{ marginBottom: '24px' }}>
          <Col span={6}>
            <Statistic
              title="代码片段总数"
              value={stats.total_code_snippets}
              prefix={<CodeOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="依赖库总数"
              value={stats.total_libraries}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="编程语言数"
              value={stats.total_languages}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="依赖关系数"
              value={stats.neo4j_stats.dependencies || 0}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Col>
        </Row>

        {/* 语言分布 */}
        {languageData.length > 0 && (
          <Card
            title="语言分布"
            size="small"
            style={{ marginBottom: '16px' }}
          >
            <Table
              columns={languageColumns}
              dataSource={languageData}
              pagination={{ pageSize: 10, size: 'small' }}
              size="small"
            />
          </Card>
        )}

        {/* 仓库分布 */}
        {repoData.length > 0 && (
          <Card
            title="仓库分布 (Top 20)"
            size="small"
            style={{ marginBottom: '16px' }}
          >
            <Table
              columns={repoColumns}
              dataSource={repoData}
              pagination={{ pageSize: 10, size: 'small' }}
              size="small"
            />
          </Card>
        )}

        {/* 热门依赖库 */}
        {dependencyData.length > 0 && (
          <Card title="热门依赖库 (Top 20)" size="small">
            <Table
              columns={dependencyColumns}
              dataSource={dependencyData}
              pagination={{ pageSize: 10, size: 'small' }}
              size="small"
            />
          </Card>
        )}
      </Card>
    </div>
  )
}

export default StatisticsDisplay

