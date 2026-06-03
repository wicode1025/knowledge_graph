<template>
  <div class="billing-page">
    <div class="page-top">
      <div>
        <h2>缴费管理</h2>
        <p class="sub">Billing & Payment</p>
      </div>
    </div>

    <!-- 上半部分：左侧双缴费 + 右侧通知 -->
    <div class="top-layout">
      <div class="left-pays">
        <!-- 电费缴费 -->
        <section class="pay-module">
          <div class="module-header">
            <div class="mh-left">
              <span class="mh-icon e"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg></span>
              <div><h3>电费缴费</h3><p>{{ unpaidBills.length }} 笔待缴账单</p></div>
            </div>
            <span :class="['mh-badge', unpaidBills.length>0?'pending':'done']">{{ unpaidBills.length>0?'待缴费':'已缴清' }}</span>
          </div>
          <div class="module-body" v-if="unpaidBills.length>0">
            <div v-for="b in unpaidBills" :key="b.bill_id" class="bill-row-item">
              <div class="bri-info">
                <span class="bri-month">{{ b.bill_month }}</span>
                <span class="bri-meta">{{ b.total_kwh }} kWh · ¥{{ b.total_amount }}</span>
                <span v-if="b.warning_flag" class="bri-warn">欠费警告</span>
              </div>
              <button class="pay-btn" @click="openPayModal(b,'electricity')">缴费</button>
            </div>
          </div>
          <div class="module-body" v-else><div class="no-data">所有账单已缴清</div></div>
        </section>

        <!-- 维修缴费 -->
        <section class="pay-module">
          <div class="module-header">
            <div class="mh-left">
              <span class="mh-icon r"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg></span>
              <div><h3>维修缴费</h3><p>本月待缴维修费用</p></div>
            </div>
            <span :class="['mh-badge', repairBillStatus]">{{ repairBillStatusText }}</span>
          </div>
          <div class="module-body" v-if="repairItems.length > 0">
            <div v-for="item in repairItems" :key="item.ref_id" class="repair-row">
              <div class="rr-info"><span class="rr-name">{{ item.item_desc }}</span><span class="rr-ref">单号 {{ item.ref_id?.slice(-8) }}</span></div>
              <div class="rr-cost">¥{{ item.amount.toFixed(2) }}</div>
            </div>
          </div>
          <div class="module-body" v-else-if="elecBill && elecBill.repair_cost == 0">
            <div class="no-data">本月无维修费用</div>
          </div>
          <div class="module-empty" v-else><p>暂无待缴维修费</p></div>
        </section>
      </div>

      <!-- 右侧通知栏 -->
      <section class="notice-panel">
        <div class="notice-head">
          <div class="nh-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
            <span>缴费通知</span>
          </div>
          <span class="nh-count">{{ notices.length }}</span>
        </div>
        <div class="notice-body">
          <div v-if="notices.length === 0" class="no-notice">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#d0d5dd" stroke-width="1.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            <p>一切正常</p>
          </div>
          <div v-for="n in notices" :key="n.id" :class="['n-item', n.is_pinned ? 'urgent' : n.is_read ? 'read' : 'unread']" @click="openNoticeDetail(n)">
            <div class="n-dot"></div>
            <div class="n-content">
              <div class="n-title">{{ n.title }}</div>
              <div class="n-text">{{ n.content.length > 45 ? n.content.slice(0,45)+'...' : n.content }}</div>
              <div class="n-footer">
                <span>{{ n.bill_month }}</span>
                <span>{{ n.created_at?.slice(0,10) }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- 底部：缴费历史 -->
    <section class="history-module">
      <div class="module-header">
        <div class="mh-left">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          <div><h3>缴费历史</h3><p>查询历史记录</p></div>
        </div>
        <div class="history-filters">
          <select v-model="histFilter.type" class="hf-select"><option value="all">全部状态</option><option value="paid">已缴费</option><option value="unpaid">未缴费</option></select>
          <select v-model="histFilter.year" class="hf-select"><option value="all">全部年份</option><option v-for="y in availableYears" :key="y" :value="y">{{ y }}年</option></select>
        </div>
      </div>
      <div class="module-body">
        <table class="history-table" v-if="filteredHistory.length">
          <thead><tr><th>账单月份</th><th>用电量</th><th>电费</th><th>维修费</th><th>合计</th><th>缴费日期</th><th>状态</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="b in filteredHistory" :key="b.bill_id" :class="{ dim: b.status === 2, warn: b.warning_flag }">
              <td class="td-month">{{ b.bill_month }}</td>
              <td>{{ b.total_kwh }} kWh</td>
              <td>¥{{ b.electricity_cost }}</td>
              <td>{{ b.repair_cost > 0 ? '¥' + b.repair_cost : '-' }}</td>
              <td class="fw-600">¥{{ b.total_amount }}</td>
              <td>{{ b.paid_date || '-' }}</td>
              <td><span :class="['h-st', 'st-' + b.status]">{{ b.status_text }}</span></td>
              <td><button v-if="b.status !== 2" class="h-pay-btn" @click="openPayModal(b,'bill')">缴费</button><span v-else class="h-paid">已缴</span></td>
            </tr>
          </tbody>
        </table>
        <div class="empty-hint" v-else>暂无匹配记录</div>
      </div>
    </section>

    <!-- ========== 通知详情弹窗 ========== -->
    <Teleport to="body">
      <Transition name="pay-fade">
        <div class="pay-overlay" v-if="showNoticeDetail" @click.self="showNoticeDetail = false">
          <div class="notice-detail-dialog">
            <div class="ndd-header">
              <div class="ndd-h-left">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
                <span>缴费通知详情</span>
              </div>
              <button class="pay-close" @click="showNoticeDetail = false">&times;</button>
            </div>
            <div class="ndd-body" v-if="noticeDetail">
              <div class="ndd-bill-period">{{ noticeDetail.title }}</div>
              <div class="ndd-content-text">{{ noticeDetail.content }}</div>
              <div class="ndd-footer-meta">
                <span>账单周期：{{ noticeDetail.bill_month }}</span>
                <span>发送时间：{{ noticeDetail.created_at?.slice(0, 10) }}</span>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- ========== 支付弹窗 ========== -->
    <Teleport to="body">
      <Transition name="pay-fade">
        <div class="pay-overlay" v-if="showPayModal" @click.self="showPayModal = false">
          <div class="pay-dialog" v-if="showPayModal">
            <div class="pay-header">
              <h3>{{ payType === 'electricity' ? '电费缴费' : '账单缴费' }}</h3>
              <button class="pay-close" @click="showPayModal = false">&times;</button>
            </div>
            <div v-if="payStep === 1" class="pay-body">
              <div class="pay-bill-summary">
                <div class="pbs-row"><span>账单月份</span><span>{{ payTarget?.bill_month }}</span></div>
                <div class="pbs-row"><span>电费</span><span>¥{{ payTarget?.electricity_cost }}</span></div>
                <div class="pbs-row" v-if="payTarget?.repair_cost > 0"><span>维修费</span><span>¥{{ payTarget?.repair_cost }}</span></div>
                <div class="pbs-row total"><span>应缴合计</span><span>¥{{ payTarget?.total_amount }}</span></div>
              </div>
              <div class="pay-methods">
                <p class="pm-label">选择支付方式</p>
                <div class="pm-options">
                  <div :class="['pm-opt', { selected: payMethod === 'card' }]" @click="payMethod = 'card'">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="4" width="22" height="16" rx="2"/><line x1="5" y1="10" x2="19" y2="10"/></svg>
                    <span>银行卡</span>
                  </div>
                  <div :class="['pm-opt', { selected: payMethod === 'wechat' }]" @click="payMethod = 'wechat'">
                    <span class="pm-icon" style="background:#07c160">微</span>
                    <span>微信支付</span>
                  </div>
                </div>
              </div>
              <button class="pay-submit-btn" @click="payStep = 2">下一步</button>
            </div>
            <div v-if="payStep === 2" class="pay-body">
              <div class="pay-amount-display">¥{{ payTarget?.total_amount }}</div>
              <p class="pay-pass-label">请输入支付密码</p>
              <div class="pay-pass-inputs">
                <input v-for="i in 6" :key="i" :ref="el => payInputs[i-1]=el" v-model="payDigits[i-1]" maxlength="1" type="password" class="pay-digit" @input="onDigitInput($event, i)" @keydown.backspace="onDigitBack($event, i)"/>
              </div>
              <p class="pay-hint">模拟支付，输入任意6位数字</p>
            </div>
            <div v-if="payStep === 3" class="pay-body pay-processing">
              <div class="spinner"></div><p>正在处理...</p>
            </div>
            <div v-if="payStep === 4" class="pay-body pay-done">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#67c23a" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              <h4>缴费成功</h4><p>{{ payTarget?.bill_month }} 已支付 ¥{{ payTarget?.total_amount }}</p>
              <button class="pay-done-btn" @click="finishPay">完成</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getCurrentBill, getMyBills, payBill, getNotices } from '../api'

