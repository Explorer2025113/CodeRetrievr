import { Card, List, Tag, Space, Divider } from 'antd'
import { CodeOutlined, FileTextOutlined, LinkOutlined } from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import { SearchResultItem } from '../services/api'
import CodeDisplay from './CodeDisplay'
import ExplanationDisplay from './ExplanationDisplay'
import './SearchResults.css'

interface SearchResultsProps {
  results: SearchResultItem[]
}

const getSimilarityColor = (score: number): string => {
  const percentage = score * 100
  if (percentage >= 80) return 'green'
  if (percentage >= 50) return 'orange'
  return 'red'
}

const SearchResults = ({ results }: SearchResultsProps) => {
  const { t } = useTranslation()
  
  return (
    <div className="search-results">
      <Card title={t('results.found', { count: results.length })}>
        <List
          itemLayout="vertical"
          dataSource={results}
          renderItem={(item, index) => (
            <List.Item key={item.id || index}>
              <Card className="result-card" hoverable>
                {/* 头部信息 */}
                <div className="result-header">
                  <Space wrap>
                    {item.name && (
                      <Tag icon={<CodeOutlined />} color="blue">
                        {item.name}
                      </Tag>
                    )}
                    {item.type && (
                      <Tag color="geekblue">{item.type}</Tag>
                    )}
                    {item.language && (
                      <Tag color="green">{item.language}</Tag>
                    )}
                    <Tag color={getSimilarityColor(item.score)}>
                      {t('results.similarity')}: {(item.score * 100).toFixed(1)}%
                    </Tag>
                  </Space>
                </div>

                {/* 文件路径和仓库信息 */}
                {(item.file_path || item.repo_name) && (
                  <div className="result-meta">
                    <Space wrap>
                      {item.file_path && (
                        <span>
                          <FileTextOutlined /> {item.file_path}
                        </span>
                      )}
                      {item.repo_name && (
                        <span>
                          <LinkOutlined /> {item.repo_name}
                        </span>
                      )}
                      {item.repo_url && (
                        <a
                          href={item.repo_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ color: '#1890ff' }}
                        >
                          {t('results.viewRepo')}
                        </a>
                      )}
                    </Space>
                  </div>
                )}

                {/* 依赖库 */}
                {item.dependencies && item.dependencies.length > 0 && (
                  <div className="result-dependencies">
                    <strong>{t('results.dependencies')}：</strong>
                    <Space wrap style={{ marginTop: '8px' }}>
                      {item.dependencies.map((dep, idx) => (
                        <Tag key={idx} color="purple">{dep}</Tag>
                      ))}
                    </Space>
                  </div>
                )}

                <Divider />

                {/* 代码显示 */}
                {item.code ? (
                  <CodeDisplay code={item.code} language={item.language || 'python'} />
                ) : (
                  <div style={{ padding: '16px', background: '#f5f5f5', borderRadius: '4px', color: '#999' }}>
                    {t('results.codeUnavailable')}
                  </div>
                )}

                {/* 复用说明 */}
                {item.explanation && (
                  <div style={{ marginTop: '16px' }}>
                    <ExplanationDisplay explanation={item.explanation} />
                  </div>
                )}

                {/* 相关代码 */}
                {item.related_codes && item.related_codes.length > 0 && (
                  <div className="result-related" style={{ marginTop: '16px' }}>
                    <strong>{t('results.relatedCodes')}：</strong>
                    <Space wrap style={{ marginTop: '8px' }}>
                      {item.related_codes.map((codeId, idx) => (
                        <Tag key={idx} color="cyan">{codeId}</Tag>
                      ))}
                    </Space>
                  </div>
                )}
              </Card>
            </List.Item>
          )}
        />
      </Card>
    </div>
  )
}

export default SearchResults

