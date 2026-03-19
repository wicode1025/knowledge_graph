<template>
  <div class="kg-page">
    <!-- 页面头部 -->
    <div class="kg-header">
      <div class="header-left">
        <h1><span class="icon">🕸️</span> 电力用户知识图谱</h1>
        <p class="subtitle">基于Neo4j图数据库的20个家庭用电关系可视化</p>
      </div>
      <div class="header-actions">
        <button @click="loadGraph" :disabled="loading" class="btn-primary">
          <span v-if="!loading">🔄</span> {{ loading ? '加载中...' : '刷新图谱' }}
        </button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-content">
          <div class="stat-value">{{ nodeStats.users }}</div>
          <div class="stat-label">用户数量</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🔌</div>
        <div class="stat-content">
          <div class="stat-value">{{ nodeStats.devices }}</div>
          <div class="stat-label">设备数量</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🔗</div>
        <div class="stat-content">
          <div class="stat-value">{{ relationCount }}</div>
          <div class="stat-label">关系数量</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-value">{{ clusterCount }}</div>
          <div class="stat-label">用户分群</div>
        </div>
      </div>
    </div>

    <div class="kg-content">
      <!-- 左侧：图可视化 -->
      <div class="graph-section">
        <div class="section-header">
          <h2>用户关系网络图</h2>
          <div class="view-controls">
            <button
              v-for="mode in viewModes"
              :key="mode.value"
              :class="['mode-btn', { active: currentMode === mode.value }]"
              @click="currentMode = mode.value"
            >
              {{ mode.label }}
            </button>
          </div>
        </div>
        <div ref="graphChartRef" class="graph-chart"></div>

        <!-- 图例 -->
        <div class="graph-legend">
          <div class="legend-item" v-for="item in legendItems" :key="item.name">
            <span class="legend-dot" :style="{ background: item.color }"></span>
            <span class="legend-name">{{ item.name }}</span>
          </div>
        </div>
      </div>

      <!-- 右侧：用户列表 -->
      <div class="users-panel">
        <div class="panel-header">
          <h3>用户列表</h3>
          <span class="user-count">{{ users.length }} 个家庭</span>
        </div>
        <div class="users-list">
          <div
            v-for="user in users"
            :key="user.user_id"
            class="user-card"
            :class="{ active: selectedUser === user.user_id }"
            @click="selectUser(user)"
          >
            <div class="user-header">
              <span class="user-id">{{ user.house_num }}</span>
              <span class="energy-badge" :class="getEnergyClass(user.energy_level)">
                {{ user.energy_level }}
              </span>
            </div>
            <div class="user-info">
              <div class="info-row">
                <span class="label">日均用电</span>
                <span class="value">{{ user.avg_daily_kwh?.toFixed(1) }} kWh</span>
              </div>
              <div class="info-row">
                <span class="label">行为类型</span>
                <span class="value behavior" :class="getBehaviorClass(user.behavior_label)">
                  {{ user.behavior_label }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 选中用户详情 -->
    <div v-if="selectedUserData" class="detail-panel">
      <div class="detail-header">
        <h3>👤 {{ selectedUserData.house_num }} 用户详情</h3>
        <button class="close-btn" @click="selectedUser = null">✕</button>
      </div>
      <div class="detail-content">
        <div class="detail-section">
          <h4>基本信息</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="label">用户ID</span>
              <span class="value">{{ selectedUserData.user_id }}</span>
            </div>
            <div class="detail-item">
              <span class="label">能耗等级</span>
              <span class="value">{{ selectedUserData.energy_level }}</span>
            </div>
            <div class="detail-item">
              <span class="label">行为标签</span>
              <span class="value">{{ selectedUserData.behavior_label }}</span>
            </div>
            <div class="detail-item">
              <span class="label">用电模式</span>
              <span class="value">{{ selectedUserData.consumption_pattern }}</span>
            </div>
          </div>
        </div>
        <div class="detail-section">
          <h4>用电统计</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="label">日均用电</span>
              <span class="value highlight">{{ selectedUserData.avg_daily_kwh?.toFixed(2) }} kWh</span>
            </div>
            <div class="detail-item">
              <span class="label">用电波动</span>
              <span class="value">{{ selectedUserData.std_daily_kwh?.toFixed(2) }} kWh</span>
            </div>
            <div class="detail-item">
              <span class="label">最大日用电</span>
              <span class="value">{{ selectedUserData.max_daily_kwh?.toFixed(2) }} kWh</span>
            </div>
            <div class="detail-item">
              <span class="label">最小日用电</span>
              <span class="value">{{ selectedUserData.min_daily_kwh?.toFixed(2) }} kWh</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getKGGraph, getKGFullGraph, getUserList } from '../api'

