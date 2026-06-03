<template>
  <div class="devices-page">
    <!-- 顶部 -->
    <div class="page-top">
      <div>
        <h2>设备管理</h2>
        <p class="sub">Device Management</p>
      </div>
      <button class="add-device-btn" @click="openWizard">+ 添加新设备</button>
    </div>

    <!-- 月选择器 -->
    <div class="month-picker">
      <span class="mp-label">查看月份</span>
      <button class="mp-arrow" @click="prevMonth">&lt;</button>
      <span class="mp-current">{{ viewMonth }}</span>
      <button class="mp-arrow" @click="nextMonth">&gt;</button>
    </div>

    <!-- 设备卡片网格 -->
    <div class="device-grid" v-if="devices.length">
      <div v-for="d in devices" :key="d.device_id" class="device-card" :class="{ damaged: !d.is_active }">
        <!-- 电表区域 -->
        <div class="meter-section">
          <div class="meter-ring">
            <svg viewBox="0 0 120 120" class="meter-svg">
              <circle cx="60" cy="60" r="52" fill="none" stroke="#edf0f4" stroke-width="8"/>
              <circle cx="60" cy="60" r="52" fill="none" stroke="currentColor" stroke-width="8"
                stroke-linecap="round" class="meter-arc"
                :stroke-dasharray="meterDash(d)"
                :stroke-dashoffset="0"
                :style="{ color: meterColor(d), transform: 'rotate(-90deg)', transformOrigin: '60px 60px' }"/>
            </svg>
            <div class="meter-center">
              <span class="meter-kwh">{{ getDeviceKwh(d.device_id) }}</span>
              <span class="meter-unit">kWh</span>
            </div>
          </div>
          <div class="meter-scale">
            <span>0</span><span>25%</span><span>50%</span><span>75%</span><span>100%</span>
          </div>
        </div>

        <!-- 设备信息 -->
        <div class="card-info">
          <div class="card-header">
            <h3>{{ d.custom_name }}</h3>
            <span class="type-badge">{{ d.device_type_code }}</span>
          </div>
          <div class="card-stats">
            <div class="stat">
              <span class="s-label">当前功率</span>
              <span class="s-value">{{ d.effective_power || d.rated_power }}<small>W</small></span>
            </div>
            <div class="stat">
              <span class="s-label">使用习惯</span>
              <span class="s-value">{{ d.usage_habit_name || '-' }}</span>
            </div>
            <div class="stat">
              <span class="s-label">已用年限</span>
              <span class="s-value">{{ d.usage_years?.toFixed(1) }}<small> 年</small></span>
            </div>
            <div class="stat">
              <span class="s-label">损坏概率</span>
              <span class="s-value" :class="{ 'text-red': d.damage_probability > 0.5 }">{{ (d.damage_probability * 100).toFixed(1) }}<small>%</small></span>
            </div>
          </div>
          <div class="damage-bar-wrap">
            <div class="damage-bar">
              <div class="damage-fill" :style="{ width: (d.damage_probability * 100).toFixed(0) + '%' }"
                :class="{ danger: d.damage_probability > 0.5, critical: d.damage_probability > 0.8 }"></div>
            </div>
            <span class="damage-text">{{ d.damage_probability > 0.8 ? '建议立即更换' : d.damage_probability > 0.5 ? '注意维护' : '运行良好' }}</span>
          </div>
          <div class="card-actions">
            <span class="status-dot" :class="{ active: d.is_active, broken: !d.is_active }">
              {{ d.is_active ? '正常运行' : '已损坏' }}
            </span>
            <div class="action-btns">
              <button v-if="!d.is_active" class="act-btn repair-btn" @click="$router.push('/repair')">报修</button>
              <button class="act-btn del-btn" @click="confirmDel(d.device_id)">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="empty-hint" v-else>
      <p>暂无用电设备</p>
      <span>点击上方按钮添加您的第一台设备</span>
    </div>

    <!-- ========== 添加设备向导 ========== -->
    <Teleport to="body">
      <Transition name="wizard-fade">
        <div class="wizard-overlay" v-if="showWizard" @click.self="showWizard = false">
          <Transition name="wizard-slide">
            <div class="wizard-panel" v-if="showWizard">
              <!-- 进度条 -->
              <div class="wizard-progress">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: (wizStep / 4 * 100) + '%' }"></div>
                </div>
                <div class="progress-steps">
                  <span :class="{ done: wizStep >= 1, active: wizStep === 1 }">选择大类</span>
                  <span :class="{ done: wizStep >= 2, active: wizStep === 2 }">选择型号</span>
                  <span :class="{ done: wizStep >= 3, active: wizStep === 3 }">使用习惯</span>
                  <span :class="{ done: wizStep >= 4, active: wizStep === 4 }">确认添加</span>
                </div>
              </div>

              <!-- 步骤1: 选择大类 -->
              <div v-if="wizStep === 1" class="wizard-body">
                <h3>选择设备大类</h3>
                <div class="cat-grid">
                  <div v-for="(items, cat) in cats" :key="cat" class="cat-card" @click="pickCat(cat)">
                    <span class="cat-name">{{ cat }}</span>
                    <span class="cat-count">{{ items.length }} 种</span>
                  </div>
                </div>
              </div>

              <!-- 步骤2: 选择具体型号 -->
              <div v-if="wizStep === 2" class="wizard-body">
                <div class="wiz-back" @click="wizStep = 1">← 返回选择大类</div>
                <h3>选择具体型号</h3>
                <div class="type-list">
                  <div v-for="d in curTypes" :key="d.type_code" class="type-item" @click="pickType(d)">
                    <div class="type-info">
                      <span class="type-name">{{ d.device_name }}</span>
                      <span class="type-meta">{{ d.default_power }}W · 寿命 {{ d.expected_lifespan_years }} 年</span>
                    </div>
                    <span class="type-arrow">&gt;</span>
                  </div>
                </div>
              </div>

              <!-- 步骤3: 使用习惯 -->
              <div v-if="wizStep === 3" class="wizard-body">
                <div class="wiz-back" @click="wizStep = 2">← 返回选择型号</div>
                <h3>{{ selType?.device_name }}</h3>
                <div class="form-row">
                  <div class="form-group">
                    <label>额定功率</label>
                    <div class="power-input">
                      <input v-model="form.rated_power" type="number" class="f-input" />
                      <span class="unit">W</span>
                    </div>
                    <span class="hint">默认 {{ selType?.default_power }}W，可手动调整</span>
                  </div>
                  <div class="form-group">
                    <label>品牌</label>
                    <div class="brand-select-wrap">
                      <select v-model="form.brand_choice" class="f-input">
                        <option value="">请选择品牌</option>
                        <option v-for="b in selDetail?.brands" :key="b.name" :value="b.name">{{ b.name }}</option>
                      </select>
                    </div>
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>平均每天使用</label>
                    <div class="power-input">
                      <input v-model="form.daily_usage_hours" type="number" step="0.5" class="f-input" />
                      <span class="unit">小时</span>
                    </div>
                  </div>
                  <div class="form-group">
                    <label>已使用年限</label>
                    <div class="power-input">
                      <input v-model="form.usage_years" type="number" step="0.1" class="f-input" />
                      <span class="unit">年</span>
                    </div>
                  </div>
                </div>
                <div class="form-group full">
                  <label>使用习惯</label>
                  <div class="habit-options">
                    <div v-for="h in selDetail?.habits" :key="h.id"
                      :class="['habit-chip', { selected: form.usage_habit_id === h.id }]"
                      @click="form.usage_habit_id = h.id">
                      {{ h.name }}
                    </div>
                  </div>
                </div>
                <button class="wiz-next" @click="wizStep = 4">下一步</button>
              </div>

              <!-- 步骤4: 确认 -->
              <div v-if="wizStep === 4" class="wizard-body">
                <div class="wiz-back" @click="wizStep = 3">← 返回修改</div>
                <h3>确认设备信息</h3>
                <div class="confirm-card">
                  <div class="confirm-row"><span>设备类型</span><span>{{ selType?.device_name }}</span></div>
                  <div class="confirm-row"><span>额定功率</span><span>{{ form.rated_power }} W</span></div>
                  <div class="confirm-row"><span>品牌</span><span>{{ form.brand_choice || '未选择' }}</span></div>
                  <div class="confirm-row"><span>日均使用</span><span>{{ form.daily_usage_hours }} 小时</span></div>
                  <div class="confirm-row"><span>已用年限</span><span>{{ form.usage_years }} 年</span></div>
                  <div class="confirm-row"><span>使用习惯</span><span>{{ habitName }}</span></div>
                </div>
                <button class="wiz-next primary" @click="submitAdd" :disabled="submitting">
                  {{ submitting ? '添加中...' : '确认添加' }}
                </button>
              </div>

              <!-- 关闭按钮 -->
              <button class="wiz-close" @click="showWizard = false">&times;</button>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>

    <!-- 删除确认弹窗 -->
    <Teleport to="body">
      <Transition name="wizard-fade">
        <div class="wizard-overlay" v-if="showDelConfirm" @click.self="cancelDel">
          <div class="del-dialog">
            <h3>确认删除</h3>
            <p>删除后该设备及其用电记录将无法恢复，确定要删除吗？</p>
            <div class="del-actions">
              <button class="act-btn" @click="cancelDel">取消</button>
              <button class="act-btn del-confirm" @click="doDel">确认删除</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  getMyDevices, getDeviceTypes, getDeviceTypeDetail, addDevice, deleteDevice,
  getMonthlyConsumption, getSystemMonth,
} from '../api'

