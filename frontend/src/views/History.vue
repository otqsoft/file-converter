<template>
  <div class="history-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>历史转换记录</span>
          <el-button type="primary" @click="loadData" :loading="store.loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table :data="store.tasks" v-loading="store.loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="filename" label="文件名" min-width="200" show-overflow-tooltip />
        <el-table-column label="转换类型" width="140">
          <template #default="{ row }">
            <el-tag size="small" :type="row.conversion_type === 'office_to_pdf' ? 'primary' : 'success'">
              {{ row.conversion_type === 'office_to_pdf' ? 'Office → PDF' : '音视频转换' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="格式" width="120">
          <template #default="{ row }">
            {{ row.original_format.toUpperCase() }} → {{ row.target_format.toUpperCase() }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="文件大小" width="120">
          <template #default="{ row }">
            {{ formatSize(row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'completed'"
              type="primary"
              size="small"
              link
              @click="download(row)"
            >
              <el-icon><Download /></el-icon>
              下载
            </el-button>
            <el-button
              type="danger"
              size="small"
              link
              @click="handleDelete(row)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper" v-if="store.total > 20">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="20"
          :total="store.total"
          layout="prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Download, Delete } from '@element-plus/icons-vue'
import { useConverterStore } from '@/stores/converter'
import { conversionApi } from '@/api'
import type { ConversionTask } from '@/api'

const store = useConverterStore()
const currentPage = ref(1)

onMounted(() => {
  loadData()
})

const loadData = () => {
  store.fetchTasks({ page: currentPage.value, page_size: 20 })
}

const handlePageChange = () => {
  loadData()
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'warning',
    processing: '',
    completed: 'success',
    failed: 'danger',
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '等待中',
    processing: '转换中',
    completed: '已完成',
    failed: '失败',
  }
  return map[status] || status
}

const formatSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const download = (task: ConversionTask) => {
  const url = conversionApi.getDownloadUrl(task.id)
  const a = document.createElement('a')
  a.href = url
  a.download = task.output_filename || 'output'
  a.click()
}

const handleDelete = async (task: ConversionTask) => {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？', '确认删除', {
      type: 'warning',
    })
    await store.deleteTask(task.id)
    ElMessage.success('删除成功')
  } catch {
    // cancelled
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

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
