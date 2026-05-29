import request from './request'

export function getProjects() {
  return request.get('/projects')
}

export function getProject(id: number) {
  return request.get(`/projects/${id}`)
}

export function createProject(data: any) {
  return request.post('/projects', data)
}

export function updateProject(id: number, data: any) {
  return request.put(`/projects/${id}`, data)
}

export function deleteProject(id: number) {
  return request.delete(`/projects/${id}`)
}
