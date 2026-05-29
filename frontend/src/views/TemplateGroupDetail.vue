<template>
  <div>
    <a-button style="margin-bottom: 16px" @click="router.push('/template-groups')">
      ← 返回模板组列表
    </a-button>

    <a-card v-if="group" :title="group.name">
      <p>{{ group.description || '暂无描述' }}</p>
    </a-card>

    <a-card title="上传新模板" style="margin-top: 16px">
      <a-upload :before-upload="handleUpload" :showUploadList="false" accept=".docx" multiple>
        <a-button type="primary" :loading="uploading">
          <UploadOutlined /> 选择 .docx 文件上传（可多选）
        </a-button>
      </a-upload>
    </a-card>

    <a-card title="模板列表" style="margin-top: 16px">
      <a-table :dataSource="templates" :columns="columns" rowKey="id" :loading="loading">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <a-popconfirm title="确认删除此模板?" @confirm="handleDeleteTemplate(record.id)">
              <a style="color: red">删除</a>
            </a-popconfirm>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UploadOutlined } from '@ant-design/icons-vue'
import { getTemplateGroup, uploadTemplate, deleteTemplate } from '../api/templateGroup'

const route = useRoute()
const router = useRouter()
const groupId = Number(route.params.id)
const group = ref<any>(null)
const templates = ref<any[]>([])
const loading = ref(false)
const uploading = ref(false)

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '文件名', dataIndex: 'file_name', key: 'file_name' },
  { title: '操作', key: 'action', width: 100 },
]

async function load() {
  loading.value = true
  try {
    const res: any = await getTemplateGroup(groupId)
    const data = res.data
    group.value = { name: data.name, description: data.description }
    templates.value = data.templates || []
  } finally {
    loading.value = false
  }
}

async function handleUpload(file: File): Promise<boolean> {
  uploading.value = true
  try {
    await uploadTemplate(groupId, { file })
    message.success(`"${file.name}" 上传成功`)
    load()
  } finally {
    uploading.value = false
  }
  return false
}

async function handleDeleteTemplate(templateId: number) {
  await deleteTemplate(groupId, templateId)
  message.success('删除成功')
  load()
}

onMounted(load)
</script>
