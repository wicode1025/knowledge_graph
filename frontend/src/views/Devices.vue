<template>
  <div class="devices">
    <h1>用电设备</h1>

    <!-- 用户选择器 -->
    <div class="user-selector">
      <label>选择用户：</label>
      <select v-model="selectedUser" @change="onUserChange">
        <option v-for="user in users" :key="user.user_id" :value="user.user_id">
          {{ user.house_num }}
        </option>
      </select>
    </div>

    <!-- 设备统计 -->
    <div class="stats">
      <div class="stat-card">
        <h3>设备数量</h3>
        <p class="value">{{ devices.length }}</p>
        <p class="label">个</p>
      </div>
      <div class="stat-card">
        <h3>设备类型</h3>
        <p class="value">{{ uniqueDeviceTypes }}</p>
        <p class="label">种</p>
      </div>
    </div>

    <!-- 设备列表 -->
    <div class="device-list">
      <div v-for="device in devices" :key="device.device_id" class="device-card">
        <div class="device-icon">{{ getDeviceIcon(device.device_name_cn) }}</div>
        <div class="device-info">
          <h3>{{ device.device_name_cn }}</h3>
          <p class="type">{{ device.device_code }}</p>
          <p class="id">ID: {{ device.device_id }}</p>
        </div>
      </div>
    </div>

    <!-- 设备类型统计图 -->
    <div class="chart-container">
      <h2>设备类型分布</h2>
      <div ref="chartRef" style="width: 100%; height: 400px;"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getUserList, getDevices } from '../api'

const users = ref([])
const selectedUser = ref('')
const devices = ref([])
const chartRef = ref(null)

const deviceIcons = {
  '冰箱': '🧊',
  '冰柜': '❄️',
  '洗衣机': '🧺',
  '干衣机': '👕',
  '洗碗机': '🍽️',
  '电视': '📺',
  '电视站点': '📺',
  '电脑': '💻',
  '电脑站点': '💻',
  '微波炉': '🍳',
  '电水壶': '🫖',
  '烤面包机': '🍞',
  '电暖器': '🔥',
  '音响': '🔊',
  '洗干一体机': '🧺',
  '冰柜1': '❄️',
  '冰柜2': '❄️',
  '冰箱冰柜': '🧊',
  '车库冰箱': '🧊',
  '车库冰柜': '❄️',
}

const uniqueDeviceTypes = computed(() => {
  const types = new Set(devices.value.map(d => d.device_name_cn))
  return types.size
})

function getDeviceIcon(name) {
  return deviceIcons[name] || '📦'
}

async function loadData() {
  try {
    // 获取用户列表
    const usersRes = await getUserList()
    users.value = usersRes.data.users || []

    if (users.value.length > 0 && !selectedUser.value) {
      selectedUser.value = users.value[0].user_id
    }

    await loadDevices()
  } catch (error) {
    console.error('Error loading data:', error)
  }
}

async function loadDevices() {
  try {
    const devicesRes = await getDevices(selectedUser.value)
    devices.value = devicesRes.data.devices || []

    await nextTick()
    initChart()
  } catch (error) {
    console.error('Error loading devices:', error)
  }
}

function onUserChange() {
  loadDevices()
}

function initChart() {
  if (!chartRef.value) return

  const chart = echarts.init(chartRef.value)

  // 统计设备类型
  const deviceCounts = {}
  devices.value.forEach(d => {
    const name = d.device_name_cn
    deviceCounts[name] = (deviceCounts[name] || 0) + 1
  })

  const data = Object.entries(deviceCounts).map(([name, value]) => ({ name, value }))

  chart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      top: '5%',
      left: 'center'
    },
    series: [
      {
        name: '设备类型',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 18,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: data
      }
    ]
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.devices { padding: 20px; }

.user-selector {
  margin-bottom: 20px;
  padding: 15px;
  background: #fff;
  border-radius: 8px;
}

.user-selector select {
  padding: 8px 15px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 200px;
}

.stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-card h3 {
  margin: 0 0 10px;
  font-size: 14px;
  color: #666;
}

.stat-card .value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.stat-card .label {
  font-size: 12px;
  color: #999;
  margin: 5px 0 0;
}

.device-list {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.device-card {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
}

.device-icon {
  font-size: 40px;
  margin-right: 20px;
}

.device-info h3 {
  margin: 0 0 5px;
  font-size: 16px;
}

.device-info .type {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.device-info .id {
  margin: 5px 0 0;
  color: #999;
  font-size: 12px;
}

.chart-container {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.chart-container h2 {
  margin: 0 0 20px;
  font-size: 18px;
}
</style>
