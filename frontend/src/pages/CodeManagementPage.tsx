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
import { useTranslation } from 'react-i18next'
import { api, CodeSnippetWithId } from '../services/api'
import './CodeManagementPage.css'

const { TextArea } = Input
const { Option } = Select

const CodeManagementPage = () => {
  const { t } = useTranslation()
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
        message.info(t('management.noCodes'))
      }
    } catch (error: any) {
      console.error('Failed to load codes:', error)
      const errorMessage = error?.response?.data?.detail || error?.message || t('management.loadFailed')
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
        content: t('management.deleteSuccess'),
        duration: 2,
      })
      loadCodes()
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || t('management.deleteFailed')
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
          content: t('management.updateSuccess'),
          duration: 2,
        })
      } else {
        // 添加
        await api.addCodeSnippet(values)
        message.success({
          content: t('management.addSuccess'),
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
      const errorMessage = error?.response?.data?.detail || error?.message || t('management.operationFailed')
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
      title: t('management.codeId'),
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
      title: t('management.name'),
      dataIndex: 'name',
      key: 'name',
      width: 150,
      render: (text: string) => text || '-',
    },
    {
      title: t('management.type'),
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (text: string) => text ? <Tag color="geekblue">{text}</Tag> : '-',
    },
    {
      title: t('management.language'),
      dataIndex: 'language',
      key: 'language',
      width: 100,
      render: (text: string) => text ? <Tag color="green">{text}</Tag> : '-',
    },
    {
      title: t('management.repo'),
      dataIndex: 'repo_name',
      key: 'repo_name',
      width: 200,
      render: (text: string) => text || '-',
    },
    {
      title: t('management.filePath'),
      dataIndex: 'file_path',
      key: 'file_path',
      width: 250,
      ellipsis: true,
      render: (text: string) => text || '-',
    },
    {
      title: t('management.dependencies'),
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
      title: t('management.codePreview'),
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
      title: t('management.actions'),
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
            {t('management.edit')}
          </Button>
          <Popconfirm
            title={t('management.deleteConfirm')}
            onConfirm={() => handleDelete(record.code_id)}
            okText={t('management.confirm')}
            cancelText={t('management.cancel')}
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
              size="small"
            >
              {t('management.delete')}
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div className="code-management-page">
      <Card
        title={t('management.title')}
        extra={
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={loadCodes}
            >
              {t('management.refresh')}
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleAdd}
            >
              {t('management.addCode')}
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={codes}
          rowKey="code_id"
          loading={loading}
          pagination={{ pageSize: 10, showSizeChanger: true, showTotal: (total) => t('management.total', { total }) }}
          scroll={{ x: 1400 }}
        />
      </Card>

      <Modal
        title={editingCode ? t('management.editTitle') : t('management.addTitle')}
        open={isModalVisible}
        onOk={handleSubmit}
        onCancel={handleCancel}
        width={800}
        okText={t('management.confirm')}
        cancelText={t('management.cancel')}
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
            label={t('management.codeContent')}
            rules={[{ required: true, message: t('management.codePlaceholder') }]}
          >
            <TextArea
              rows={10}
              placeholder={t('management.codePlaceholder')}
              style={{ fontFamily: 'monospace' }}
            />
          </Form.Item>

          <Form.Item
            name="name"
            label={t('management.name')}
          >
            <Input placeholder={t('management.namePlaceholder')} />
          </Form.Item>

          <Form.Item
            name="type"
            label={t('management.type')}
            rules={[{ required: true, message: t('management.typePlaceholder') }]}
          >
            <Select>
              <Option value="function">{t('management.function')}</Option>
              <Option value="class">{t('management.class')}</Option>
              <Option value="method">{t('management.method')}</Option>
              <Option value="module">{t('management.module')}</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="language"
            label={t('management.language')}
            rules={[{ required: true, message: t('management.languagePlaceholder') }]}
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
            label={t('management.filePath')}
          >
            <Input placeholder={t('management.filePathPlaceholder')} />
          </Form.Item>

          <Form.Item
            name="repo_name"
            label={t('management.repo')}
          >
            <Input placeholder={t('management.repoNamePlaceholder')} />
          </Form.Item>

          <Form.Item
            name="repo_url"
            label={t('management.repo') + ' URL'}
          >
            <Input placeholder={t('management.repoUrlPlaceholder')} />
          </Form.Item>

          <Form.Item
            name="dependencies"
            label={t('management.dependencies')}
            tooltip={t('management.dependenciesTooltip')}
          >
            <Input placeholder={t('management.dependenciesPlaceholder')} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default CodeManagementPage