const elecBill = ref(null)
const bills = ref([])
const showPayModal = ref(false)
const payStep = ref(1)
const payMethod = ref('card')
const payTarget = ref(null)
const payType = ref('electricity')
const payDigits = ref(['','','','','',''])
const payInputs = ref([])
const histFilter = reactive({ type: 'all', year: 'all' })

const latestBillMonth = computed(() => bills.value.length > 0 ? bills.value[0].bill_month : '--')
const unpaidBills = computed(() => bills.value.filter(b => b.status !== 2))
const elecBillStatus = computed(() => {
  if (!elecBill.value) return 'none'
  if (elecBill.value.status === 2) return 'done'
  if (elecBill.value.warning_flag) return 'warn'
  return 'pending'
})
const elecBillStatusText = computed(() => {
  if (!elecBill.value) return '无账单'; if (elecBill.value.status === 2) return '已缴费'
  if (elecBill.value.warning_flag) return '欠费提醒'; return '待缴费'
})
const repairBillStatus = computed(() => {
  if (!elecBill.value || elecBill.value.repair_cost == 0) return 'none'
  if (elecBill.value.status === 2) return 'done'; return 'pending'
})
const repairBillStatusText = computed(() => {
  if (!elecBill.value || elecBill.value.repair_cost == 0) return '无费用'
  if (elecBill.value.status === 2) return '已缴'; return '待缴费'
})
const repairItems = computed(() => {
  if (!elecBill.value || !elecBill.value.items) return []
  return elecBill.value.items.filter(i => i.item_type === 2)
})
const availableYears = computed(() => {
  const s = new Set(); bills.value.forEach(b => s.add(b.bill_month.split('-')[0])); return [...s].sort().reverse()
})
const filteredHistory = computed(() => {
  let result = [...bills.value]
  if (histFilter.type === 'paid') result = result.filter(b => b.status === 2)
  if (histFilter.type === 'unpaid') result = result.filter(b => b.status !== 2)
  if (histFilter.year !== 'all') result = result.filter(b => b.bill_month.startsWith(histFilter.year))
  return result
})
const notices = ref([])

