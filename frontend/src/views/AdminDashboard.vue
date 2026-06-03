<template>
  <div class="admin-page">
    <div class="page-top">
      <h2>管理后台</h2>
      <div class="tab-bar">
        <router-link to="/admin" :class="['tab', { active: tab === 'dashboard' }]">系统概览</router-link>
        <router-link to="/admin/kg" :class="['tab', { active: tab === 'kg' }]">知识图谱</router-link>
        <router-link to="/admin/data" :class="['tab', { active: tab === 'data' }]">数据管理</router-link>
      </div>
    </div>

    <!-- ========== 系统概览 ========== -->
    <div v-if="tab === 'dashboard'">
      <div class="advance-section">
        <div class="advance-card">
          <div class="advance-info">
            <span class="current-month-label">当前系统月份</span>
            <span class="current-month-value">{{ sysMonth }}</span>
            <span class="elapsed-label">已运行 {{ stats.total_months_elapsed }} 个月</span>
          </div>
          <button class="advance-btn" @click="handleAdvance" :disabled="advancing">{{ advancing ? '推进中...' : '推进至下月' }}</button>
          <div class="advance-hint">自动计算用电量并生成账单通知</div>
        </div>
        <div class="advance-result" v-if="advanceResult">推进完成！{{ advanceResult.records_created }} 条记录，{{ advanceResult.bills_created }} 张账单</div>
        <div class="advance-error" v-if="advanceError">{{ advanceError }}</div>
      </div>
      <div class="stats-grid">
        <div class="st-card"><div class="st-val">{{ stats.total_users }}</div><div class="st-lbl">用户总数</div></div>
        <div class="st-card"><div class="st-val">{{ stats.active_devices }}/{{ stats.total_devices }}</div><div class="st-lbl">活跃/总设备</div></div>
        <div class="st-card"><div class="st-val">{{ stats.damaged_devices }}</div><div class="st-lbl">损坏设备</div></div>
        <div class="st-card"><div class="st-val">{{ stats.bills_collected }}</div><div class="st-lbl">账单收缴</div></div>
        <div class="st-card"><div class="st-val">{{ stats.pending_repairs }}</div><div class="st-lbl">待审核维修</div></div>
        <div class="st-card"><div class="st-val">{{ stats.unit_price?.toFixed(2) }}/度</div><div class="st-lbl">电价</div></div>
      </div>

      <!-- 公告 -->
      <section class="panel">
        <div class="panel-head"><h3>系统公告</h3><button class="btn-sm" @click="showAnnForm = !showAnnForm">{{ showAnnForm ? '取消' : '+ 发布' }}</button></div>
        <div class="ann-form" v-if="showAnnForm">
          <input v-model="annForm.title" placeholder="标题" class="af-input" />
          <textarea v-model="annForm.content" placeholder="内容" class="af-textarea" rows="2"></textarea>
          <label class="af-check"><input type="checkbox" v-model="annForm.is_pinned"/> 置顶</label>
          <button class="btn-sm primary" @click="submitAnn">发布</button>
        </div>
        <div class="ann-list" v-if="adminAnns.length">
          <div v-for="a in adminAnns" :key="a.id" class="ann-row">
            <div class="ar-info"><span :class="{pinned:a.is_pinned}">{{ a.is_pinned ? '📌 ' : '' }}{{ a.title }}</span><span class="ar-text">{{ a.content.slice(0,50) }}...</span></div>
            <div class="ar-actions"><span class="ar-date">{{ a.created_at?.slice(0,10) }}</span><button class="btn-del" @click="confirmDelAnn(a.id)">删除</button></div>
          </div>
        </div>
        <div class="empty-hint" v-else>暂无公告</div>
      </section>

      <!-- 留言 -->
      <section class="panel">
        <div class="panel-head"><h3>用户留言 ({{ adminMsgs.length }})</h3></div>
        <div class="msg-list" v-if="adminMsgs.length">
          <div v-for="m in adminMsgs" :key="m.id" class="msg-row">
            <div class="mr-left">
              <span class="mr-user">{{ m.household_name }}</span>
              <span class="mr-content">{{ m.content }}</span>
              <span class="mr-date">{{ m.created_at?.slice(0,10) }}</span>
            </div>
            <div class="mr-right">
              <template v-if="m.reply"><span class="mr-replied">已回复: {{ m.reply }}</span></template>
              <template v-else>
                <button v-if="replyForm.id !== m.id" class="btn-sm" @click="replyForm.id=m.id;replyForm.text=''">回复</button>
                <span v-else class="reply-inline"><input v-model="replyForm.text" placeholder="回复" class="af-input s"/><button class="btn-sm primary" @click="doReply(m.id,replyForm.text)">发送</button><button class="btn-sm" @click="replyForm.id=null">取消</button></span>
              </template>
              <button class="btn-del" @click="confirmDelMsg(m.id)">删除</button>
            </div>
          </div>
        </div>
        <div class="empty-hint" v-else>暂无留言</div>
      </section>
    </div>

    <!-- ========== 知识图谱 ========== -->
    <div v-if="tab === 'kg'" class="kg-full-wrap">
      <div class="kg-top">
        <span class="kg-count">{{ kgNodes }} 个节点 · {{ kgLinks }} 条关系</span>
        <div class="kg-filters">
          <select v-model="kgFilter.energy" class="kf-sel" @change="applyFilter"><option value="all">全部能耗等级</option><option v-for="(v,k) in kgStats?.energy_dist" :key="k" :value="k">{{ k }} ({{ v }})</option></select>
          <select v-model="kgFilter.category" class="kf-sel" @change="applyFilter"><option value="all">全部设备类别</option><option v-for="(v,k) in kgStats?.device_cat_dist" :key="k" :value="k">{{ k }} ({{ v }})</option></select>
        </div>
      </div>
      <div class="kg-main-row">
        <div class="kg-chart-area" ref="adminKgChart"></div>
        <div class="kg-side" :class="{open:kgPanelOpen}">
          <template v-if="!kgPanelOpen">
            <div class="kgs-trigger" @click="kgPanelOpen=true"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg><span class="kgs-text">统计</span></div>
          </template>
          <template v-else>
            <div class="kgs-head"><span>全局统计</span><button class="kgs-close" @click="kgPanelOpen=false">×</button></div>
            <div class="kgs-body">
              <div v-if="kgDetail">
                <!-- 用户详情 -->
                <template v-if="kgDetail.type==='user'">
                  <h4 class="kgs-dname">{{ kgDetail.name }}</h4>
                  <span class="kgs-tag" :style="{background:elBg(kgDetail.energy_level)}">{{ kgDetail.energy_level }}</span>
                  <div class="kgs-rows"><div class="kgsr"><span>月均用电</span><span>{{ kgDetail.avg_kwh }} kWh</span></div><div class="kgsr"><span>设备数</span><span>{{ kgDetail.active }}/{{ kgDetail.device_count }} 运行中</span></div><div class="kgsr"><span>账单</span><span>{{ kgDetail.paid }}/{{ kgDetail.bills }} 已缴</span></div><div class="kgsr" v-if="kgDetail.income"><span>收入</span><span>¥{{ kgDetail.income.toLocaleString() }}</span></div><div class="kgsr" v-if="kgDetail.area"><span>住房</span><span>{{ kgDetail.area }} m²</span></div><div class="kgsr" v-if="kgDetail.warning"><span>状态</span><span class="text-red">有欠费</span></div></div>
                </template>
                <!-- 设备详情 -->
                <template v-else-if="kgDetail.type==='device'">
                  <h4 class="kgs-dname">{{ kgDetail.name }}</h4>
                  <span class="kgs-tag" :class="kgDetail.is_active?'on':'off'">{{ kgDetail.is_active?'运行中':'已损坏' }}</span>
                  <div class="kgs-rows"><div class="kgsr"><span>所属用户</span><span>{{ kgDetail.household_name }}</span></div><div class="kgsr"><span>功率</span><span>{{ kgDetail.power }} W</span></div><div class="kgsr"><span>年限</span><span>{{ kgDetail.usage_years?.toFixed(1) }}年</span></div><div class="kgsr"><span>损坏率</span><span :class="kgDetail.damage_prob>0.5?'text-red':''">{{ (kgDetail.damage_prob*100).toFixed(1) }}%</span></div></div>
                </template>
              </div>
              <div v-else>
                <div class="kgs-section"><div class="kgs-st">系统概览</div><div class="kgs-rows"><div class="kgsr"><span>用户</span><span>{{ kgStats?.total_users }}</span></div><div class="kgsr"><span>设备</span><span>{{ kgStats?.total_devices }}</span></div><div class="kgsr"><span>账单</span><span>{{ kgStats?.total_bills }}</span></div></div></div>
                <div class="kgs-section"><div class="kgs-st">缴费概况</div><div class="kgs-rows"><div class="kgsr"><span>已缴</span><span class="on">{{ kgStats?.paid_bills }}</span></div><div class="kgsr"><span>未缴</span><span class="off">{{ kgStats?.unpaid_bills }}</span></div><div class="kgsr"><span>欠费用户</span><span>{{ kgStats?.warning_users }}</span></div></div></div>
                <div class="kgs-section"><div class="kgs-st">能耗分布</div><div class="kgs-chart" ref="energyBarChart"></div></div>
                <div class="kgs-section"><div class="kgs-st">损坏风险</div><div class="kgs-rows" v-if="kgStats?.high_risk?.length"><div v-for="r in kgStats.high_risk" :key="r.name" class="kgsr"><span>{{ r.user }}</span><span class="text-red">{{ (r.prob*100).toFixed(0) }}%</span></div></div><div v-else class="kgs-empty">无高风险设备</div></div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- ========== 数据管理 ========== -->
    <div v-if="tab === 'data'">
      <div class="data-subtabs">
        <button :class="['dtab',{active:dataSub==='users'}]" @click="dataSub='users';loadDataTab()">用户管理</button>
        <button :class="['dtab',{active:dataSub==='devices'}]" @click="dataSub='devices';loadDataTab()">设备管理</button>
        <button :class="['dtab',{active:dataSub==='repairs'}]" @click="dataSub='repairs';loadDataTab()">维修审核</button>
        <button :class="['dtab',{active:dataSub==='announcements'}]" @click="dataSub='announcements';loadDataTab()">系统公告</button>
        <button :class="['dtab',{active:dataSub==='messages'}]" @click="dataSub='messages';loadDataTab()">用户留言</button>
      </div>

      <!-- 用户管理 -->
      <div v-if="dataSub==='users'" class="data-table-wrap">
        <div class="dt-toolbar"><button class="btn-sm primary" @click="showUserForm=true;editUserForm={username:'',real_name:'',password:''}">+ 新增用户</button></div>
        <div v-if="showUserForm" class="user-form"><input v-model="editUserForm.username" placeholder="用户名" class="af-input"/><input v-model="editUserForm.real_name" placeholder="姓名" class="af-input"/><input v-model="editUserForm.password" placeholder="密码" class="af-input" type="password"/><button class="btn-sm primary" @click="createUser">创建</button><button class="btn-sm" @click="showUserForm=false">取消</button></div>
        <table class="dt"><thead><tr><th>户号</th><th>用户名</th><th>姓名</th><th>电话</th><th>设备</th><th>操作</th></tr></thead>
          <tbody><tr v-for="u in dataUsers" :key="u.household_id"><td>{{ u.household_id }}</td><td>{{ u.username }}</td><td>{{ u.real_name }}</td><td>{{ u.phone||'-' }}</td><td>{{ u.device_count }}</td><td><button class="btn-sm" @click="openUserDetail(u.household_id)">详情</button><button class="btn-sm" @click="deleteUser(u.household_id)">删除</button></td></tr></tbody>
        </table>
      </div>

      <!-- 设备管理 -->
      <div v-if="dataSub==='devices'" class="data-table-wrap">
        <table class="dt"><thead><tr><th>设备</th><th>类别</th><th>用户</th><th>功率</th><th>年限</th><th>损坏率</th><th>状态</th><th>操作</th></tr></thead>
          <tbody><tr v-for="d in dataDevices" :key="d.device_id"><td>{{ d.custom_name||d.device_name }}</td><td>{{ d.category }}</td><td>{{ d.household_name }}</td><td>{{ d.effective_power||d.rated_power }}W</td><td>{{ d.usage_years?.toFixed(1) }}年</td><td :class="d.damage_probability>0.5?'text-red':''">{{ (d.damage_probability*100).toFixed(1) }}%</td><td><span :class="d.is_active?'stat-ok':'stat-bad'">{{ d.is_active?'正常':'损坏' }}</span></td><td><button class="btn-del" @click="deleteDevice(d.device_id)">删除</button></td></tr></tbody>
        </table>
      </div>

      <!-- 维修审核 -->
      <div v-if="dataSub==='repairs'" class="data-table-wrap">
        <table class="dt"><thead><tr><th>单号</th><th>用户</th><th>设备</th><th>故障</th><th>状态</th><th>费用</th><th>操作</th></tr></thead>
          <tbody><tr v-for="o in dataRepairs" :key="o.order_id"><td class="td-mono">{{ o.order_id?.slice(-8) }}</td><td>{{ o.household_name }}</td><td>{{ o.device_name }}</td><td>{{ o.fault_text }} {{ o.fault_description?.slice(0,20) }}</td><td>{{ o.status_text }}</td><td>{{ o.repair_cost?'¥'+o.repair_cost:'-' }}</td><td><button v-if="o.status===1" class="btn-sm" @click="assignRepair(o)">派单</button><button v-if="o.status===3" class="btn-sm" @click="completeRepair(o)">完成</button></td></tr></tbody>
        </table>
      </div>

      <!-- 系统公告 -->
      <div v-if="dataSub==='announcements'" class="data-table-wrap">
        <div class="ann-form-bar"><input v-model="annForm.title" placeholder="公告标题" class="af-input"/><textarea v-model="annForm.content" placeholder="公告内容" class="af-textarea" rows="2"></textarea><label class="af-check"><input type="checkbox" v-model="annForm.is_pinned"/>置顶</label><button class="btn-sm primary" @click="submitAnn">发布</button></div>
        <table class="dt"><thead><tr><th>标题</th><th>内容</th><th>置顶</th><th>日期</th><th>操作</th></tr></thead><tbody><tr v-for="a in dataAnnouncements" :key="a.id"><td>{{ a.title }}</td><td class="td-desc">{{ a.content.slice(0,60) }}...</td><td>{{ a.is_pinned?'是':'否' }}</td><td>{{ a.created_at?.slice(0,10) }}</td><td><button class="btn-del" @click="confirmDelAnn(a.id)">删除</button></td></tr></tbody></table>
      </div>

      <!-- 用户留言 -->
      <div v-if="dataSub==='messages'" class="data-table-wrap">
        <table class="dt"><thead><tr><th>用户</th><th>内容</th><th>回复</th><th>日期</th><th>操作</th></tr></thead><tbody><tr v-for="m in dataMessages" :key="m.id"><td>{{ m.household_name }}</td><td>{{ m.content }}</td><td>{{ m.reply||'未回复' }}</td><td>{{ m.created_at?.slice(0,10) }}</td><td><button v-if="!m.reply" class="btn-sm" @click="replyForm.id=m.id;replyForm.text=''">回复</button><button class="btn-del" @click="confirmDelMsg(m.id)">删除</button></td></tr></tbody></table>
      </div>

      <!-- 用户详情弹窗 -->
      <Teleport to="body"><Transition name="pop"><div class="pop-overlay" v-if="userDetail" @click.self="userDetail=null"><div class="pop-detail">
        <div class="pd-head"><h3>{{ userDetail.real_name }}</h3><span class="pd-id">{{ userDetail.household_id }}</span><button class="ph-close" @click="userDetail=null">×</button></div>
        <div class="pd-body">
          <div class="pd-sec"><div class="pd-st">基本信息</div><div class="pd-grid"><div class="pdg"><span>性别</span><span>{{ {1:'男',2:'女'}[userDetail.gender]||'--' }}</span></div><div class="pdg"><span>出生</span><span>{{ userDetail.birth_year||'--' }}年{{ userDetail.birth_month||'--' }}月</span></div><div class="pdg"><span>学历</span><span>{{ {1:'小学',2:'初中',3:'高中',4:'大专',5:'本科',6:'硕士',7:'博士'}[userDetail.education]||'--' }}</span></div><div class="pdg"><span>婚姻</span><span>{{ {1:'未婚',2:'已婚',3:'离异',4:'丧偶'}[userDetail.marital]||'--' }}</span></div><div class="pdg"><span>职业</span><span>{{ userDetail.occupation||'--' }}</span></div><div class="pdg"><span>电话</span><span>{{ userDetail.phone||'--' }}</span></div><div class="pdg"><span>作息</span><span>{{ userDetail.schedule||'--' }}</span></div><div class="pdg"><span>健康</span><span>{{ userDetail.health||'--' }}</span></div><div class="pdg full"><span>地址</span><span>{{ userDetail.address||'--' }}</span></div></div></div>
          <div class="pd-sec" v-if="userDetail.housing"><div class="pd-st">住房</div><div class="pd-grid"><div class="pdg"><span>类型</span><span>{{ userDetail.housing.type||'--' }}</span></div><div class="pdg"><span>面积</span><span>{{ userDetail.housing.area||'--' }} m²</span></div><div class="pdg"><span>户型</span><span>{{ userDetail.housing.bedroom }}室{{ userDetail.housing.living }}厅</span></div><div class="pdg"><span>楼层</span><span>{{ userDetail.housing.floor||'--' }}/{{ userDetail.housing.total_floors||'--' }}</span></div></div></div>
          <div class="pd-sec" v-if="userDetail.income"><div class="pd-st">收入</div><div class="pd-grid"><div class="pdg"><span>个人</span><span>¥{{ userDetail.income.personal?.toLocaleString()||'--' }}</span></div><div class="pdg"><span>家庭</span><span>¥{{ userDetail.income.household?.toLocaleString()||'--' }}</span></div></div></div>
          <div class="pd-sec"><div class="pd-st">用电 ({{ userDetail.devices?.length||0 }}台设备)</div>
            <div class="pd-device-list" v-if="userDetail.devices?.length"><div v-for="d in userDetail.devices" :key="d.id" class="pdd"><span>{{ d.name }}</span><span>{{ d.type }} · {{ d.power }}W · {{ d.years?.toFixed(1) }}年 <span :class="d.damage_prob>0.5?'text-red':''">{{ (d.damage_prob*100).toFixed(1) }}%</span></span></div></div>
          </div>
          <div class="pd-sec"><div class="pd-st">账单 (已缴{{ userDetail.paid_bills }}/{{ userDetail.bills }})</div><div class="pd-grid"><div v-for="b in userDetail.recent_bills" :key="b.month" class="pdg"><span>{{ b.month }}</span><span>{{ b.kwh }}kWh · ¥{{ b.amount }} · {{ b.status }}</span></div></div></div>
          <div class="pd-sec" v-if="userDetail.family?.length"><div class="pd-st">家庭成员</div><div v-for="m in userDetail.family" :key="m.name" class="pbr"><span>{{ {2:'配偶',3:'子女',4:'父母'}[m.relation]||'亲属' }}</span><span>{{ m.name }}</span></div></div>
        </div>
      </div></div></Transition></Teleport>
    </div>

    <!-- 删除确认弹窗 -->
    <Teleport to="body"><Transition name="pop"><div class="pop-overlay" v-if="delTarget" @click.self="delTarget=null"><div class="pop-dialog"><h3>确认删除</h3><p>删除后不可恢复，确定吗？</p><div class="pop-actions"><button class="btn-sm" @click="delTarget=null">取消</button><button class="btn-sm danger" @click="doDel">确认删除</button></div></div></div></Transition></Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import {
  getAdminDashboard, advanceSystemMonth, getSystemMonth,
  getAdminAnnouncements, createAnnouncement, deleteAnnouncement,
  getAdminMessages, replyMessage, deleteMessage, getAdminUsers,
  getAdminRepairOrders, getKGFullGraph, getAdminUserDetail,
  getMyDevices, assignRepair, completeRepair,
  adminCreateUser, adminDeleteUser, deleteDevice as apiDeleteDevice,
} from '../api'

