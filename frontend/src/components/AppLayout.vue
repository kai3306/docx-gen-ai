<template>
  <a-layout style="min-height: 100vh">
    <a-layout-sider v-model:collapsed="collapsed" collapsible theme="dark">
      <div class="logo">
        <span v-if="!collapsed">AI文档生成平台</span>
        <span v-else>AI</span>
      </div>
      <a-menu theme="dark" mode="inline" :selectedKeys="[selectedKey]">
        <a-menu-item key="dashboard" @click="goTo('/dashboard')">
          <DashboardOutlined />
          <span>工作台</span>
        </a-menu-item>
        <a-menu-item key="projects" @click="goTo('/projects')">
          <FolderOutlined />
          <span>项目管理</span>
        </a-menu-item>
        <a-sub-menu key="forms" title="表单管理">
          <template #icon><FormOutlined /></template>
          <a-menu-item key="form-fill" @click="goTo('/form-fill')">填写表单</a-menu-item>
          <a-menu-item key="form-templates" @click="goTo('/form-templates')">表单模板</a-menu-item>
        </a-sub-menu>
        <a-sub-menu key="templates" title="模板组管理">
          <template #icon><FolderOpenOutlined /></template>
          <a-menu-item key="template-groups" @click="goTo('/template-groups')">模板组列表</a-menu-item>
        </a-sub-menu>
        <a-menu-item key="ai-generate" @click="goTo('/ai-generate')">
          <RobotOutlined />
          <span>文档生成</span>
        </a-menu-item>
        <a-menu-item key="documents" @click="goTo('/documents')">
          <FileTextOutlined />
          <span>文档管理</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header class="header">
        <a-row type="flex" justify="space-between" align="middle">
          <a-col>
            <span style="color: #fff; font-size: 16px">{{ pageTitle }}</span>
          </a-col>
          <a-col>
            <a-dropdown>
              <span style="color: #fff; cursor: pointer">
                <UserOutlined /> {{ userStore.user?.username || '用户' }}
              </span>
              <template #overlay>
                <a-menu>
                  <a-menu-item @click="logout">退出登录</a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </a-col>
        </a-row>
      </a-layout-header>
      <a-layout-content style="margin: 16px; padding: 24px; background: #fff; border-radius: 4px; min-height: 360px">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  DashboardOutlined, FolderOutlined, UploadOutlined,
  RobotOutlined, FileTextOutlined, UserOutlined,
  FormOutlined, FolderOpenOutlined,
} from '@ant-design/icons-vue'
import { useUserStore } from '../stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const collapsed = ref(false)

const pageTitles: Record<string, string> = {
  dashboard: '工作台',
  projects: '项目管理',
  projectdetail: '项目详情',
  upload: '数据上传',
  aigenerate: '文档生成',
  documentlist: '文档管理',
  formtemplatelist: '表单模板',
  formtemplateedit: '设计表单',
  formfill: '填写表单',
  templategrouplist: '模板组管理',
  templategroupdetail: '模板组详情',
}

const selectedKey = computed(() => {
  const name = (route.name as string) || ''
  return name.toLowerCase()
})

const pageTitle = computed(() => {
  return pageTitles[selectedKey.value] || 'AI检测文档自动生成平台'
})

function goTo(path: string) {
  router.push(path)
}

function logout() {
  userStore.clearToken()
  router.push('/login')
}

onMounted(() => {
  userStore.fetchUser()
})
</script>

<style scoped>
.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
}
.header {
  background: #001529;
  padding: 0 24px;
}
</style>