const graphChartRef = ref(null)
const loading = ref(false)
const users = ref([])
const selectedUser = ref(null)
const selectedUserData = ref(null)
const currentMode = ref('all')
const graphData = ref({ nodes: [], relations: [] })

const viewModes = [
  { value: 'all', label: '全部' },
  { value: 'cluster', label: '按分群' },
  { value: 'similar', label: '相似关系' }
]

const legendItems = [
  { name: '用户节点', color: '#5470C6' },
  { name: '节能型', color: '#52C41A' },
  { name: '正常型', color: '#1890FF' },
  { name: '高耗型', color: '#F5222D' },
  { name: '设备节点', color: '#91CC75' },
  { name: '标签节点', color: '#FAC858' }
]

const nodeStats = computed(() => {
  const nodes = graphData.value.nodes || []
  return {
    users: nodes.filter(n => n.type === 'User').length,
    devices: nodes.filter(n => n.type === 'Device').length
  }
})

const relationCount = computed(() => {
  return graphData.value.relations?.length || 0
})

const clusterCount = computed(() => {
  const labels = new Set(users.value.map(u => u.behavior_label))
  return labels.size
})

const selectedUserDataFunc = computed(() => {
  return selectedUserData.value
})

async function loadGraph() {
  loading.value = true
  try {
    // 加载用户列表
    const userRes = await getUserList()
    const userList = userRes.data.users || userRes.data || []
    users.value = userList

    // 加载图数据
    const fullRes = await getKGFullGraph()
    if (fullRes.data.nodes && fullRes.data.nodes.length > 0) {
      graphData.value = fullRes.data
      await nextTick()
      initGraphChart()
    }

    // 强制更新计算属性
    if (users.value.length > 0) {
      console.log('Users loaded:', users.value.length)
    }
  } catch (error) {
    console.error('Error loading graph:', error)
  } finally {
    loading.value = false
  }
}

function selectUser(user) {
  selectedUser.value = user.user_id
  selectedUserData.value = user
}

function getEnergyClass(level) {
  const map = { '低': 'low', '中': 'medium', '高': 'high', '极高': 'extreme' }
  return map[level] || ''
}

function getBehaviorClass(label) {
  const map = { '节能型': 'green', '正常型': 'blue', '高耗能型': 'red', '波动型': 'purple' }
  return map[label] || 'blue'
}

