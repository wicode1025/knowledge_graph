<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-brand">
        <span class="brand-icon">⚡</span>
        电力用户画像系统
      </div>
      <div class="nav-links">
        <router-link to="/" class="nav-item">
          <span class="nav-icon">🏠</span>首页
        </router-link>
        <router-link to="/devices" class="nav-item">
          <span class="nav-icon">🔌</span>设备分析
        </router-link>
        <router-link to="/clustering" class="nav-item">
          <span class="nav-icon">👥</span>用户分群
        </router-link>
        <router-link to="/graph" class="nav-item">
          <span class="nav-icon">🕸️</span>知识图谱
        </router-link>
      </div>
    </nav>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f5f7fa;
}
#app {
  min-height: 100vh;
}
.navbar {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: #fff;
  padding: 0 30px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 12px rgba(0,0,0,0.15);
}
.nav-brand {
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}
.brand-icon {
  font-size: 22px;
}
.nav-links {
  display: flex;
  gap: 5px;
}
.nav-item {
  color: rgba(255,255,255,0.7);
  text-decoration: none;
  padding: 10px 16px;
  display: flex;
  align-items: center;
  gap: 6px;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s;
}
.nav-item:hover {
  color: #fff;
  background: rgba(255,255,255,0.1);
}
.nav-item.router-link-active {
  color: #fff;
  background: rgba(64, 158, 255, 0.3);
}
.nav-icon {
  font-size: 16px;
}
.main-content {
  padding: 20px;
}
</style>