const showNoticeDetail = ref(false)
const noticeDetail = ref(null)

function openNoticeDetail(n) { noticeDetail.value = n; showNoticeDetail.value = true }
function payFromNotice() {
  const b = bills.value.find(x => x.bill_id === noticeDetail.value.bill_id)
  if (b) { showNoticeDetail.value = false; openPayModal(b, 'electricity') }
}

onMounted(async () => {
  try {
    const [cRes, bRes, nRes] = await Promise.all([getCurrentBill(), getMyBills(), getNotices()])
    elecBill.value = cRes.data.bill
    bills.value = bRes.data.bills || []
    notices.value = nRes.data.notices || []
    if (bills.value.length > 0) histFilter.year = bills.value[0].bill_month.split('-')[0]
  } catch (e) { console.error(e) }
})

function openPayModal(bill, type) { payTarget.value = bill; payType.value = type; payStep.value = 1; payDigits.value = ['','','','','','']; payMethod.value = 'card'; showPayModal.value = true }
function openPayModalById(billId) { const b = bills.value.find(x => x.bill_id === billId); if (b) openPayModal(b, 'electricity') }
function onDigitInput(e, idx) { if (e.target.value && idx < 6 && payInputs.value[idx]) payInputs.value[idx].focus(); if (idx === 6 && payDigits.value.every(d => d)) { setTimeout(() => payStep.value = 3, 300); setTimeout(() => payStep.value = 4, 1500) } }
function onDigitBack(_, idx) { if (!payDigits.value[idx-1] && idx > 1 && payInputs.value[idx-2]) payInputs.value[idx-2].focus() }
async function finishPay() { if (payTarget.value) { try { await payBill(payTarget.value.bill_id) } catch (e) {} } showPayModal.value = false; const [cRes, bRes, nRes] = await Promise.all([getCurrentBill(), getMyBills(), getNotices()]); elecBill.value = cRes.data.bill; bills.value = bRes.data.bills || []; notices.value = nRes.data.notices || [] }
</script>