const route = useRoute()
const tab = computed(() => {
  if (route.path === '/admin/kg') return 'kg'
  if (route.path === '/admin/data') return 'data'
  return 'dashboard'
})

// 概览
const stats = reactive({ total_users:0,total_devices:0,active_devices:0,damaged_devices:0,pending_repairs:0,bills_collected:'0/0',total_months_elapsed:0,unit_price:0 })
const sysMonth = ref(''); const advancing = ref(false); const advanceResult = ref(null); const advanceError = ref('')
const adminAnns = ref([]); const showAnnForm = ref(false); const annForm = reactive({title:'',content:'',is_pinned:false})
const adminMsgs = ref([]); const replyForm = reactive({id:null,text:''}); const delTarget = ref(null); const delType = ref('')

async function loadOverview() {
  const [a,s,ann,msg] = await Promise.all([getAdminDashboard(),getSystemMonth(),getAdminAnnouncements(),getAdminMessages()])
  Object.assign(stats,a.data.stats); sysMonth.value=s.data.year_month; adminAnns.value=ann.data.announcements||[]; adminMsgs.value=msg.data.messages||[]
}
onMounted(loadOverview)

async function handleAdvance() { if(!confirm('确定推进至下月？'))return; advancing.value=true; try{const r=await advanceSystemMonth();advanceResult.value=r.data;await loadOverview()}catch(e){advanceError.value=e.response?.data?.message||'失败'}finally{advancing.value=false} }
async function submitAnn() { if(!annForm.title.trim())return; await createAnnouncement(annForm); showAnnForm.value=false; annForm.title='';annForm.content='';annForm.is_pinned=false; const r=await getAdminAnnouncements();adminAnns.value=r.data.announcements||[] }
function confirmDelAnn(id) { delTarget.value=id; delType.value='ann' }
function confirmDelMsg(id) { delTarget.value=id; delType.value='msg' }
async function doDel() {
  if(delType.value==='ann'){await deleteAnnouncement(delTarget.value);const r=await getAdminAnnouncements();adminAnns.value=r.data.announcements||[]}
  else if(delType.value==='msg'){await deleteMessage(delTarget.value);const r=await getAdminMessages();adminMsgs.value=r.data.messages||[]}
  delTarget.value=null;delType.value=''
}
async function doReply(id,text) { await replyMessage(id,text); const r=await getAdminMessages();adminMsgs.value=r.data.messages||[]; replyForm.id=null;replyForm.text='' }

