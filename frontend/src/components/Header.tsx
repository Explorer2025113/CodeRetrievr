import { Layout, Typography } from 'antd'
import { CodeOutlined } from '@ant-design/icons'

const { Header: AntHeader } = Layout
const { Title } = Typography

const Header = () => {
  return (
    <AntHeader
      style={{
        display: 'flex',
        alignItems: 'center',
        padding: '0 24px',
        background: '#001529',
        color: '#fff',
      }}
    >
      <CodeOutlined style={{ fontSize: '24px', marginRight: '12px' }} />
      <Title level={4} style={{ margin: 0, color: '#fff' }}>
        CodeRetrievr
      </Title>
      <div style={{ marginLeft: 'auto', fontSize: '14px', opacity: 0.8 }}>
        代码检索与复用平台
      </div>
    </AntHeader>
  )
}

export default Header

