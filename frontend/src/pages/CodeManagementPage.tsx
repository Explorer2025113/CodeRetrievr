import { useState, useEffect } from 'react'
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Space,
  message,
  Popconfirm,
  Tag,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
} from '@ant-design/icons'
import { api, CodeSnippetWithId } from '../services/api'
import './CodeManagementPage.css'

const { TextArea } = Input
const { Option } = Select

const CodeManagementPage = () => {
  const [loading, setLoading] = useState(false)
  const [codes, setCodes] = useState<CodeSnippetWithId[]>([])
  const [isModalVisible, setIsModalVisible] = useState(false)
  const [editingCode, setEditingCode] = useState<CodeSnippetWithId | null>(null)
  const [form] = Form.useForm()

  useEffect(() => {
    loadCodes()
  }, [])

  const loadCodes = async () => {
    try {
      setLoading(true)
      const data = await api.getCodeSnippets({ limit: 1000 })
      setCodes(data as CodeSnippetWithId[])
      if (data.length === 0) {
        message.info('暂无代码片段，请添加代码片段')
      }
    } catch (error: any) {
      console.error('Failed to load codes:', error)
      const errorMessage = error?.response?.data?.detail || error?.message || '加载代码列表失败'
      message.error({
        content: errorMessage,
        duration: 5,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = () => {
    setEditingCode(null)
    form.resetFields()
    setIsModalVisible(true)
  }

  const handleEdit = (code: CodeSnippetWithId) => {
    setEditingCode(code)
    // 将依赖库数组转换为逗号分隔的字符串
    const formValues = {
      ...code,
      dependencies: code.dependencies?.join(', ') || '',
    }
    form.setFieldsValue(formValues)
    setIsModalVisible(true)
  }

  const handleDelete = async (codeId: string) => {
    try {
      await api.deleteCodeSnippet(codeId)
      message.success({
        content: '删除成功',
        duration: 2,
      })
      loadCodes()
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || '删除失败'
      message.error({
        content: errorMessage,
        duration: 5,
      })
    }
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      
      // 处理依赖库：将逗号分隔的字符串转换为数组
      if (values.dependencies && typeof values.dependencies === 'string') {
        values.dependencies = values.dependencies
          .split(',')
          .map((dep: string) => dep.trim())
          .filter((dep: string) => dep.length > 0)
      }
      
      if (editingCode) {
        // 更新
        await api.updateCodeSnippet(editingCode.code_id, values)
        message.success({
          content: '更新成功',
          duration: 2,
        })
      } else {
        // 添加
        await api.addCodeSnippet(values)
        message.success({
          content: '添加成功',
          duration: 2,
        })
      }
      
      setIsModalVisible(false)
      form.resetFields()
      setEditingCode(null)
      loadCodes()
    } catch (error: any) {
      if (error?.errorFields) {
        // 表单验证错误
        return
      }
      const errorMessage = error?.response?.data?.detail || error?.message || '操作失败'
      message.error({
        content: errorMessage,
        duration: 5,
      })
    }
  }

  const handleCancel = () => {
    setIsModalVisible(false)
    form.resetFields()
    setEditingCode(null)
  }

  const columns = [
    {
      title: '代码ID',
      dataIndex: 'code_id',
      key: 'code_id',
      width: 180,
      render: (text: string) => (
        <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>
          {text ? `${text.substring(0, 8)}...` : '-'}
        </span>
      ),
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      width: 150,
      render: (text: string) => text || '-',
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (text: string) => text ? <Tag color="geekblue">{text}</Tag> : '-',
    },
    {
      title: '语言',
      dataIndex: 'language',
      key: 'language',
      width: 100,
      render: (text: string) => text ? <Tag color="green">{text}</Tag> : '-',
    },
    {
      title: '仓库',
      dataIndex: 'repo_name',
      key: 'repo_name',
      width: 200,
      render: (text: string) => text || '-',
    },
    {
      title: '文件路径',
      dataIndex: 'file_path',
      key: 'file_path',
      width: 250,
      ellipsis: true,
      render: (text: string) => text || '-',
    },
    {
      title: '依赖库',
      dataIndex: 'dependencies',
      key: 'dependencies',
      render: (deps: string[]) => (
        deps && deps.length > 0 ? (
          <Space wrap>
            {deps.map((dep, idx) => (
              <Tag key={idx} color="purple">{dep}</Tag>
            ))}
          </Space>
        ) : '-'
      ),
    },
    {
      title: '代码预览',
      dataIndex: 'code',
      key: 'code',
      width: 200,
      ellipsis: true,
      render: (code: string) => (
        code ? (
          <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>
            {code.substring(0, 50)}{code.length > 50 ? '...' : ''}
          </span>
        ) : '-'
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right' as const,
      render: (_: any, record: CodeSnippetWithId) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            size="small"
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个代码片段吗？"
            onConfirm={() => handleDelete(record.code_id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
              size="small"
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div className="code-management-page">
      <Card
        title="代码管理"
        extra={
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={loadCodes}
            >
              刷新
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleAdd}
            >
              添加代码
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={codes}
          rowKey="code_id"
          loading={loading}
          pagination={{ pageSize: 10, showSizeChanger: true, showTotal: (total) => `共 ${total} 条` }}
          scroll={{ x: 1400 }}
        />
      </Card>

      <Modal
        title={editingCode ? '编辑代码片段' : '添加代码片段'}
        open={isModalVisible}
        onOk={handleSubmit}
        onCancel={handleCancel}
        width={800}
        okText="确定"
        cancelText="取消"
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            type: 'function',
            language: 'python',
          }}
        >
          <Form.Item
            name="code"
            label="代码内容"
            rules={[{ required: true, message: '请输入代码内容' }]}
          >
            <TextArea
              rows={10}
              placeholder="请输入代码内容"
              style={{ fontFamily: 'monospace' }}
            />
          </Form.Item>

          <Form.Item
            name="name"
            label="名称"
          >
            <Input placeholder="函数名或类名" />
          </Form.Item>

          <Form.Item
            name="type"
            label="类型"
            rules={[{ required: true, message: '请选择类型' }]}
          >
            <Select>
              <Option value="function">函数</Option>
              <Option value="class">类</Option>
              <Option value="method">方法</Option>
              <Option value="module">模块</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="language"
            label="编程语言"
            rules={[{ required: true, message: '请选择编程语言' }]}
          >
            <Select>
              <Option value="python">Python</Option>
              <Option value="java">Java</Option>
              <Option value="cpp">C++</Option>
              <Option value="javascript">JavaScript</Option>
              <Option value="typescript">TypeScript</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="file_path"
            label="文件路径"
          >
            <Input placeholder="例如: src/utils/helper.py" />
          </Form.Item>

          <Form.Item
            name="repo_name"
            label="仓库名称"
          >
            <Input placeholder="例如: username/repo" />
          </Form.Item>

          <Form.Item
            name="repo_url"
            label="仓库URL"
          >
            <Input placeholder="例如: https://github.com/username/repo" />
          </Form.Item>

          <Form.Item
            name="dependencies"
            label="依赖库（逗号分隔）"
            tooltip="多个依赖库请用逗号分隔，例如: requests, numpy, pandas"
          >
            <Input placeholder="例如: requests, numpy, pandas" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default CodeManagementPage