// 知识图谱
const adminKgChart = ref(null); const kgNodes=ref(0);const kgLinks=ref(0);const kgStats=ref(null);const kgPanelOpen=ref(true);const kgDetail=ref(null);const kgFilter=reactive({energy:'all',category:'all'});const energyBarChart=ref(null)
let kgInstance=null; let kgAllData=null

async function loadAdminKG() {
  if (!adminKgChart.value) return
  try { const r = await getKGFullGraph(); const d=r.data; kgAllData=d; kgNodes.value=d.nodes?.length||0; kgLinks.value=d.links?.length||0; kgStats.value=d.stats
    if(kgInstance)kgInstance.dispose(); kgInstance=echarts.init(adminKgChart.value)
    renderKGChart()
    nextTick(()=>{ renderEnergyBar() })
    kgInstance.on('click',(p)=>{ if(p.dataType==='node'&&p.data?.detail){ kgDetail.value=p.data.detail;kgPanelOpen.value=true } })
    kgInstance.on('dblclick',(p)=>{ if(p.dataType==='node'&&p.data.group==='user'){ const g=p.data.id;p.data.group==='user'?toggleUserDevices(p.data.id):null } })
  } catch(e) { console.error(e) }
}

function renderKGChart(filtered) {
  let d = filtered || kgAllData; if(!d)return
  kgInstance.setOption({tooltip:{show:false},series:[{type:'graph',layout:'force',roam:true,draggable:true,force:{repulsion:250,edgeLength:[80,200],gravity:0.1},data:d.nodes,links:d.links,label:{show:true,fontSize:10,color:'#444'},lineStyle:{color:'#dce3ea',width:1.5,opacity:0.6},emphasis:{focus:'adjacency',lineStyle:{width:3,color:'#5b8def'}}}]},true)
}

