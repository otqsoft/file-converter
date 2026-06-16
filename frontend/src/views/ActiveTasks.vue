<template>
  <div class="active-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>进行中的任务</span>
          <el-button type="primary" @click="loadData" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-empty v-if="!loading && tasks.length === 0" description="暂无进行中的任务" />

      <div v-else class="task-list">
        <div v-for="task in tasks" :key="task.id" class="task-item">
          <div class="task-main">
            <div class="task-info">
              <el-tag :type="task.status === 'processing' ? '' : 'warning'" size="small">
                {{ task.status === 'processing' ? '转换中' : '等待中' }}
              </el-tag>
              <span class="filename">{{ task.filename }}</span>
              <span class="format-tag">
                {{ task.original_format.toUpperCase() }} → {{ task.target_format.toUpperCase() }}
              </span>
            </div>
            <div class="task-progress">
              <el-progress
                :percentage="task.progress"
                :stroke-width="8"
                style="width: 200px"
              />
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { conversionApi } from '@/api'
import type { ConversionTask } from '@/api'

const tasks = ref<ConversionTask[]>([])
const loading = ref(false)
let pollTimer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  loadData()
  pollTimer = setInterval(loadData, 3000)
})

onUnmounted(() => {
  if (pollTimer) {
    clearInterval(pollTimer)
  }
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await conversionApi.getActiveTasks()
    tasks.value = res.data.items
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  transition: box-shadow 0.2s;
}

.task-item:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.task-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filename {
  font-weight: 500;
  color: #303133;
}

.format-tag {
  color: #909399;
  font-size: 13px;
}
</style>
