<template>
  <div v-if="project">
    <a-button style="margin-bottom: 16px" @click="router.push('/projects')">← 返回项目列表</a-button>

    <a-card :title="project.name">
      <a-descriptions :column="2">
        <a-descriptions-item label="项目ID">{{ project.id }}</a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag :color="project.status === 'active' ? 'green' : 'default'">
            {{ project.status === 'active' ? '进行中' : '已归档' }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="项目编号">{{ project.project_number || '-' }}</a-descriptions-item>
        <a-descriptions-item label="委托类别">{{ project.commission_type || '-' }}</a-descriptions-item>
        <a-descriptions-item label="客户名称">{{ project.customer_name || '-' }}</a-descriptions-item>
        <a-descriptions-item label="描述" :span="2">{{ project.description || '-' }}</a-descriptions-item>
      </a-descriptions>
    </a-card>

    <a-card title="关联文档" style="margin-top: 16px">
      <a-table :dataSource="documents" :columns="docColumns" rowKey="id" :loading="docLoading">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <a @click.prevent="downloadDocument(record.id, record.file_name)" style="cursor: pointer">下载</a>
          </template>
          <template v-else-if="column.key === 'doc_type'">
            {{ typeLabels[record.doc_type] || record.doc_type }}
          </template>
        </template>
      </a-table>
    </a-card>

    <a-card title="AI 二次渲染" style="margin-top: 16px">
      <a-row :gutter="16">
        <a-col :span="12">
          <h4>上传功能清单</h4>
          <a-upload-dragger
            :before-upload="handleUploadFeatureList"
            :showUploadList="false"
            accept=".docx,.xlsx,.xls,.md,.txt"
          >
            <p class="ant-upload-drag-icon"><InboxOutlined /></p>
            <p class="ant-upload-text">点击或拖拽文件上传</p>
            <p class="ant-upload-hint">支持 .docx / .xlsx / .md / .txt 格式</p>
          </a-upload-dragger>
          <div v-if="featureTaskId" style="margin-top: 8px">
            <a-tag color="green">功能清单已上传 (任务 #{{ featureTaskId }})</a-tag>
          </div>
        </a-col>
        <a-col :span="12">
          <h4>操作</h4>
          <p style="color: #666">上传功能清单后点击生成，AI 会根据功能清单内容对文档进行增强渲染。</p>
          <a-button type="primary" :loading="aiRunning" :disabled="!featureTaskId" @click="handleAiReRender" style="margin-top: 8px">
            AI 生成 + 二次渲染
          </a-button>
          <div v-if="aiDone" style="margin-top: 8px">
            <a-tag color="green">二次渲染完成！请下载最终文档：</a-tag>
            <a-space direction="vertical" style="margin-top: 8px">
              <a-tag v-for="doc in finalDocs" :key="doc.id" color="purple">
                {{ doc.file_name }}
                <a @click.prevent="downloadDocument(doc.id, doc.file_name)" style="margin-left: 8px; cursor: pointer">
                  <DownloadOutlined /> 下载
                </a>
              </a-tag>
            </a-space>
          </div>
        </a-col>
      </a-row>
    </a-card>
  </div>
  <div v-else><a-spin /></div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { DownloadOutlined, InboxOutlined } from '@ant-design/icons-vue'
import { getProject } from '../api/project'
import { getDocuments, downloadDocument, reRenderDocuments } from '../api/doc'
import { uploadSurvey } from '../api/upload'
import { generate } from '../api/ai'

const route = useRoute()
const router = useRouter()
const project = ref<any>(null)
const documents = ref<any[]>([])
const docLoading = ref(false)

// Secondary render
const featureTaskId = ref<number | undefined>(undefined)
const aiRunning = ref(false)
const aiDone = ref(false)
const finalDocs = ref<any[]>([])

const typeLabels: Record<string, string> = {
  test_case: '测试用例',
  test_result: '执行结果',
  test_plan: '测试计划',
  test_report: '测试报告',
  record: '原始记录',
}

const docColumns = [
  { title: '文件名', dataIndex: 'file_name', key: 'file_name' },
  { title: '类型', key: 'doc_type' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '生成时间', dataIndex: 'created_at', key: 'created_at' },
  { title: '操作', key: 'action', width: 100 },
]

async function loadData() {
  const id = Number(route.params.id)
  try {
    project.value = (await getProject(id)).data || (await getProject(id))
  } catch {
    message.error('项目不存在')
    router.push('/projects')
    return
  }

  docLoading.value = true
  try {
    const res: any = await getDocuments()
    const allDocs = res.data?.data || res.data || []
    documents.value = allDocs.filter((d: any) => d.project_id === id)
  } finally {
    docLoading.value = false
  }
}

async function handleUploadFeatureList(file: File): Promise<boolean> {
  try {
    const res: any = await uploadSurvey(file, project.value?.id)
    const data = res.data || res
    featureTaskId.value = data.task_id || data.id
    message.success('功能清单上传成功')
  } catch {
    // handled by interceptor
  }
  return false
}

async function handleAiReRender() {
  if (!featureTaskId.value) return
  aiRunning.value = true
  aiDone.value = false
  try {
    await generate(featureTaskId.value, 'test_case')

    const docIds = documents.value.filter(d => d.id).map(d => d.id)
    const reRes: any = await reRenderDocuments({
      doc_ids: docIds,
      task_id: featureTaskId.value,
    })
    const data = reRes.data || reRes

    if (data.doc_ids) {
      finalDocs.value = data.doc_ids.map((id: number) => ({
        id,
        file_name: `文档 #${id}（AI增强）`,
      }))
    }
    aiDone.value = true
    message.success('二次渲染完成')
  } catch {
    // handled by interceptor
  } finally {
    aiRunning.value = false
  }
}

onMounted(loadData)
</script>
