import { useState } from 'react'
import { Card, Button, Space, message, Tag } from 'antd'
import { CopyOutlined, DownOutlined, UpOutlined } from '@ant-design/icons'
import { PrismAsync as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import './CodeDisplay.css'

interface CodeDisplayProps {
  code: string
  language?: string
  maxLines?: number
}

const CodeDisplay = ({ code, language = 'python', maxLines = 20 }: CodeDisplayProps) => {
  const [expanded, setExpanded] = useState(false)
  const [copied, setCopied] = useState(false)

  if (!code) {
    return null
  }

  const lines = code.split('\n')
  const shouldTruncate = lines.length > maxLines
  const displayCode = shouldTruncate && !expanded
    ? lines.slice(0, maxLines).join('\n') + '\n...'
    : code

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      message.success('代码已复制到剪贴板')
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      message.error('复制失败，请手动复制')
    }
  }

  const getLanguageColor = (lang: string) => {
    const colorMap: Record<string, string> = {
      python: 'green',
      java: 'orange',
      cpp: 'blue',
      javascript: 'yellow',
      typescript: 'cyan',
      go: 'geekblue',
      rust: 'red',
    }
    return colorMap[lang.toLowerCase()] || 'default'
  }

  return (
    <div className="code-display">
      <Card
        size="small"
        title={
          <Space>
            <span>代码片段</span>
            <Tag color={getLanguageColor(language)}>
              {language.toUpperCase()}
            </Tag>
          </Space>
        }
        extra={
          <Space>
            <Button
              type="text"
              icon={<CopyOutlined />}
              onClick={handleCopy}
              size="small"
            >
              {copied ? '已复制' : '复制'}
            </Button>
            {shouldTruncate && (
              <Button
                type="text"
                icon={expanded ? <UpOutlined /> : <DownOutlined />}
                onClick={() => setExpanded(!expanded)}
                size="small"
              >
                {expanded ? '收起' : '展开'}
              </Button>
            )}
          </Space>
        }
        className="code-card"
      >
        <SyntaxHighlighter
          language={language.toLowerCase()}
          style={vscDarkPlus}
          customStyle={{
            margin: 0,
            borderRadius: '4px',
            fontSize: '14px',
            lineHeight: '1.5',
          }}
          showLineNumbers
          wrapLines
        >
          {displayCode}
        </SyntaxHighlighter>
      </Card>
    </div>
  )
}

export default CodeDisplay

