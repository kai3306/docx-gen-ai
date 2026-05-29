<template>
  <div>
    <a-row justify="space-between" style="margin-bottom: 16px">
      <a-col><h2>模板组管理</h2></a-col>
      <a-col>
        <a-button type="primary" @click="showCreate = true">新建模板组</a-button>
      </a-col>
    </a-row>

    <a-table :dataSource="groups" :columns="columns" rowKey="id" :loading="loading">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'action'">
          <a-space>
            <a @click="router.push(`/template-groups/${record.id}`)">管理模板</a>
            <a-popconfirm title="确认删除?" @confirm="handleDelete(record.id)">
              <a style="color: red">删除</a>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <a-modal v-model:open="showCreate" title="新建模板组" @ok="handleCreate" :confirmLoading="creating">
      <a-form layout="vertical">
        <a-form-item label="名称" required>
          <a-input v-model:value="form.name" placeholder="例如：测试文档组" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="form.description" rows="2" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { getTemplateGroups, createTemplateGroup, deleteTemplateGroup } from '../api/templateGroup'

const router = useRouter()
const groups = ref<any[]>([])
const loading = ref(false)
const showCreate = ref(false)
const creating = ref(false)
const form = reactive({ name: '', description: '' })

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '名称', dataIndex: 'name', key: 'name' },
  { title: '描述', dataIndex: 'description', key: 'description' },
  { title: '模板数', dataIndex: 'template_count', key: 'template_count', width: 100 },
  { title: '操作', key: 'action', width: 180 },
]

async function load() {
  loading.value = true
  try {
    const res: any = await getTemplateGroups()
    groups.value = res.data || []
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  if (!form.name) { message.warning('请输入名称'); return }
  creating.value = true
  try {
    await createTemplateGroup({ ...form })
    message.success('创建成功')
    showCreate.value = false
    form.name = ''; form.description = ''
    load()
  } finally { creating.value = false }
}

async function handleDelete(id: number) {
  await deleteTemplateGroup(id)
  message.success('删除成功')
  load()
}

onMounted(load)
</script>
