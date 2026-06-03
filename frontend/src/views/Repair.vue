<template>
  <div class="repair-page">
    <div class="page-top">
      <div>
        <h2>维修报单</h2>
        <p class="sub">Repair Service</p>
      </div>
      <button class="add-btn" v-if="damagedDevices.length > 0" @click="openWizard">+ 新建报修</button>
    </div>

    <!-- 设备状态区 -->
    <section class="status-section">
      <!-- 全部正常 -->
      <div class="all-good" v-if="damagedDevices.length === 0">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#67c23a" stroke-width="1.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        <div>
          <strong>所有设备运行正常</strong>
          <p>当前 {{ devices.length }} 台设备均处于正常工作状态，暂无需报修。</p>
        </div>
      </div>

      <!-- 损坏设备列表 -->
      <div class="damaged-list" v-else>
        <div class="dl-header">
          <h3>故障设备</h3>
          <span>{{ damagedDevices.length }} 台需要维修</span>
        </div>
        <div v-for="d in damagedDevices" :key="d.device_id" class="damaged-card">
          <div class="dc-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e74c3c" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          </div>
          <div class="dc-body">
            <div class="dc-name">{{ d.custom_name }}</div>
            <div class="dc-meta">{{ d.device_type_code }} · {{ d.effective_power || d.rated_power }}W · 已用 {{ d.usage_years?.toFixed(1) }} 年</div>
            <div class="dc-prob">损坏概率 {{ (d.damage_probability * 100).toFixed(1) }}%</div>
          </div>
          <button class="dc-repair-btn" @click="startRepair(d)">报修</button>
        </div>
      </div>

      <!-- 正常设备折叠 -->
      <div class="normal-devices" v-if="normalDevices.length > 0">
        <div class="nd-header" @click="showNormal = !showNormal">
          <span>正常设备 ({{ normalDevices.length }} 台)</span>
          <span class="nd-arrow" :class="{ open: showNormal }">▼</span>
        </div>
        <div class="nd-list" v-if="showNormal">
          <span v-for="d in normalDevices" :key="d.device_id" class="nd-tag">{{ d.custom_name }}</span>
        </div>
      </div>
    </section>

    <!-- 报修历史 -->
    <section class="history-module">
      <div class="module-header">
        <h3>报修记录</h3>
      </div>
      <div class="module-body">
        <table class="history-table" v-if="orders.length">
          <thead><tr><th>单号</th><th>设备</th><th>故障类型</th><th>描述</th><th>状态</th><th>费用</th><th>评价</th></tr></thead>
          <tbody>
            <tr v-for="o in orders" :key="o.order_id">
              <td class="td-id">{{ o.order_id?.slice(-8) }}</td>
              <td>{{ o.device_name }}</td>
              <td>{{ o.fault_text }}</td>
              <td class="td-desc">{{ o.fault_description?.slice(0, 30) }}{{ o.fault_description?.length > 30 ? '...' : '' }}</td>
              <td><span :class="['h-st', 'st-' + o.status]">{{ o.status_text }}</span></td>
              <td>{{ o.repair_cost ? '¥' + o.repair_cost : '-' }}</td>
              <td>
                <span v-if="o.rating">{{ '★'.repeat(o.rating) }}</span>
                <button v-else-if="o.status >= 4" class="rate-btn" @click="rateOrder(o)">评价</button>
                <span v-else>-</span>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="empty-hint" v-else>暂无报修记录</div>
      </div>
    </section>

    <!-- ========== 报修向导 ========== -->
    <Teleport to="body">
      <Transition name="wiz-fade">
        <div class="wiz-overlay" v-if="showWizard" @click.self="showWizard = false">
          <div class="wiz-panel">
            <!-- 进度条 -->
            <div class="wiz-progress">
              <div class="wiz-bar"><div class="wiz-fill" :style="{ width: (wizStep / 3 * 100) + '%' }"></div></div>
              <div class="wiz-steps">
                <span :class="{ done: wizStep >= 1, active: wizStep === 1 }">选择设备</span>
                <span :class="{ done: wizStep >= 2, active: wizStep === 2 }">描述故障</span>
                <span :class="{ done: wizStep >= 3, active: wizStep === 3 }">确认提交</span>
              </div>
            </div>

            <!-- 步骤1: 选设备 -->
            <div v-if="wizStep === 1" class="wiz-body">
              <h3>选择报修设备</h3>
              <div class="device-options">
                <div v-for="d in damagedDevices" :key="d.device_id"
                  :class="['dev-opt', { selected: form.device_id === d.device_id }]"
                  @click="form.device_id = d.device_id; form.device_type = d.device_type_code">
                  <div class="do-name">{{ d.custom_name }}</div>
                  <div class="do-meta">{{ d.device_type_code }} · 损坏概率 {{ (d.damage_probability * 100).toFixed(0) }}%</div>
                </div>
              </div>
              <button class="wiz-next" :disabled="!form.device_id" @click="wizStep = 2">下一步</button>
            </div>

            <!-- 步骤2: 描述故障 -->
            <div v-if="wizStep === 2" class="wiz-body">
              <div class="wiz-back" @click="wizStep = 1">← 返回</div>
              <h3>描述故障情况</h3>
              <div class="form-group">
                <label>故障类型</label>
                <div class="fault-grid">
                  <div v-for="f in faultOptions" :key="f.value"
                    :class="['fault-chip', { selected: form.fault_type === f.value }]"
                    @click="form.fault_type = f.value">
                    {{ f.label }}
                  </div>
                </div>
              </div>
              <div class="form-group">
                <label>详细描述</label>
                <textarea v-model="form.fault_description" class="f-textarea" placeholder="请描述故障现象，如：空调不制冷，开机后出风口无冷风，已经出现一周..." rows="3"></textarea>
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>联系人</label>
                  <input v-model="form.contact_name" class="f-input" placeholder="姓名" />
                </div>
                <div class="form-group">
                  <label>联系电话</label>
                  <input v-model="form.contact_phone" class="f-input" placeholder="手机号" />
                </div>
              </div>
              <div class="form-group">
                <label>预约上门日期</label>
                <input type="date" v-model="form.appointment_date" class="f-input" />
              </div>
              <button class="wiz-next" @click="wizStep = 3">下一步</button>
            </div>

            <!-- 步骤3: 确认 -->
            <div v-if="wizStep === 3" class="wiz-body">
              <div class="wiz-back" @click="wizStep = 2">← 返回修改</div>
              <h3>确认报修信息</h3>
              <div class="confirm-card">
                <div class="cc-row"><span>报修设备</span><span>{{ selDeviceName }}</span></div>
                <div class="cc-row"><span>故障类型</span><span>{{ faultLabel }}</span></div>
                <div class="cc-row"><span>故障描述</span><span>{{ form.fault_description }}</span></div>
                <div class="cc-row"><span>联系人</span><span>{{ form.contact_name }}</span></div>
                <div class="cc-row"><span>联系电话</span><span>{{ form.contact_phone }}</span></div>
                <div class="cc-row"><span>上门日期</span><span>{{ form.appointment_date || '尽快安排' }}</span></div>
              </div>
              <button class="wiz-next primary" @click="submitRepair" :disabled="submitting">{{ submitting ? '提交中...' : '确认提交' }}</button>
            </div>

            <button class="wiz-close" @click="showWizard = false">&times;</button>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getMyDevices, getRepairOrders, createRepairOrder, rateRepair } from '../api'

