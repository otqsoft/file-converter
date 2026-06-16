<template>
  <div class="converter-page">
    <!-- 上传区域 -->
    <div class="section-card">
      <div class="section-header">
        <div class="section-icon upload-icon">
          <el-icon :size="24"><UploadFilled /></el-icon>
        </div>
        <div>
          <h3>上传文件</h3>
          <p>支持文档、图片、音视频等多种格式</p>
        </div>
      </div>
      <el-upload
        ref="uploadRef"
        class="modern-upload"
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        :show-file-list="false"
        :limit="1"
      >
        <div class="upload-inner" v-if="!selectedFile">
          <div class="upload-icon-wrap">
            <el-icon :size="48" color="var(--primary)"><UploadFilled /></el-icon>
          </div>
          <p class="upload-hint">拖拽文件到此处，或 <em>点击选择</em></p>
          <p class="upload-tip">单个文件最大 500MB</p>
        </div>
        <div class="file-preview" v-else>
          <div class="file-icon-box" :style="{ background: getFileColor(originalFormat) }">
            <span>{{ originalFormat.toUpperCase() }}</span>
          </div>
          <div class="file-meta">
            <p class="file-name">{{ selectedFile.name }}</p>
            <p class="file-size">{{ formatFileSize(selectedFile.size) }}</p>
          </div>
          <el-button type="danger" text @click.stop="clearFile">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
      </el-upload>
    </div>

    <!-- 目标格式选择 -->
    <div class="section-card" v-if="selectedFile && availableFormats.length > 0">
      <div class="section-header">
        <div class="section-icon target-icon">
          <el-icon :size="24"><Aim /></el-icon>
        </div>
        <div>
          <h3>选择目标格式</h3>
          <p>{{ originalFormat.toUpperCase() }} 可转换为以下格式</p>
        </div>
      </div>

      <div class="format-groups">
        <div v-for="group in availableFormats" :key="group.label" class="format-group">
          <h4 class="group-label">{{ group.label }}</h4>
          <div class="format-options">
            <div
              v-for="fmt in group.formats"
              :key="fmt.value"
              class="format-chip"
              :class="{ active: targetFormat === fmt.value }"
              @click="targetFormat = fmt.value"
            >
              <span class="chip-label">{{ fmt.label }}</span>
              <span class="chip-ext">.{{ fmt.value }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="convert-action">
        <el-button
          type="primary"
          size="large"
          :loading="converting"
          :disabled="!targetFormat"
          @click="handleConvert"
          class="convert-btn"
        >
          <el-icon v-if="!converting"><Refresh /></el-icon>
          {{ converting ? '转换中...' : '开始转换' }}
        </el-button>
      </div>
    </div>

    <!-- 转换结果列表 -->
    <div class="section-card" v-if="taskList.length > 0">
      <div class="section-header">
        <div class="section-icon result-icon">
          <el-icon :size="24"><List /></el-icon>
        </div>
        <div>
          <h3>转换结果</h3>
          <p>同一文件可多次选择不同格式转换</p>
        </div>
      </div>
      <div class="task-list">
        <div v-for="task in taskList" :key="task.id" class="task-item">
          <div class="task-left">
            <div class="task-format-badge" :style="{ background: getFileColor(task.target_format) }">
              {{ task.target_format.toUpperCase() }}
            </div>
            <div class="task-info">
              <p class="task-format-text">
                {{ task.original_format.toUpperCase() }} → {{ task.target_format.toUpperCase() }}
              </p>
              <div class="task-progress-row">
                <el-progress
                  v-if="task.status === 'processing' || task.status === 'pending'"
                  :percentage="task.progress"
                  :stroke-width="6"
                  style="flex: 1"
                />
                <el-tag
                  v-else
                  :type="task.status === 'completed' ? 'success' : 'danger'"
                  size="small"
                  effect="light"
                >
                  {{ task.status === 'completed' ? '已完成' : '失败' }}
                </el-tag>
              </div>
              <p v-if="task.error_message" class="task-error">{{ task.error_message }}</p>
            </div>
          </div>
          <div class="task-right">
            <el-button
              v-if="task.status === 'completed'"
              type="primary"
              size="small"
              @click="downloadTask(task)"
            >
              <el-icon><Download /></el-icon>
              下载
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 支持的转换类型 -->
    <div class="quick-convert-section">
      <div class="section-card">
        <div class="section-header">
          <div class="section-icon info-icon">
            <el-icon :size="24"><InfoFilled /></el-icon>
          </div>
          <div>
            <h3>支持的转换类型</h3>
            <p>快速了解可用的转换功能</p>
          </div>
        </div>
        <div class="convert-types-grid">
          <div class="type-card" v-for="item in convertTypes" :key="item.title">
            <div class="type-icon" :style="{ background: item.bg }">
              <el-icon :size="20" :color="item.color"><component :is="item.icon" /></el-icon>
            </div>
            <h4>{{ item.title }}</h4>
            <p>{{ item.desc }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  UploadFilled, Close, Aim, Refresh, Download, InfoFilled,
  Document, Picture, VideoCamera, Headset, List
} from '@element-plus/icons-vue'
import { useConverterStore } from '@/stores/converter'
import { conversionApi } from '@/api'
import type { ConversionTask } from '@/api'

const store = useConverterStore()
const uploadRef = ref()
const selectedFile = ref<File | null>(null)
const targetFormat = ref('')
const converting = ref(false)
const taskList = ref<ConversionTask[]>([])
const pollTimers: Map<number, ReturnType<typeof setInterval>> = new Map()

const OFFICE_FORMATS = ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'odt', 'ods', 'odp']
const PDF_FORMATS = ['pdf']
const IMAGE_FORMATS = ['png', 'jpg', 'jpeg', 'bmp', 'gif', 'tiff', 'webp']
const MEDIA_FORMATS = ['avi', 'mkv', 'mov', 'flv', 'mp4', 'gif', 'webm', 'mp3', 'wav', 'aac', 'flac', 'ogg']
const MD_FORMATS = ['md']

