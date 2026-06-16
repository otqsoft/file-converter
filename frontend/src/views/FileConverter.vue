<template>
  <div class="converter-page">
    <el-card class="upload-card">
      <template #header>
        <div class="card-header">
          <span>文件上传与转换</span>
        </div>
      </template>

      <el-upload
        ref="uploadRef"
        class="upload-area"
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        accept=".doc,.docx,.xls,.xlsx,.ppt,.pptx,.odt,.ods,.odp,.avi,.mkv,.mov,.flv,.mp4,.gif,.webm,.mp3,.wav,.aac,.flac,.ogg"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 Office 文件（Word、Excel、PowerPoint）转 PDF，以及音视频格式互转
          </div>
        </template>
      </el-upload>

      <div v-if="selectedFile" class="format-section">
        <el-divider content-position="left">转换设置</el-divider>

        <div class="file-info">
          <el-tag type="info" size="large">{{ selectedFile.name }}</el-tag>
          <el-tag type="warning" size="large">{{ originalFormat.toUpperCase() }}</el-tag>
          <el-icon><Right /></el-icon>
        </div>

        <div class="target-format">
          <span class="label">目标格式：</span>
          <el-select v-model="targetFormat" placeholder="选择目标格式" style="width: 200px">
            <el-option-group v-if="isOfficeFormat" label="Office 转换">
              <el-option label="PDF" value="pdf" />
            </el-option-group>
            <el-option-group v-if="isMediaFormat" label="视频格式">
              <el-option label="MP4" value="mp4" />
              <el-option label="AVI" value="avi" />
              <el-option label="MKV" value="mkv" />
              <el-option label="MOV" value="mov" />
              <el-option label="FLV" value="flv" />
              <el-option label="WebM" value="webm" />
              <el-option label="GIF" value="gif" />
            </el-option-group>
            <el-option-group v-if="isMediaFormat" label="音频格式">
              <el-option label="MP3" value="mp3" />
              <el-option label="WAV" value="wav" />
              <el-option label="AAC" value="aac" />
              <el-option label="FLAC" value="flac" />
              <el-option label="OGG" value="ogg" />
            </el-option-group>
          </el-select>
        </div>

        <el-button
          type="primary"
          size="large"
          :loading="store.loading"
          :disabled="!targetFormat"
          @click="handleConvert"
        >
          <el-icon><Upload /></el-icon>
          开始转换
        </el-button>
      </div>
    </el-card>

    <el-card v-if="currentTask" class="task-status-card">
      <template #header>
        <div class="card-header">
          <span>当前任务</span>
          <el-tag :type="statusType" size="small">{{ statusText }}</el-tag>
        </div>
      </template>

      <div class="task-info">
        <div class="task-detail">
          <span class="label">文件名：</span>
          <span>{{ currentTask.filename }}</span>
        </div>
        <div class="task-detail">
          <span class="label">转换类型：</span>
          <span>{{ currentTask.conversion_type === 'office_to_pdf' ? 'Office → PDF' : '音视频格式转换' }}</span>
        </div>
        <div class="task-detail">
          <span class="label">状态：</span>
          <el-progress
            :percentage="currentTask.progress"
            :status="currentTask.status === 'completed' ? 'success' : currentTask.status === 'failed' ? 'exception' : undefined"
            style="width: 300px"
          />
        </div>
        <div v-if="currentTask.error_message" class="task-error">
          <el-alert :title="currentTask.error_message" type="error" show-icon :closable="false" />
        </div>
        <div v-if="currentTask.status === 'completed'" class="task-actions">
          <el-button type="success" @click="downloadResult">
            <el-icon><Download /></el-icon>
            下载转换结果
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Upload, Right, Download } from '@element-plus/icons-vue'
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
const MEDIA_FORMATS = ['avi', 'mkv', 'mov', 'flv', 'mp4', 'gif', 'webm', 'mp3', 'wav', 'aac', 'flac', 'ogg']

const originalFormat = computed(() => {
  if (!selectedFile.value) return ''
  const name = selectedFile.value.name
  return name.split('.').pop()?.toLowerCase() || ''
})

const isOfficeFormat = computed(() => OFFICE_FORMATS.includes(originalFormat.value))
const isMediaFormat = computed(() => MEDIA_FORMATS.includes(originalFormat.value))

const statusType = computed(() => {
  if (!currentTask.value) return 'info'
  const map: Record<string, string> = {
    pending: 'warning',
    processing: '',
    completed: 'success',
    failed: 'danger',
  }
  return map[currentTask.value.status] || 'info'
})

const statusText = computed(() => {
  if (!currentTask.value) return ''
  const map: Record<string, string> = {
    pending: '等待中',
    processing: '转换中',
    completed: '已完成',
    failed: '失败',
  }
  return map[currentTask.value.status] || ''
})

const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
  targetFormat.value = ''
}

const handleConvert = async () => {
  if (!selectedFile.value || !targetFormat.value) return

  try {
    const task = await store.uploadAndConvert(selectedFile.value, targetFormat.value)
    currentTask.value = task
    ElMessage.success('文件已上传，正在转换中...')

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

.upload-card {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  padding: 40px 0;
}

.format-section {
  margin-top: 20px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.target-format {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.target-format .label {
  font-weight: 500;
  color: #606266;
}

.task-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.task-detail {
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-detail .label {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
}

.task-error {
  margin-top: 8px;
}

.task-actions {
  margin-top: 8px;
}
</style>
