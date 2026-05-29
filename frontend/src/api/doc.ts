import request from './request'

export function batchGenerateDocuments(data: {
  project_id?: number
  project_name?: string
  project_product_info?: string
  project_version_info?: string
  task_id?: number
  form_data_id?: number
  template_ids: number[]
  naming_rule: string
  field_values?: Record<string, any>
}) {
  return request.post('/documents/generate', data)
}

export function reRenderDocuments(data: {
  doc_ids: number[]
  task_id: number
}) {
  return request.post('/documents/re-render', data)
}

export function getDocuments() {
  return request.get('/documents')
}

export function getDownloadUrl(docId: number) {
  return `/api/doc/${docId}`
}

export async function downloadDocument(docId: number, fileName?: string) {
  const blob = await request.get(`/doc/${docId}`, { responseType: 'blob' }) as any
  const url = window.URL.createObjectURL(blob instanceof Blob ? blob : new Blob([blob]))
  const a = document.createElement('a')
  a.href = url
  a.download = fileName || ''
  a.click()
  window.URL.revokeObjectURL(url)
}
