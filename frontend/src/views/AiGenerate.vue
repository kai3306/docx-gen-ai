<template>
  <div>
    <h2>文档生成</h2>

    <!-- Phase 1: Initial Render -->
    <a-card title="初次渲染" style="margin-bottom: 16px">
      <a-form layout="vertical">
        <a-row :gutter="16">
          <a-col :span="8">
            <a-form-item label="选择表单模板" required>
              <a-select v-model:value="selectedTemplateId" placeholder="选择表单模板" @change="onFormTemplateChange">
                <a-select-option v-for="t in formTemplates" :key="t.id" :value="t.id">{{ t.name }}</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="项目名称">
              <a-input v-model:value="projectName" placeholder="将自动创建项目" />
            </a-form-item>
          </a-col>
        </a-row>

        <!-- Dynamic form fields -->
        <template v-if="fields.length > 0">
          <a-divider>填写表单字段</a-divider>
          <a-row :gutter="16">
            <a-col :span="8" v-for="field in fields" :key="field.field_key">
              <a-form-item :label="field.label" :required="field.required">
                <a-input v-if="field.type === 'text'" v-model:value="fieldValues[field.field_key]" :placeholder="`请输入${field.label}`" />
                <a-textarea v-else-if="field.type === 'textarea'" v-model:value="fieldValues[field.field_key]" :rows="2" :placeholder="`请输入${field.label}`" />
                <a-date-picker v-else-if="field.type === 'date'" v-model:value="fieldValues[field.field_key]" style="width: 100%" />
                <a-select v-else-if="field.type === 'select'" v-model:value="fieldValues[field.field_key]" :placeholder="`请选择${field.label}`">
                  <a-select-option v-for="opt in (field.options || [])" :key="opt" :value="opt">{{ opt }}</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>
        </template>

        <a-divider>选择模板与命名</a-divider>
        <a-row :gutter="16">
          <a-col :span="8">
            <a-form-item label="选择模板组">
              <a-select v-model:value="selectedGroupId" placeholder="选择模板组" @change="onGroupChange">
                <a-select-option v-for="g in templateGroups" :key="g.id" :value="g.id">{{ g.name }}</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="16">
            <a-form-item v-if="groupTemplates.length > 0" label="选择模板（可多选）">
              <a-checkbox-group v-model:value="selectedTemplateIds" style="width: 100%">
                <a-checkbox v-for="t in groupTemplates" :key="t.id" :value="t.id">
                  {{ t.name }} ({{ t.doc_type || 'doc' }})
                </a-checkbox>
              </a-checkbox-group>
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="16">
            <a-form-item label="文档命名规则">
              <a-input v-model:value="namingRule" placeholder='例如: {project_name}_{doc_type}' />
              <div style="margin-top: 4px; color: #888; font-size: 12px">
                可用变量：<code style="margin-right: 4px" v-for="v in availableVars" :key="v">{{ '{' + v + '}' }}</code>
              </div>
              <div v-if="fileNamePreview" style="margin-top: 4px; color: #1890ff; font-size: 12px">
                预览：{{ fileNamePreview }}
              </div>
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>

      <a-button type="primary" size="large" :loading="generating" :disabled="!canGenerate" @click="handleInitialGenerate" style="margin-top: 8px">
        生成文档（初次渲染）
      </a-button>

      <!-- Generated docs result -->
      <div v-if="initDocs.length > 0" style="margin-top: 16px">
        <a-divider />
        <h4>生成的文档：</h4>
        <a-space direction="vertical">
          <a-tag v-for="doc in initDocs" :key="doc.id" color="blue">
            {{ doc.file_name }}
            <a @click.prevent="downloadDocument(doc.id, doc.file_name)" style="margin-left: 8px; cursor: pointer">
              <DownloadOutlined /> 下载
            </a>
          </a-tag>
        </a-space>
        <div style="margin-top: 12px">
          <a-button size="small" @click="router.push(`/projects/${currentProjectId}`)">查看项目详情</a-button>
        </div>
      </div>
    </a-card>

    <!-- Phase 2: Secondary Render -->
    <a-card v-if="initDocs.length > 0" title="AI 二次渲染（可选）" style="margin-bottom: 16px">
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
          <p style="color: #666">上传功能清单后点击生成，AI 会根据功能清单内容对初次生成的文档进行增强渲染。</p>
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
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { DownloadOutlined, InboxOutlined } from '@ant-design/icons-vue'
import { getFormTemplates } from '../api/formTemplate'
import { createFormData } from '../api/formData'
import { getTemplateGroups, getTemplateGroup } from '../api/templateGroup'
import { uploadSurvey } from '../api/upload'
import { generate } from '../api/ai'
import { batchGenerateDocuments, reRenderDocuments, downloadDocument } from '../api/doc'

// Form
const formTemplates = ref<any[]>([])
const selectedTemplateId = ref<number | undefined>(undefined)
const fields = ref<any[]>([])
const fieldValues = reactive<Record<string, any>>({})

