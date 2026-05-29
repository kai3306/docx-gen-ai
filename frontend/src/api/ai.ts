import request from './request'

export function generate(taskId: number, generateType: string) {
  return request.post('/ai/generate', { task_id: taskId, generate_type: generateType })
}

export function getAiTasks() {
  return request.get('/ai/tasks')
}

export function getAiTask(taskId: number) {
  return request.get(`/ai/tasks/${taskId}`)
}
