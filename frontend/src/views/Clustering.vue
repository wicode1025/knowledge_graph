<template>
  <div class="clustering">
    <h1>智能用户分群</h1>

    <div class="actions">
      <button @click="loadClusters" :disabled="loading">
        {{ loading ? '加载中...' : '重新分群' }}
      </button>
      <button @click="exportToNeo4j" :disabled="exporting">
        {{ exporting ? '导出中...' : '导出到Neo4j' }}
      </button>
    </div>

    <!-- 分群统计卡片 -->
    <div class="cluster-summary">
      <div
        v-for="cluster in clusters"
        :key="cluster.cluster_id"
        class="cluster-card"
        :class="getClusterClass(cluster.cluster_label)"
      >
        <div class="cluster-header">
          <span class="cluster-id">Cluster {{ cluster.cluster_id }}</span>
          <span class="cluster-label">{{ cluster.cluster_label }}</span>
        </div>
        <div class="cluster-stats">
          <div class="stat">
            <span class="value">{{ cluster.user_count }}</span>
            <span class="label">用户数</span>
          </div>
          <div class="stat">
            <span class="value">{{ cluster.avg_energy }}</span>
            <span class="label">日均kWh</span>
          </div>
          <div class="stat">
            <span class="value">{{ cluster.avg_cv }}</span>
            <span class="label">波动系数</span>
          </div>
        </div>
        <!-- 用户列表 -->
        <div class="cluster-users-list">
          <div
            v-for="userId in cluster.users"
            :key="userId"
            class="user-chip"
            @click="selectUser(userId)"
          >
            {{ userId }}
          </div>
        </div>
      </div>
    </div>

    <!-- 分群分布柱状图 -->
    <div class="chart-section">
      <div class="chart-container">
        <h2>各分群用户数量</h2>
        <div ref="barChartRef" style="width: 100%; height: 300px;"></div>
      </div>
    </div>

    <!-- 用户详情面板 -->
    <div v-if="selectedUser" class="user-detail-panel">
      <div class="panel-header">
        <h2>用户详情 - {{ selectedUser }}</h2>
        <button class="close-btn" @click="selectedUser = null">×</button>
      </div>

      <!-- 用户用电特征 -->
      <div class="detail-stats">
        <div class="stat-box">
          <div class="stat-value">{{ userDetail.avg_daily_kwh || '-' }}</div>
          <div class="stat-label">日均用电 (kWh)</div>
        </div>
        <div class="stat-box">
          <div class="stat-value">{{ userDetail.cluster_label || '-' }}</div>
          <div class="stat-label">所属分群</div>
        </div>
      </div>

      <!-- 相似用户 -->
      <div class="similar-section">
        <h3>相似用户推荐</h3>
        <div v-if="similarUsers.length > 0" class="similar-list">
          <div v-for="user in similarUsers" :key="user.user_id" class="similar-card">
            <div class="similar-header">
              <span class="user-id">{{ user.user_id }}</span>
              <span class="similarity">{{ user.similarity_score }}% 相似</span>
            </div>
            <div class="similar-info">
              <span>日均: {{ user.avg_daily_kwh }} kWh</span>
              <span class="tag">{{ user.cluster_label }}</span>
            </div>
          </div>
        </div>
        <div v-else class="no-data">暂无相似用户</div>
      </div>

      <!-- 用户用电趋势 -->
      <div class="trend-section">
        <h3>最近30天用电趋势</h3>
        <div ref="trendChartRef" style="width: 100%; height: 250px;"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { getUserClusters, getUserProfile, getSimilarUsersFromCluster, getDailyConsumption, exportClustersToNeo4j } from '../api'

const loading = ref(false)
const exporting = ref(false)
const clusters = ref([])
const selectedUser = ref(null)
const userDetail = ref({})
const similarUsers = ref([])
const barChartRef = ref(null)
const trendChartRef = ref(null)

// 加载分群数据
async function loadClusters() {
  loading.value = true
  try {
    const res = await getUserClusters()
    clusters.value = res.data.clusters || []
    await nextTick()
    initBarChart()
  } catch (error) {
    console.error('Error loading clusters:', error)
  } finally {
    loading.value = false
  }
}

// 选择用户
async function selectUser(userId) {
  selectedUser.value = userId
  userDetail.value = {}
  similarUsers.value = []

  try {
    // 获取用户详情
    const profileRes = await getUserProfile(userId)
    userDetail.value = profileRes.data

    // 从分群数据中获取该用户的分群标签
    const userCluster = clusters.value.find(c => c.users && c.users.includes(userId))
    if (userCluster) {
      userDetail.value.cluster_label = userCluster.cluster_label
    }

    // 获取相似用户
    const similarRes = await getSimilarUsersFromCluster(userId, 5)
    similarUsers.value = similarRes.data.similar_users || []

    // 获取用电趋势
    const trendRes = await getDailyConsumption(userId, 30)

    await nextTick()
    initTrendChart(trendRes.data || [])
  } catch (error) {
    console.error('Error loading user detail:', error)
  }
}