const originalFormat = computed(() => {
  if (!selectedFile.value) return ''
  return selectedFile.value.name.split('.').pop()?.toLowerCase() || ''
})

const availableFormats = computed(() => {
  const fmt = originalFormat.value
  const groups: { label: string; formats: { label: string; value: string }[] }[] = []

  if (OFFICE_FORMATS.includes(fmt)) {
    groups.push({
      label: '文档格式',
      formats: [
        { label: 'PDF', value: 'pdf' },
        { label: 'Word', value: 'docx' },
        { label: 'Excel', value: 'xlsx' },
        { label: '纯文本', value: 'txt' },
      ],
    })
  }

  if (PDF_FORMATS.includes(fmt)) {
    groups.push({
      label: 'PDF 转出',
      formats: [
        { label: 'Word', value: 'docx' },
        { label: 'Excel', value: 'xlsx' },
        { label: 'PNG 图片', value: 'png' },
        { label: 'JPG 图片', value: 'jpg' },
        { label: 'Markdown', value: 'md' },
      ],
    })
  }

  if (MD_FORMATS.includes(fmt)) {
    groups.push({
      label: 'Markdown 转出',
      formats: [
        { label: 'PDF', value: 'pdf' },
      ],
    })
  }

  if (IMAGE_FORMATS.includes(fmt)) {
    groups.push({
      label: '图片转换',
      formats: [
        { label: 'PNG', value: 'png' },
        { label: 'JPG', value: 'jpg' },
        { label: 'BMP', value: 'bmp' },
        { label: 'WebP', value: 'webp' },
        { label: 'PDF', value: 'pdf' },
      ],
    })
  }

  if (MEDIA_FORMATS.includes(fmt)) {
    groups.push({
      label: '视频格式',
      formats: [
        { label: 'MP4', value: 'mp4' },
        { label: 'AVI', value: 'avi' },
        { label: 'MKV', value: 'mkv' },
        { label: 'MOV', value: 'mov' },
        { label: 'FLV', value: 'flv' },
        { label: 'WebM', value: 'webm' },
        { label: 'GIF', value: 'gif' },
      ],
    })
    groups.push({
      label: '音频格式',
      formats: [
        { label: 'MP3', value: 'mp3' },
        { label: 'WAV', value: 'wav' },
        { label: 'AAC', value: 'aac' },
        { label: 'FLAC', value: 'flac' },
        { label: 'OGG', value: 'ogg' },
      ],
    })
  }

  return groups
})