const devices = ref([])
const orders = ref([])
const showWizard = ref(false)
const wizStep = ref(1)
const submitting = ref(false)
const showNormal = ref(false)
const form = reactive({ device_id: '', device_type: '', fault_type: 1, fault_description: '', contact_name: '', contact_phone: '', appointment_date: '' })

const damagedDevices = computed(() => devices.value.filter(d => !d.is_active))
const normalDevices = computed(() => devices.value.filter(d => d.is_active))
const selDeviceName = computed(() => damagedDevices.value.find(d => d.device_id === form.device_id)?.custom_name || '-')
const faultLabel = computed(() => faultOptions.find(f => f.value === form.fault_type)?.label || '-')

const faultOptions = [
  { value: 1, label: '无法开机' }, { value: 2, label: '运行异常/效果差' },
  { value: 3, label: '漏电/跳闸' }, { value: 4, label: '噪音/异响过大' },
  { value: 5, label: '不制冷/不制热' }, { value: 6, label: '漏水/渗水' },
  { value: 7, label: '频繁启停' }, { value: 8, label: '异味/冒烟' },
  { value: 9, label: '显示异常/报错' }, { value: 10, label: '其他故障' },
]

onMounted(async () => {
  const [dRes, oRes] = await Promise.all([getMyDevices(), getRepairOrders()])
  devices.value = dRes.data.devices || []
  orders.value = oRes.data.orders || []
})