function initGraphChart() {
  if (!graphChartRef.value) return

  let chart = echarts.getInstanceByDom(graphChartRef.value)
  if (chart) chart.dispose()
  chart = echarts.init(graphChartRef.value)

  const allNodes = graphData.value.nodes || []
  const allRelations = graphData.value.relations || []

  // 过滤用户节点
  const userNodes = allNodes.filter(n => n.type === 'User')
  const deviceNodes = allNodes.filter(n => n.type === 'Device')
  const labelNodes = allNodes.filter(n => ['EnergyLevel', 'BehaviorLabel', 'ConsumptionPattern'].includes(n.type))

  // 颜色映射
  const colors = {
    'User': '#5470C6',
    '节能型': '#52C41A',
    '正常型': '#1890FF',
    '高耗能型': '#F5222D',
    '波动型': '#722ED1',
    'Device': '#91CC75',
    'EnergyLevel': '#EE6666',
    'BehaviorLabel': '#FAC858',
    'ConsumptionPattern': '#73C0DE'
  }

  // 构建节点和关系
  const processedNodes = []
  const processedLinks = []
  const nodeSet = new Set()

  // 1. 添加所有用户节点（20个）
  userNodes.forEach((user, idx) => {
    const behaviorLabel = user.behavior_label || '正常型'
    const color = colors[behaviorLabel] || colors['User']

    processedNodes.push({
      id: user.id,
      name: user.house_num || user.id,
      category: 0,
      symbolSize: 45,
      itemStyle: {
        color: color,
        borderColor: '#fff',
        borderWidth: 2
      },
      userData: user
    })
    nodeSet.add(user.id)
  })

  // 2. 添加设备节点（限制数量）
  const deviceMap = {}
  userNodes.forEach(user => {
    const userId = user.id.split('_')[1]
    // 过滤掉总用电(Aggregate)，只保留具体设备
    const userDevices = deviceNodes.filter(d =>
      d.id.includes(userId) &&
      d.id !== `Aggregate_${userId}` &&
      d.device_name !== 'Aggregate' &&
      d.device_name !== '总用电' &&
      !d.id.includes('Aggregate')
    )
    userDevices.slice(0, 3).forEach(device => {
      if (!nodeSet.has(device.id)) {
        nodeSet.add(device.id)
        const devName = device.device_name_cn || device.device_name || device.id
        // 再次检查名称
        if (devName === '总用电' || devName === 'Aggregate') return

        processedNodes.push({
          id: device.id,
          name: devName,
          category: 4,
          symbolSize: 25,
          itemStyle: { color: colors['Device'] }
        })
      }
      // 用户-设备关系
      processedLinks.push({
        source: user.id,
        target: device.id,
        lineStyle: { color: '#91CC75', width: 1, curveness: 0.1 }
      })
    })
  })

  // 3. 添加行为标签节点
  const behaviorLabels = [...new Set(userNodes.map(u => u.behavior_label).filter(Boolean))]
  behaviorLabels.forEach(bl => {
    const id = 'BL_' + bl
    if (!nodeSet.has(id)) {
      nodeSet.add(id)
      processedNodes.push({
        id: id,
        name: bl,
        category: 3,
        symbolSize: 35,
        itemStyle: { color: colors[bl] || colors['BehaviorLabel'] }
      })
    }
    // 用户-行为标签关系
    userNodes.filter(u => u.behavior_label === bl).forEach(u => {
      processedLinks.push({
        source: u.id,
        target: id,
        lineStyle: { color: colors[bl] || '#FAC858', width: 2, curveness: 0.05 }
      })
    })
  })

  // 4. 根据模式添加用户间相似关系
  if (currentMode.value === 'similar') {
    // 添加相似用户关系（基于行为标签）
    for (let i = 0; i < userNodes.length; i++) {
      for (let j = i + 1; j < userNodes.length; j++) {
        if (userNodes[i].behavior_label === userNodes[j].behavior_label) {
          processedLinks.push({
            source: userNodes[i].id,
            target: userNodes[j].id,
            lineStyle: { color: '#5470C6', width: 1.5, type: 'dashed', curveness: 0.2 }
          })
        }
      }
    }
  }

  const categories = [
    { name: '用户', itemStyle: { color: '#5470C6' } },
    { name: '能耗等级', itemStyle: { color: '#EE6666' } },
    { name: '用电模式', itemStyle: { color: '#73C0DE' } },
    { name: '行为标签', itemStyle: { color: '#FAC858' } },
    { name: '设备', itemStyle: { color: '#91CC75' } }
  ]

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        if (params.dataType === 'node') {
          const data = params.data
          if (data.userData) {
            const u = data.userData
            return `<div style="padding: 8px;">
              <b>${u.house_num}</b><br/>
              日均用电: ${u.avg_daily_kwh?.toFixed(1)} kWh<br/>
              行为标签: ${u.behavior_label}<br/>
              能耗等级: ${u.energy_level}
            </div>`
          }
          return params.name
        }
        return ''
      }
    },
    legend: {
      data: categories.map(c => c.name),
      bottom: 10
    },
    series: [{
      type: 'graph',
      layout: currentMode.value === 'cluster' ? 'force' : 'force',
      force: {
        repulsion: 300,
        gravity: 0.15,
        edgeLength: 100
      },
      data: processedNodes.map(n => ({
        ...n,
        category: n.category !== undefined ? n.category : 0
      })),
      links: processedLinks,
      categories: categories,
      roam: true,
      label: {
        show: true,
        position: 'right',
        formatter: '{b}',
        fontSize: 11,
        color: '#333'
      },
      lineStyle: {
        color: 'source',
        curveness: 0.1
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: {
          width: 4
        }
      }
    }]
  }

  chart.setOption(option)

  // 点击事件
  chart.on('click', function(params) {
    if (params.dataType === 'node' && params.data.userData) {
      selectUser(params.data.userData)
    }
  })
}

