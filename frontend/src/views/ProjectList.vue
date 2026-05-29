<template>
  <div>
    <a-row justify="space-between" style="margin-bottom: 16px">
      <a-col><h2>项目管理</h2></a-col>
      <a-col>
        <a-button type="primary" @click="showCreateModal = true">新建项目</a-button>
      </a-col>
    </a-row>

    <a-table :dataSource="projects" :columns="columns" :loading="loading" rowKey="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'action'">
          <a-space>
            <a @click="router.push(`/projects/${record.id}`)">查看</a>
            <a @click="handleEdit(record)">编辑</a>
            <a-popconfirm title="确认删除?" @confirm="handleDelete(record.id)">
              <a style="color: red">删除</a>
            </a-popconfirm>
          </a-space>
        </template>
        <template v-else-if="column.key === 'status'">
          <a-tag :color="record.status === 'active' ? 'green' : 'default'">
            {{ record.status === 'active' ? '进行中' : '已归档' }}
          </a-tag>
        </template>
      </template>
    </a-table>

    <!-- Create/Edit Modal -->
    <a-modal
      v-model:open="showCreateModal"
      :title="editingProject ? '编辑项目' : '新建项目'"
      @ok="handleSave"
      :confirmLoading="saving"
    >
      <a-form layout="vertical">
        <a-form-item label="项目名称" required>
          <a-input v-model:value="form.name" placeholder="请输入项目名称" />
        </a-form-item>
        <a-form-item label="项目编号">
          <a-input v-model:value="form.project_number" placeholder="请输入项目编号" />
        </a-form-item>
        <a-form-item label="委托类别">
          <a-input v-model:value="form.commission_type" placeholder="例如：登记测试" />
        </a-form-item>
        <a-form-item label="客户名称">
          <a-input v-model:value="form.customer_name" placeholder="请输入客户名称" />
        </a-form-item>
        <a-form-item label="项目描述">
          <a-textarea v-model:value="form.description" rows="3" placeholder="项目描述（可选）" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { getProjects, createProject, updateProject, deleteProject } from '../api/project'

const router = useRouter()
const projects = ref<any[]>([])
const loading = ref(false)
const showCreateModal = ref(false)
const saving = ref(false)
const editingProject = ref<any>(null)

const form = reactive({
  name: '',
  project_number: '',
  commission_type: '',
  customer_name: '',
  description: '',
})

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '项目名称', dataIndex: 'name', key: 'name' },
  { title: '项目编号', dataIndex: 'project_number', key: 'project_number' },
  { title: '委托类别', dataIndex: 'commission_type', key: 'commission_type' },
  { title: '客户名称', dataIndex: 'customer_name', key: 'customer_name' },
  { title: '状态', key: 'status', width: 100 },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at' },
  { title: '操作', key: 'action', width: 180 },
]

async function loadProjects() {
  loading.value = true
  try {
    const res: any = await getProjects()
    projects.value = res.data || res || []
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  if (!form.name) {
    message.warning('请输入项目名称')
    return
  }
  saving.value = true
  try {
    if (editingProject.value) {
      await updateProject(editingProject.value.id, { ...form })
      message.success('更新成功')
    } else {
      await createProject({ ...form })
      message.success('创建成功')
    }
    showCreateModal.value = false
    resetForm()
    loadProjects()
  } finally {
    saving.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await deleteProject(id)
    message.success('删除成功')
    loadProjects()
  } catch {
    // handled by interceptor
  }
}

function resetForm() {
  editingProject.value = null
  form.name = ''
  form.project_number = ''
  form.commission_type = ''
  form.customer_name = ''
  form.description = ''
}

function handleEdit(record: any) {
  editingProject.value = record
  Object.assign(form, {
    name: record.name,
    project_number: record.project_number || '',
    commission_type: record.commission_type || '',
    customer_name: record.customer_name || '',
    description: record.description || '',
  })
  showCreateModal.value = true
}

onMounted(loadProjects)
</script>
