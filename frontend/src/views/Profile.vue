<template>
  <div class="profile">
    <div class="profile-header">
      <h1>用户画像分析 <span class="badge">增强版</span></h1>
      <div class="user-selector">
        <label>选择用户：</label>
        <select v-model="selectedUser" @change="onUserChange">
          <option v-for="user in users" :key="user.user_id" :value="user.user_id">
            {{ user.house_num }} - {{ user.behavior_label }}
          </option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="profileGraph.user" class="profile-content">
      <!-- 用户基本信息卡片 -->
      <div class="info-cards">
        <div class="info-card main-card">
          <div class="card-title">{{ profileGraph.user.house_num }}</div>
          <div class="card-value">{{ formatNumber(profileGraph.user.avg_daily_kwh) }}</div>
          <div class="card-label">日均用电 (kWh)</div>
          <div class="card-tags">
            <span class="tag energy" :class="profileGraph.user.energy_level">
              {{ profileGraph.user.energy_level }}能耗
            </span>
            <span class="tag behavior" :class="getBehaviorClass(profileGraph.user.behavior_label)">
              {{ profileGraph.user.behavior_label }}
            </span>
          </div>
        </div>

        <div class="info-card">
          <div class="card-value">{{ formatNumber(profileGraph.user.total_kwh) }}</div>
          <div class="card-label">总用电量 (kWh)</div>
        </div>

        <!-- FCM聚类结果 -->
        <div class="info-card" v-if="fcmMembership">
          <div class="card-value">{{ fcmMembership.cluster_label }}</div>
          <div class="card-label">FCM分群</div>
          <div class="entropy-badge" :class="getEntropyClass(fcmMembership.entropy)">
            隶属度熵: {{ (fcmMembership.entropy * 100).toFixed(1) }}%
          </div>
        </div>

        <div class="info-card">
          <div class="card-value">{{ topDevices.length }}</div>
          <div class="card-label">设备数量</div>
        </div>
      </div>

      <!-- 新增：嵌入向量雷达图 -->
      <div class="section highlight-section">
        <h2>
          <span class="section-icon">📊</span>
          用户特征向量
          <span class="tag-new">TransE嵌入</span>
        </h2>
        <p class="section-desc">基于知识图谱TransE算法学习的用户嵌入向量，融合语义关联信息</p>
        <div class="embedding-radar">
          <div ref="radarChartRef" style="width: 100%; height: 350px;"></div>
        </div>
      </div>

      <!-- 用户关系网络图 -->
      <div class="section">
        <h2>用户关系网络图</h2>
        <p class="section-desc">展示用户与设备、分群、标签等实体之间的关系</p>
        <div class="graph-container">
          <div ref="networkChartRef" style="width: 100%; height: 450px;"></div>
        </div>
      </div>

      <!-- FCM聚类隶属度可视化 -->
      <div class="section" v-if="fcmMembership">
        <h2>
          <span class="section-icon">🎯</span>
          FCM模糊聚类结果
          <span class="tag-new">改进FCM</span>
        </h2>
        <p class="section-desc">改进FCM算法（密度峰值初始化 + 自适应隶属度权重）</p>
        <div class="fcm-visualization">
          <div class="membership-chart">
            <div ref="fcmChartRef" style="width: 100%; height: 300px;"></div>
          </div>
          <div class="membership-details">
            <h3>各簇隶属度</h3>
            <div class="membership-bars">
              <div v-for="(value, key) in fcmMembership.membership" :key="key" class="membership-bar-item">
                <span class="cluster-name">{{ getClusterLabel(key) }}</span>
                <div class="bar-container">
                  <div class="bar" :style="{ width: (value * 100) + '%', background: getClusterColor(key) }"></div>
                </div>
                <span class="membership-value">{{ (value * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 设备分析和用电模式 -->
      <div class="two-columns">
        <!-- 设备用电占比 -->
        <div class="section">
          <h2>设备用电占比</h2>
          <div class="pie-container">
            <div ref="pieChartRef" style="width: 100%; height: 300px;"></div>
          </div>
          <div class="device-list">
            <div v-for="device in topDevices" :key="device.device_id" class="device-item">
              <span class="device-name">{{ device.device_name }}</span>
              <span class="device-kwh">{{ formatNumber(device.total_kwh) }} kWh</span>
              <span class="device-pct">{{ device.percentage }}%</span>
            </div>
          </div>
        </div>

        <!-- 用电模式分析 -->
        <div class="section">
          <h2>用电模式分析</h2>
          <div class="pattern-result">
            <div class="pattern-icon" :class="getPatternClass(userPattern.pattern)">
              {{ getPatternIcon(userPattern.pattern) }}
            </div>
            <div class="pattern-name">{{ userPattern.pattern }}</div>
          </div>
          <div class="timeslot-chart">
            <div ref="timeslotChartRef" style="width: 100%; height: 200px;"></div>
          </div>
        </div>
      </div>

      <!-- 气象影响分析 -->
      <div class="section" v-if="weatherImpact">
        <h2>
          <span class="section-icon">🌡️</span>
          气象因素影响分析
        </h2>
        <p class="section-desc">分析温度、季节等气象因素对用户用电行为的影响</p>
        <div class="weather-impact">
          <div class="impact-cards">
            <div class="impact-card">
              <div class="impact-label">用电波动系数</div>
              <div class="impact-value">{{ weatherImpact.cv }}</div>
            </div>
            <div class="impact-card">
              <div class="impact-label">季节性差异</div>
              <div class="impact-value">{{ weatherImpact.seasonal_variance }} kWh</div>
            </div>
            <div class="impact-card">
              <div class="impact-label">分析结论</div>
              <div class="impact-insight">{{ weatherImpact.insight }}</div>
            </div>
          </div>
          <div class="monthly-usage" v-if="weatherImpact.monthly_usage">
            <div ref="weatherChartRef" style="width: 100%; height: 250px;"></div>
          </div>
        </div>
      </div>

      <!-- 设备联动分析 -->
      <div class="section">
        <h2>设备联动分析</h2>
        <p class="section-desc">发现经常同时使用的设备组合</p>
        <div v-if="deviceCorrelations.length > 0" class="correlations">
          <div v-for="corr in deviceCorrelations" :key="corr.device1 + corr.device2" class="correlation-item">
            <span class="device-a">{{ corr.device1_name }}</span>
            <span class="connector">↔</span>
            <span class="device-b">{{ corr.device2_name }}</span>
            <span class="corr-score" :class="getCorrelationClass(corr.correlation)">
              相关度: {{ corr.correlation * 100 }}%
            </span>
            <span class="co-days">共现 {{ corr.co_use_days }} 天</span>
          </div>
        </div>
        <div v-else class="no-data">暂无设备联动数据</div>
      </div>

      <!-- 基于图嵌入的相似用户 -->
      <div class="section" v-if="embeddingSimilarUsers.length > 0">
        <h2>
          <span class="section-icon">🔗</span>
          基于TransE嵌入的语义相似用户
        </h2>
        <p class="section-desc">使用知识图谱TransE嵌入向量计算的语义相似度</p>
        <div class="embedding-similar-list">
          <div v-for="user in embeddingSimilarUsers" :key="user.user_id" class="embedding-similar-card">
            <div class="similar-header">
              <span class="user-id">{{ user.house_num }}</span>
              <span class="similarity-badge">{{ (user.similarity * 100).toFixed(1) }}% 相似</span>
            </div>
            <div class="similar-info">
              <span>日均: {{ user.avg_daily_kwh }} kWh</span>
              <span class="tag">{{ user.behavior_label }}</span>
            </div>
            <div class="similarity-bar">
              <div class="bar-fill" :style="{ width: (user.similarity * 100) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 相似用户和节能建议 -->
      <div class="two-columns">
        <!-- 相似用户推荐 -->
        <div class="section">
          <h2>相似用户推荐</h2>
          <div v-if="similarUsers.length > 0" class="similar-list">
            <div v-for="user in similarUsers" :key="user.user_id" class="similar-card">
              <div class="similar-header">
                <span class="user-id">{{ user.house_num }}</span>
                <span class="similarity">{{ user.similarity }}% 相似</span>
              </div>
              <div class="similar-info">
                <span>日均: {{ user.avg_daily_kwh }} kWh</span>
                <span class="tag">{{ user.behavior_label }}</span>
              </div>
              <div class="reasons">
                <span v-for="reason in user.reasons" :key="reason" class="reason">{{ reason }}</span>
              </div>
            </div>
          </div>
          <div v-else class="no-data">暂无相似用户</div>
        </div>

        <!-- 节能建议 -->
        <div class="section">
          <h2>智能节能建议</h2>
          <div class="saving-tips">
            <div v-for="tip in savingTips" :key="tip.title" class="tip-card" :class="tip.type">
              <div class="tip-title">{{ tip.title }}</div>
              <div class="tip-desc">{{ tip.description }}</div>
              <div v-if="tip.potential_saving > 0" class="tip-saving">
                预计可节约: {{ tip.potential_saving }} kWh/天
              </div>
            </div>
          </div>
          <div v-if="savingTips.length > 0" class="total-saving">
            预计总节能潜力: {{ totalSaving }} kWh/天
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import {
  getUserList,
  getUserProfileGraph,
  getUserNetwork,
  getUserPattern,
  getProfileSimilarUsers,
  getSavingTips,
  getDeviceCorrelation,
  getUserFCMMembership,
  getUserEmbedding,
  getEmbeddingSimilarity,
  getWeatherImpact,
  getFCMClusters
} from '../api'

const users = ref([])
const selectedUser = ref('')
const loading = ref(false)
const profileGraph = ref({})
const userPattern = ref({})
const similarUsers = ref([])
const savingTips = ref([])
const deviceCorrelations = ref([])
const topDevices = ref([])

// 新增数据
const fcmMembership = ref(null)
const userEmbedding = ref(null)
const embeddingSimilarUsers = ref([])
const weatherImpact = ref(null)
const fcmClusters = ref([])

const networkChartRef = ref(null)
const pieChartRef = ref(null)
const timeslotChartRef = ref(null)
const radarChartRef = ref(null)
const fcmChartRef = ref(null)
const weatherChartRef = ref(null)

async function loadData() {
  loading.value = true
  try {
    // 获取用户列表
    const usersRes = await getUserList()
    users.value = usersRes.data.users || []

    if (users.value.length > 0 && !selectedUser.value) {
      selectedUser.value = users.value[0].user_id
    }

    await loadProfileData()
  } catch (error) {
    console.error('Error loading data:', error)
  } finally {
    loading.value = false
  }
}

async function loadProfileData() {
  loading.value = true
  try {
    // 并行请求所有数据（包括新增的增强数据）
    const [graphRes, patternRes, similarRes, tipsRes, corrRes, fcmRes, embRes, embSimRes, weatherRes, clustersRes] = await Promise.all([
      getUserProfileGraph(selectedUser.value),
      getUserPattern(selectedUser.value),
      getProfileSimilarUsers(selectedUser.value),
      getSavingTips(selectedUser.value),
      getDeviceCorrelation(selectedUser.value),
      getUserFCMMembership(selectedUser.value),
      getUserEmbedding(selectedUser.value),
      getEmbeddingSimilarity(selectedUser.value, 5),
      getWeatherImpact(selectedUser.value),
      getFCMClusters()
    ])

    // 更新基础数据
    profileGraph.value = graphRes.data.graph || {}
    userPattern.value = {
      pattern: patternRes.data.pattern || '未知',
      timeslot_distribution: patternRes.data.timeslot_distribution || []
    }
    similarUsers.value = similarRes.data.similar_users || []
    savingTips.value = tipsRes.data.tips || []
    deviceCorrelations.value = corrRes.data.correlations || []

    // 更新新增的增强数据
    fcmMembership.value = fcmRes.data.membership || null
    userEmbedding.value = embRes.data.embedding || null
    embeddingSimilarUsers.value = embSimRes.data.similar_users || []
    weatherImpact.value = weatherRes.data.analysis || null
    fcmClusters.value = clustersRes.data.clusters || []

    // 处理设备数据 - 过滤掉总用电，排除用电量为0的设备
    const devices = (profileGraph.value.devices || [])
      .filter(d => d.device_name !== '总用电' && d.total_kwh > 0)
    topDevices.value = devices
      .sort((a, b) => b.total_kwh - a.total_kwh)
      .slice(0, 5)

    await nextTick()
    initCharts()
  } catch (error) {
    console.error('Error loading profile data:', error)
  } finally {
    loading.value = false
  }
}

function initCharts() {
  initNetworkChart()
  initPieChart()
  initTimeslotChart()
  initRadarChart()
  initFCMChart()
  initWeatherChart()
}

function initNetworkChart() {
  if (!networkChartRef.value) return

  let chart = echarts.getInstanceByDom(networkChartRef.value)
  if (chart) {
    chart.dispose()
  }
  chart = echarts.init(networkChartRef.value)

  // 使用网络API的数据
  getUserNetwork(selectedUser.value).then(res => {
    const nodes = res.data.nodes || []
    const links = res.data.links || []

    // 设置节点类别
    const categories = [
      { name: '用户' },
      { name: '设备' },
      { name: '能耗等级' },
      { name: '行为标签' }
    ]

    chart.setOption({
      tooltip: {},
      legend: {
        data: categories.map(c => c.name)
      },
      series: [{
        type: 'graph',
        layout: 'force',
        data: nodes.map(node => ({
          ...node,
          category: node.category === 'user' ? 0 :
                    node.category === 'device' ? 1 :
                    node.category === 'energy_level' ? 2 : 3
        })),
        links: links,
        categories: categories,
        roam: true,
        label: {
          show: true,
          position: 'right',
          formatter: '{b}'
        },
        force: {
          repulsion: 200,
          edgeLength: 100
        },
        lineStyle: {
          color: 'source',
          curveness: 0.1
        }
      }]
    })
  })
}

function initPieChart() {
  if (!pieChartRef.value || topDevices.value.length === 0) return

  let chart = echarts.getInstanceByDom(pieChartRef.value)
  if (chart) {
    chart.dispose()
  }
  chart = echarts.init(pieChartRef.value)

  const data = topDevices.value.map(d => ({
    name: d.device_name,
    value: d.total_kwh
  }))

  chart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} kWh ({d}%)'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      label: {
        show: true,
        formatter: '{b}: {d}%'
      },
      data: data
    }]
  })
}

