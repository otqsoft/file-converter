import axios from 'axios'

const rootURL = import.meta.env.VITE_API_ROOT_URL || ''

const api = axios.create({
  baseURL: `${rootURL}/api`,
  timeout: 60000,
})

export interface ConversionTask {
  id: number
  filename: string
  original_format: string
  target_format: string
  conversion_type: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  output_filename: string | null
  file_size: number
  output_file_size: number | null
  duration: number | null
  error_message: string | null
  created_at: string
  updated_at: string
}

export interface TaskListResponse {
  total: number
  items: ConversionTask[]
}

export const conversionApi = {
  upload(file: File, targetFormat: string) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('target_format', targetFormat)
    return api.post<ConversionTask>('/conversions/upload', formData)
  },

  getTask(taskId: number) {
    return api.get<ConversionTask>(`/conversions/${taskId}`)
  },

  listTasks(params?: { status?: string; page?: number; page_size?: number }) {
    return api.get<TaskListResponse>('/conversions/', { params })
  },

  getActiveTasks() {
    return api.get<TaskListResponse>('/conversions/active')
  },

  deleteTask(taskId: number) {
    return api.delete(`/conversions/${taskId}`)
  },

  getDownloadUrl(taskId: number) {
    return `${rootURL}/api/conversions/${taskId}/download`
  },
}

export default api
