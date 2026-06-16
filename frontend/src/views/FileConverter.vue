<template>
  <div class="converter-page">
    <div class="converter-grid">
      <div class="upload-section">
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

        <div class="section-card" v-if="selectedFile">
          <div class="section-header">
            <div class="section-icon target-icon">
              <el-icon :size="24"><Aim /></el-icon>
            </div>
            <div>
              <h3>选择目标格式</h3>
              <p>根据源文件类型，可选以下格式</p>
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
              :loading="store.loading"
              :disabled="!targetFormat"
              @click="handleConvert"
              class="convert-btn"
            >
              <el-icon v-if="!store.loading"><Refresh /></el-icon>
              {{ store.loading ? '转换中...' : '开始转换' }}
            </el-button>
          </div>
        </div>
      </div>

      <div class="status-section" v-if="currentTask">
        <div class="section-card">
          <div class="section-header">
            <div class="section-icon status-icon" :class="currentTask.status">
              <el-icon :size="24"><Loading v-if="currentTask.status === 'processing'" /><CircleCheck v-else-if="currentTask.status === 'completed'" /><WarningFilled v-else /></el-icon>
            </div>
            <div>
              <h3>转换状态</h3>
              <p>{{ currentTask.filename }}</p>
            </div>
          </div>

          <div class="status-body">
            <div class="status-row">
              <span class="status-label">类型</span>
              <el-tag :type="currentTask.conversion_type.includes('pdf') ? 'primary' : 'success'" size="small" effect="plain">
                {{ getConversionLabel(currentTask.conversion_type) }}
              </el-tag>
            </div>
            <div class="status-row">
              <span class="status-label">格式</span>
              <span class="status-value">{{ currentTask.original_format.toUpperCase() }} → {{ currentTask.target_format.toUpperCase() }}</span>
            </div>
            <div class="status-row">
              <span class="status-label">进度</span>
              <el-progress
                :percentage="currentTask.progress"
                :status="progressStatus"
                :stroke-width="10"
                style="flex: 1"
              />
            </div>

            <el-alert
              v-if="currentTask.error_message"
              :title="currentTask.error_message"
              type="error"
              show-icon
              :closable="false"
              class="error-alert"
            />

            <el-button
              v-if="currentTask.status === 'completed'"
              type="success"
              size="large"
              @click="downloadResult"
              class="download-btn"
            >
              <el-icon><Download /></el-icon>
              下载文件
            </el-button>
          </div>
        </div>
      </div>
    </div>

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
  UploadFilled, Close, Aim, Refresh, Loading, CircleCheck,
  WarningFilled, Download, InfoFilled, Document, Picture, VideoCamera, Headset
} from '@element-plus/icons-vue'
import { useConverterStore } from '@/stores/converter'
import { conversionApi } from '@/api'
import type { ConversionTask } from '@/api'

const store = useConverterStore()
const uploadRef = ref()
const selectedFile = ref<File | null>(null)
const targetFormat = ref('')
const currentTask = ref<ConversionTask | null>(null)
let pollTimer: ReturnType<typeof setInterval> | null = null

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

const progressStatus = computed(() => {
  if (!currentTask.value) return undefined
  if (currentTask.value.status === 'completed') return 'success'
  if (currentTask.value.status === 'failed') return 'exception'
  return undefined
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

const getConversionLabel = (type: string) => {
  const map: Record<string, string> = {
    office_to_pdf: 'Office → PDF',
    pdf_to_word: 'PDF → Word',
    pdf_to_excel: 'PDF → Excel',
    pdf_to_image: 'PDF → 图片',
    pdf_to_markdown: 'PDF → Markdown',
    image_to_image: '图片转换',
    image_to_pdf: '图片 → PDF',
    word_convert: 'Word 转换',
    excel_convert: 'Excel 转换',
    media_convert: '音视频转换',
  }
  return map[type] || type
}

const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
  targetFormat.value = ''
}

const clearFile = () => {
  selectedFile.value = null
  targetFormat.value = ''
}

const handleConvert = async () => {
  if (!selectedFile.value || !targetFormat.value) return
  try {
    const task = await store.uploadAndConvert(selectedFile.value, targetFormat.value)
    currentTask.value = task
    ElMessage.success('文件已上传，正在转换...')
    startPolling(task.id)
  } catch (err: any) {
    ElMessage.error(err.response?.data?.detail || '上传失败')
  }
}

const startPolling = (taskId: number) => {
  stopPolling()
  pollTimer = setInterval(async () => {
    const task = await store.pollTask(taskId)
    if (task) {
      currentTask.value = task
      if (task.status === 'completed' || task.status === 'failed') {
        stopPolling()
        if (task.status === 'completed') {
          ElMessage.success('转换完成！')
        } else {
          ElMessage.error('转换失败：' + task.error_message)
        }
      }
    }
  }, 2000)
}

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

const downloadResult = () => {
  if (currentTask.value) {
    const url = conversionApi.getDownloadUrl(currentTask.value.id)
    const a = document.createElement('a')
    a.href = url
    a.download = currentTask.value.output_filename || 'output'
    a.click()
  }
}
</script>

<style scoped>
.converter-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.converter-grid {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 24px;
  align-items: start;
}

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

.upload-icon { background: var(--primary-bg); color: var(--primary); }
.target-icon { background: #fef3c7; color: #f59e0b; }
.status-icon { background: #ecfdf5; color: #10b981; }
.status-icon.processing { background: #eef2ff; color: var(--primary); animation: pulse 2s infinite; }
.status-icon.failed { background: #fef2f2; color: #ef4444; }
.info-icon { background: #f0f9ff; color: #0ea5e9; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

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
  width: 80px;
  height: 80px;
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
  width: 52px;
  height: 52px;
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

.format-groups {
  padding: 20px 24px;
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
  margin-bottom: 16px;
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
  height: 48px;
  font-size: 15px;
  font-weight: 600;
  border-radius: var(--radius-sm) !important;
}

.status-body {
  padding: 20px 24px;
}

.status-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.status-row:last-child {
  margin-bottom: 0;
}

.status-label {
  font-size: 13px;
  color: var(--text-muted);
  min-width: 50px;
}

.status-value {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.error-alert {
  margin-top: 16px;
}

.download-btn {
  width: 100%;
  height: 48px;
  font-size: 15px;
  font-weight: 600;
  margin-top: 16px;
  border-radius: var(--radius-sm) !important;
}

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
  padding: 20px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  transition: all 0.2s;
}

.type-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.type-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}

.type-card h4 {
  font-size: 14px;
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
  .converter-grid {
    grid-template-columns: 1fr;
  }
  .convert-types-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
