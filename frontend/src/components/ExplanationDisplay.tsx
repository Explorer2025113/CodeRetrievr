import { useState } from 'react'
import { Card, Button, Collapse } from 'antd'
import { DownOutlined, UpOutlined, FileTextOutlined } from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { PrismAsync as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import './ExplanationDisplay.css'

interface ExplanationDisplayProps {
  explanation: string
}

const ExplanationDisplay = ({ explanation }: ExplanationDisplayProps) => {
  const [expanded, setExpanded] = useState(true)

  return (
    <Card
      className="explanation-card"
      title={
        <span>
          <FileTextOutlined /> 复用说明
        </span>
      }
      extra={
        <Button
          type="text"
          icon={expanded ? <UpOutlined /> : <DownOutlined />}
          onClick={() => setExpanded(!expanded)}
          size="small"
        >
          {expanded ? '收起' : '展开'}
        </Button>
      }
    >
      {expanded && (
        <div className="explanation-content">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ node, inline, className, children, ...props }: any) {
                const match = /language-(\w+)/.exec(className || '')
                return !inline && match ? (
                  <SyntaxHighlighter
                    style={vscDarkPlus}
                    language={match[1]}
                    PreTag="div"
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code className={className} {...props}>
                    {children}
                  </code>
                )
              },
            }}
          >
            {explanation}
          </ReactMarkdown>
        </div>
      )}
    </Card>
  )
}

export default ExplanationDisplay

