<template>
  <div>
    <a-row justify="space-between" style="margin-bottom: 16px">
      <a-col><h2>表单模板管理</h2></a-col>
      <a-col>
        <a-space>
          <a-button @click="router.push('/form-templates/edit')">新建表单模板</a-button>
          <a-button type="primary" @click="router.push('/form-templates/edit?base=1')">新建公共字段集</a-button>
        </a-space>
      </a-col>
    </a-row>

    <a-table :dataSource="templates" :columns="columns" rowKey="id" :loading="loading">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'name'">
          {{ record.name }}
          <a-tag v-if="record.is_base" color="orange" style="margin-left: 4px">公共字段</a-tag>
        </template>
        <template v-if="column.key === 'fields'">
          {{ (record.fields || []).length }} 个字段
        </template>
        <template v-if="column.key === 'inherit'">
          {{ record.base_template_name || '-' }}
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a @click="router.push(`/form-templates/edit/${record.id}`)">编辑</a>
            <a-popconfirm title="确认删除?" @confirm="handleDelete(record.id)">
              <a style="color: red">删除</a>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { getFormTemplates, deleteFormTemplate } from '../api/formTemplate'

const router = useRouter()
const templates = ref<any[]>([])
const loading = ref(false)

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '名称', key: 'name' },
  { title: '描述', dataIndex: 'description', key: 'description' },
  { title: '继承自', key: 'inherit', width: 120 },
  { title: '字段数', key: 'fields', width: 100 },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at' },
  { title: '操作', key: 'action', width: 150 },
]

async function load() {
  loading.value = true
  try {
    const res: any = await getFormTemplates()
    templates.value = res.data || []
  } finally {
    loading.value = false
  }
}

async function handleDelete(id: number) {
  await deleteFormTemplate(id)
  message.success('删除成功')
  load()
}

onMounted(load)
</script>
