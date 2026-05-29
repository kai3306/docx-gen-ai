<template>
  <div>
    <h2>数据上传</h2>
    <a-tabs v-model:activeKey="activeTab">
      <a-tab-pane key="form" tab="填写表单">
        <a-card>
          <a-form layout="inline" style="margin-bottom: 16px">
            <a-form-item label="关联项目">
              <a-select v-model:value="selectedProjectId" style="width: 200px" placeholder="选择项目" allowClear>
                <a-select-option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item label="选择表单模板">
              <a-select v-model:value="selectedTemplateId" style="width: 250px" placeholder="选择表单模板" @change="onTemplateChange">
                <a-select-option v-for="t in formTemplates" :key="t.id" :value="t.id">{{ t.name }}</a-select-option>
              </a-select>
            </a-form-item>
          </a-form>
        </a-card>

        <a-card v-if="fields.length > 0" title="字段填写" style="margin-top: 16px">
          <a-form layout="vertical">
            <a-form-item
              v-for="field in fields"
              :key="field.field_key"
              :label="field.label"
              :required="field.required"
            >
              <a-input
                v-if="field.type === 'text'"
                v-model:value="fieldValues[field.field_key]"
                :placeholder="`请输入${field.label}`"
              />
              <a-textarea
                v-else-if="field.type === 'textarea'"
                v-model:value="fieldValues[field.field_key]"
                :rows="3"
                :placeholder="`请输入${field.label}`"
              />
              <a-date-picker
                v-else-if="field.type === 'date'"
                v-model:value="fieldValues[field.field_key]"
                style="width: 100%"
              />
              <a-select
                v-else-if="field.type === 'select'"
                v-model:value="fieldValues[field.field_key]"
                :placeholder="`请选择${field.label}`"
                style="width: 100%"
              >
                <a-select-option v-for="opt in (field.options || [])" :key="opt" :value="opt">{{ opt }}</a-select-option>
              </a-select>
            </a-form-item>
            <a-button type="primary" :loading="saving" @click="handleSave">保存表单数据</a-button>
          </a-form>
        </a-card>
      </a-tab-pane>

      <a-tab-pane key="upload" tab="上传功能清单">
        <a-card>
          <a-form layout="inline" style="margin-bottom: 16px">
            <a-form-item label="关联项目">
              <a-select v-model:value="uploadProjectId" style="width: 200px" placeholder="选择项目" allowClear>
                <a-select-option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</a-select-option>
              </a-select>
            </a-form-item>
          </a-form>

          <a-upload-dragger
            :before-upload="handleUpload"
            :showUploadList="false"
            accept=".docx,.xlsx,.xls,.md,.txt"
          >
            <p class="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p class="ant-upload-text">点击或拖拽文件到此区域上传</p>
            <p class="ant-upload-hint">支持 .docx / .xlsx / .md / .txt 格式的功能清单文件</p>
          </a-upload-dragger>
        </a-card>

        <a-card v-if="result" title="解析结果" style="margin-top: 16px">
          <a-descriptions :column="2">
            <a-descriptions-item label="文件格式">{{ result.source_format }}</a-descriptions-item>
            <a-descriptions-item label="内容长度">{{ result.content_length }} 字符</a-descriptions-item>
          </a-descriptions>
          <a-divider />
          <h4>内容预览：</h4>
          <pre style="background: #f5f5f5; padding: 12px; max-height: 300px; overflow: auto; white-space: pre-wrap">
            {{ result.content_preview }}
          </pre>
          <a-button type="primary" @click="goToGenerate" style="margin-top: 12px">
            下一步：AI生成
          </a-button>
        </a-card>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { InboxOutlined } from '@ant-design/icons-vue'
import { getFormTemplates } from '../api/formTemplate'
import { createFormData } from '../api/formData'
import { getProjects } from '../api/project'
import { uploadSurvey } from '../api/upload'

const router = useRouter()
const activeTab = ref('form')

// Shared
const projects = ref<any[]>([])

// Form tab
const formTemplates = ref<any[]>([])
const selectedTemplateId = ref<number | undefined>(undefined)
const selectedProjectId = ref<number | undefined>(undefined)
const fields = ref<any[]>([])
const fieldValues = reactive<Record<string, any>>({})
const saving = ref(false)

// Upload tab
const uploadProjectId = ref<number | undefined>(undefined)
const result = ref<any>(null)

async function loadProjects() {
  try {
    const res: any = await getProjects()
    projects.value = res.data || res || []
  } catch { /* ignore */ }
}

async function loadFormTemplates() {
  try {
    const res: any = await getFormTemplates()
    formTemplates.value = res.data || []
  } catch { /* ignore */ }
}

async function onTemplateChange() {
  fields.value = []
  Object.keys(fieldValues).forEach(k => delete fieldValues[k])
  const template = formTemplates.value.find(t => t.id === selectedTemplateId.value)
  if (template) {
    fields.value = template.fields || []
  }
}

async function handleSave() {
  if (!selectedTemplateId.value) {
    message.warning('请选择表单模板')
    return
  }
  for (const f of fields.value) {
    if (f.required && !fieldValues[f.field_key]) {
      message.warning(`请填写 ${f.label}`)
      return
    }
  }
  saving.value = true
  try {
    await createFormData({
      form_template_id: selectedTemplateId.value,
      project_id: selectedProjectId.value,
      field_values: { ...fieldValues },
    })
    message.success('保存成功')
  } finally {
    saving.value = false
  }
}

async function handleUpload(file: File): Promise<boolean> {
  try {
    const res: any = await uploadSurvey(file, uploadProjectId.value)
    result.value = res.data
    message.success('文件上传并解析成功')
  } catch {
    // error handled by interceptor
  }
  return false
}

function goToGenerate() {
  router.push('/ai-generate')
}

onMounted(() => {
  loadProjects()
  loadFormTemplates()
})
</script>