// Project metadata for auto-create
const projectName = ref('')
const currentProjectId = ref<number | undefined>(undefined)

// Templates
const templateGroups = ref<any[]>([])
const selectedGroupId = ref<number | undefined>(undefined)
const groupTemplates = ref<any[]>([])
const selectedTemplateIds = ref<number[]>([])

// Naming
const namingRule = ref('{project_name}_{template_name}')
const availableVars = ref<string[]>(['project_name', 'project_number', 'commission_type', 'customer_name', 'doc_type', 'template_name'])

// Generation state
const generating = ref(false)
const initDocs = ref<any[]>([])
let formDataId: number | undefined = undefined

// Secondary render
const featureTaskId = ref<number | undefined>(undefined)
const aiRunning = ref(false)
const aiDone = ref(false)
const finalDocs = ref<any[]>([])

const canGenerate = computed(() => {
  return selectedTemplateIds.value.length > 0 && namingRule.value.trim()
})

const fileNamePreview = computed(() => {
  if (!namingRule.value) return ''
  let p = namingRule.value
  p = p.replace(/\{project_name\}/g, '项目名')
  p = p.replace(/\{doc_type\}/g, '文档类型')
  p = p.replace(/\{template_name\}/g, '模板名称')
  p = p.replace(/\{project_number\}/g, '项目编号')
  p = p.replace(/\{commission_type\}/g, '委托类别')
  p = p.replace(/\{customer_name\}/g, '客户名称')
  return p
})

async function loadInit() {
  try {
    const [ftRes, tgRes]: any[] = await Promise.all([
      getFormTemplates(),
      getTemplateGroups(),
    ])
    formTemplates.value = ftRes.data || ftRes || []
    templateGroups.value = tgRes.data || tgRes || []
  } catch { /* ignore */ }
}

async function onFormTemplateChange() {
  fields.value = []
  Object.keys(fieldValues).forEach(k => delete fieldValues[k])
  const t = formTemplates.value.find(f => f.id === selectedTemplateId.value)
  if (t) {
    fields.value = t.fields || []
    // Auto-populate available naming vars from form fields
    const fieldKeys = (t.fields || []).map((f: any) => f.field_key)
    availableVars.value = ['project_name', 'project_number', 'commission_type', 'customer_name', 'doc_type', ...fieldKeys]
  }
}

async function onGroupChange() {
  groupTemplates.value = []
  selectedTemplateIds.value = []
  if (!selectedGroupId.value) return
  try {
    const res: any = await getTemplateGroup(selectedGroupId.value)
    const data = res.data || res
    groupTemplates.value = data.templates || []
  } catch { /* ignore */ }
}

async function handleInitialGenerate() {
  if (selectedTemplateIds.value.length === 0) return

  // Save form data in background (non-critical)
  let fdId: number | undefined
  if (Object.keys(fieldValues).some(k => fieldValues[k])) {
    try {
      const res: any = await createFormData({
        form_template_id: selectedTemplateId.value!,
        field_values: { ...fieldValues },
      })
      fdId = (res.data || res)?.id
    } catch {
      // Non-critical, continue
    }
  }

  generating.value = true
  try {
    // Pass field_values directly so backend uses them for naming + rendering
    const res: any = await batchGenerateDocuments({
      project_name: projectName.value || undefined,
      form_data_id: fdId,
      field_values: { ...fieldValues },
      template_ids: selectedTemplateIds.value,
      naming_rule: namingRule.value || '{doc_type}',
    })
    const data = res.data || res

    currentProjectId.value = data.project_id

    if (data.mode === 'single') {
      initDocs.value = [{ id: data.doc_id, file_name: data.file_name }]
    } else {
      initDocs.value = [{ id: data.doc_id, file_name: data.file_name, isZip: true }]
      if (data.child_doc_ids) {
        initDocs.value = [
          { id: data.doc_id, file_name: data.file_name, isZip: true },
          ...data.child_doc_ids.map((id: number) => ({ id, file_name: `文档 #${id}` })),
        ]
      }
    }
    message.success('初次渲染完成')
  } catch {
    // handled by interceptor
  } finally {
    generating.value = false
  }
}

async function handleUploadFeatureList(file: File): Promise<boolean> {
  try {
    const res: any = await uploadSurvey(file, currentProjectId.value)
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
    // 1. AI generate
    await generate(featureTaskId.value, 'test_case')

    // 2. Re-render initial docs
    const docIds = initDocs.value.filter(d => !d.isZip).map(d => d.id)
    const reRes: any = await reRenderDocuments({
      doc_ids: docIds,
      task_id: featureTaskId.value,
    })
    const data = reRes.data || reRes

    if (data.doc_ids) {
      finalDocs.value = data.doc_ids.map((id: number, i: number) => ({
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

onMounted(loadInit)
</script>
