import request from './request'

export function getFormTemplates() {
  return request.get('/form-templates')
}

export function getBaseFormTemplates() {
  return request.get('/form-templates/bases')
}

export function getFormTemplate(id: number) {
  return request.get(`/form-templates/${id}`)
}

export function createFormTemplate(data: {
  name: string
  description?: string
  fields: { field_key: string; label: string; type: string; required?: boolean; options?: string[] }[]
  is_base?: boolean
  base_template_id?: number | null
}) {
  return request.post('/form-templates', data)
}

export function updateFormTemplate(id: number, data: any) {
  return request.put(`/form-templates/${id}`, data)
}

export function deleteFormTemplate(id: number) {
  return request.delete(`/form-templates/${id}`)
}