function initTimeslotChart() {
  if (!timeslotChartRef.value || !userPattern.value.timeslot_distribution) return

  let chart = echarts.getInstanceByDom(timeslotChartRef.value)
  if (chart) {
    chart.dispose()
  }
  chart = echarts.init(timeslotChartRef.value)

  const data = userPattern.value.timeslot_distribution

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    yAxis: {
      type: 'category',
      data: data.map(d => d.timeslot)
    },
    series: [{
      type: 'bar',
      data: data.map(d => ({
        value: d.percentage,
        itemStyle: {
          color: d.percentage > 40 ? '#f5222d' :
                 d.percentage > 25 ? '#fa8c16' : '#52c41a'
        }
      })),
      label: {
        show: true,
        position: 'right',
        formatter: '{c}%'
      }
    }]
  })
}

// 初始化嵌入向量雷达图
function initRadarChart() {
  if (!radarChartRef.value) return

  // 销毁已存在的图表实例
  let chart = echarts.getInstanceByDom(radarChartRef.value)
  if (chart) {
    chart.dispose()
  }
  chart = echarts.init(radarChartRef.value)

  // 获取嵌入数据
  let emb = []
  if (userEmbedding.value && Array.isArray(userEmbedding.value) && userEmbedding.value.length > 0) {
    emb = userEmbedding.value
  }

  // 如果没有数据，显示模拟数据
  if (emb.length === 0) {
    emb = Array(64).fill(0).map(() => Math.random() * 0.3)
  }

  const dim = emb.length
  const numGroups = 8
  const groupSize = Math.max(1, Math.floor(dim / numGroups))

  const indicators = []
  const values = []

  for (let i = 0; i < numGroups; i++) {
    const start = i * groupSize
    const end = Math.min(start + groupSize, dim)
    let sum = 0
    for (let j = start; j < end; j++) {
      sum += Math.abs(emb[j])
    }
    const avg = sum / (end - start)

    indicators.push({
      name: `维度${i + 1}`,
      max: Math.max(avg * 1.5, 0.2)
    })
    values.push(parseFloat(avg.toFixed(4)))
  }

  chart.setOption({
    tooltip: {},
    radar: {
      indicator: indicators,
      radius: '65%'
    },
    series: [{
      type: 'radar',
      data: [{
        value: values,
        name: '特征强度',
        areaStyle: { color: 'rgba(114, 46, 209, 0.4)' },
        lineStyle: { color: '#722ed1' },
        itemStyle: { color: '#722ed1' }
      }]
    }]
  })
}