function applyFilter() {
  if(!kgAllData)return
  let nodes=[...kgAllData.nodes]; let links=[...kgAllData.links]
  if(kgFilter.energy!=='all'){ const keep=new Set(); nodes.forEach(n=>{if(n.category==='device')keep.add(n.id); if(n.category==='user'&&n.detail?.energy_level===kgFilter.energy)keep.add(n.id) }); nodes=nodes.map(n=>({...n,itemStyle:{...n.itemStyle,opacity:keep.has(n.id)?1:0.15}})) }
  if(kgFilter.category!=='all'){ const keep=new Set(); nodes.forEach(n=>{if(n.category==='user')keep.add(n.id); if(n.category==='device'&&n.detail?.category===kgFilter.category)keep.add(n.id) }); nodes=nodes.map(n=>({...n,itemStyle:{...n.itemStyle,opacity:keep.has(n.id)?1:0.15}})) }
  renderKGChart({nodes,links})
}

function renderEnergyBar() {
  if(!energyBarChart.value||!kgStats.value?.energy_dist)return
  const c=echarts.init(energyBarChart.value); const d=kgStats.value.energy_dist
  c.setOption({grid:{top:4,right:8,bottom:16,left:28},xAxis:{type:'category',data:Object.keys(d),axisLabel:{fontSize:8}},yAxis:{type:'value',axisLabel:{fontSize:8},splitLine:{lineStyle:{color:'#f0f0f0'}}},series:[{type:'bar',data:Object.values(d),itemStyle:{color:params=>['#67c23a','#5470c6','#e6a23c','#e74c3c'][params.dataIndex]}}]})
}

