<template>
  <div>
    <a-button style="margin-bottom: 16px" @click="router.push('/form-templates')">
      ← 返回表单模板列表
    </a-button>

    <a-card :title="isEdit ? '编辑表单模板' : '新建表单模板'">
      <a-form layout="vertical">
        <a-form-item label="模板名称" required>
          <a-input v-model:value="form.name" placeholder="例如：项目信息表单" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="form.description" rows="2" />
        </a-form-item>
        <a-form-item label="类型">
          <a-switch v-model:checked="form.is_base" :disabled="isEdit">
            <template #checked>公共字段集</template>
            <template #unchecked>普通表单</template>
          </a-switch>
        </a-form-item>
        <a-form-item v-if="!form.is_base" label="继承公共字段">
          <a-select v-model:value="form.base_template_id" placeholder="选择公共字段集（可选）" allowClear @change="onBaseChange">
            <a-select-option v-for="b in baseTemplates" :key="b.id" :value="b.id">{{ b.name }} ({{ (b.fields || []).length }}字段)</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>

      <a-divider>字段定义</a-divider>

      <div v-for="(field, idx) in form.fields" :key="idx" style="border: 1px solid #d9d9d9; border-radius: 4px; padding: 16px; margin-bottom: 12px">
        <a-row :gutter="12" align="middle">
          <a-col :span="6">
            <a-form-item :label="`字段Key`">
              <a-input v-model:value="field.field_key" placeholder="例如: project_name" />
            </a-form-item>
          </a-col>
          <a-col :span="6">
            <a-form-item label="显示名称">
              <a-input v-model:value="field.label" placeholder="例如: 项目名称" />
            </a-form-item>
          </a-col>
          <a-col :span="4">
            <a-form-item label="类型">
              <a-select v-model:value="field.type">
                <a-select-option value="text">文本</a-select-option>
                <a-select-option value="textarea">多行文本</a-select-option>
                <a-select-option value="date">日期</a-select-option>
                <a-select-option value="select">下拉选择</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="2">
            <a-form-item label="必填">
              <a-switch v-model:checked="field.required" />
            </a-form-item>
          </a-col>
          <a-col :span="4">
            <a-button danger @click="form.fields.splice(idx, 1)">删除</a-button>
          </a-col>
        </a-row>
        <a-form-item v-if="field.type === 'select'" label="选项（逗号分隔）">
          <a-input v-model:value="field.optionsText" placeholder="选项1,选项2,选项3" />
        </a-form-item>
      </div>

      <a-button type="dashed" block @click="addField" style="margin-bottom: 16px">
        + 添加字段
      </a-button>

      <a-space>
        <a-button type="primary" :loading="saving" @click="handleSave">保存</a-button>
        <a-button @click="router.push('/form-templates')">取消</a-button>
      </a-space>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { getFormTemplate, getBaseFormTemplates, createFormTemplate, updateFormTemplate } from '../api/formTemplate'

const router = useRouter()
const route = useRoute()
const isEdit = computed(() => route.params.id && route.params.id !== 'new')
const saving = ref(false)
const baseTemplates = ref<any[]>([])

const form = reactive({
  name: '',
  description: '',
  is_base: false,
  base_template_id: undefined as number | undefined,
  fields: [] as any[],
})

function addField() {
  form.fields.push({
    field_key: '',
    label: '',
    type: 'text',
    required: false,
    options: [],
    optionsText: '',
  })
}

async function onBaseChange() {
  // When base template changes, reload inherited fields
  if (!form.base_template_id) return
  try {
    const res: any = await getFormTemplate(form.base_template_id)
    const baseData = res.data
    // Keep only non-inherited fields (user-added)
    // Then prepend base fields
    const baseFields = (baseData.fields || []).map((f: any) => ({
      ...f,
      optionsText: (f.options || []).join(','),
      _inherited: true,
    }))
    const ownFields = form.fields.filter((f: any) => !f._inherited)
    const existingKeys = new Set(ownFields.map((f: any) => f.field_key))
    const inherited = baseFields.filter((f: any) => !existingKeys.has(f.field_key))
    form.fields = [...inherited, ...ownFields]
  } catch { /* ignore */ }
}

async function loadTemplate() {
  if (!isEdit.value) {
    // New: check query param for base mode
    if (route.query.base === '1') {
      form.is_base = true
    }
    return
  }
  try {
    const res: any = await getFormTemplate(Number(route.params.id))
    const data = res.data
    form.name = data.name
    form.description = data.description || ''
    form.is_base = data.is_base || false
    form.base_template_id = data.base_template_id || undefined
    form.fields = (data.fields || []).map((f: any) => ({
      ...f,
      optionsText: (f.options || []).join(','),
    }))
  } catch {
    message.error('模板不存在')
    router.push('/form-templates')
  }
}

async function handleSave() {
  if (!form.name) {
    message.warning('请输入模板名称')
    return
  }
  saving.value = true
  try {
    const payload = {
      name: form.name,
      description: form.description,
      is_base: form.is_base,
      base_template_id: form.is_base ? null : (form.base_template_id || null),
      fields: form.fields.map((f: any) => ({
        field_key: f.field_key,
        label: f.label,
        type: f.type,
        required: f.required,
        options: f.optionsText ? f.optionsText.split(',').map((s: string) => s.trim()).filter(Boolean) : [],
      })),
    }
    if (isEdit.value) {
      await updateFormTemplate(Number(route.params.id), payload)
      message.success('更新成功')
    } else {
      await createFormTemplate(payload)
      message.success('创建成功')
    }
    router.push('/form-templates')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const res: any = await getBaseFormTemplates()
    baseTemplates.value = res.data || []
  } catch { /* ignore */ }
  await loadTemplate()
})
</script>