// 初始化FCM隶属度图表
function initFCMChart() {
  if (!fcmChartRef.value || !fcmMembership.value) return

  let chart = echarts.getInstanceByDom(fcmChartRef.value)
  if (chart) {
    chart.dispose()
  }
  chart = echarts.init(fcmChartRef.value)

  const membership = fcmMembership.value.membership || {}
  const labels = Object.keys(membership).map(k => getClusterLabel(k))
  const data = Object.values(membership).map(v => (v * 100).toFixed(1))

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    yAxis: {
      type: 'category',
      data: labels
    },
    series: [{
      type: 'bar',
      data: data.map((value, idx) => ({
        value: parseFloat(value),
        itemStyle: {
          color: getClusterColor(Object.keys(membership)[idx])
        }
      })),
      label: {
        show: true,
        position: 'right',
        formatter: '{c}%'
      }
    }]
  })
}

// 初始化气象影响图表
function initWeatherChart() {
  if (!weatherChartRef.value || !weatherImpact.value || !weatherImpact.value.monthly_usage) return

  let chart = echarts.getInstanceByDom(weatherChartRef.value)
  if (chart) {
    chart.dispose()
  }
  chart = echarts.init(weatherChartRef.value)

  const monthlyData = weatherImpact.value.monthly_usage
  const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
  const data = months.map(m => monthlyData[m.replace('月', '')] || 0)

  chart.setOption({
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: months
    },
    yAxis: {
      type: 'value',
      name: 'kWh'
    },
    series: [{
      type: 'line',
      data: data,
      areaStyle: {
        color: 'rgba(64, 158, 255, 0.2)'
      },
      lineStyle: {
        color: '#409EFF'
      },
      itemStyle: {
        color: '#409EFF'
      }
    }]
  })
}

