import { defineStore } from 'pinia'
import { ref } from 'vue'
import { conversionApi } from '@/api'
import type { ConversionTask } from '@/api'

export const useConverterStore = defineStore('converter', () => {
  const tasks = ref<ConversionTask[]>([])
  const activeTasks = ref<ConversionTask[]>([])
  const loading = ref(false)
  const total = ref(0)

  const uploadAndConvert = async (file: File, targetFormat: string) => {
    loading.value = true
    try {
      const res = await conversionApi.upload(file, targetFormat)
      tasks.value.unshift(res.data)
      return res.data
    } finally {
      loading.value = false
    }
  }

  const fetchTasks = async (params?: { status?: string; page?: number; page_size?: number }) => {
    loading.value = true
    try {
      const res = await conversionApi.listTasks(params)
      tasks.value = res.data.items
      total.value = res.data.total
    } finally {
      loading.value = false
    }
  }

  const fetchActiveTasks = async () => {
    try {
      const res = await conversionApi.getActiveTasks()
      activeTasks.value = res.data.items
    } catch {
      activeTasks.value = []
    }
  }

  const pollTask = async (taskId: number): Promise<ConversionTask | null> => {
    try {
      const res = await conversionApi.getTask(taskId)
      return res.data
    } catch {
      return null
    }
  }

  const deleteTask = async (taskId: number) => {
    await conversionApi.deleteTask(taskId)
    tasks.value = tasks.value.filter((t) => t.id !== taskId)
    activeTasks.value = activeTasks.value.filter((t) => t.id !== taskId)
  }

  return {
    tasks,
    activeTasks,
    loading,
    total,
    uploadAndConvert,
    fetchTasks,
    fetchActiveTasks,
    pollTask,
    deleteTask,
  }
})