const devices = ref([])
const showWizard = ref(false)
const wizStep = ref(1)
const submitting = ref(false)
const cats = ref({})
const curTypes = ref([])
const selType = ref(null)
const selDetail = ref(null)
const form = reactive({ device_type_code: '', rated_power: 0, brand_choice: '', daily_usage_hours: 1, usage_years: 0, usage_habit_id: null })
const deviceKwhMap = ref({})

const viewMonth = ref('')
const sysYear = ref(2026)
const sysMonth = ref(1)

const habitName = computed(() => {
  if (!selDetail.value || !form.usage_habit_id) return '未选择'
  const h = selDetail.value.habits.find(x => x.id === form.usage_habit_id)
  return h ? h.name : '未选择'
})

function meterDash(d) {
  const kwh = parseFloat(deviceKwhMap.value[d.device_id]) || 0
  const maxKwh = (d.effective_power || d.rated_power) * 24 * 31 / 1000
  const pct = Math.min(1, Math.max(0, maxKwh > 0 ? kwh / maxKwh : 0))
  const len = 2 * Math.PI * 52
  return `${(len * pct).toFixed(1)} ${len}`
}

function meterColor(d) {
  const pct = (deviceKwhMap.value[d.device_id] || 0) / ((d.effective_power || d.rated_power) * 24 * 31 / 1000) || 0
  if (pct > 0.7) return '#27ae60'
  if (pct > 0.3) return '#5470c6'
  return '#95a5a6'
}