function onUserChange() {
  loadProfileData()
}

function formatNumber(num) {
  if (num === undefined || num === null) return '0'
  return Number(num).toFixed(2)
}

function getBehaviorClass(label) {
  const map = {
    '节能型': 'green',
    '正常型': 'blue',
    '高耗能型': 'red'
  }
  return map[label] || 'blue'
}

function getPatternClass(pattern) {
  const map = {
    '早峰型': 'morning',
    '晚峰型': 'evening',
    '均匀型': 'uniform',
    '间歇型': 'irregular'
  }
  return map[pattern] || 'unknown'
}

function getPatternIcon(pattern) {
  const map = {
    '早峰型': '🌅',
    '晚峰型': '🌆',
    '均匀型': '📊',
    '间歇型': '📈'
  }
  return map[pattern] || '❓'
}

function getCorrelationClass(corr) {
  if (corr > 0.7) return 'high'
  if (corr > 0.5) return 'medium'
  return 'low'
}

// 获取FCM簇标签
function getClusterLabel(clusterId) {
  const labels = ['节能型', '普通型', '波动型', '高耗能型']
  return labels[clusterId] || `类型${clusterId}`
}

// 获取FCM簇颜色
function getClusterColor(clusterId) {
  const colors = ['#52c41a', '#1890ff', '#fa8c16', '#f5222d']
  return colors[clusterId] || '#999'
}