function elBg(lv){return{'节能型':'#e8f5e9','普通型':'#eef2ff','摆渡型':'#fef3e2','高耗能型':'#fde8e8'}[lv]||'#f0f2f5'}

const expandedUsers=new Set()
function toggleUserDevices(uid) { expandedUsers.has(uid)?expandedUsers.delete(uid):expandedUsers.add(uid); if(!kgAllData)return; const nodes=kgAllData.nodes.map(n=>{ if(n.group&&n.group!=='user'&&n.group===uid) return{...n,hidden:!expandedUsers.has(uid)}; return n }); const vSet=new Set(nodes.filter(n=>!n.hidden).map(n=>n.id)); const links=kgAllData.links.filter(l=>vSet.has(l.source)&&vSet.has(l.target)); renderKGChart({nodes,links}) }

const dataSub=ref('users')
const dataUsers=ref([]);const dataDevices=ref([]);const dataRepairs=ref([]);const dataAnnouncements=ref([]);const dataMessages=ref([])
const userDetail=ref(null)
const showUserForm=ref(false);const editUserForm=reactive({username:'',real_name:'',password:''})

async function loadDataTab() {
  if(dataSub.value==='users'){const r=await getAdminUsers();dataUsers.value=r.data.users||[]}
  if(dataSub.value==='devices'){const r=await getMyDevices();dataDevices.value=r.data.devices||[]}
  if(dataSub.value==='repairs'){const r=await getAdminRepairOrders();dataRepairs.value=r.data.orders||[]}
  if(dataSub.value==='announcements'){const r=await getAdminAnnouncements();dataAnnouncements.value=r.data.announcements||[]}
  if(dataSub.value==='messages'){const r=await getAdminMessages();dataMessages.value=r.data.messages||[]}
}
watch(tab,(v)=>{if(v==='kg')nextTick(loadAdminKG); if(v==='data')loadDataTab()},{immediate:true})

