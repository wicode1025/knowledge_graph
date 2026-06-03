<template>
  <div class="home">
    <!-- 顶部简介 -->
    <div class="hero">
      <div class="hero-left">
        <div class="avatar-circle">{{ hh.real_name?.charAt(0) || '?' }}</div>
        <div class="hero-info">
          <h2>{{ hh.real_name || '未设置姓名' }}</h2>
          <div class="hero-tags">
            <span v-if="hh.gender" class="htag">{{ optLabel('gender', hh.gender) }}</span>
            <span v-if="hh.birth_year" class="htag">{{ hh.birth_year }} 年</span>
            <span v-if="hh.occupation" class="htag">{{ optLabel('occupation', hh.occupation) }}</span>
            <span class="htag">{{ optLabel('education', hh.education_level) }}</span>
          </div>
        </div>
      </div>
      <div class="hero-right">
        <span class="hero-ym">{{ sysMonth }}</span>
        <span class="hero-ym-label">当前月份</span>
      </div>
    </div>

    <!-- 统计卡片行 -->
    <div class="stat-row">
      <div class="stat-item">
        <div class="stat-icon s1">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-val">{{ summary.total_kwh }} <small>kWh</small></div>
          <div class="stat-lbl">上月用电</div>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon s2">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="6" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-val">¥{{ (summary.total_kwh * 0.55).toFixed(0) }}</div>
          <div class="stat-lbl">预估电费</div>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon s3">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-val">{{ summary.device_count }}</div>
          <div class="stat-lbl">用电设备</div>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon s4">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
        </div>
        <div class="stat-body">
          <div class="stat-val">{{ billsCount }}</div>
          <div class="stat-lbl">累计账单</div>
        </div>
      </div>
    </div>

    <!-- 双栏布局 -->
    <div class="main-layout">
      <div class="content-left">
        <!-- 基本信息 -->
        <section class="panel">
      <div class="panel-head">
        <h3>基本信息</h3>
        <button class="action-btn" @click="toggleEdit('basic')">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          {{ editing === 'basic' ? '取消' : '编辑' }}
        </button>
      </div>
      <div class="panel-body" v-if="editing !== 'basic'">
        <div class="info-grid cols-4">
          <div class="info-cell"><span class="cell-label">姓名</span><span class="cell-value">{{ hh.real_name || '-' }}</span></div>
          <div class="info-cell"><span class="cell-label">性别</span><span class="cell-value">{{ optLabel('gender', hh.gender) }}</span></div>
          <div class="info-cell"><span class="cell-label">出生年月</span><span class="cell-value">{{ hh.birth_year || '--' }}年{{ hh.birth_month || '--' }}月</span></div>
          <div class="info-cell"><span class="cell-label">民族</span><span class="cell-value">{{ optLabel('ethnicity', hh.ethnicity) }}</span></div>
          <div class="info-cell"><span class="cell-label">学历</span><span class="cell-value">{{ optLabel('education', hh.education_level) }}</span></div>
          <div class="info-cell"><span class="cell-label">婚姻状况</span><span class="cell-value">{{ optLabel('marital', hh.marital_status) }}</span></div>
          <div class="info-cell"><span class="cell-label">政治面貌</span><span class="cell-value">{{ optLabel('political', hh.political_status) }}</span></div>
          <div class="info-cell"><span class="cell-label">宗教信仰</span><span class="cell-value">{{ optLabel('religion', hh.religion) }}</span></div>
          <div class="info-cell"><span class="cell-label">职业</span><span class="cell-value">{{ optLabel('occupation', hh.occupation) }}</span></div>
          <div class="info-cell"><span class="cell-label">工作单位</span><span class="cell-value">{{ hh.work_unit || '-' }}</span></div>
          <div class="info-cell"><span class="cell-label">联系电话</span><span class="cell-value">{{ hh.phone || '-' }}</span></div>
          <div class="info-cell"><span class="cell-label">城乡分类</span><span class="cell-value">{{ optLabel('urban', hh.is_urban) }}</span></div>
          <div class="info-cell"><span class="cell-label">日常作息</span><span class="cell-value">{{ optLabel('schedule', hh.daily_schedule) }}</span></div>
          <div class="info-cell"><span class="cell-label">健康自评</span><span class="cell-value">{{ optLabel('health', hh.self_health) }}</span></div>
          <div class="info-cell full-width"><span class="cell-label">详细地址</span><span class="cell-value">{{ hh.address_detail || '-' }}</span></div>
        </div>
      </div>
      <div class="panel-body edit-body" v-else>
        <div class="info-grid cols-4">
          <label class="f-field"><span>姓名</span><input v-model="edits.basic.real_name" class="f-input" /></label>
          <label class="f-field"><span>性别</span><select v-model="edits.basic.gender" class="f-input"><option value="">请选择</option><option v-for="o in options.gender" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></label>
          <label class="f-field"><span>出生年份</span><input v-model="edits.basic.birth_year" type="number" class="f-input" /></label>
          <label class="f-field"><span>出生月份</span><input v-model="edits.basic.birth_month" type="number" min="1" max="12" class="f-input" /></label>
          <label class="f-field"><span>民族</span><select v-model="edits.basic.ethnicity" class="f-input"><option value="">请选择</option><option v-for="o in options.ethnicity" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></label>
          <label class="f-field"><span>学历</span><select v-model="edits.basic.education_level" class="f-input"><option value="">请选择</option><option v-for="o in options.education" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></label>
          <label class="f-field"><span>婚姻状况</span><select v-model="edits.basic.marital_status" class="f-input"><option value="">请选择</option><option v-for="o in options.marital" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></label>
          <label class="f-field"><span>政治面貌</span><select v-model="edits.basic.political_status" class="f-input"><option value="">请选择</option><option v-for="o in options.political" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></label>
          <label class="f-field"><span>宗教信仰</span><select v-model="edits.basic.religion" class="f-input"><option value="">请选择</option><option v-for="o in options.religion" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></label>
          <label class="f-field"><span>职业</span><select v-model="edits.basic.occupation" class="f-input"><option value="">请选择</option><option v-for="o in options.occupation" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></label>
          <label class="f-field"><span>工作单位</span><input v-model="edits.basic.work_unit" class="f-input" /></label>
          <label class="f-field"><span>联系电话</span><input v-model="edits.basic.phone" class="f-input" /></label>
          <label class="f-field"><span>城乡分类</span><select v-model="edits.basic.is_urban" class="f-input"><option value="">请选择</option><option v-for="o in options.urban" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></label>
          <label class="f-field"><span>日常作息</span><select v-model="edits.basic.daily_schedule" class="f-input"><option value="">请选择</option><option v-for="o in options.schedule" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></label>
          <label class="f-field"><span>健康自评</span><select v-model="edits.basic.self_health" class="f-input"><option value="">请选择</option><option v-for="o in options.health" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></label>
          <label class="f-field full-width"><span>详细地址</span><input v-model="edits.basic.address_detail" class="f-input" /></label>
        </div>
        <div class="save-bar"><button class="save-btn" @click="saveBasic">保存修改</button></div>
      </div>
    </section>

    <!-- 住房 + 家庭成员 双栏 -->
    <div class="dual-panels">
      <section class="panel">
        <div class="panel-head">
          <h3>住房信息</h3>
          <button class="action-btn" @click="toggleEdit('housing')">{{ editing === 'housing' ? '取消' : '编辑' }}</button>
        </div>
        <div class="panel-body" v-if="editing !== 'housing'">
          <div class="info-grid cols-2">
            <div class="info-cell"><span class="cell-label">住房类型</span><span class="cell-value">{{ optLabel('housing_type', housing?.housing_type) }}</span></div>
            <div class="info-cell"><span class="cell-label">建筑面积</span><span class="cell-value">{{ housing?.housing_area ? housing.housing_area + ' m²' : '-' }}</span></div>
            <div class="info-cell"><span class="cell-label">卧室 / 客厅</span><span class="cell-value">{{ housing?.bedroom_count || 0 }} 室 {{ housing?.living_room_count || 0 }} 厅</span></div>
            <div class="info-cell"><span class="cell-label">所在楼层</span><span class="cell-value">{{ housing?.floor_level || '-' }} / {{ housing?.total_floors || '-' }} 层</span></div>
            <div class="info-cell"><span class="cell-label">电梯</span><span class="cell-value">{{ housing?.has_elevator ? '有' : '无' }}</span></div>
            <div class="info-cell"><span class="cell-label">供暖方式</span><span class="cell-value">{{ optLabel('heating', housing?.heating_type) }}</span></div>
            <div class="info-cell"><span class="cell-label">房屋朝向</span><span class="cell-value">{{ optLabel('orientation', housing?.orientation) }}</span></div>
            <div class="info-cell"><span class="cell-label">房龄</span><span class="cell-value">{{ housing?.building_age ? housing.building_age + ' 年' : '-' }}</span></div>
          </div>
        </div>
        <div class="panel-body edit-body" v-else>
          <div class="info-grid cols-2">
            <label class="f-field"><span>住房类型</span><select v-model="edits.housing.housing_type" class="f-input"><option value="">请选择</option><option v-for="o in options.housing_type" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></label>
            <label class="f-field"><span>建筑面积 (m²)</span><input v-model="edits.housing.housing_area" type="number" class="f-input" /></label>
            <label class="f-field"><span>卧室数</span><input v-model="edits.housing.bedroom_count" type="number" class="f-input" /></label>
            <label class="f-field"><span>客厅数</span><input v-model="edits.housing.living_room_count" type="number" class="f-input" /></label>
            <label class="f-field"><span>所在楼层</span><input v-model="edits.housing.floor_level" type="number" class="f-input" /></label>
            <label class="f-field"><span>总楼层</span><input v-model="edits.housing.total_floors" type="number" class="f-input" /></label>
            <label class="f-field"><span>电梯</span><select v-model="edits.housing.has_elevator" class="f-input"><option value="">请选择</option><option value="1">有</option><option value="0">无</option></select></label>
            <label class="f-field"><span>供暖方式</span><select v-model="edits.housing.heating_type" class="f-input"><option value="">请选择</option><option v-for="o in options.heating" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></label>
            <label class="f-field"><span>房屋朝向</span><select v-model="edits.housing.orientation" class="f-input"><option value="">请选择</option><option v-for="o in options.orientation" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></label>
            <label class="f-field"><span>房龄 (年)</span><input v-model="edits.housing.building_age" type="number" class="f-input" /></label>
          </div>
          <div class="save-bar"><button class="save-btn" @click="saveHousing">保存修改</button></div>
        </div>
      </section>

      <section class="panel">
        <div class="panel-head">
          <h3>家庭成员</h3>
          <button class="action-btn" @click="toggleEdit('family')">{{ editing === 'family' ? '完成' : '管理' }}</button>
        </div>
        <div class="panel-body">
          <div class="member-list">
            <div v-for="m in members" :key="m.member_seq" class="member-row">
              <div class="mem-avatar">{{ m.name?.charAt(0) }}</div>
              <div class="mem-info">
                <span class="mem-name">{{ m.name }}</span>
                <span class="mem-tag">{{ relText(m.relation) }}</span>
              </div>
              <span :class="['mem-status', { away: !m.is_cohabit }]">{{ m.is_cohabit ? '同住' : '分居' }}</span>
              <button v-if="editing === 'family'" class="mem-del" @click="deleteMember(m.id)">&times;</button>
            </div>
            <div v-if="members.length === 0" class="empty-text">暂无家庭成员信息</div>
          </div>
          <div v-if="editing === 'family'" class="add-mem">
            <input v-model="nf.name" placeholder="姓名" class="f-input f-sm" />
            <select v-model="nf.relation" class="f-input f-sm"><option :value="2">配偶</option><option :value="3">子女</option><option :value="4">父母</option><option :value="5">其他</option></select>
            <input v-model="nf.birth_year" placeholder="出生年份" type="number" class="f-input f-sm" />
            <button class="save-btn small" @click="addMember">添加</button>
          </div>
        </div>
      </section>
    </div>

    <!-- 收入信息 -->
    <section class="panel">
      <div class="panel-head">
        <h3>收入信息</h3>
        <button class="action-btn" @click="toggleEdit('income')">{{ editing === 'income' ? '取消' : '编辑' }}</button>
      </div>
      <div class="panel-body" v-if="editing !== 'income'">
        <div class="info-grid cols-4">
          <div class="info-cell"><span class="cell-label">个人年收入</span><span class="cell-value num">¥{{ income?.personal_income?.toLocaleString() || '-' }}</span></div>
          <div class="info-cell"><span class="cell-label">家庭年收入</span><span class="cell-value num">¥{{ income?.household_income?.toLocaleString() || '-' }}</span></div>
          <div class="info-cell"><span class="cell-label">收入来源</span><span class="cell-value">{{ optLabel('income_source', income?.income_source) }}</span></div>
          <div class="info-cell"><span class="cell-label">经济自评</span><span class="cell-value stars">{{ '★'.repeat(income?.self_evaluated_wealth || 0) }}{{ '☆'.repeat(5 - (income?.self_evaluated_wealth || 0)) }}</span></div>
        </div>
      </div>
      <div class="panel-body edit-body" v-else>
        <div class="info-grid cols-2">
          <label class="f-field"><span>个人年收入 (¥)</span><input v-model="edits.income.personal_income" type="number" class="f-input" /></label>
          <label class="f-field"><span>家庭年收入 (¥)</span><input v-model="edits.income.household_income" type="number" class="f-input" /></label>
          <label class="f-field"><span>收入来源</span><select v-model="edits.income.income_source" class="f-input"><option value="">请选择</option><option v-for="o in options.income_source" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></label>
          <label class="f-field"><span>经济自评 (1-5)</span><input v-model="edits.income.self_evaluated_wealth" type="number" min="1" max="5" class="f-input" /></label>
        </div>
        <div class="save-bar"><button class="save-btn" @click="saveIncome">保存修改</button></div>
      </div>
    </section>

      </div>

      <!-- 右侧面板 -->
      <aside class="content-right">
        <!-- 公告 -->
        <section class="announce-panel">
          <div class="ann-head">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
            <span>系统公告</span>
          </div>
          <div class="ann-body">
            <div v-if="announcements.length === 0" class="ann-empty">暂无公告</div>
            <div v-for="a in announcements" :key="a.id" :class="['ann-item', { pinned: a.is_pinned }]">
              <div class="ann-dot"></div>
              <div class="ann-info">
                <div class="ann-title">{{ a.title }}</div>
                <div class="ann-text">{{ a.content }}</div>
                <div class="ann-date">{{ a.created_at?.slice(0, 10) }}</div>
              </div>
            </div>
          </div>
        </section>

        <!-- 留言板 -->
        <section class="msg-panel">
          <div class="ann-head">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            <span>留言板</span>
          </div>
          <div class="msg-body">
            <div v-if="messages.length === 0 && !showMsgForm" class="ann-empty">暂无留言</div>
            <div v-for="m in messages" :key="m.id" class="msg-item">
              <div class="msg-bubble">
                <div class="msg-text">{{ m.content }}</div>
                <div class="msg-meta">
                  <span>{{ m.created_at?.slice(0, 10) }}</span>
                  <span v-if="m.reply" class="msg-replied">已回复</span>
                  <span v-else class="msg-withdraw" @click="withdrawMsg(m.id)">撤回</span>
                </div>
              </div>
              <div class="msg-reply-bubble" v-if="m.reply">
                <span class="msg-reply-label">管理员回复</span>
                <div class="msg-reply-text">{{ m.reply }}</div>
              </div>
            </div>
          </div>
          <div class="msg-input-area">
            <textarea v-if="showMsgForm" v-model="msgContent" placeholder="输入留言内容..." class="msg-textarea" rows="2" ref="msgInput"></textarea>
            <div class="msg-actions">
              <button v-if="!showMsgForm" class="msg-btn" @click="showMsgForm = true">写留言</button>
              <template v-else>
                <button class="msg-btn primary" @click="submitMsg" :disabled="!msgContent.trim()">发送</button>
                <button class="msg-btn" @click="showMsgForm = false">取消</button>
              </template>
            </div>
          </div>
        </section>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import {
  getMyHousehold, updateMyHousehold, updateHousingInfo, updateIncomeInfo,
  getFamilyMembers, addFamilyMember, deleteFamilyMember,
  getConsumptionSummary, getSystemMonth, getOptions, getAnnouncements,
  getMessages, sendMessage, withdrawMessage,
} from '../api'

