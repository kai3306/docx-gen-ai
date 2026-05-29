export interface User {
  id: number
  username: string
}

export interface Project {
  id: number
  name: string
  project_number?: string
  commission_type?: string
  customer_name?: string
  description?: string
  status: string
  created_at: string
  updated_at: string
}

export interface AiTask {
  id: number
  project_id: number | null
  task_type: string
  source_format: string
  source_content?: string
  ai_response?: any
  status: string
  created_at: string
}

export interface Document {
  id: number
  project_id: number
  doc_type: string
  file_name: string
  status: string
  created_at: string
}

export interface ApiResponse<T = any> {
  success: boolean
  message: string
  data?: T
}