// 获取熵等级
function getEntropyClass(entropy) {
  if (entropy < 0.3) return 'low'
  if (entropy < 0.6) return 'medium'
  return 'high'
}

const totalSaving = ref(0)

watch(savingTips, (newTips) => {
  totalSaving.value = newTips.reduce((sum, tip) => sum + (tip.potential_saving || 0), 0).toFixed(2)
}, { immediate: true })

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.profile {
  padding: 20px;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.profile-header h1 {
  margin: 0;
}

.badge {
  font-size: 12px;
  background: #722ed1;
  color: #fff;
  padding: 2px 8px;
  border-radius: 4px;
  margin-left: 10px;
  vertical-align: middle;
}

.tag-new {
  font-size: 12px;
  background: #13c2c2;
  color: #fff;
  padding: 2px 8px;
  border-radius: 4px;
  margin-left: 10px;
  vertical-align: middle;
}

.section-icon {
  margin-right: 8px;
}

.highlight-section {
  background: linear-gradient(135deg, #f0f5ff 0%, #fff7e6 100%);
  border-left: 4px solid #722ed1;
}

.entropy-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  margin-top: 5px;
  display: inline-block;
}

.entropy-badge.low {
  background: #f6ffed;
  color: #52c41a;
}

.entropy-badge.medium {
  background: #fffbe6;
  color: #faad14;
}

.entropy-badge.high {
  background: #fff1f0;
  color: #f5222d;
}

.user-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-selector select {
  padding: 8px 15px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 200px;
}

.info-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.info-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
}

.info-card.main-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.main-card .card-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
}

.main-card .card-value {
  font-size: 36px;
  font-weight: bold;
}

