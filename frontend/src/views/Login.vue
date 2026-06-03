<template>
  <div class="login-page">
    <!-- 顶部装饰线 -->
    <div class="top-accent"></div>

    <!-- 左侧装饰区 -->
    <div class="login-wrapper">
      <div class="brand-panel">
        <div class="brand-content">
          <div class="power-icon">
            <svg viewBox="0 0 64 64" width="64" height="64">
              <circle cx="32" cy="32" r="28" fill="none" stroke="#5470c6" stroke-width="1.5" opacity="0.3"/>
              <circle cx="32" cy="32" r="20" fill="none" stroke="#5470c6" stroke-width="1" opacity="0.5"/>
              <polygon points="34,12 24,34 30,34 26,52 40,28 34,28 38,12" fill="#5470c6" opacity="0.85"/>
            </svg>
          </div>
          <h1>Power User Profiling</h1>
          <p class="subtitle">基于知识图谱的电力用户画像系统</p>
          <div class="feature-tags">
            <span class="tag">Knowledge Graph</span>
            <span class="tag">FCM Clustering</span>
            <span class="tag">Neo4j</span>
          </div>
        </div>
      </div>

      <div class="form-panel">
        <div class="form-content">
          <h2>Sign In</h2>
          <p class="form-desc">登录您的账户以查看用电画像</p>

          <div class="role-toggle">
            <button :class="['role-btn',{active:loginRole==='user'}]" @click="loginRole='user'" type="button">家庭用户</button>
            <button :class="['role-btn',{active:loginRole==='admin'}]" @click="loginRole='admin'" type="button">管理员</button>
          </div>

          <div class="demo-links">
            <span @click="fillDemo('admin')" class="demo-link">管理员 Demo</span>
            <span class="demo-sep">|</span>
            <span @click="fillDemo('user')" class="demo-link">用户 Demo</span>
          </div>

          <form @submit.prevent="handleLogin">
            <div class="field">
              <label>Username</label>
              <input
                type="text"
                v-model="form.username"
                placeholder="输入用户名"
                :disabled="loading"
                autocomplete="username"
              />
            </div>
            <div class="field">
              <label>Password</label>
              <input
                type="password"
                v-model="form.password"
                placeholder="输入密码"
                :disabled="loading"
                autocomplete="current-password"
              />
            </div>
            <div class="error-msg" v-if="error">{{ error }}</div>
            <button type="submit" class="submit-btn" :disabled="loading">
              {{ loading ? '登录中...' : '登 录' }}
            </button>
          </form>
          <div class="register-link">
            还没有账户？<router-link to="/register">立即注册</router-link>
          </div>

        </div>
      </div>
    </div>

    <!-- 底部装饰 -->
    <div class="footer-wave">
      <svg viewBox="0 0 1200 60" preserveAspectRatio="none">
        <path d="M0,40 C200,10 400,50 600,30 C800,10 1000,50 1200,20 L1200,60 L0,60 Z" fill="#5470c6" opacity="0.06"/>
        <path d="M0,50 C300,30 600,55 900,40 C1050,32 1150,48 1200,45 L1200,60 L0,60 Z" fill="#5470c6" opacity="0.04"/>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const loginRole = ref('user')
const form = reactive({ username: '', password: '' })

function fillDemo(role) {
  loginRole.value = role
  const accounts = { admin: 'admin', user: 'user001' }
  form.username = accounts[role]
  form.password = role === 'admin' ? 'admin123' : 'pass123456'
}

