import request from './request'

export function getTemplateGroups() {
  return request.get('/template-groups')
}

export function getTemplateGroup(id: number) {
  return request.get(`/template-groups/${id}`)
}

export function createTemplateGroup(data: { name: string; description?: string }) {
  return request.post('/template-groups', data)
}

export function updateTemplateGroup(id: number, data: { name?: string; description?: string }) {
  return request.put(`/template-groups/${id}`, data)
}

export function deleteTemplateGroup(id: number) {
  return request.delete(`/template-groups/${id}`)
}

export function uploadTemplate(groupId: number, data: { name?: string; doc_type?: string; file: File }) {
  const formData = new FormData()
  formData.append('name', data.name || '')
  if (data.doc_type) formData.append('doc_type', data.doc_type)
  formData.append('file', data.file)
  return request.post(`/template-groups/${groupId}/templates`, formData)
}

export function deleteTemplate(groupId: number, templateId: number) {
  return request.delete(`/template-groups/${groupId}/templates/${templateId}`)
}