const hh = reactive({})
const housing = ref({})
const income = ref({})
const members = ref([])
const summary = reactive({ total_kwh: 0, device_count: 0 })
const announcements = ref([])
const messages = ref([])
const showMsgForm = ref(false)
const msgContent = ref('')
const sysMonth = ref('')
const billsCount = ref(0)
const options = reactive({})
const editing = ref(null)
const edits = reactive({ basic: {}, housing: {}, income: {} })
const nf = reactive({ name: '', relation: 2, birth_year: null })

const relText = (r) => ({ 1: '本人', 2: '配偶', 3: '子女', 4: '父母', 5: '岳父母/公婆', 6: '兄弟姐妹', 7: '其他' }[r] || '')

function optLabel(cat, val) {
  if (!val && val !== 0) return '-'
  const opts = options[cat]
  if (!opts) return String(val)
  const found = opts.find(o => String(o.item_key) === String(val))
  return found ? found.item_value : String(val)
}

onMounted(async () => {
  try {
    const [hRes, cRes, sRes, oRes, aRes, mRes] = await Promise.all([
      getMyHousehold(), getConsumptionSummary(), getSystemMonth(), getOptions(), getAnnouncements(), getMessages()
    ])
    Object.assign(hh, hRes.data.household)
    housing.value = hRes.data.housing || {}
    income.value = hRes.data.income || {}
    members.value = hRes.data.members || []
    Object.assign(summary, cRes.data)
    sysMonth.value = sRes.data.year_month
    billsCount.value = sRes.data.total_months_elapsed || 0
    Object.assign(options, oRes.data.options || {})
    announcements.value = aRes.data.announcements || []
    messages.value = mRes.data.messages || []
  } catch (e) { console.error(e) }
})

