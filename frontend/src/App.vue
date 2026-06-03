<template>
  <div id="app">
    <aside class="sidebar" v-if="!hideNav">
      <!-- 系统标题 -->
      <div class="sidebar-top">
        <p class="sys-name">电力用户画像系统</p>
        <p class="sys-ver">V2.0</p>
      </div>

      <!-- 用户区 -->
      <div class="user-block">
        <span class="user-avatar">{{ roleText.charAt(0) }}</span>
        <div>
          <p class="user-name">{{ savedUser || '用户' }}</p>
          <p class="user-role">{{ roleText }}</p>
        </div>
      </div>

      <!-- 导航菜单 -->
      <nav class="nav-menu">
        <p class="nav-group-title">导航</p>

        <template v-if="userRole !== 'admin'">
          <router-link to="/" class="nav-link">首页</router-link>
          <router-link to="/profile" class="nav-link">用电画像</router-link>
          <router-link to="/devices" class="nav-link">设备管理</router-link>
          <router-link to="/billing" class="nav-link">电费缴费</router-link>
          <router-link to="/repair" class="nav-link">维修报单</router-link>
        </template>
        <template v-else>
          <router-link to="/admin" class="nav-link">系统概览</router-link>
          <router-link to="/admin/kg" class="nav-link">知识图谱</router-link>
          <router-link to="/admin/data" class="nav-link">数据管理</router-link>
        </template>
      </nav>

      <!-- 底部 -->
      <div class="sidebar-bottom">
        <button @click="handleLogout" class="logout-link">退出登录</button>
      </div>
    </aside>

    <main class="main-content" :class="{ 'no-sidebar': hideNav }">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const hideNav = computed(() => route.meta.hideNav)
const userRole = computed(() => localStorage.getItem('role') || 'user')
const savedUser = computed(() => {
  try { return JSON.parse(localStorage.getItem('user') || '{}').username } catch { return '' }
})
const roleText = computed(() => userRole.value === 'admin' ? '管理员' : '家庭用户')

function handleLogout() {
  localStorage.clear()
  window.location.href = '/login'
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
  background: #f5f6f8;
  color: #333;
  font-size: 14px;
}
#app { min-height: 100vh; display: flex; }

/* ======== 侧边栏 ======== */
.sidebar {
  width: 200px;
  min-height: 100vh;
  background: #fff;
  border-right: 1px solid #e8eaed;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0; left: 0; bottom: 0;
  z-index: 100;
}

.sidebar-top {
  padding: 22px 20px 16px;
  border-bottom: 1px solid #f0f1f3;
}
.sys-name {
  font-size: 13px;
  font-weight: 600;
  color: #2c3e50;
  letter-spacing: 0.3px;
}
.sys-ver {
  font-size: 10px;
  color: #aaa;
  margin-top: 2px;
}

.user-block {
  padding: 14px 20px;
  border-bottom: 1px solid #f0f1f3;
  display: flex;
  align-items: center;
  gap: 10px;
}
.user-avatar {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: #2c3e50;
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 500;
  flex-shrink: 0;
}
.user-name { font-size: 13px; color: #2c3e50; }
.user-role { font-size: 11px; color: #999; margin-top: 1px; }

.nav-menu {
  flex: 1;
  padding: 10px 0;
}
.nav-group-title {
  font-size: 10px;
  color: #bbb;
  padding: 6px 20px 8px;
  letter-spacing: 0.5px;
}
.nav-link {
  display: block;
  padding: 8px 20px;
  font-size: 13px;
  color: #555;
  text-decoration: none;
  border-left: 2px solid transparent;
  margin: 1px 0;
  transition: all 0.15s;
}
.nav-link:hover {
  color: #2c3e50;
  background: #f8f9fb;
  border-left-color: #ddd;
}
.nav-link.router-link-active {
  color: #2c3e50;
  background: #f0f2f5;
  border-left-color: #2c3e50;
  font-weight: 500;
}

.sidebar-bottom {
  padding: 12px 20px;
  border-top: 1px solid #f0f1f3;
}
.logout-link {
  font-size: 12px;
  color: #999;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  font-family: inherit;
  transition: color 0.15s;
}
.logout-link:hover { color: #c0392b; }

/* ======== 主内容区 ======== */
.main-content {
  flex: 1;
  margin-left: 200px;
  min-height: 100vh;
  width: calc(100vw - 200px);
  overflow-x: hidden;
}
.main-content.no-sidebar {
  margin-left: 0;
  width: 100vw;
}
</style>
