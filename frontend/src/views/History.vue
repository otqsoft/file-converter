<template>
  <div class="history-page">
    <div class="section-card">
      <div class="section-header">
        <div class="section-icon clock-icon">
          <el-icon :size="24"><Clock /></el-icon>
        </div>
        <div>
          <h3>历史转换记录</h3>
          <p>查看所有已完成和失败的转换任务</p>
        </div>
        <div style="flex:1"></div>
        <el-button @click="loadData" :loading="store.loading" round>
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>

      <div class="table-wrap">
        <el-table :data="store.tasks" v-loading="store.loading" stripe>
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="filename" label="文件名" min-width="200" show-overflow-tooltip />
          <el-table-column label="类型" width="140">
            <template #default="{ row }">
              <el-tag size="small" effect="plain" :type="getTypeTag(row.conversion_type)">
                {{ getConversionLabel(row.conversion_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="格式" width="130">
            <template #default="{ row }">
              <span class="format-text">{{ row.original_format.toUpperCase() }} → {{ row.target_format.toUpperCase() }}</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="大小" width="100">
            <template #default="{ row }">
              {{ formatSize(row.file_size) }}
            </template>
          </el-table-column>
          <el-table-column label="时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="140" fixed="right">
            <template #default="{ row }">
              <el-button v-if="row.status === 'completed'" type="primary" size="small" link @click="download(row)">
                <el-icon><Download /></el-icon> 下载
              </el-button>
              <el-button type="danger" size="small" link @click="handleDelete(row)">
                <el-icon><Delete /></el-icon> 删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="pagination-wrap" v-if="store.total > 20">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="20"
          :total="store.total"
          layout="prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Clock, Refresh, Download, Delete } from '@element-plus/icons-vue'
import { useConverterStore } from '@/stores/converter'
import { conversionApi } from '@/api'
import type { ConversionTask } from '@/api'

const store = useConverterStore()
const currentPage = ref(1)

onMounted(() => loadData())

const loadData = () => store.fetchTasks({ page: currentPage.value, page_size: 20 })
const handlePageChange = () => loadData()

const getConversionLabel = (type: string) => {
  const map: Record<string, string> = {
    office_to_pdf: 'Office→PDF', pdf_to_word: 'PDF→Word', pdf_to_excel: 'PDF→Excel',
    pdf_to_image: 'PDF→图片', pdf_to_markdown: 'PDF→MD', image_to_image: '图片转换',
    image_to_pdf: '图片→PDF', word_convert: 'Word转换', excel_convert: 'Excel转换',
    media_convert: '音视频转换',
  }
  return map[type] || type
}

const getTypeTag = (type: string) => {
  if (type.includes('pdf') || type.includes('word') || type.includes('excel') || type.includes('office')) return 'primary'
  if (type.includes('image') || type.includes('media')) return 'success'
  return 'info'
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = { pending: 'warning', processing: '', completed: 'success', failed: 'danger' }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = { pending: '等待中', processing: '转换中', completed: '已完成', failed: '失败' }
  return map[status] || status
}

const formatSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateStr: string) => new Date(dateStr).toLocaleString('zh-CN')

const download = (task: ConversionTask) => {
  const a = document.createElement('a')
  a.href = conversionApi.getDownloadUrl(task.id)
  a.download = task.output_filename || 'output'
  a.click()
}

const handleDelete = async (task: ConversionTask) => {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？', '确认删除', { type: 'warning' })
    await store.deleteTask(task.id)
    ElMessage.success('删除成功')
  } catch {}
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

.clock-icon { background: #fef3c7; color: #f59e0b; }

.section-header h3 {
  font-size: 15px;
  font-weight: 600;
}

.section-header p {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

.table-wrap {
  padding: 0;
}

.format-text {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.pagination-wrap {
  padding: 16px 24px;
  display: flex;
  justify-content: center;
}
</style>