function toggleEdit(target) {
  if (editing.value === target) {
    editing.value = null
  } else {
    if (target === 'basic') Object.assign(edits.basic, JSON.parse(JSON.stringify(hh)))
    else if (target === 'housing') Object.assign(edits.housing, JSON.parse(JSON.stringify(housing.value || {})))
    else if (target === 'income') Object.assign(edits.income, JSON.parse(JSON.stringify(income.value || {})))
    editing.value = target
  }
}

async function saveBasic() { await updateMyHousehold(edits.basic); Object.assign(hh, edits.basic); editing.value = null }
async function saveHousing() { await updateHousingInfo(edits.housing); Object.assign(housing.value, edits.housing); editing.value = null }
async function saveIncome() { await updateIncomeInfo(edits.income); Object.assign(income.value, edits.income); editing.value = null }
async function addMember() { if (!nf.name) return; await addFamilyMember(nf); const r = await getFamilyMembers(); members.value = r.data.members; Object.assign(nf, { name: '', relation: 2, birth_year: null }) }
async function deleteMember(id) { await deleteFamilyMember(id); const r = await getFamilyMembers(); members.value = r.data.members }

async function submitMsg() { if (!msgContent.value.trim()) return; await sendMessage(msgContent.value); msgContent.value = ''; showMsgForm.value = false; const r = await getMessages(); messages.value = r.data.messages || [] }
async function withdrawMsg(id) { if(!confirm('撤回该留言？'))return; try{await withdrawMessage(id);const r=await getMessages();messages.value=r.data.messages||[]}catch(e){alert(e.response?.data?.message||'撤回失败')} }
</script>

