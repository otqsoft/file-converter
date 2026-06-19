<template>
  <div class="app-wrapper">
    <header class="app-header">
      <div class="header-left">
        <div class="logo-box">
          <img src="/logo.png" alt="logo" />
        </div>
        <div class="logo-text">
          <h1>FileConvert</h1>
          <span>文件格式转换工具</span>
        </div>
      </div>
      <div class="header-right">
        <span class="version-tag">v1.0.1</span>
      </div>
    </header>
    <main class="app-main">
      <router-view />
    </main>
    <footer class="app-footer">
      <span>文件格式转换工具 · 出品：Q-Quick</span>
    </footer>
  </div>
</template>

<script setup lang="ts">
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --primary: #4f46e5;
  --primary-light: #818cf8;
  --primary-dark: #3730a3;
  --primary-bg: #eef2ff;
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
  --header-height: 60px;
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
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  height: var(--header-height);
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #3730a3 100%);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 12px rgba(30, 27, 75, 0.3);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-box {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;

  img {
    width: 36px;
    height: 36px;
  }
}

.logo-text h1 {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.3px;
}

.logo-text span {
  font-size: 10px;
  color: rgba(255,255,255,0.5);
  display: block;
  margin-top: -1px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.version-tag {
  font-size: 11px;
  color: rgba(255,255,255,0.35);
}

.app-main {
  flex: 1;
  padding: 28px 32px;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
}

.app-footer {
  text-align: center;
  padding: 32px;
  font-size: 12px;
  color: var(--text-muted);
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
