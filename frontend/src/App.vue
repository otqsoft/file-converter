<template>
  <div class="app-wrapper">
    <aside class="app-sidebar">
      <div class="sidebar-header">
        <div class="logo-box">
          <el-icon :size="28" color="#fff"><SetUp /></el-icon>
        </div>
        <div class="logo-text">
          <h1>FileConvert</h1>
          <span>格式转换工具</span>
        </div>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        router
        background-color="transparent"
        text-color="rgba(255,255,255,0.65)"
        active-text-color="#fff"
      >
        <el-menu-item index="/">
          <el-icon><Switch /></el-icon>
          <span>格式转换</span>
        </el-menu-item>
        <el-menu-item index="/active">
          <el-icon><Loading /></el-icon>
          <span>进行中任务</span>
        </el-menu-item>
        <el-menu-item index="/history">
          <el-icon><Clock /></el-icon>
          <span>历史记录</span>
        </el-menu-item>
      </el-menu>
      <div class="sidebar-footer">
        <div class="support-info">
          <el-icon><InfoFilled /></el-icon>
          <span>v1.0.0</span>
        </div>
      </div>
    </aside>
    <main class="app-main">
      <header class="main-header">
        <div class="breadcrumb-area">
          <span class="page-title">{{ pageTitle }}</span>
        </div>
        <div class="header-actions">
          <el-tag effect="plain" round>MinIO 存储</el-tag>
        </div>
      </header>
      <div class="main-content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Switch, Loading, Clock, InfoFilled, SetUp } from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  const map: Record<string, string> = {
    '/': '格式转换',
    '/active': '进行中任务',
    '/history': '历史记录',
  }
  return map[route.path] || '格式转换'
})
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --primary: #4f46e5;
  --primary-light: #818cf8;
  --primary-dark: #3730a3;
  --primary-bg: #eef2ff;
  --sidebar-bg: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%);
  --surface: #ffffff;
  --surface-hover: #f8fafc;
  --border: #e2e8f0;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --radius: 12px;
  --radius-sm: 8px;
  --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.05);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background-color: #f1f5f9;
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
}

.app-wrapper {
  display: flex;
  min-height: 100vh;
}

.app-sidebar {
  width: 240px;
  background: var(--sidebar-bg);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
}

.sidebar-header {
  padding: 24px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-box {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text h1 {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.5px;
}

.logo-text span {
  font-size: 11px;
  color: rgba(255,255,255,0.5);
}

.sidebar-menu {
  flex: 1;
  border-right: none !important;
  padding: 8px 12px;
}

.sidebar-menu .el-menu-item {
  height: 44px;
  line-height: 44px;
  border-radius: var(--radius-sm);
  margin-bottom: 4px;
  font-size: 14px;
  font-weight: 500;
}

.sidebar-menu .el-menu-item:hover {
  background: rgba(255,255,255,0.1) !important;
}

.sidebar-menu .el-menu-item.is-active {
  background: rgba(255,255,255,0.15) !important;
  color: #fff !important;
}

.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(255,255,255,0.08);
}

.support-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255,255,255,0.4);
  font-size: 12px;
}

.app-main {
  flex: 1;
  margin-left: 240px;
  display: flex;
  flex-direction: column;
}

.main-header {
  height: 64px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  position: sticky;
  top: 0;
  z-index: 50;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.main-content {
  flex: 1;
  padding: 28px 32px;
}

.el-card {
  border-radius: var(--radius) !important;
  border: 1px solid var(--border) !important;
  box-shadow: var(--shadow) !important;
}

.el-card__header {
  border-bottom: 1px solid var(--border) !important;
  padding: 18px 24px !important;
}

.el-button--primary {
  background: var(--primary) !important;
  border-color: var(--primary) !important;
}

.el-button--primary:hover {
  background: var(--primary-light) !important;
  border-color: var(--primary-light) !important;
}
</style>