const convertTypes = [
  { title: 'PDF → Word', desc: '将 PDF 转换为可编辑的 Word 文档', icon: Document, bg: '#eef2ff', color: '#4f46e5' },
  { title: 'PDF → Excel', desc: '提取 PDF 表格数据为 Excel 文件', icon: Document, bg: '#ecfdf5', color: '#10b981' },
  { title: 'PDF → 图片', desc: '将 PDF 页面导出为高清 PNG/JPG', icon: Picture, bg: '#fef3c7', color: '#f59e0b' },
  { title: 'PDF ↔ Markdown', desc: 'PDF 与 Markdown 格式双向转换', icon: Document, bg: '#fce7f3', color: '#ec4899' },
  { title: 'Office → PDF', desc: 'Word、Excel、PPT 转 PDF 格式', icon: Document, bg: '#eef2ff', color: '#4f46e5' },
  { title: '图片互转', desc: 'PNG、JPG、BMP、WebP 格式互转', icon: Picture, bg: '#ecfdf5', color: '#10b981' },
  { title: '音视频转换', desc: 'MP4、AVI、MKV、MOV 等格式互转', icon: VideoCamera, bg: '#fef3c7', color: '#f59e0b' },
  { title: '音频提取', desc: '从视频中提取 MP3、WAV 等音频', icon: Headset, bg: '#fce7f3', color: '#ec4899' },
]

const getFileColor = (ext: string) => {
  const colors: Record<string, string> = {
    pdf: '#ef4444', doc: '#3b82f6', docx: '#3b82f6',
    xls: '#22c55e', xlsx: '#22c55e', ppt: '#f97316', pptx: '#f97316',
    png: '#8b5cf6', jpg: '#8b5cf6', jpeg: '#8b5cf6', gif: '#8b5cf6',
    mp4: '#06b6d4', avi: '#06b6d4', mkv: '#06b6d4', mov: '#06b6d4',
    mp3: '#f43f5e', wav: '#f43f5e', md: '#ec4899',
  }
  return colors[ext] || '#64748b'
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
  targetFormat.value = ''
  taskList.value = []
  stopAllPolling()
}

const clearFile = () => {
  selectedFile.value = null
  targetFormat.value = ''
  taskList.value = []
  stopAllPolling()
}

const handleConvert = async () => {
  if (!selectedFile.value || !targetFormat.value) return
  converting.value = true
  try {
    const task = await store.uploadAndConvert(selectedFile.value, targetFormat.value)
    taskList.value.unshift(task)
    ElMessage.success(`已提交转换：${originalFormat.value.toUpperCase()} → ${targetFormat.value.toUpperCase()}`)
    targetFormat.value = ''
    startPolling(task.id)
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '上传失败')
  } finally {
    converting.value = false
  }
}

const startPolling = (taskId: number) => {
  const timer = setInterval(async () => {
    const task = await store.pollTask(taskId)
    if (task) {
      const idx = taskList.value.findIndex(t => t.id === taskId)
      if (idx !== -1) taskList.value[idx] = task
      if (task.status === 'completed' || task.status === 'failed') {
        clearInterval(timer)
        pollTimers.delete(taskId)
        if (task.status === 'completed') {
          ElMessage.success(`${task.target_format.toUpperCase()} 转换完成！`)
        } else {
          ElMessage.error(`转换失败：${task.error_message}`)
        }
      }
    }
  }, 2000)
  pollTimers.set(taskId, timer)
}