function startRepair(d) { form.device_id = d.device_id; form.device_type = d.device_type_code; form.fault_type = 1; form.fault_description = ''; form.contact_name = ''; form.contact_phone = ''; form.appointment_date = ''; showWizard.value = true; wizStep.value = 1 }

async function submitRepair() {
  submitting.value = true
  try { await createRepairOrder(form); showWizard.value = false; wizStep.value = 1; const [dRes, oRes] = await Promise.all([getMyDevices(), getRepairOrders()]); devices.value = dRes.data.devices || []; orders.value = oRes.data.orders || [] }
  catch (e) { console.error(e) }
  finally { submitting.value = false }
}

async function rateOrder(o) { const r = prompt('评分 1-5 星：', '5'); if (r) { await rateRepair(o.order_id, parseInt(r)); const res = await getRepairOrders(); orders.value = res.data.orders || [] } }
</script>

<style scoped>
.repair-page { padding: 24px; width: 100%; box-sizing: border-box; }
.page-top { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 18px; }
.page-top h2 { font-size: 20px; font-weight: 500; color: #2c3e50; margin: 0; }
.sub { font-size: 12px; color: #999; margin: 2px 0 0; }
.add-btn { padding: 9px 22px; background: #2c3e50; color: #fff; border: none; border-radius: 6px; font-size: 13px; cursor: pointer; font-family: inherit; }
.add-btn:hover { background: #5470c6; }

/* 设备状态 */
.status-section { margin-bottom: 18px; }
.all-good { display: flex; align-items: center; gap: 14px; padding: 24px; background: #f6fdf6; border: 1px solid #d4edda; border-radius: 10px; }
.all-good strong { font-size: 14px; color: #2c3e50; display: block; }
.all-good p { font-size: 12px; color: #888; margin: 2px 0 0; }

.damaged-list { display: flex; flex-direction: column; gap: 10px; margin-bottom: 12px; }
.dl-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.dl-header h3 { font-size: 13px; font-weight: 600; color: #555; margin: 0; }
.dl-header span { font-size: 11px; color: #e74c3c; }
.damaged-card { display: flex; align-items: center; gap: 12px; padding: 14px 16px; background: #fff; border: 1px solid #fcc; border-radius: 8px; }
.dc-body { flex: 1; }
.dc-name { font-size: 13px; font-weight: 600; color: #333; }
.dc-meta { font-size: 11px; color: #999; margin: 2px 0; }
.dc-prob { font-size: 11px; color: #e74c3c; }
.dc-repair-btn { padding: 8px 18px; background: #e74c3c; color: #fff; border: none; border-radius: 6px; font-size: 12px; cursor: pointer; font-family: inherit; }
.dc-repair-btn:hover { background: #c0392b; }

.normal-devices { background: #fff; border: 1px solid #edf0f4; border-radius: 8px; }
.nd-header { display: flex; justify-content: space-between; padding: 10px 16px; font-size: 12px; color: #999; cursor: pointer; }
.nd-arrow { transition: transform 0.2s; }
.nd-arrow.open { transform: rotate(180deg); }
.nd-list { padding: 0 16px 12px; display: flex; flex-wrap: wrap; gap: 6px; }
.nd-tag { font-size: 11px; padding: 3px 10px; background: #e8f5e9; color: #67c23a; border-radius: 4px; }

/* 历史 */
.history-module { background: #fff; border: 1px solid #edf0f4; border-radius: 10px; overflow: hidden; }
.module-header { padding: 12px 18px; border-bottom: 1px solid #f0f2f5; }
.module-header h3 { font-size: 13px; font-weight: 600; color: #555; margin: 0; }
.module-body { padding: 16px 18px; }
.history-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.history-table th { text-align: left; padding: 6px 0 8px; font-size: 10px; color: #aaa; font-weight: 500; border-bottom: 1px solid #f0f2f5; }
.history-table td { padding: 8px 0; border-bottom: 1px solid #f8f9fb; }
.td-id { font-family: monospace; font-size: 11px; color: #999; }
.td-desc { max-width: 140px; color: #666; }
.h-st { font-size: 10px; padding: 2px 7px; border-radius: 4px; }
.st-1 { background: #fef3e2; color: #e6a23c; }
.st-2 { background: #eef2ff; color: #5470c6; }
.st-3 { background: #eef2ff; color: #5470c6; }
.st-4 { background: #e8f5e9; color: #67c23a; }
.st-5 { background: #f0f2f5; color: #999; }
.st-6 { background: #f5f5f5; color: #bbb; }
.rate-btn { font-size: 11px; padding: 2px 8px; border: 1px solid #5470c6; background: #fff; color: #5470c6; border-radius: 4px; cursor: pointer; font-family: inherit; }
.empty-hint { text-align: center; padding: 28px; color: #ccc; font-size: 13px; }

/* 向导 */
.wiz-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.4); z-index: 2000; display: flex; align-items: center; justify-content: center; }
.wiz-panel { background: #fff; border-radius: 12px; width: 500px; max-width: 92vw; max-height: 90vh; overflow-y: auto; padding: 0; position: relative; }
.wiz-close { position: absolute; top: 12px; right: 14px; background: none; border: none; font-size: 22px; color: #ccc; cursor: pointer; }
.wiz-close:hover { color: #333; }
.wiz-progress { padding: 24px 24px 0; }
.wiz-bar { height: 3px; background: #edf0f4; border-radius: 2px; margin-bottom: 10px; }
.wiz-fill { height: 100%; background: #2c3e50; border-radius: 2px; transition: width 0.4s ease; }
.wiz-steps { display: flex; justify-content: space-between; font-size: 11px; color: #ccc; }
.wiz-steps span.done { color: #2c3e50; }
.wiz-steps span.active { color: #2c3e50; font-weight: 600; }
.wiz-body { padding: 18px 24px 24px; }
.wiz-body h3 { font-size: 15px; font-weight: 500; color: #2c3e50; margin: 0 0 14px; }
.wiz-back { font-size: 12px; color: #999; cursor: pointer; margin-bottom: 8px; display: inline-block; }
.wiz-back:hover { color: #5470c6; }
.wiz-next { width: 100%; padding: 11px 0; background: #2c3e50; color: #fff; border: none; border-radius: 8px; font-size: 13px; cursor: pointer; font-family: inherit; }
.wiz-next:hover { background: #5470c6; }
.wiz-next:disabled { opacity: 0.5; cursor: not-allowed; }
.wiz-next.primary { background: #27ae60; }
.wiz-next.primary:hover { background: #2ecc71; }

.device-options { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; }
.dev-opt { padding: 12px 14px; border: 1px solid #edf0f4; border-radius: 8px; cursor: pointer; transition: all 0.15s; }
.dev-opt:hover { border-color: #5470c6; }
.dev-opt.selected { border-color: #2c3e50; background: #f8f9fb; }
.do-name { font-size: 13px; font-weight: 500; color: #333; }
.do-meta { font-size: 11px; color: #aaa; margin-top: 2px; }

.form-group { margin-bottom: 14px; }
.form-group label { display: block; font-size: 11px; color: #999; margin-bottom: 4px; }
.fault-grid { display: flex; flex-wrap: wrap; gap: 6px; }
.fault-chip { padding: 6px 14px; border: 1px solid #e0e0e0; border-radius: 20px; font-size: 12px; color: #666; cursor: pointer; transition: all 0.15s; user-select: none; }
.fault-chip:hover { border-color: #5470c6; color: #5470c6; }
.fault-chip.selected { background: #2c3e50; color: #fff; border-color: #2c3e50; }
.f-textarea { width: 100%; padding: 10px 12px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 13px; outline: none; font-family: inherit; resize: vertical; }
.f-textarea:focus { border-color: #5470c6; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.f-input { width: 100%; padding: 8px 12px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 13px; outline: none; font-family: inherit; box-sizing: border-box; }
.f-input:focus { border-color: #5470c6; }

.confirm-card { background: #f8f9fb; border-radius: 8px; padding: 14px; margin-bottom: 16px; }
.cc-row { display: flex; justify-content: space-between; padding: 7px 0; font-size: 12px; border-bottom: 1px solid #eef0f3; }
.cc-row:last-child { border-bottom: none; }
.cc-row span:first-child { color: #999; }
.cc-row span:last-child { color: #333; font-weight: 500; max-width: 60%; text-align: right; }

.wiz-fade-enter-active, .wiz-fade-leave-active { transition: opacity 0.25s; }
.wiz-fade-enter-from, .wiz-fade-leave-to { opacity: 0; }
</style>
