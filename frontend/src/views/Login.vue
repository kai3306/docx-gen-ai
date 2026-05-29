<template>
  <div class="login-container">
    <a-card title="AI检测文档自动生成平台" style="width: 400px">
      <a-form :model="form" layout="vertical" @finish="handleLogin">
        <a-form-item label="用户名" name="username" :rules="[{ required: true, message: '请输入用户名' }]">
          <a-input v-model:value="form.username" placeholder="请输入用户名" />
        </a-form-item>
        <a-form-item label="密码" name="password" :rules="[{ required: true, message: '请输入密码' }]">
          <a-input-password v-model:value="form.password" placeholder="请输入密码" />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" block :loading="loading">
            登录
          </a-button>
        </a-form-item>
        <a-form-item>
          <a-button block @click="handleRegister">
            注册新账号
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { login, register } from '../api/auth'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

async function handleLogin() {
  loading.value = true
  try {
    const res: any = await login(form.username, form.password)
    userStore.setToken(res.access_token)
    message.success('登录成功')
    router.push('/dashboard')
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  if (!form.username || !form.password) {
    message.warning('请先输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const res: any = await register(form.username, form.password)
    userStore.setToken(res.access_token)
    message.success('注册成功')
    router.push('/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f2f5;
}
</style>
