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
            <span class="link-sep">|</span>
            <span class="doc-link" @click="showDoc = true">操作文档</span>
          </div>

        </div>
      </div>
    </div>

    <!-- 操作文档弹窗 -->
    <Teleport to="body">
      <Transition name="pop">
        <div class="doc-overlay" v-if="showDoc" @click.self="showDoc = false">
          <div class="doc-modal">
            <div class="doc-head">
              <div>
                <h2>系统操作手册</h2>
                <p class="doc-sub">电力用户画像知识图谱系统 · 文档编号 KG-OP-001 · V1.0</p>
              </div>
              <button class="doc-close" @click="showDoc = false">×</button>
            </div>
            <div class="doc-content">

              <!-- 第1章 系统概述 -->
              <section>
                <h3>第1章 系统概述</h3>

                <h4>1.1 系统简介</h4>
                <p>本系统基于知识图谱技术对电力用户的用电行为、设备配置、缴费记录、家庭特征等多维度数据进行可视化建模与分析，帮助用户了解自身用电习惯，辅助管理者进行全局用电调度。</p>
                <div class="doc-accounts">
                  <span><b>管理员</b>&nbsp; admin / 123456</span>
                  <span><b>用户1</b>&nbsp; user001 / 123456</span>
                  <span><b>用户2</b>&nbsp; user002 / 123456</span>
                  <span><b>用户3</b>&nbsp; user003 / 123456</span>
                </div>
                <p class="doc-note">※ 本系统为演示版本，数据存储于浏览器本地。清除浏览器缓存或更换浏览器将恢复初始演示数据。</p>

                <h4>1.2 技术特性</h4>
                <ul>
                  <li><b>知识图谱可视化</b>：基于 ECharts 力导向图，支持节点点击详查、双击展开折叠、自由拖拽缩放</li>
                  <li><b>威布尔分布模型</b>：设备损坏概率采用 Weibull 分布计算，参数由设备类型、品牌品质系数和已用年限共同决定</li>
                  <li><b>月度模拟引擎</b>：管理员一键推进，自动生成全量用户当月用电、账单，更新设备状态并检测欠费</li>
                  <li><b>老化功率修正</b>：设备有效功率随使用年限按二次衰减曲线动态调整</li>
                </ul>
              </section>

              <!-- 第2章 家庭用户 -->
              <section>
                <h3>第2章 家庭用户操作指南</h3>

                <h4>2.1 登录系统</h4>
                <ol>
                  <li>打开系统网址，进入登录界面</li>
                  <li>确认角色切换按钮选中「家庭用户」（蓝色高亮）</li>
                  <li>输入用户名和密码，或点击「用户 Demo」快速填充 user001 / 123456</li>
                  <li>点击「登 录」按钮，验证通过后自动跳转至用户首页</li>
                </ol>

                <h4>2.2 首页 — 个人信息维护</h4>
                <p>用户首页以左右双栏布局展示。左侧展示个人画像摘要（头像/姓名/标签）、四项核心统计指标、基本信息面板、住房信息面板、家庭成员面板、收入信息面板。右侧为系统公告栏和留言板。</p>
                <p><b>编辑信息</b>：点击各面板右上角「编辑」按钮进入编辑状态，下拉选项字段均从系统选项字典获取。修改后点击「保存」实时更新。</p>
                <p><b>家庭成员管理</b>：点击「管理」按钮可添加或删除家庭成员（姓名/关系/是否同住）。</p>
                <p><b>留言板</b>：点击「写留言」发送留言给管理员。未回复留言可撤回，已回复留言不可撤回。</p>

                <h4>2.3 用电画像 — 知识图谱</h4>
                <p>系统的核心可视化模块。左侧展示用户画像卡片、彩色标签词云和月度用电趋势折线图。右侧为力导向知识图谱。</p>
                <p><b>交互操作</b>：</p>
                <ul>
                  <li><b>双击大类节点</b>：展开/折叠该类别下所有子节点。初始仅显示中心用户节点 + 5 个大类节点。</li>
                  <li><b>单击任意节点</b>：右侧滑出详情面板，查看该节点的完整数据信息。</li>
                  <li>设备节点颜色按六大类别区分（蓝=空调/黄=厨房/绿=清洁/红=影音/青=照明/棕=其他）</li>
                  <li>图谱支持鼠标滚轮缩放和拖拽平移</li>
                </ul>

                <h4>2.4 设备管理</h4>
                <p>以卡片网格展示用户所有用电设备，每张卡片含设备名称、环形用电图、有效功率、使用习惯、已用年限和损坏概率。</p>
                <p><b>添加设备</b>：四步向导（选择类别 → 选择型号 → 填写品牌和参数 → 确认）。系统自动使用威布尔分布计算有效功率和损坏概率。</p>
                <p><b>删除设备</b>：点击卡片上的「删除」按钮，确认后移除。</p>
                <p><b>月份切换</b>：顶部切换按钮可查看不同月份的设备用电数据。</p>

                <h4>2.5 电费缴费</h4>
                <p>左侧列出待缴账单，点击「缴费」进入四步支付向导（账单摘要 → 支付方式 → 密码输入 → 处理完成）。缴费后账单状态变为「已缴」。右侧展示缴费通知栏，底部表格展示缴费历史（支持按状态和年份筛选）。</p>

                <h4>2.6 维修报单</h4>
                <p>页面展示设备运行状态：正常设备以绿色提示汇总，损坏设备以红色卡片展示。报修流程为三步向导（选择设备 → 选择故障类型并填写描述 → 确认提交）。维修完成后可对服务进行一至五星评价。</p>
              </section>

              <!-- 第3章 管理员 -->
              <section>
                <h3>第3章 管理员操作指南</h3>

                <h4>3.1 系统概览 — 月度推进</h4>
                <p><b>「推进至下月」</b>是系统最重要的管理员操作。点击按钮并确认后，系统自动执行以下流程：遍历所有用户活动设备计算当月用电量 → 汇总维修费用生成当月账单 → 检查连续欠费（≥2 月）并标记警告 → 更新设备使用年限并重新计算损坏概率 → 损坏概率超 80% 的设备标记为损坏 → 系统月份 +1。</p>
                <p>推进完成后显示结果提示（"推进完成！XX 条记录，YY 张账单"）。</p>

                <h4>3.2 系统概览 — 公告与留言</h4>
                <p><b>公告管理</b>：管理员可发布/置顶/删除系统公告，公告将在所有用户首页右侧展示。置顶公告优先显示。</p>
                <p><b>留言管理</b>：展示所有用户留言，管理员可逐条回复（内联输入框）或删除。</p>

                <h4>3.3 知识图谱（管理员视角）</h4>
                <p>页面顶部下拉框可选择任意家庭用户，查看其个性化知识图谱。页面布局和交互与用户端「用电画像」完全一致：左侧画像面板 + 右侧力导向图。切换用户后图谱即时刷新。</p>

                <h4>3.4 数据管理</h4>
                <p>五个子标签页：</p>
                <ul>
                  <li><b>用户管理</b>：表格展示全部用户（户号/用户名/姓名/电话/设备数），支持新增/编辑/查看详情/删除，搜索框可按姓名或用户名实时筛选</li>
                  <li><b>设备管理</b>：全部用户设备列表，支持按设备名称搜索和按类别下拉筛选，可删除设备</li>
                  <li><b>维修审核</b>：全部维修工单列表，支持按状态下拉筛选（待处理/已派单/维修中/已完成）；待处理工单可「派单」（输入维修人员姓名），维修中工单可「完成」（输入维修费用金额）</li>
                  <li><b>系统公告</b>：发布公告（标题/内容/置顶标记），置顶公告优先排列</li>
                  <li><b>用户留言</b>：全部留言列表（用户/内容/回复状态/日期），点击「回复」展开内联输入框</li>
                </ul>
              </section>

              <!-- 第4章 数据说明 -->
              <section>
                <h3>第4章 数据与算法说明</h3>
                <p><b>演示数据规模</b>：4 个演示用户 · 34 种预设电器 · 20 台设备 · 6 个月用电记录 · 19 类选项字典</p>
                <p><b>威布尔分布模型</b>：P(损坏) = 1 - exp(-(t / η)^β)，其中 η = 预期寿命 × 1.2 × BQF（品牌品质系数）。老化功率修正采用二次衰减曲线。</p>
                <p><b>数据存储</b>：本系统为纯前端演示版本，数据存储于浏览器 localStorage 中。同一浏览器内关闭标签页后重新打开数据保留。清除缓存或更换浏览器将恢复初始数据。</p>
              </section>

              <!-- 第5章 常见问题 -->
              <section>
                <h3>第5章 常见问题</h3>
                <div class="doc-faq">
                  <p><b>Q：登录时提示"用户名或密码错误"？</b><br>A：检查角色切换是否正确，确认键盘未开启大写锁定。演示账号密码均为 123456。</p>
                  <p><b>Q：推进月份后账单在哪看？</b><br>A：退出管理员账号，以家庭用户身份登录，进入「电费缴费」即可查看新生成的账单。</p>
                  <p><b>Q：如何判断设备是否损坏？</b><br>A：管理员推进月份时，系统根据威布尔分布自动计算损坏概率。超过 80% 阈值的设备被标记为损坏。</p>
                  <p><b>Q：数据会不会丢失？</b><br>A：同一浏览器内数据持久保留。清除浏览器缓存、使用无痕模式、更换浏览器或设备将恢复初始数据。</p>
                  <p><b>Q：知识图谱节点太密看不清？</b><br>A：使用鼠标滚轮缩放；双击已展开的大类节点可折叠子节点，减少画面复杂度。</p>
                  <p><b>Q：如何注册新用户？</b><br>A：登录界面点击「立即注册」，按六步向导依次填写账户、基本信息、住房、设备偏好、收入信息即可。</p>
                </div>
              </section>

            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

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
import { login } from '../api/index.js'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const loginRole = ref('user')
const form = reactive({ username: '', password: '' })
const showDoc = ref(false)

