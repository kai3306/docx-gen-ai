<template>
  <div>
    <h2>填写表单</h2>

    <a-card>
      <a-form layout="inline" style="margin-bottom: 16px">
        <a-form-item label="选择表单模板">
          <a-select v-model:value="selectedTemplateId" style="width: 250px" placeholder="选择表单模板" @change="onTemplateChange">
            <a-select-option v-for="t in formTemplates" :key="t.id" :value="t.id">{{ t.name }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="关联项目">
          <a-select v-model:value="selectedProjectId" style="width: 200px" placeholder="选择项目（可选）" allowClear>
            <a-select-option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</a-select-option>
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { getFormTemplates } from '../api/formTemplate'
import { createFormData, getFormData, updateFormData } from '../api/formData'
import { getProjects } from '../api/project'

const formTemplates = ref<any[]>([])
const projects = ref<any[]>([])
const selectedTemplateId = ref<number | undefined>(undefined)
const selectedProjectId = ref<number | undefined>(undefined)
const fields = ref<any[]>([])
const fieldValues = reactive<Record<string, any>>({})
const saving = ref(false)
const existingFormDataId = ref<number | null>(null)

async function load() {
  try {
    const [ftRes, pRes]: any[] = await Promise.all([getFormTemplates(), getProjects()])
    formTemplates.value = ftRes.data || []
    projects.value = pRes || []
  } catch { /* ignore */ }
}

async function onTemplateChange() {
  fields.value = []
  Object.keys(fieldValues).forEach(k => delete fieldValues[k])
  existingFormDataId.value = null

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
  // Validate required fields
  for (const f of fields.value) {
    if (f.required && !fieldValues[f.field_key]) {
      message.warning(`请填写 ${f.label}`)
      return
    }
  }
  saving.value = true
  try {
    if (existingFormDataId.value) {
      await updateFormData(existingFormDataId.value, { field_values: { ...fieldValues } })
      message.success('更新成功')
    } else {
      await createFormData({
        form_template_id: selectedTemplateId.value,
        project_id: selectedProjectId.value,
        field_values: { ...fieldValues },
      })
      message.success('保存成功')
    }
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