<style scoped>
.billing-page { padding: 24px; width: 100%; box-sizing: border-box; }
.page-top { margin-bottom: 18px; }
.page-top h2 { font-size: 20px; font-weight: 500; color: #2c3e50; margin: 0; }
.sub { font-size: 12px; color: #999; margin: 2px 0 0; }

/* 上半部分：左右布局 */
.top-layout { display: flex; gap: 14px; margin-bottom: 14px; }
.left-pays { flex: 1; display: flex; flex-direction: column; gap: 14px; min-width: 0; }

/* 模块通用 */
.pay-module { background: #fff; border: 1px solid #edf0f4; border-radius: 10px; overflow: hidden; }
.module-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 18px; border-bottom: 1px solid #f0f2f5; }
.mh-left { display: flex; align-items: center; gap: 10px; }
.mh-icon { width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.mh-icon.e { background: #eef2ff; color: #5470c6; }
.mh-icon.r { background: #fff2e8; color: #e6a23c; }
.mh-left h3 { font-size: 13px; font-weight: 600; color: #2c3e50; margin: 0; }
.mh-left p { font-size: 11px; color: #999; margin: 1px 0 0; }
.mh-badge { font-size: 10px; padding: 3px 10px; border-radius: 20px; font-weight: 500; }
.mh-badge.done { background: #e8f5e9; color: #67c23a; }
.mh-badge.pending { background: #fef3e2; color: #e6a23c; }
.mh-badge.warn { background: #fde8e8; color: #e74c3c; }
.mh-badge.none { background: #f0f2f5; color: #999; }
.module-body { padding: 16px 18px; }
.module-empty { padding: 24px 18px; text-align: center; color: #ccc; font-size: 13px; }
.module-empty p { margin: 0 0 4px; }

/* 缴费卡片 */
.pay-card { display: flex; align-items: center; justify-content: space-between; }
.pay-amount { font-size: 28px; font-weight: 700; color: #2c3e50; }
.pay-meta { font-size: 12px; color: #999; margin-top: 2px; }
.pay-btn { padding: 10px 24px; background: #2c3e50; color: #fff; border: none; border-radius: 8px; font-size: 13px; cursor: pointer; font-family: inherit; }
.pay-btn:hover { background: #5470c6; }
.done-stamp { padding: 10px 20px; background: #e8f5e9; color: #67c23a; border-radius: 8px; font-size: 13px; font-weight: 500; }
.no-data { color: #aaa; font-size: 13px; text-align: center; padding: 8px 0; }
.bill-row-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: #f8f9fb; border-radius: 8px; margin-bottom: 8px; }
.bill-row-item:last-child { margin-bottom: 0; }
.bri-info { display: flex; flex-direction: column; gap: 2px; }
.bri-month { font-size: 13px; font-weight: 600; color: #333; }
.bri-meta { font-size: 11px; color: #999; }
.bri-warn { font-size: 10px; color: #e74c3c; background: #fde8e8; padding: 1px 6px; border-radius: 3px; align-self: flex-start; margin-top: 2px; }

/* 维修 */
.repair-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: #f8f9fb; border-radius: 8px; margin-bottom: 6px; }
.repair-row:last-child { margin-bottom: 0; }
.rr-info { display: flex; flex-direction: column; gap: 2px; }
.rr-name { font-size: 13px; color: #333; }
.rr-ref { font-size: 11px; color: #aaa; }
.rr-cost { font-size: 15px; font-weight: 600; color: #e6a23c; }

/* ======== 右侧通知面板 ======== */
.notice-panel {
  width: 320px; flex-shrink: 0; background: #fff; border: 1px solid #edf0f4; border-radius: 10px;
  display: flex; flex-direction: column; overflow: hidden;
}
.notice-head {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 16px; border-bottom: 1px solid #f0f2f5;
}
.nh-title { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; color: #555; }
.nh-count { font-size: 11px; color: #999; background: #f0f2f5; padding: 2px 8px; border-radius: 10px; }
.notice-body { flex: 1; padding: 8px; overflow-y: auto; max-height: 400px; }
.no-notice { display: flex; flex-direction: column; align-items: center; padding: 36px 0; gap: 10px; }
.no-notice p { font-size: 13px; color: #bbb; }

.n-item { padding: 10px 10px 10px 14px; border-radius: 6px; margin-bottom: 4px; border-left: 3px solid transparent; display: flex; gap: 10px; cursor: default; transition: background 0.15s; }
.n-item:hover { background: #fafbfc; }
.n-item.unread { border-left-color: #5470c6; background: #f8f9fd; }
.n-item.read { border-left-color: #d0d5dd; opacity: 0.7; }
.n-item.urgent { border-left-color: #e74c3c; background: #fff5f5; }
.n-dot { width: 6px; height: 6px; border-radius: 50%; background: #5470c6; margin-top: 6px; flex-shrink: 0; }
.n-item.read .n-dot { background: #d0d5dd; }
.n-item.urgent .n-dot { background: #e74c3c; }
.n-content { flex: 1; min-width: 0; }
.n-title { font-size: 12px; font-weight: 600; color: #333; margin-bottom: 2px; }
.n-text { font-size: 11px; color: #888; line-height: 1.5; word-break: break-all; }
.n-footer { display: flex; gap: 10px; margin-top: 4px; font-size: 10px; color: #ccc; }

/* ======== 历史 ======== */
.history-module { background: #fff; border: 1px solid #edf0f4; border-radius: 10px; overflow: hidden; }
.history-filters { display: flex; gap: 6px; }
.hf-select { font-size: 11px; padding: 4px 8px; border: 1px solid #e0e0e0; border-radius: 5px; background: #fff; color: #555; font-family: inherit; outline: none; cursor: pointer; }
.history-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.history-table th { text-align: left; padding: 8px 0 10px; font-size: 10px; color: #aaa; font-weight: 500; border-bottom: 1px solid #f0f2f5; }
.history-table td { padding: 8px 0; border-bottom: 1px solid #f8f9fb; }
tr.dim { opacity: 0.6; }
tr.warn { background: #fffaf0; }
.fw-600 { font-weight: 600; }
.td-month { font-weight: 500; }
.h-st { font-size: 10px; padding: 2px 7px; border-radius: 4px; }
.st-1 { background: #fef3e2; color: #e6a23c; }
.st-2 { background: #e8f5e9; color: #67c23a; }
.st-3 { background: #fde8e8; color: #e74c3c; }
.empty-hint { text-align: center; padding: 28px; color: #ccc; font-size: 13px; }

/* ======== 通知详情弹窗 ======== */
.notice-detail-dialog { background: #fff; border-radius: 12px; width: 440px; max-width: 92vw; overflow: hidden; }
.ndd-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid #f0f2f5; }
.ndd-h-left { display: flex; align-items: center; gap: 8px; color: #555; font-size: 14px; font-weight: 500; }
.ndd-body { padding: 20px 24px; }
.ndd-bill-period { font-size: 13px; color: #999; margin-bottom: 14px; padding: 6px 12px; background: #f8f9fb; border-radius: 6px; display: inline-block; }
.ndd-content-text { font-size: 13px; color: #555; line-height: 1.8; padding: 14px 16px; background: #f8f9fb; border-radius: 8px; margin-bottom: 14px; }
.ndd-footer-meta { display: flex; gap: 20px; font-size: 11px; color: #bbb; margin-top: 12px; }

/* 通知可点击 */
.n-item { cursor: pointer; }

/* ======== 支付弹窗 ======== */
.pay-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.4); z-index: 2000; display: flex; align-items: center; justify-content: center; }
.pay-dialog { background: #fff; border-radius: 12px; width: 420px; max-width: 92vw; overflow: hidden; }
.pay-header { display: flex; justify-content: space-between; align-items: center; padding: 18px 24px; border-bottom: 1px solid #f0f2f5; }
.pay-header h3 { font-size: 16px; font-weight: 500; color: #2c3e50; margin: 0; }
.pay-close { background: none; border: none; font-size: 22px; color: #ccc; cursor: pointer; }
.pay-body { padding: 24px; }
.pay-bill-summary { background: #f8f9fb; border-radius: 8px; padding: 16px; margin-bottom: 20px; }
.pbs-row { display: flex; justify-content: space-between; padding: 6px 0; font-size: 13px; color: #666; }
.pbs-row.total { border-top: 1px solid #e8eaed; padding-top: 10px; margin-top: 4px; font-size: 15px; font-weight: 600; color: #2c3e50; }
.pm-label { font-size: 11px; color: #999; margin: 0 0 8px; }
.pm-options { display: flex; gap: 10px; }
.pm-opt { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 14px 8px; border: 1px solid #e0e0e0; border-radius: 8px; cursor: pointer; font-size: 12px; color: #888; transition: all 0.15s; }
.pm-opt:hover { border-color: #5470c6; }
.pm-opt.selected { border-color: #2c3e50; color: #2c3e50; background: #f8f9fb; }
.pm-icon { width: 20px; height: 20px; border-radius: 4px; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600; }
.pay-submit-btn { width: 100%; padding: 12px 0; background: #2c3e50; color: #fff; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; font-family: inherit; }
.pay-amount-display { text-align: center; font-size: 36px; font-weight: 600; color: #2c3e50; margin-bottom: 8px; }
.pay-pass-label { text-align: center; font-size: 13px; color: #888; margin: 0 0 16px; }
.pay-pass-inputs { display: flex; gap: 10px; justify-content: center; margin-bottom: 16px; }
.pay-digit { width: 44px; height: 52px; border: 1px solid #e0e0e0; border-radius: 8px; text-align: center; font-size: 22px; outline: none; }
.pay-hint { text-align: center; font-size: 11px; color: #ccc; }
.pay-processing { text-align: center; padding: 48px 24px; }
.spinner { width: 36px; height: 36px; border: 3px solid #edf0f4; border-top-color: #2c3e50; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px; }
@keyframes spin { to { transform: rotate(360deg); } }
.pay-processing p { font-size: 14px; color: #888; }
.pay-done { text-align: center; padding: 36px 24px; }
.pay-done h4 { font-size: 18px; color: #2c3e50; margin: 12px 0 6px; }
.pay-done p { font-size: 13px; color: #888; margin: 0 0 20px; }
.pay-done-btn { padding: 10px 40px; background: #2c3e50; color: #fff; border: none; border-radius: 6px; font-size: 13px; cursor: pointer; font-family: inherit; }
.pay-fade-enter-active, .pay-fade-leave-active { transition: opacity 0.25s; }
.pay-fade-enter-from, .pay-fade-leave-to { opacity: 0; }
</style>