// 导出到Neo4j
async function exportToNeo4j() {
  exporting.value = true
  try {
    const res = await exportClustersToNeo4j()
    if (res.data.status === 'success') {
      alert('导出成功！')
    } else {
      alert('导出失败: ' + res.data.message)
    }
  } catch (error) {
    alert('导出失败: ' + error.message)
  } finally {
    exporting.value = false
  }
}

// 获取分群样式
function getClusterClass(label) {
  const map = {
    '节能型': 'cluster-green',
    '普通型': 'cluster-blue',
    '波动型': 'cluster-yellow',
    '高耗能型': 'cluster-red'
  }
  return map[label] || 'cluster-blue'
}

// 初始化柱状图
function initBarChart() {
  if (!barChartRef.value || clusters.value.length === 0) return

  const chart = echarts.init(barChartRef.value)

  const xData = clusters.value.map(c => c.cluster_label)
  const yData = clusters.value.map(c => c.user_count)

  const colors = ['#52c41a', '#1890ff', '#faad14', '#f5222d']

  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: xData
    },
    yAxis: {
      type: 'value',
      name: '用户数'
    },
    series: [{
      type: 'bar',
      data: yData.map((val, idx) => ({
        value: val,
        itemStyle: { color: colors[idx] }
      })),
      barWidth: '50%'
    }]
  })
}

// 初始化趋势图
function initTrendChart(data) {
  if (!trendChartRef.value || !data.length) return

  const chart = echarts.init(trendChartRef.value)

  const dates = data.map(d => d.date).reverse()
  const values = data.map(d => d.total_kwh || 0)

  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { rotate: 45 }
    },
    yAxis: {
      type: 'value',
      name: '用电量 (kWh)'
    },
    series: [{
      type: 'line',
      data: values,
      smooth: true,
      areaStyle: { color: 'rgba(84, 112, 198, 0.2)' },
      itemStyle: { color: '#5470C6' }
    }]
  })
}

onMounted(() => {
  loadClusters()
})
</script>

<style scoped>
.clustering { padding: 20px; }

.actions {
  margin-bottom: 20px;
}

.actions button {
  padding: 10px 20px;
  margin-right: 10px;
  border: none;
  border-radius: 4px;
  background: #5470C6;
  color: #fff;
  cursor: pointer;
}

.actions button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.cluster-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.cluster-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.cluster-green { border-top: 4px solid #52c41a; }
.cluster-blue { border-top: 4px solid #1890ff; }
.cluster-yellow { border-top: 4px solid #faad14; }
.cluster-red { border-top: 4px solid #f5222d; }

.cluster-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.cluster-id { font-weight: bold; font-size: 16px; }

.cluster-label {
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.cluster-green .cluster-label { background: #f6ffed; color: #52c41a; }
.cluster-blue .cluster-label { background: #e6f7ff; color: #1890ff; }
.cluster-yellow .cluster-label { background: #fffbe6; color: #faad14; }
.cluster-red .cluster-label { background: #fff1f0; color: #f5222d; }

.cluster-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 15px;
}

.stat { text-align: center; }
.stat .value { display: block; font-size: 24px; font-weight: bold; }
.stat .label { font-size: 12px; color: #999; }

.cluster-users-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.user-chip {
  padding: 4px 10px;
  background: #f5f5f5;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
}

.user-chip:hover { background: #e6f7ff; }

.chart-section {
  margin-bottom: 30px;
}

.chart-container {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.chart-container h2 {
  margin: 0 0 15px;
  font-size: 18px;
}

.user-detail-panel {
  background: #fff;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.panel-header h2 { margin: 0; }

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: #999;
}

.detail-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 25px;
}

.stat-box {
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
  text-align: center;
}

.stat-box .stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.stat-box .stat-label {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.similar-section {
  margin-bottom: 25px;
}

.similar-section h3 {
  margin: 0 0 15px;
  font-size: 16px;
}

.similar-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.similar-card {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.similar-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.similar-header .user-id { font-weight: bold; }

.similarity {
  color: #52c41a;
  font-size: 12px;
}

.similar-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
}

.similar-info .tag {
  padding: 2px 6px;
  background: #e6f7ff;
  color: #1890ff;
  border-radius: 4px;
}

.no-data {
  padding: 20px;
  text-align: center;
  color: #999;
}

.trend-section h3 {
  margin: 0 0 15px;
  font-size: 16px;
}
</style>
