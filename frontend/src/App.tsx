import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Layout, ConfigProvider } from 'antd'
import { useTranslation } from 'react-i18next'
import zhCN from 'antd/locale/zh_CN'
import enUS from 'antd/locale/en_US'
import Header from './components/Header'
import SearchPage from './pages/SearchPage'
import './App.css'

const { Content, Footer } = Layout

function AppContent() {
  const { t, i18n } = useTranslation()
  const antdLocale = i18n.language === 'en-US' ? enUS : zhCN

  return (
    <ConfigProvider locale={antdLocale}>
      <Layout className="app-layout">
        <Header />
        <Content className="app-content">
          <Routes>
            <Route path="/" element={<SearchPage />} />
          </Routes>
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          {t('app.footer')}
        </Footer>
      </Layout>
    </ConfigProvider>
  )
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  )
}

export default App