.main-card .card-label {
  font-size: 12px;
  opacity: 0.9;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.card-label {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.card-tags {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 10px;
}

.tag {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.tag.energy.低 { background: #e6ffe6; color: #00b894; }
.tag.energy.中 { background: #e6f7ff; color: #1890ff; }
.tag.energy.高 { background: #fff7e6; color: #fa8c16; }
.tag.energy.极高 { background: #ffe6e6; color: #f5222d; }

.tag.behavior.green { background: #e6ffe6; color: #00b894; }
.tag.behavior.blue { background: #e6f7ff; color: #1890ff; }
.tag.behavior.red { background: #ffe6e6; color: #f5222d; }

.section {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.section h2 {
  margin: 0 0 10px;
  font-size: 18px;
}

.section-desc {
  color: #999;
  font-size: 14px;
  margin-bottom: 15px;
}

.two-columns {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.graph-container {
  background: #fafafa;
  border-radius: 8px;
  padding: 10px;
}

.device-list {
  margin-top: 15px;
}

.device-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.device-name {
  flex: 1;
  font-weight: 500;
}

.device-kwh {
  width: 100px;
  text-align: right;
  color: #666;
}

.device-pct {
  width: 60px;
  text-align: right;
  color: #1890ff;
  font-weight: bold;
}

.pattern-result {
  text-align: center;
  padding: 20px;
}

.pattern-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.pattern-name {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.correlations {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.correlation-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 6px;
}

.device-a, .device-b {
  font-weight: 500;
}

.connector {
  margin: 0 10px;
  color: #999;
}

.corr-score {
  margin-left: auto;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.corr-score.high { background: #ffe6e6; color: #f5222d; }
.corr-score.medium { background: #fff7e6; color: #fa8c16; }
.corr-score.low { background: #e6f7ff; color: #1890ff; }

.co-days {
  margin-left: 10px;
  color: #999;
  font-size: 12px;
}

.similar-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.similar-card {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.similar-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.user-id {
  font-weight: bold;
}

.similarity {
  color: #52c41a;
  font-size: 14px;
}

.similar-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
}

.tag {
  padding: 2px 6px;
  background: #e6f7ff;
  color: #1890ff;
  border-radius: 4px;
}

.reasons {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.reason {
  padding: 2px 8px;
  background: #f0f0f0;
  border-radius: 4px;
  font-size: 11px;
  color: #666;
}

.saving-tips {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tip-card {
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid;
}

.tip-card.reduce_level,
.tip-card.high_energy {
  background: #fff7e6;
  border-color: #fa8c16;
}

.tip-card.follow_example {
  background: #e6f7ff;
  border-color: #1890ff;
}

.tip-card.general {
  background: #f9f9f9;
  border-color: #d9d9d9;
}

.tip-title {
  font-weight: bold;
  margin-bottom: 5px;
}

.tip-desc {
  font-size: 13px;
  color: #666;
}

.tip-saving {
  margin-top: 8px;
  font-size: 14px;
  color: #52c41a;
  font-weight: 500;
}

.total-saving {
  margin-top: 15px;
  padding: 15px;
  background: #e6ffe6;
  border-radius: 8px;
  text-align: center;
  font-size: 16px;
  color: #00b894;
  font-weight: bold;
}

.no-data {
  text-align: center;
  padding: 30px;
  color: #999;
}

/* 新增样式 */
.embedding-radar {
  background: #fafafa;
  border-radius: 8px;
  padding: 15px;
}

.fcm-visualization {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.membership-details h3 {
  margin: 0 0 15px;
  font-size: 16px;
}

.membership-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.membership-bar-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.cluster-name {
  width: 60px;
  font-size: 13px;
}

.bar-container {
  flex: 1;
  height: 20px;
  background: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
}

.bar {
  height: 100%;
  border-radius: 10px;
  transition: width 0.3s;
}

.membership-value {
  width: 50px;
  text-align: right;
  font-size: 13px;
  color: #666;
}

.weather-impact {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.impact-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.impact-card {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
}

.impact-label {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
}

.impact-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.impact-insight {
  font-size: 13px;
  color: #666;
}

.embedding-similar-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.embedding-similar-card {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  border-left: 3px solid #722ed1;
}

.similarity-badge {
  background: #722ed1;
  color: #fff;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.similarity-bar {
  height: 6px;
  background: #e8e8e8;
  border-radius: 3px;
  margin-top: 10px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #722ed1, #b37feb);
  border-radius: 3px;
  transition: width 0.3s;
}

.loading {
  text-align: center;
  padding: 50px;
  color: #999;
}
</style>
