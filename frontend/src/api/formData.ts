import request from './request'

export function getFormData(params?: { project_id?: number; form_template_id?: number }) {
  return request.get('/form-data', { params })
}

export function getFormDataById(id: number) {
  return request.get(`/form-data/${id}`)
}

export function createFormData(data: {
  form_template_id: number
  project_id?: number
  field_values: Record<string, any>
}) {
  return request.post('/form-data', data)
}

export function updateFormData(id: number, data: { field_values: Record<string, any> }) {
  return request.put(`/form-data/${id}`, data)
}
