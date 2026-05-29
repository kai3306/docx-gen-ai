import request from './request'

export function uploadSurvey(file: File, projectId?: number) {
  const formData = new FormData()
  formData.append('file', file)
  if (projectId) {
    formData.append('project_id', String(projectId))
  }
  return request.post('/upload/survey', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  })
}
