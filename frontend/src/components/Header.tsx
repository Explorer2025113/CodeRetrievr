import { Layout, Typography, Select } from 'antd'
import { CodeOutlined, GlobalOutlined } from '@ant-design/icons'
import { useTranslation } from 'react-i18next'
import { useMemo } from 'react'

const { Header: AntHeader } = Layout
const { Title } = Typography
const { Option } = Select

const Header = () => {
  const { t, i18n } = useTranslation()

  const handleLanguageChange = (value: string) => {
    i18n.changeLanguage(value)
  }

  const currentLanguage = useMemo(() => i18n.language || 'zh-CN', [i18n.language])

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
        {t('header.title')}
      </Title>
      <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ fontSize: '14px', opacity: 0.8 }}>
          {t('header.subtitle')}
        </div>
        <Select
          value={currentLanguage}
          onChange={handleLanguageChange}
          style={{ width: 120 }}
          suffixIcon={<GlobalOutlined />}
        >
          <Option value="zh-CN">{t('language.zh')}</Option>
          <Option value="en-US">{t('language.en')}</Option>
        </Select>
      </div>
    </AntHeader>
  )
}

export default Header

