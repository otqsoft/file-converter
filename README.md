<div align="center">
	<img src="static/logo.png">
    <h1>
        文件格式转换工具
    </h1>
    <p align="center">
    <img src="https://img.shields.io/badge/python-3.8+-blue.svg" />
    <img src="https://img.shields.io/badge/FastAPI-0.95+-green.svg" />
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" />
    <img src="https://img.shields.io/pypi/v/wifi-densepose.svg" />
    <img src="https://img.shields.io/badge/-Vue3-34495e?logo=vue.j" />
    <img src="https://img.shields.io/badge/-TypeScript-blue?logo=typescript&logoColor=white" />
    <img src="https://img.shields.io/badge/-Pinia-yellow?logo=picpay&logoColor=white" />
    <img src="https://img.shields.io/badge/-ESLint-4b32c3?logo=eslint&logoColor=white" />
    <img src="https://img.shields.io/badge/-Axios-008fc7?logo=axios.js&logoColor=white" />
    <img src="https://img.shields.io/badge/-Prettier-ef9421?logo=Prettier&logoColor=white" alt="Prettier">
	</p>
	<p>&nbsp;</p>
</div>


支持 Office 文件转 PDF 和音视频格式互转的 Web 应用。

## 技术栈

- **后端**: Python + FastAPI + FFmpeg + LibreOffice
- **前端**: Vue 3 + TypeScript + Vite + Element Plus + Axios
- **存储**: MinIO (S3 兼容)
- **数据库**: SQLite (可切换 PostgreSQL)

## 功能

- Office 文件（Word、Excel、PowerPoint）转 PDF
- 音视频格式互转（MP4、AVI、MKV、MOV、FLV、WebM、GIF 等）
- 文件上传至 MinIO 存储
- 转换结果下载
- 历史转换记录查询
- 进行中任务实时查看

## 快速开始

### Docker Compose（推荐）

```bash
docker-compose up -d
```

- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- MinIO 控制台: http://localhost:9001

### 本地开发

#### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### 前端

```bash
cd frontend
npm install
npm run dev
```

## API 文档

启动后端后访问 http://localhost:8000/docs 查看 Swagger 文档。

## 支持的格式

### Office → PDF
- 输入: doc, docx, xls, xlsx, ppt, pptx, odt, ods, odp
- 输出: pdf

### 音视频转换
- 输入/输出: avi, mkv, mov, flv, mp4, gif, webm, mp3, wav, aac, flac, ogg