watch(currentMode, () => {
  initGraphChart()
})

onMounted(() => {
  loadGraph()
})
</script>

<style scoped>
.kg-page {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 100px);
}

.kg-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left h1 {
  font-size: 24px;
  color: #1a1a2e;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
}

.header-left .icon {
  font-size: 28px;
}

.subtitle {
  color: #666;
  margin: 5px 0 0;
  font-size: 14px;
}

.btn-primary {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: transform 0.2s;
}

.btn-primary:hover {
  transform: translateY(-2px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.stat-icon {
  font-size: 32px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #1a1a2e;
}

.stat-label {
  font-size: 13px;
  color: #666;
}

.kg-content {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 20px;
}

.graph-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h2 {
  font-size: 18px;
  margin: 0;
  color: #1a1a2e;
}

.view-controls {
  display: flex;
  gap: 8px;
}

.mode-btn {
  padding: 6px 14px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.mode-btn.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.graph-chart {
  width: 100%;
  height: 500px;
}

.graph-legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding-top: 10px;
  border-top: 1px solid #eee;
  margin-top: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #666;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.users-panel {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  max-height: 600px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.panel-header h3 {
  font-size: 16px;
  margin: 0;
}

.user-count {
  font-size: 12px;
  color: #999;
}

.users-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.user-card {
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.user-card:hover {
  border-color: #667eea;
  background: #f8f9ff;
}

.user-card.active {
  border-color: #667eea;
  background: #f0f3ff;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.user-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.user-id {
  font-weight: 600;
  color: #1a1a2e;
}

.energy-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
}

.energy-badge.low { background: #f6ffed; color: #52c41a; }
.energy-badge.medium { background: #e6f7ff; color: #1890ff; }
.energy-badge.high { background: #fff7e6; color: #fa8c16; }
.energy-badge.extreme { background: #fff1f0; color: #f5222d; }

.user-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.info-row .label {
  color: #999;
}

.info-row .value {
  color: #333;
  font-weight: 500;
}

.info-row .value.behavior.green { color: #52c41a; }
.info-row .value.behavior.blue { color: #1890ff; }
.info-row .value.behavior.red { color: #f5222d; }

.detail-panel {
  margin-top: 20px;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.detail-header h3 {
  margin: 0;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #999;
}

.detail-section {
  margin-bottom: 20px;
}

.detail-section h4 {
  font-size: 14px;
  color: #666;
  margin: 0 0 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item .label {
  font-size: 12px;
  color: #999;
}

.detail-item .value {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.detail-item .value.highlight {
  color: #667eea;
  font-size: 16px;
}

@media (max-width: 1200px) {
  .kg-content {
    grid-template-columns: 1fr;
  }
  .users-panel {
    max-height: 400px;
  }
  .detail-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
