<template>
  <div class="active-page">
    <div class="section-card">
      <div class="section-header">
        <div class="section-icon loading-icon">
          <el-icon :size="24"><Loading /></el-icon>
        </div>
        <div>
          <h3>进行中的任务</h3>
          <p>实时查看正在转换的任务进度</p>
        </div>
        <div style="flex:1"></div>
        <el-button @click="loadData" :loading="loading" round>
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>

      <div class="tasks-body">
        <el-empty v-if="!loading && tasks.length === 0" description="暂无进行中的任务" />

        <div v-else class="task-list">
          <div v-for="task in tasks" :key="task.id" class="task-item">
            <div class="task-left">
              <div class="task-status-dot" :class="task.status"></div>
              <div class="task-info">
                <p class="task-name">{{ task.filename }}</p>
                <p class="task-meta">
                  <el-tag size="small" effect="plain" :type="task.status === 'processing' ? 'primary' : 'warning'">
                    {{ task.status === 'processing' ? '转换中' : '等待中' }}
                  </el-tag>
                  <span class="format-text">{{ task.original_format.toUpperCase() }} → {{ task.target_format.toUpperCase() }}</span>
                </p>
              </div>
            </div>
            <div class="task-right">
              <el-progress :percentage="task.progress" :stroke-width="8" style="width: 180px" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Loading, Refresh } from '@element-plus/icons-vue'
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
  if (pollTimer) clearInterval(pollTimer)
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
.section-card {
  background: var(--surface);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  overflow: hidden;
}

.section-header {
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 14px;
  border-bottom: 1px solid var(--border);
}

.section-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.loading-icon { background: var(--primary-bg); color: var(--primary); animation: pulse 2s infinite; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.section-header h3 {
  font-size: 15px;
  font-weight: 600;
}

.section-header p {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

.tasks-body {
  padding: 16px 24px;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  transition: all 0.2s;
}

.task-item:hover {
  box-shadow: var(--shadow);
  border-color: var(--primary-light);
}

.task-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.task-status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--text-muted);
  flex-shrink: 0;
}

.task-status-dot.processing {
  background: var(--primary);
  animation: dotPulse 1.5s infinite;
}

.task-status-dot.pending {
  background: var(--warning);
}

@keyframes dotPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.4); }
  50% { box-shadow: 0 0 0 6px rgba(79, 70, 229, 0); }
}

.task-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
}

.format-text {
  font-size: 12px;
  color: var(--text-muted);
}
</style>
