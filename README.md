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

一站式文件格式转换解决方案，支持文档、图片、音视频等多种格式的互转。

## 核心特性

### 文档转换
- **PDF → Word/Excel**：提取 PDF 内容转换为可编辑的 Word 文档或 Excel 表格
- **PDF → 图片**：将 PDF 页面导出为高清 PNG/JPG 图片
- **PDF → Markdown**：将 PDF 转换为结构化的 Markdown 文档
- **Office → PDF**：Word、Excel、PPT 转 PDF，保留原始排版
- **Word/Excel 互转**：支持 Office 格式之间的转换及导出 TXT/CSV

### 图片转换
- **图片格式互转**：PNG、JPG、BMP、WebP 格式之间自由转换
- **图片 → PDF**：将图片转换为 PDF 文档

### 音视频转换
- **视频格式互转**：MP4、AVI、MKV、MOV、FLV、WebM、GIF 等格式互转
- **音频格式互转**：MP3、WAV、AAC、FLAC、OGG 格式互转
- **音频提取**：从视频中提取音频轨道

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue 3 + TypeScript | 类型安全的响应式 UI |
| UI 框架 | Element Plus | 企业级组件库 |
| 构建工具 | Vite | 极速开发体验 |
| 后端 | Python + FastAPI | 高性能异步 API |
| 文档转换 | LibreOffice | 开源办公套件，支持格式最全 |
| PDF 处理 | PyMuPDF | 高性能 PDF 渲染与解析 |
| 音视频 | FFmpeg | 业界标准多媒体处理 |
| 存储 | MinIO | S3 兼容的对象存储 |
| 数据库 | SQLite | 轻量级，可切换 PostgreSQL |

## 快速开始

### Docker Compose（推荐）

```bash
docker-compose up -d
```

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | http://localhost:3000 | Web 界面 |
| 后端 API | http://localhost:8000/docs | Swagger 文档 |
| MinIO 控制台 | http://localhost:9001 | 文件管理 (minioadmin/minioadmin) |

### 本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 前端
cd frontend
npm install
npm run dev
```

## 项目结构

```
file-converter/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库连接
│   │   ├── routers/             # API 路由
│   │   ├── models/              # 数据模型
│   │   ├── schemas/             # Pydantic 模式
│   │   └── services/
│   │       ├── converter.py     # 格式转换核心
│   │       ├── minio_service.py # MinIO 存储
│   │       └── task_manager.py  # 任务调度
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/                 # API 封装
│   │   ├── views/               # 页面组件
│   │   ├── stores/              # Pinia 状态
│   │   ├── router/              # 路由配置
│   │   └── App.vue
│   ├── Dockerfile
│   └── nginx.conf
└── docker-compose.yml
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/conversions/upload` | 上传文件并转换 |
| GET | `/api/conversions/` | 查询历史记录 |
| GET | `/api/conversions/active` | 查询进行中的任务 |
| GET | `/api/conversions/{id}` | 查询任务详情 |
| GET | `/api/conversions/{id}/download` | 下载转换结果 |
| DELETE | `/api/conversions/{id}` | 删除任务记录 |

## 支持的格式

| 类型 | 支持格式 |
|------|----------|
| 文档 | doc, docx, xls, xlsx, ppt, pptx, odt, ods, odp, pdf, txt, csv, md |
| 图片 | png, jpg, jpeg, bmp, gif, tiff, webp |
| 视频 | mp4, avi, mkv, mov, flv, webm, gif |
| 音频 | mp3, wav, aac, flac, ogg |

## License

MIT