function getDeviceKwh(deviceId) {
  const v = deviceKwhMap.value[deviceId]
  return v !== undefined && v !== null ? Number(v).toFixed(1) : '--'
}

async function loadData() {
  try {
    const [dRes, sRes] = await Promise.all([getMyDevices(), getSystemMonth()])
    devices.value = dRes.data.devices || []
    sysYear.value = sRes.data.current_year
    sysMonth.value = sRes.data.current_month
    // 默认显示上一个月（有数据的月份）
    viewMonth.value = prevMonthStr(`${sRes.data.current_year}-${String(sRes.data.current_month).padStart(2, '0')}`)
    await loadDeviceKwh()
  } catch (e) { console.error(e) }
}

function prevMonthStr(ym) {
  let [y, m] = ym.split('-').map(Number)
  if (m === 1) { y--; m = 12 } else { m-- }
  return `${y}-${String(m).padStart(2, '0')}`
}

async function loadDeviceKwh() {
  deviceKwhMap.value = {}
  try {
    const res = await getMonthlyConsumption({ year_month: viewMonth.value })
    const data = res.data.data || []
    const entry = data.find(e => e.year_month === viewMonth.value)
    if (entry && entry.devices && entry.devices.length > 0) {
      const map = {}
      entry.devices.forEach(d => { map[d.device_id] = parseFloat(d.kwh) || 0 })
      deviceKwhMap.value = map
    }
  } catch (e) { console.error(e) }
}