async function openUserDetail(hid){const r=await getAdminUserDetail(hid);userDetail.value=r.data.user}
async function doAssign(o){const n=prompt('维修人员：','张师傅');if(n){await assignRepair(o.order_id,n);loadDataTab()}}
async function doComplete(o){const c=prompt('费用(元)：','100');if(c){await completeRepair(o.order_id,{repair_cost:parseFloat(c),repair_result:'已修复'});loadDataTab()}}

async function createUser(){if(!editUserForm.username)return;await adminCreateUser(editUserForm);showUserForm.value=false;loadDataTab()}
async function deleteUser(hid){if(!confirm('确定删除用户 '+hid+' ？'))return;await adminDeleteUser(hid);loadDataTab()}
async function deleteDevice(did){if(!confirm('确定删除？'))return;await apiDeleteDevice(did);loadDataTab()}
async function deleteRepair(oid){if(!confirm('确定删除？'))return;await deleteMessage(oid);loadDataTab()}
</script>

<style scoped>
.admin-page{padding:20px 24px;width:100%;box-sizing:border-box}
.page-top{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:18px}
.page-top h2{font-size:18px;font-weight:500;color:#2c3e50;margin:0}
.tab-bar{display:flex;gap:4px}
.tab{padding:8px 20px;font-size:13px;color:#888;text-decoration:none;border-bottom:2px solid transparent;transition:all .15s}
.tab:hover{color:#2c3e50}
.tab.active{color:#2c3e50;font-weight:600;border-bottom-color:#5470c6}

/* 统计 */
.stats-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px}
.st-card{background:#fff;border:1px solid #edf0f4;border-radius:8px;padding:18px;text-align:center}
.st-val{font-size:24px;font-weight:600;color:#2c3e50}
.st-lbl{font-size:11px;color:#999;margin-top:4px}

.advance-section{margin-bottom:16px}
.advance-card{background:linear-gradient(135deg,#5470c6,#3b82f6);border-radius:10px;padding:20px;text-align:center;color:#fff}
.current-month-value{font-size:32px;font-weight:700;display:block}
.current-month-label{font-size:12px;opacity:.8}
.elapsed-label{font-size:11px;opacity:.6;display:block;margin-top:4px}
.advance-btn{padding:10px 36px;background:#fff;color:#5470c6;border:none;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;margin-top:12px;font-family:inherit}
.advance-btn:disabled{opacity:.6}
.advance-result{background:#ecf8e8;border:1px solid #91cc75;border-radius:6px;padding:10px 14px;margin-top:10px;font-size:12px}
.advance-error{background:#fde8e8;border:1px solid #ee6666;border-radius:6px;padding:10px 14px;margin-top:10px;font-size:12px;color:#c33}
.advance-hint{font-size:11px;opacity:.7;margin-top:6px}

/* 面板 */
.panel{background:#fff;border:1px solid #edf0f4;border-radius:8px;margin-bottom:14px;overflow:hidden}
.panel-head{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-bottom:1px solid #f0f2f5}
.panel-head h3{font-size:13px;font-weight:600;color:#555;margin:0}

.ann-form{padding:12px 16px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;border-bottom:1px solid #f0f2f5}
.af-input{padding:6px 10px;border:1px solid #e0e0e0;border-radius:4px;font-size:12px;outline:none;font-family:inherit}
.af-textarea{padding:6px 10px;border:1px solid #e0e0e0;border-radius:4px;font-size:12px;outline:none;resize:vertical;font-family:inherit}
.af-input.s{width:100px}
.af-check{font-size:11px;color:#888;display:flex;align-items:center;gap:4px}
.ann-list{padding:4px 10px}
.ann-row,.msg-row{display:flex;justify-content:space-between;align-items:center;padding:8px 6px;border-bottom:1px solid #f8f9fb;gap:10px}
.ann-row:last-child,.msg-row:last-child{border-bottom:none}
.ar-info{display:flex;flex-direction:column;gap:2px}
.ar-info span{font-size:12px;color:#333}.ar-info span.pinned{color:#e6a23c}
.ar-text{font-size:10px;color:#999}
.ar-actions,.mr-right{display:flex;align-items:center;gap:8px;flex-shrink:0}
.ar-date{font-size:10px;color:#ccc}
.mr-left{display:flex;flex-direction:column;gap:2px;flex:1}
.mr-user{font-size:12px;font-weight:600;color:#2c3e50}
.mr-content{font-size:11px;color:#555}
.mr-date{font-size:10px;color:#ccc}
.mr-replied{font-size:11px;color:#67c23a}
.reply-inline{display:flex;gap:4px;align-items:center}
.btn-sm{padding:4px 12px;border:1px solid #e0e0e0;border-radius:4px;background:#fff;font-size:11px;color:#666;cursor:pointer;font-family:inherit}
.btn-sm.primary{background:#2c3e50;color:#fff;border-color:#2c3e50}
.btn-sm:hover{border-color:#5470c6;color:#5470c6}
.btn-sm.primary:hover{background:#5470c6}
.btn-del{font-size:11px;padding:3px 8px;border:1px solid #e0e0e0;background:#fff;color:#e74c3c;border-radius:4px;cursor:pointer;font-family:inherit}
.btn-del:hover{background:#fde8e8}
.empty-hint{text-align:center;padding:20px;color:#ccc;font-size:12px}

/* KG */
.kg-full-wrap{display:flex;flex-direction:column;height:calc(100vh - 130px)}
.kg-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-shrink:0}
.kg-count{font-size:11px;color:#aaa}
.kg-filters{display:flex;gap:6px}
.kf-sel{padding:4px 10px;border:1px solid #e0e0e0;border-radius:4px;font-size:11px;color:#666;background:#fff;outline:none;cursor:pointer;font-family:inherit}
.kg-main-row{flex:1;display:flex;gap:0;overflow:hidden;min-height:0}
.kg-chart-area{flex:1;background:#fafbfc;border:1px solid #edf0f4;border-radius:8px 0 0 8px;overflow:hidden}
.kg-side{flex-shrink:0;background:#fff;border:1px solid #edf0f4;border-left:none;border-radius:0 8px 8px 0;display:flex;flex-direction:column;transition:width .25s;overflow:hidden}
.kg-side:not(.open){width:44px}
.kg-side.open{width:280px}
.kgs-trigger{display:flex;flex-direction:column;align-items:center;gap:4px;padding:14px 8px;cursor:pointer;color:#999}
.kgs-trigger:hover{color:#5470c6;background:#f8f9fb}
.kgs-text{font-size:10px;writing-mode:vertical-rl;letter-spacing:2px}
.kgs-head{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;border-bottom:1px solid #f0f2f5;font-size:12px;font-weight:600;color:#888}
.kgs-close{background:none;border:none;font-size:16px;color:#ccc;cursor:pointer}
.kgs-body{flex:1;overflow-y:auto;padding:12px 14px}
.kgs-dname{font-size:14px;font-weight:600;color:#2c3e50;margin:0 0 6px}
.kgs-tag{display:inline-block;padding:2px 8px;border-radius:4px;font-size:10px;margin-bottom:8px;color:#888;background:#f0f2f5}
.kgs-tag.on{background:#e8f5e9;color:#52c41a}
.kgs-tag.off{background:#fde8e8;color:#ff4d4f}
.kgs-section{margin-bottom:12px}
.kgs-st{font-size:10px;color:#bbb;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px;padding-bottom:4px;border-bottom:1px solid #f5f5f5}
.kgs-rows{display:flex;flex-direction:column}
.kgsr{display:flex;justify-content:space-between;padding:4px 0;font-size:11px;border-bottom:1px solid #fafafa}
.kgsr span:first-child{color:#aaa}
.kgsr span:last-child{color:#555}
.kgsr span.on{color:#52c41a}
.kgsr span.off{color:#ff4d4f}
.kgs-chart{width:100%;height:90px}
.kgs-empty{font-size:11px;color:#ccc;text-align:center;padding:8px 0}
.text-red{color:#ff4d4f!important}
.stat-ok{color:#52c41a}.stat-bad{color:#ff4d4f}

/* 数据管理 */
.data-table-wrap{overflow-x:auto}
.dt-toolbar{margin-bottom:10px}
.user-form{display:flex;gap:8px;align-items:center;margin-bottom:12px;flex-wrap:wrap}
.td-mono{font-family:monospace;font-size:11px;color:#999}
.td-desc{max-width:200px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ann-form-bar{display:flex;gap:8px;align-items:center;padding:10px 0;flex-wrap:wrap}

/* 详情弹窗 */
.pop-detail{background:#fff;border-radius:10px;width:620px;max-width:94vw;max-height:85vh;overflow-y:auto}
.pd-head{display:flex;align-items:center;gap:10px;padding:16px 20px;border-bottom:1px solid #f0f2f5;position:sticky;top:0;background:#fff;z-index:1}
.pd-head h3{font-size:16px;font-weight:600;color:#2c3e50;margin:0}
.pd-id{font-size:11px;color:#ccc;font-family:monospace}
.pd-body{padding:16px 20px}
.pd-sec{margin-bottom:16px}
.pd-st{font-size:10px;color:#bbb;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px;padding-bottom:4px;border-bottom:1px solid #f5f5f5}
.pd-grid{display:grid;grid-template-columns:1fr 1fr;gap:4px 16px}
.pdg{display:flex;justify-content:space-between;padding:4px 0;font-size:11px;border-bottom:1px solid #fafafa}
.pdg span:first-child{color:#aaa}
.pdg span:last-child{color:#555}
.pdg.full{grid-column:span 2}
.pd-device-list{display:flex;flex-direction:column;gap:4px}
.pdd{display:flex;justify-content:space-between;padding:4px 0;font-size:11px;border-bottom:1px solid #fafafa}
.pbr{display:flex;justify-content:space-between;padding:4px 0;font-size:11px;border-bottom:1px solid #fafafa}

/* 数据标签 */
.data-subtabs{display:flex;gap:4px;margin-bottom:14px}
.dtab{padding:6px 16px;border:1px solid #e0e0e0;border-radius:6px;background:#fff;font-size:12px;color:#888;cursor:pointer;font-family:inherit}
.dtab.active{background:#2c3e50;color:#fff;border-color:#2c3e50}
.dt{width:100%;border-collapse:collapse;font-size:12px;background:#fff;border:1px solid #edf0f4;border-radius:8px;overflow:hidden}
.dt th{padding:10px 14px;text-align:left;font-size:10px;color:#aaa;text-transform:uppercase;font-weight:500;background:#fafbfc}
.dt td{padding:10px 14px;border-top:1px solid #f5f5f5}

/* 弹窗 */
.pop-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.3);z-index:3000;display:flex;align-items:center;justify-content:center}
.pop-dialog{background:#fff;border-radius:10px;padding:28px 32px;width:360px;text-align:center}
.pop-dialog h3{font-size:15px;color:#2c3e50;margin:0 0 8px}
.pop-dialog p{font-size:12px;color:#888;margin:0 0 20px}
.pop-actions{display:flex;gap:10px;justify-content:center}
.btn-sm.danger{background:#e74c3c;color:#fff;border-color:#e74c3c}
.pop-enter-active,.pop-leave-active{transition:opacity .2s}
.pop-enter-from,.pop-leave-to{opacity:0}
</style>