<style scoped>
.home { padding: 24px; width: 100%; box-sizing: border-box; }

/* --- 顶部简介 --- */
.hero {
  display: flex; align-items: center; justify-content: space-between;
  background: #fff; border: 1px solid #edf0f4; border-radius: 10px;
  padding: 20px 24px; margin-bottom: 14px; width: 100%; box-sizing: border-box;
}
.hero-left { display: flex; align-items: center; gap: 16px; }
.avatar-circle {
  width: 48px; height: 48px; border-radius: 50%;
  background: #f0f2f5; color: #999;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; font-weight: 500; flex-shrink: 0;
}
.hero-info h2 { font-size: 18px; font-weight: 500; color: #2c3e50; margin: 0 0 6px; }
.hero-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.htag { font-size: 11px; padding: 2px 8px; background: #f0f2f5; color: #888; border-radius: 4px; }
.hero-right { text-align: right; flex-shrink: 0; }
.hero-ym { display: block; font-size: 22px; font-weight: 600; color: #2c3e50; }
.hero-ym-label { font-size: 10px; color: #aaa; }

/* --- 双栏布局 --- */
.main-layout { display: flex; gap: 14px; }
.content-left { flex: 1; min-width: 0; }
.content-right { width: 280px; flex-shrink: 0; }

/* --- 右侧公告 --- */
.announce-panel { background: #fff; border: 1px solid #edf0f4; border-radius: 10px; overflow: hidden; position: sticky; top: 12px; }
.ann-head { display: flex; align-items: center; gap: 6px; padding: 12px 16px; font-size: 12px; font-weight: 600; color: #888; border-bottom: 1px solid #f0f2f5; }
.ann-body { padding: 8px 10px; max-height: 500px; overflow-y: auto; }
.ann-empty { text-align: center; padding: 24px 0; color: #ccc; font-size: 12px; }
.ann-item { display: flex; gap: 8px; padding: 10px 8px; border-radius: 6px; margin-bottom: 2px; }
.ann-item.pinned { background: #fef9f0; }
.ann-dot { width: 6px; height: 6px; border-radius: 50%; background: #5470c6; margin-top: 6px; flex-shrink: 0; }
.ann-item.pinned .ann-dot { background: #e6a23c; }
.ann-info { flex: 1; min-width: 0; }
.ann-title { font-size: 12px; font-weight: 600; color: #333; margin-bottom: 2px; }
.ann-text { font-size: 11px; color: #888; line-height: 1.5; }
.ann-date { font-size: 10px; color: #ccc; margin-top: 4px; }

/* --- 留言板 --- */
.msg-panel { background: #fff; border: 1px solid #edf0f4; border-radius: 10px; overflow: hidden; margin-top: 14px; }
.msg-body { padding: 8px 10px; max-height: 300px; overflow-y: auto; }
.msg-item { margin-bottom: 8px; }
.msg-bubble { background: #f0f2f5; border-radius: 8px; padding: 8px 12px; }
.msg-text { font-size: 12px; color: #333; line-height: 1.5; }
.msg-meta { display: flex; gap: 8px; margin-top: 4px; font-size: 10px; color: #bbb; }
.msg-replied { color: #67c23a; }
.msg-withdraw { color: #ccc; cursor: pointer; font-size: 10px; }
.msg-withdraw:hover { color: #e74c3c; }
.msg-reply-bubble { margin-top: 4px; margin-left: 12px; padding: 8px 12px; background: #eef2ff; border-radius: 8px; border-left: 3px solid #5470c6; }
.msg-reply-label { font-size: 10px; color: #5470c6; display: block; margin-bottom: 2px; }
.msg-reply-text { font-size: 12px; color: #555; }
.msg-input-area { padding: 8px 10px; border-top: 1px solid #f0f2f5; }
.msg-textarea { width: 100%; padding: 8px 10px; border: 1px solid #e0e0e0; border-radius: 6px; font-size: 12px; outline: none; resize: vertical; font-family: inherit; box-sizing: border-box; }
.msg-textarea:focus { border-color: #5470c6; }
.msg-actions { display: flex; gap: 6px; margin-top: 6px; }
.msg-btn { padding: 5px 14px; border: 1px solid #e0e0e0; border-radius: 6px; background: #fff; font-size: 11px; color: #666; cursor: pointer; font-family: inherit; transition: all 0.15s; }
.msg-btn:hover { border-color: #5470c6; color: #5470c6; }
.msg-btn.primary { background: #2c3e50; color: #fff; border-color: #2c3e50; }
.msg-btn.primary:hover { background: #5470c6; border-color: #5470c6; }
.msg-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* --- 统计行 --- */
.stat-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 18px; width: 100%; }
.stat-item {
  background: #fff; border: 1px solid #edf0f4; border-radius: 10px; padding: 16px 14px;
  display: flex; align-items: center; gap: 12px; transition: box-shadow 0.2s;
}
.stat-item:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.stat-icon {
  width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.s1 { background: #eef2ff; color: #5470c6; }
.s2 { background: #fef3e2; color: #e6a23c; }
.s3 { background: #e8f5e9; color: #67c23a; }
.s4 { background: #fce4ec; color: #e91e63; }
.stat-val { font-size: 17px; font-weight: 600; color: #2c3e50; white-space: nowrap; }
.stat-val small { font-size: 11px; font-weight: 400; color: #999; }
.stat-lbl { font-size: 11px; color: #999; }

/* --- 面板 --- */
.panel { background: #fff; border: 1px solid #edf0f4; border-radius: 10px; margin-bottom: 14px; overflow: hidden; width: 100%; box-sizing: border-box; }
.panel:hover { box-shadow: 0 1px 8px rgba(0,0,0,0.04); }
.panel-head {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 18px; border-bottom: 1px solid #f2f4f7;
}
.panel-head h3 { font-size: 13px; font-weight: 600; color: #2c3e50; margin: 0; }
.panel-body { padding: 16px 18px; }
.edit-body { background: #fbfcfd; }
.action-btn {
  display: flex; align-items: center; gap: 5px;
  font-size: 12px; color: #888; background: none; border: 1px solid #e0e0e0;
  border-radius: 6px; padding: 4px 10px; cursor: pointer; transition: all 0.15s; font-family: inherit;
}
.action-btn:hover { color: #5470c6; border-color: #5470c6; }

/* --- 信息网格 --- */
.info-grid { display: grid; gap: 0; }
.cols-4 { grid-template-columns: repeat(4, 1fr); }
.cols-2 { grid-template-columns: repeat(2, 1fr); }
.info-cell {
  padding: 10px 0; border-bottom: 1px solid #f8f9fb; display: flex; flex-direction: column; gap: 3px;
}
.info-cell.full-width { grid-column: span 2; }
.cell-label { font-size: 10px; color: #aaa; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 500; }
.cell-value { font-size: 13px; color: #333; }
.cell-value.num { font-family: 'SF Mono', 'Cascadia Code', monospace; color: #5470c6; font-weight: 500; }
.stars { color: #e6a23c; letter-spacing: 2px; font-size: 14px; }

/* --- 表单 --- */
.f-field { display: flex; flex-direction: column; gap: 3px; padding: 6px 0; }
.f-field.full-width { grid-column: span 2; }
.f-field span { font-size: 10px; color: #aaa; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 500; }
.f-input {
  width: 100%; padding: 7px 9px; border: 1px solid #e0e0e0; border-radius: 6px;
  font-size: 13px; color: #333; background: #fff; outline: none; font-family: inherit;
  transition: border-color 0.15s, box-shadow 0.15s; box-sizing: border-box;
}
.f-input:focus { border-color: #5470c6; box-shadow: 0 0 0 3px rgba(84,112,198,0.08); }
select.f-input { appearance: none; background: #fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12'%3E%3Cpath d='M3 5l3 3 3-3' fill='none' stroke='%23999' stroke-width='1.5'/%3E%3C/svg%3E") no-repeat right 10px center; padding-right: 30px; cursor: pointer; }
.save-bar { margin-top: 14px; text-align: right; }
.save-btn {
  padding: 8px 24px; background: #2c3e50; color: #fff; border: none; border-radius: 6px;
  font-size: 13px; cursor: pointer; transition: all 0.15s; font-family: inherit;
}
.save-btn:hover { background: #5470c6; }
.save-btn.small { padding: 5px 12px; font-size: 11px; }

/* --- 双栏 --- */
.dual-panels { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; width: 100%; }

/* --- 成员 --- */
.member-list { display: flex; flex-direction: column; gap: 1px; min-height: 50px; }
.member-row { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #f8f9fb; }
.mem-avatar {
  width: 30px; height: 30px; border-radius: 50%; background: #eef2ff; color: #5470c6;
  display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; flex-shrink: 0;
}
.mem-info { display: flex; flex-direction: column; gap: 1px; }
.mem-name { font-size: 13px; font-weight: 500; color: #333; }
.mem-tag { font-size: 11px; color: #999; }
.mem-status { font-size: 10px; color: #67c23a; margin-left: auto; padding: 2px 7px; background: #e8f5e9; border-radius: 4px; white-space: nowrap; }
.mem-status.away { color: #999; background: #f5f5f5; }
.mem-del { background: none; border: none; color: #ccc; font-size: 16px; cursor: pointer; padding: 0 2px; }
.mem-del:hover { color: #e74c3c; }
.empty-text { color: #ccc; font-size: 13px; padding: 18px 0; text-align: center; }
.add-mem { display: flex; gap: 6px; margin-top: 10px; align-items: center; }
.f-sm { flex: 1; min-width: 0; }
</style>
