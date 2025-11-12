import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import Header from './components/Header'
import SearchPage from './pages/SearchPage'
import './App.css'

const { Content, Footer } = Layout

function App() {
  return (
    <Router>
      <Layout className="app-layout">
        <Header />
        <Content className="app-content">
          <Routes>
            <Route path="/" element={<SearchPage />} />
          </Routes>
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          CodeRetrievr ©2024 - 基于矢量数据库的代码检索与复用平台
        </Footer>
      </Layout>
    </Router>
  )
}

export default App