function prevMonth() { viewMonth.value = prevMonthStr(viewMonth.value); loadDeviceKwh() }
function nextMonth() { viewMonth.value = nextMonthStr(viewMonth.value); loadDeviceKwh() }
function nextMonthStr(ym) {
  let [y, m] = ym.split('-').map(Number)
  if (m === 12) { y++; m = 1 } else { m++ }
  return `${y}-${String(m).padStart(2, '0')}`
}

onMounted(loadData)

// 添加向导
async function loadTypes() { const r = await getDeviceTypes(); cats.value = r.data.categories }
async function openWizard() { await loadTypes(); showWizard.value = true; wizStep.value = 1 }
function pickCat(k) { curTypes.value = cats.value[k] || []; wizStep.value = 2 }
async function pickType(d) {
  selType.value = d
  const r = await getDeviceTypeDetail(d.type_code)
  selDetail.value = r.data
  form.device_type_code = d.type_code
  form.rated_power = d.default_power
  form.brand_choice = r.data.brands?.[0]?.name || ''
  form.daily_usage_hours = r.data.device_type?.typical_daily_hours || 1
  form.usage_years = 0
  form.usage_habit_id = r.data.habits?.[0]?.id || null
  wizStep.value = 3
}

async function submitAdd() {
  submitting.value = true
  try {
    await addDevice(form)
    showWizard.value = false
    wizStep.value = 1
    await loadData()
  } catch (e) { console.error(e) }
  finally { submitting.value = false }
}

const delTarget = ref(null)
const showDelConfirm = ref(false)

function confirmDel(deviceId) { delTarget.value = deviceId; showDelConfirm.value = true }
async function doDel() {
  if (delTarget.value) { await deleteDevice(delTarget.value); await loadData() }
  showDelConfirm.value = false; delTarget.value = null
}
function cancelDel() { showDelConfirm.value = false; delTarget.value = null }
</script>

