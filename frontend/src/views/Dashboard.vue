<template>
  <div>
    <a-row :gutter="16">
      <a-col :span="6">
        <a-card>
          <a-statistic title="项目数" :value="stats.projectCount" :value-style="{ color: '#1890ff' }">
            <template #prefix><FolderOutlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="AI生成任务" :value="stats.aiTaskCount" :value-style="{ color: '#52c41a' }">
            <template #prefix><RobotOutlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="已生成文档" :value="stats.docCount" :value-style="{ color: '#722ed1' }">
            <template #prefix><FileTextOutlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="最近项目" :value="latestProject" :value-style="{ fontSize: '14px', color: '#333' }" />
        </a-card>
      </a-col>
    </a-row>

    <a-card title="快速入口" style="margin-top: 16px">
      <a-space>
        <a-button type="primary" @click="router.push('/upload')">
          <UploadOutlined /> 上传调查表
        </a-button>
        <a-button @click="router.push('/projects')">
          <FolderOutlined /> 项目管理
        </a-button>
        <a-button @click="router.push('/ai-generate')">
          <RobotOutlined /> AI生成
        </a-button>
        <a-button @click="router.push('/documents')">
          <FileTextOutlined /> 文档管理
        </a-button>
      </a-space>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { FolderOutlined, RobotOutlined, FileTextOutlined, UploadOutlined } from '@ant-design/icons-vue'
import { getProjects } from '../api/project'
import { getAiTasks } from '../api/ai'
import { getDocuments } from '../api/doc'

const router = useRouter()

const stats = ref({ projectCount: 0, aiTaskCount: 0, docCount: 0 })
const latestProject = ref('暂无')

async function loadStats() {
  try {
    const [projectsRes, aiRes, docRes]: any[] = await Promise.all([
      getProjects(), getAiTasks(), getDocuments(),
    ])
    const projects = projectsRes.data || projectsRes || []
    const aiTasks = aiRes.data?.data || aiRes.data || []
    const docs = docRes.data?.data || docRes.data || []

    stats.value.projectCount = Array.isArray(projects) ? projects.length : 0
    stats.value.aiTaskCount = Array.isArray(aiTasks) ? aiTasks.length : 0
    stats.value.docCount = Array.isArray(docs) ? docs.length : 0

    if (Array.isArray(projects) && projects.length > 0) {
      latestProject.value = projects[0].name
    }
  } catch {
    // silently fail
  }
}

onMounted(loadStats)
</script>
