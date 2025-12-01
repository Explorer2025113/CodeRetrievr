import { useEffect, useState } from 'react'
import { Card, Row, Col, Statistic, Table, Tag, Spin, message } from 'antd'
import { CodeOutlined, DatabaseOutlined, FileTextOutlined, LinkOutlined } from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import { api, StatisticsResponse } from '../services/api'
import './StatisticsDisplay.css'

const StatisticsDisplay = () => {
  const { t } = useTranslation()
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
      const errorMessage = error?.response?.data?.detail || error?.message || t('stats.loadFailed')
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
        <Spin size="large" tip={t('stats.loading')} />
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
      title: t('stats.language'),
      dataIndex: 'language',
      key: 'language',
      render: (text: string) => <Tag color="green">{text}</Tag>,
    },
    {
      title: t('stats.snippets'),
      dataIndex: 'count',
      key: 'count',
      sorter: (a: any, b: any) => a.count - b.count,
    },
    {
      title: t('stats.percentage'),
      dataIndex: 'percentage',
      key: 'percentage',
      render: (text: string) => `${text}%`,
    },
  ]

  const repoColumns = [
    {
      title: t('stats.repo'),
      dataIndex: 'repo',
      key: 'repo',
      render: (text: string) => (
        <Tag color="blue" icon={<LinkOutlined />}>
          {text}
        </Tag>
      ),
    },
    {
      title: t('stats.snippets'),
      dataIndex: 'count',
      key: 'count',
      sorter: (a: any, b: any) => a.count - b.count,
    },
    {
      title: t('stats.percentage'),
      dataIndex: 'percentage',
      key: 'percentage',
      render: (text: string) => `${text}%`,
    },
  ]

  const dependencyColumns = [
    {
      title: t('stats.library'),
      dataIndex: 'library',
      key: 'library',
      render: (text: string) => <Tag color="purple">{text}</Tag>,
    },
    {
      title: t('stats.usage'),
      dataIndex: 'count',
      key: 'count',
      sorter: (a: any, b: any) => a.count - b.count,
    },
  ]

  return (
    <div className="statistics-display">
      <Card title={t('stats.title')} extra={<DatabaseOutlined />}>
        {/* 基础统计 */}
        <Row gutter={16} style={{ marginBottom: '24px' }}>
          <Col span={6}>
            <Statistic
              title={t('stats.totalSnippets')}
              value={stats.total_code_snippets}
              prefix={<CodeOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title={t('stats.totalLibraries')}
              value={stats.total_libraries}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title={t('stats.totalLanguages')}
              value={stats.total_languages}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title={t('stats.totalDependencies')}
              value={stats.neo4j_stats.dependencies || 0}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Col>
        </Row>

        {/* 语言分布 */}
        {languageData.length > 0 && (
          <Card
            title={t('stats.languageDistribution')}
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
            title={t('stats.repoDistribution')}
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
          <Card title={t('stats.topDependencies')} size="small">
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