<style scoped>
.devices-page { padding: 28px 32px; width: 100%; box-sizing: border-box; }
.page-top { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px; }
.page-top h2 { font-size: 20px; font-weight: 500; color: #2c3e50; margin: 0; }
.sub { font-size: 12px; color: #999; margin: 4px 0 0; font-weight: 300; }
.add-device-btn {
  padding: 9px 22px; background: #2c3e50; color: #fff; border: none; border-radius: 6px;
  font-size: 13px; cursor: pointer; font-family: inherit; transition: background 0.15s;
}
.add-device-btn:hover { background: #5470c6; }

/* 月选择器 */
.month-picker {
  display: flex; align-items: center; gap: 12px; margin-bottom: 20px;
  padding: 10px 16px; background: #fff; border: 1px solid #edf0f4; border-radius: 8px;
}
.mp-label { font-size: 12px; color: #999; }
.mp-arrow {
  width: 28px; height: 28px; border: 1px solid #e0e0e0; border-radius: 6px;
  background: #fff; cursor: pointer; font-size: 14px; color: #555;
  display: flex; align-items: center; justify-content: center; transition: all 0.15s;
}
.mp-arrow:hover { border-color: #5470c6; color: #5470c6; }
.mp-current { font-size: 15px; font-weight: 600; color: #2c3e50; }

/* 设备网格 */
.device-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; }
.device-card {
  background: #fff; border: 1px solid #edf0f4; border-radius: 10px; padding: 20px;
  display: flex; flex-direction: column; gap: 16px; transition: box-shadow 0.2s;
}
.device-card:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.device-card.damaged { opacity: 0.6; }

/* 电表 */
.meter-section { display: flex; flex-direction: column; align-items: center; }
.meter-ring { position: relative; width: 120px; height: 120px; }
.meter-svg { width: 100%; height: 100%; }
.meter-arc { transition: stroke-dasharray 0.6s ease; }
.meter-center {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;
}
.meter-kwh { display: block; font-size: 22px; font-weight: 700; color: #2c3e50; line-height: 1; }
.meter-unit { display: block; font-size: 10px; color: #999; margin-top: 2px; }
.meter-scale {
  display: flex; justify-content: space-between; width: 200px; margin-top: 8px;
  font-size: 9px; color: #ccc;
}

/* 卡片信息 */
.card-info { flex: 1; display: flex; flex-direction: column; gap: 12px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-header h3 { font-size: 14px; font-weight: 600; color: #2c3e50; margin: 0; }
.type-badge { font-size: 10px; padding: 2px 8px; background: #f0f2f5; color: #999; border-radius: 4px; }
.card-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.stat { display: flex; flex-direction: column; gap: 2px; }
.s-label { font-size: 10px; color: #aaa; }
.s-value { font-size: 14px; font-weight: 500; color: #333; }
.s-value small { font-size: 11px; color: #999; font-weight: 400; }
.text-red { color: #e74c3c; }

/* 损坏进度条 */
.damage-bar-wrap { display: flex; align-items: center; gap: 10px; }
.damage-bar { flex: 1; height: 4px; background: #edf0f4; border-radius: 2px; overflow: hidden; }
.damage-fill { height: 100%; background: #5470c6; border-radius: 2px; transition: width 0.4s ease; }
.damage-fill.danger { background: #e6a23c; }
.damage-fill.critical { background: #e74c3c; }
.damage-text { font-size: 10px; color: #999; white-space: nowrap; }

/* 底部操作栏 */
.card-actions { display: flex; justify-content: space-between; align-items: center; padding-top: 8px; border-top: 1px solid #f0f2f5; }
.status-dot { font-size: 11px; padding: 3px 10px; border-radius: 4px; }
.status-dot.active { background: #e8f5e9; color: #67c23a; }
.status-dot.broken { background: #fde8e8; color: #e74c3c; }
.action-btns { display: flex; gap: 6px; }
.act-btn { font-size: 11px; padding: 4px 12px; border-radius: 4px; border: 1px solid #e0e0e0; background: #fff; cursor: pointer; font-family: inherit; transition: all 0.15s; }
.repair-btn:hover { border-color: #e6a23c; color: #e6a23c; }
.del-btn:hover { border-color: #e74c3c; color: #e74c3c; }

.empty-hint { text-align: center; padding: 60px 20px; color: #ccc; }
.empty-hint p { font-size: 18px; margin-bottom: 8px; }
.empty-hint span { font-size: 13px; }

/* ========== 添加设备向导 ========== */
.wizard-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4); z-index: 2000;
  display: flex; align-items: center; justify-content: center;
}
.wizard-panel {
  background: #fff; border-radius: 12px; width: 560px; max-width: 92vw; max-height: 90vh;
  overflow-y: auto; padding: 0; position: relative;
}
.wiz-close {
  position: absolute; top: 12px; right: 14px;
  background: none; border: none; font-size: 22px; color: #ccc; cursor: pointer;
}
.wiz-close:hover { color: #333; }

/* 进度条 */
.wizard-progress { padding: 24px 28px 0; }
.progress-bar { height: 3px; background: #edf0f4; border-radius: 2px; margin-bottom: 12px; }
.progress-fill { height: 100%; background: #2c3e50; border-radius: 2px; transition: width 0.4s ease; }
.progress-steps { display: flex; justify-content: space-between; font-size: 11px; color: #ccc; }
.progress-steps span.done { color: #2c3e50; }
.progress-steps span.active { color: #2c3e50; font-weight: 600; }

/* 向导内容 */
.wizard-body { padding: 20px 28px 28px; }
.wizard-body h3 { font-size: 16px; font-weight: 500; color: #2c3e50; margin: 0 0 16px; }
.wiz-back { display: inline-flex; align-items: center; gap: 4px; font-size: 13px; color: #555; cursor: pointer; margin-bottom: 12px; padding: 6px 14px; border: 1px solid #e0e0e0; border-radius: 6px; background: #fff; transition: all 0.15s; user-select: none; }
.wiz-back:hover { color: #5470c6; border-color: #5470c6; background: #f8f9fd; }

/* 大类卡片 */
.cat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.cat-card {
  padding: 18px 16px; border: 1px solid #edf0f4; border-radius: 8px; cursor: pointer;
  display: flex; flex-direction: column; gap: 4px; transition: all 0.15s;
}
.cat-card:hover { border-color: #5470c6; background: #fafbfd; }
.cat-name { font-size: 14px; font-weight: 500; color: #333; }
.cat-count { font-size: 11px; color: #aaa; }

/* 型号列表 */
.type-list { display: flex; flex-direction: column; gap: 6px; }
.type-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 16px; border: 1px solid #edf0f4; border-radius: 8px; cursor: pointer;
  transition: all 0.15s;
}
.type-item:hover { border-color: #5470c6; background: #fafbfd; }
.type-info { display: flex; flex-direction: column; gap: 2px; }
.type-name { font-size: 13px; font-weight: 500; color: #333; }
.type-meta { font-size: 11px; color: #aaa; }
.type-arrow { font-size: 14px; color: #ccc; }

/* 表单行 */
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }
.form-group { display: flex; flex-direction: column; gap: 4px; }
.form-group.full { margin-bottom: 14px; }
.form-group label { font-size: 11px; color: #999; font-weight: 500; }
.f-input { width: 100%; padding: 9px 12px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 13px; outline: none; font-family: inherit; box-sizing: border-box; transition: border-color 0.15s; }
.f-input:focus { border-color: #5470c6; }
select.f-input { appearance: none; background: #fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12'%3E%3Cpath d='M3 5l3 3 3-3' fill='none' stroke='%23999' stroke-width='1.5'/%3E%3C/svg%3E") no-repeat right 10px center; padding-right: 32px; cursor: pointer; }
.power-input { display: flex; align-items: center; gap: 8px; }
.power-input .f-input { flex: 1; }
.unit { font-size: 13px; color: #999; }
.hint { font-size: 10px; color: #bbb; }

/* 习惯选择器 */
.habit-options { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 4px; }
.habit-chip {
  padding: 7px 14px; border: 1px solid #e0e0e0; border-radius: 20px; font-size: 12px;
  color: #666; cursor: pointer; transition: all 0.15s; user-select: none;
}
.habit-chip:hover { border-color: #5470c6; color: #5470c6; }
.habit-chip.selected { background: #2c3e50; color: #fff; border-color: #2c3e50; }

/* 确认卡片 */
.confirm-card {
  background: #f8f9fb; border-radius: 8px; padding: 16px; margin-bottom: 16px;
}
.confirm-row { display: flex; justify-content: space-between; padding: 8px 0; font-size: 13px; border-bottom: 1px solid #eef0f3; }
.confirm-row:last-child { border-bottom: none; }
.confirm-row span:first-child { color: #999; }
.confirm-row span:last-child { color: #333; font-weight: 500; }

.wiz-next {
  width: 100%; padding: 12px 0; background: #2c3e50; color: #fff; border: none; border-radius: 8px;
  font-size: 14px; cursor: pointer; font-family: inherit; transition: background 0.15s;
}
.wiz-next:hover { background: #5470c6; }
.wiz-next.primary { background: #27ae60; }
.wiz-next.primary:hover { background: #2ecc71; }
.wiz-next:disabled { opacity: 0.6; cursor: not-allowed; }

/* 删除确认弹窗 */
.del-dialog {
  background: #fff; border-radius: 12px; padding: 32px; width: 400px; max-width: 90vw; text-align: center;
}
.del-dialog h3 { font-size: 16px; color: #2c3e50; margin: 0 0 12px; }
.del-dialog p { font-size: 13px; color: #888; margin: 0 0 24px; line-height: 1.6; }
.del-actions { display: flex; gap: 10px; justify-content: center; }
.del-actions .act-btn { padding: 9px 28px; border-radius: 6px; font-size: 13px; cursor: pointer; font-family: inherit; border: 1px solid #e0e0e0; background: #fff; color: #555; transition: all 0.15s; }
.del-actions .act-btn:hover { border-color: #999; }
.del-actions .del-confirm { background: #e74c3c; color: #fff; border-color: #e74c3c; }
.del-actions .del-confirm:hover { background: #c0392b; border-color: #c0392b; }

/* 过渡动画 */
.wizard-fade-enter-active, .wizard-fade-leave-active { transition: opacity 0.25s; }
.wizard-fade-enter-from, .wizard-fade-leave-to { opacity: 0; }
.wizard-slide-enter-active, .wizard-slide-leave-active { transition: all 0.3s ease; }
.wizard-slide-enter-from { opacity: 0; transform: translateY(20px) scale(0.97); }
.wizard-slide-leave-to { opacity: 0; transform: translateY(-10px) scale(0.98); }
</style>