function fillDemo(role) {
  loginRole.value = role
  const accounts = { admin: 'admin', user: 'user001' }
  form.username = accounts[role]
  form.password = '123456'
}

async function handleLogin() {
  error.value = ''
  if (!form.username || !form.password) {
    error.value = '请输入用户名和密码'
    return
  }
  loading.value = true
  try {
    const res = await login(form.username, form.password)
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
      // 用 location.replace 避免浏览器缓存导致的导航栏角色错乱
      window.location.replace(user.role === 'admin' ? '/#/admin' : '/#/')
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
.register-link a { color: #5470c6; text-decoration: none; font-weight: 500; }
.register-link a:hover { text-decoration: underline; }
.link-sep { margin: 0 8px; color: #ddd; }
.doc-link { color: #5470c6; cursor: pointer; font-weight: 500; }
.doc-link:hover { text-decoration: underline; }

/* 操作文档弹窗 */
.doc-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 2000;
  display: flex; align-items: center; justify-content: center;
}
.doc-modal {
  background: #fff; border-radius: 14px; width: 860px; max-height: 88vh;
  display: flex; flex-direction: column; position: relative;
  box-shadow: 0 24px 80px rgba(0,0,0,0.2);
}
.doc-head {
  display: flex; justify-content: space-between; align-items: flex-start;
  padding: 28px 36px 18px; border-bottom: 1px solid #edf0f4;
  flex-shrink: 0;
}
.doc-head h2 { font-size: 22px; color: #1a1a2e; margin: 0; font-weight: 700; }
.doc-head .doc-sub { font-size: 12px; color: #999; margin: 4px 0 0; }
.doc-close {
  width: 32px; height: 32px; background: #f5f5f5; border: none; border-radius: 50%;
  font-size: 18px; color: #999; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all .15s;
}
.doc-close:hover { background: #e8e8e8; color: #333; }
.doc-content {
  padding: 28px 36px 36px; overflow-y: auto; flex: 1;
  font-size: 13px; color: #555; line-height: 1.8;
}
.doc-content h3 { font-size: 16px; color: #1a1a2e; margin: 28px 0 14px; padding-bottom: 8px; border-bottom: 2px solid #5470c6; }
.doc-content h4 { font-size: 14px; color: #2c3e50; margin: 18px 0 6px; font-weight: 600; }
.doc-content p { margin: 4px 0 12px; }
.doc-content b { color: #2c3e50; }
.doc-content ul, .doc-content ol { margin: 8px 0 14px; padding-left: 22px; }
.doc-content li { margin: 4px 0; }
.doc-note { font-size: 12px; color: #999; padding: 8px 14px; background: #fffbe6; border-radius: 6px; border-left: 3px solid #f5d23e; }
.doc-accounts {
  display: flex; gap: 20px; flex-wrap: wrap; margin: 12px 0; padding: 12px 16px;
  background: #f7f9fc; border-radius: 8px; font-size: 12px; border: 1px solid #edf0f4;
}
.doc-accounts span { color: #555; }
.doc-faq p { margin: 6px 0 16px; padding-left: 8px; border-left: 2px solid #edf0f4; }

/* 弹窗动画 */
.pop-enter-active, .pop-leave-active { transition: opacity 0.25s; }
.pop-enter-active .doc-modal, .pop-leave-active .doc-modal { transition: transform 0.25s; }
.pop-enter-from, .pop-leave-to { opacity: 0; }
.pop-enter-from .doc-modal { transform: scale(0.95) translateY(12px); }
.pop-leave-to .doc-modal { transform: scale(0.95) translateY(12px); }

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