async function handleLogin() {
  error.value = ''
  if (!form.username || !form.password) {
    error.value = '请输入用户名和密码'
    return
  }
  loading.value = true
  try {
    const res = await axios.post('/api/kg/auth/login/', {
      username: form.username,
      password: form.password,
    })
    if (res.data.status === 'success') {
      const { token, user } = res.data
      // 验证角色是否匹配
      if (loginRole.value === 'admin' && user.role !== 'admin') {
        error.value = '该账号不是管理员，请使用管理员账号登录'; loading.value = false; return
      }
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('role', user.role)
      localStorage.setItem('elec_user_id', user.elec_user_id || '')
      window.location.href = user.role === 'admin' ? '/admin' : '/'
    }
  } catch (err) {
    error.value = err.response?.data?.message || '用户名或密码错误'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
* { box-sizing: border-box; }

.login-page {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafbfc;
  overflow: hidden;
}

/* 顶部细线 */
.top-accent {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, #5470c6, #91cc75, #5470c6);
}

/* 主布局 */
.login-wrapper {
  display: flex;
  width: 820px;
  max-width: calc(100vw - 40px);
  background: #fff;
  border: 1px solid #e8ecf0;
  border-radius: 2px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 8px 40px rgba(0,0,0,0.06);
  overflow: hidden;
  z-index: 1;
}

/* 左侧品牌区 */
.brand-panel {
  width: 400px;
  background: #f8f9fb;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  border-right: 1px solid #eef0f4;
}

.brand-content {
  text-align: center;
}

.power-icon {
  margin-bottom: 24px;
}

.brand-panel h1 {
  font-size: 18px;
  font-weight: 500;
  color: #2c3e50;
  margin: 0 0 8px;
  letter-spacing: 0.5px;
}

.subtitle {
  font-size: 13px;
  color: #8c9aa8;
  margin: 0 0 28px;
  font-weight: 300;
}

.feature-tags {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}

.tag {
  font-size: 11px;
  padding: 4px 10px;
  border: 1px solid #dde3ea;
  border-radius: 2px;
  color: #7c8a98;
  font-weight: 300;
}

/* 右侧表单区 */
.form-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 48px;
}

.form-content {
  width: 100%;
  max-width: 280px;
}

.form-content h2 {
  font-size: 20px;
  font-weight: 400;
  color: #333;
  margin: 0 0 6px;
}

.form-desc {
  font-size: 12px;
  color: #999;
  margin: 0 0 20px;
  font-weight: 300;
}

.role-toggle { display: flex; margin-bottom: 20px; border: 1px solid #e0e0e0; border-radius: 6px; overflow: hidden; }
.role-btn { flex: 1; padding: 8px 0; background: #fff; border: none; font-size: 12px; color: #999; cursor: pointer; transition: all 0.15s; }
.role-btn.active { background: #2c3e50; color: #fff; }

.demo-links { text-align: center; margin-bottom: 18px; font-size: 11px; color: #ccc; }
.demo-link { color: #999; cursor: pointer; transition: color 0.15s; }
.demo-link:hover { color: #5470c6; }
.demo-sep { margin: 0 8px; color: #ddd; }

.field {
  margin-bottom: 20px;
}

.field label {
  display: block;
  font-size: 12px;
  color: #999;
  margin-bottom: 6px;
  font-weight: 300;
}

.field input {
  width: 100%;
  padding: 10px 0;
  border: none;
  border-bottom: 1px solid #e0e0e0;
  font-size: 14px;
  color: #333;
  outline: none;
  background: transparent;
  transition: border-color 0.2s;
}

.field input:focus {
  border-bottom-color: #5470c6;
}

.field input::placeholder {
  color: #ccc;
  font-weight: 300;
}

.field input:disabled {
  opacity: 0.5;
}

.error-msg {
  color: #c0392b;
  font-size: 12px;
  text-align: center;
  margin-bottom: 16px;
  padding: 8px 0;
}

.submit-btn {
  width: 100%;
  padding: 12px 0;
  background: #2c3e50;
  color: #fff;
  border: none;
  font-size: 13px;
  cursor: pointer;
  letter-spacing: 1px;
  transition: background 0.2s;
}

.submit-btn:hover {
  background: #5470c6;
}

.submit-btn:disabled {
  background: #bbb;
  cursor: not-allowed;
}

.register-link { text-align: center; margin-top: 20px; font-size: 12px; color: #aaa; }
.register-link a { color: #5470c6; text-decoration: none; }
.register-link a:hover { text-decoration: underline; }

/* 底部波浪 */
.footer-wave {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 60px;
}

/* 响应式 */
@media (max-width: 780px) {
  .login-wrapper {
    flex-direction: column;
    max-width: 380px;
  }
  .brand-panel {
    width: 100%;
    padding: 32px 24px;
    border-right: none;
    border-bottom: 1px solid #eef0f4;
  }
  .power-icon { margin-bottom: 16px; }
  .power-icon svg { width: 40px; height: 40px; }
  .brand-panel h1 { font-size: 15px; }
  .subtitle { margin-bottom: 16px; }
  .form-panel { padding: 32px 28px; }
  .form-desc { margin-bottom: 24px; }
}

@media (max-height: 700px) {
  .brand-panel { padding: 30px 24px; }
  .form-panel { padding: 30px 28px; }
  .field { margin-bottom: 14px; }
  .power-icon svg { width: 40px; height: 40px; }
}
</style>