const stopAllPolling = () => {
  pollTimers.forEach(timer => clearInterval(timer))
  pollTimers.clear()
}

const downloadTask = async (task: ConversionTask) => {
  try {
    const url = conversionApi.getDownloadUrl(task.id)
    const res = await fetch(url)
    if (!res.ok) {
      const err = await res.json().catch(() => null)
      throw new Error(err?.detail || '下载服务异常')
    }
    const blob = await res.blob()
    const blobUrl = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = blobUrl
    a.download = task.output_filename || 'output'
    a.click()
    URL.revokeObjectURL(blobUrl)
  } catch (err: any) {
    ElMessage.error('下载失败：' + (err.message || '下载服务异常'))
  }
}
</script>

<style scoped>
.converter-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-card {
  background: var(--surface);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  overflow: hidden;
}

.section-header {
  padding: 18px 24px;
  display: flex;
  align-items: center;
  gap: 14px;
  border-bottom: 1px solid var(--border);
}

.section-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.upload-icon { background: var(--primary-bg); color: var(--primary); }
.target-icon { background: #fef3c7; color: #f59e0b; }
.result-icon { background: #ecfdf5; color: #10b981; }
.info-icon { background: #f0f9ff; color: #0ea5e9; }

.section-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.section-header p {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

/* Upload */
.modern-upload {
  padding: 24px;
}

.modern-upload :deep(.el-upload-dragger) {
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  background: var(--surface-hover);
  transition: all 0.2s;
}

.modern-upload :deep(.el-upload-dragger:hover) {
  border-color: var(--primary-light);
  background: var(--primary-bg);
}

.upload-inner {
  padding: 32px 0;
  text-align: center;
}

.upload-icon-wrap {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: var(--primary-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.upload-hint {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.upload-hint em {
  color: var(--primary);
  font-style: normal;
  font-weight: 500;
  cursor: pointer;
}

.upload-tip {
  font-size: 12px;
  color: var(--text-muted);
}

.file-preview {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
}

.file-icon-box {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
}

.file-meta {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-size {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}

/* Format selection */
.format-groups {
  padding: 20px 24px;
}

.format-group {
  margin-bottom: 16px;
}

.format-group:last-child {
  margin-bottom: 0;
}

.group-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 10px;
}

.format-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.format-chip {
  padding: 8px 16px;
  border: 1px solid var(--border);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-primary);
}

.format-chip:hover {
  border-color: var(--primary-light);
  background: var(--primary-bg);
}

.format-chip.active {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
}

.chip-label {
  font-weight: 500;
}

.chip-ext {
  font-size: 11px;
  opacity: 0.6;
}

.convert-action {
  padding: 0 24px 24px;
}

.convert-btn {
  width: 100%;
  height: 46px;
  font-size: 15px;
  font-weight: 600;
  border-radius: var(--radius-sm) !important;
}

/* Task list */
.task-list {
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  transition: all 0.2s;
}

.task-item:hover {
  border-color: var(--primary-light);
  box-shadow: var(--shadow);
}

.task-left {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
  min-width: 0;
}

.task-format-badge {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  flex-shrink: 0;
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-format-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.task-progress-row {
  display: flex;
  align-items: center;
  margin-top: 6px;
}

.task-error {
  font-size: 12px;
  color: var(--danger);
  margin-top: 4px;
}

.task-right {
  flex-shrink: 0;
  margin-left: 16px;
}

/* Quick convert */
.quick-convert-section .section-card {
  background: var(--surface);
}

.convert-types-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  padding: 20px 24px;
}

.type-card {
  padding: 18px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  transition: all 0.2s;
}

.type-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.type-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
}

.type-card h4 {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.type-card p {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
}

@media (max-width: 1200px) {
  .convert-types-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
