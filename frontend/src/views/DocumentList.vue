<template>
  <div>
    <h2>文档管理</h2>

    <a-table :dataSource="documents" :columns="columns" rowKey="id" :loading="loading">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'doc_type'">
          {{ typeLabels[record.doc_type] || record.doc_type }}
        </template>
        <template v-else-if="column.key === 'status'">
          <a-tag :color="record.status === 'generated' ? 'blue' : 'default'">
            {{ record.status === 'generated' ? '已生成' : record.status }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a @click.prevent="downloadDocument(record.id, record.file_name)" style="cursor: pointer">
            <DownloadOutlined /> 下载
          </a>
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { DownloadOutlined } from '@ant-design/icons-vue'
import { getDocuments, downloadDocument } from '../api/doc'

const loading = ref(false)
const documents = ref<any[]>([])

const typeLabels: Record<string, string> = {
  test_case: '测试用例',
  test_result: '执行结果',
  test_plan: '测试计划',
  test_report: '测试报告',
  record: '原始记录',
  batch: 'ZIP打包',
}

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '文件名', dataIndex: 'file_name', key: 'file_name' },
  { title: '文档类型', key: 'doc_type', width: 120 },
  { title: '状态', key: 'status', width: 100 },
  { title: '生成时间', dataIndex: 'created_at', key: 'created_at' },
  { title: '操作', key: 'action', width: 100 },
]

async function loadDocuments() {
  loading.value = true
  try {
    const res: any = await getDocuments()
    documents.value = res.data?.data || res.data || []
  } finally {
    loading.value = false
  }
}

onMounted(loadDocuments)
</script>
