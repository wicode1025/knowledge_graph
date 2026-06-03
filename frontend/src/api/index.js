import axios from 'axios'

const API_BASE = '/api/kg'

// ==================== Token 拦截器 ====================
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      const requestUrl = error.config.url || ''
      if (requestUrl.includes('/auth/login/') || requestUrl.includes('/auth/register/')) {
        return Promise.reject(error)
      }
      localStorage.clear()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ==================== 认证 ====================
export function login(username, password) {
  return axios.post(`${API_BASE}/auth/login/`, { username, password })
}
export function register(username, password, email) {
  return axios.post(`${API_BASE}/auth/register/`, { username, password, email })
}
export function logout() {
  return axios.post(`${API_BASE}/auth/logout/`)
}
export function verifyToken() {
  return axios.get(`${API_BASE}/auth/verify/`)
}

// ==================== 系统月份 ====================
export function getSystemMonth() {
  return axios.get(`${API_BASE}/system/month/`)
}
export function advanceSystemMonth() {
  return axios.post(`${API_BASE}/system/month/advance/`)
}

// ==================== 用户信息 ====================
export function getMyHousehold() {
  return axios.get(`${API_BASE}/household/mine/`)
}
export function updateMyHousehold(data) {
  return axios.put(`${API_BASE}/household/mine/update/`, data)
}
export function updateHousingInfo(data) {
  return axios.put(`${API_BASE}/household/housing/update/`, data)
}
export function updateIncomeInfo(data) {
  return axios.put(`${API_BASE}/household/income/update/`, data)
}
export function getFamilyMembers() {
  return axios.get(`${API_BASE}/household/members/`)
}
export function addFamilyMember(data) {
  return axios.post(`${API_BASE}/household/members/`, data)
}
export function updateFamilyMember(id, data) {
  return axios.put(`${API_BASE}/household/members/${id}/`, data)
}
export function deleteFamilyMember(id) {
  return axios.delete(`${API_BASE}/household/members/${id}/`)
}

export function getOptions() {
  return axios.get(`${API_BASE}/options/`)
}

// ==================== 设备管理 ====================
export function getDeviceTypes() {
  return axios.get(`${API_BASE}/device-types/`)
}
export function getDeviceTypeDetail(typeCode) {
  return axios.get(`${API_BASE}/device-types/${typeCode}/`)
}
export function getMyDevices() {
  return axios.get(`${API_BASE}/devices/`)
}
export function addDevice(data) {
  return axios.post(`${API_BASE}/devices/`, data)
}
export function updateDevice(deviceId, data) {
  return axios.put(`${API_BASE}/devices/${deviceId}/`, data)
}
export function deleteDevice(deviceId) {
  return axios.delete(`${API_BASE}/devices/${deviceId}/`)
}
export function getDeviceHistory(deviceId) {
  return axios.get(`${API_BASE}/devices/${deviceId}/history/`)
}

// ==================== 用电记录 ====================
export function getMonthlyConsumption(params) {
  return axios.get(`${API_BASE}/consumption/monthly/`, { params })
}
export function getConsumptionSummary() {
  return axios.get(`${API_BASE}/consumption/summary/`)
}
export function getConsumptionTrends() {
  return axios.get(`${API_BASE}/consumption/trends/`)
}

// ==================== 缴费管理 ====================
export function getMyBills() {
  return axios.get(`${API_BASE}/bills/`)
}
export function getCurrentBill() {
  return axios.get(`${API_BASE}/bills/current/`)
}
export function getBillDetail(billId) {
  return axios.get(`${API_BASE}/bills/${billId}/`)
}
export function payBill(billId) {
  return axios.post(`${API_BASE}/bills/${billId}/pay/`)
}
export function getNotices() {
  return axios.get(`${API_BASE}/notices/`)
}

// 公告
export function getAnnouncements() {
  return axios.get(`${API_BASE}/announcements/`)
}
export function getAdminAnnouncements() {
  return axios.get(`${API_BASE}/admin/announcements/`)
}
export function createAnnouncement(data) {
  return axios.post(`${API_BASE}/admin/announcements/`, data)
}
export function updateAnnouncement(id, data) {
  return axios.put(`${API_BASE}/admin/announcements/${id}/`, data)
}
export function deleteAnnouncement(id) {
  return axios.delete(`${API_BASE}/admin/announcements/${id}/`)
}

// 留言
export function getMessages() {
  return axios.get(`${API_BASE}/messages/`)
}
export function sendMessage(content) {
  return axios.post(`${API_BASE}/messages/`, { content })
}
export function withdrawMessage(msgId) {
  return axios.delete(`${API_BASE}/messages/${msgId}/withdraw/`)
}
export function getAdminMessages() {
  return axios.get(`${API_BASE}/admin/messages/`)
}
export function replyMessage(id, reply) {
  return axios.post(`${API_BASE}/admin/messages/${id}/reply/`, { reply })
}
export function deleteMessage(id) {
  return axios.delete(`${API_BASE}/admin/messages/${id}/delete/`)
}
export function getAdminUserDetail(householdId) {
  return axios.get(`${API_BASE}/admin/users/${householdId}/`)
}
export function adminCreateUser(data) {
  return axios.post(`${API_BASE}/admin/users/create/`, data)
}
export function adminEditUser(householdId, data) {
  return axios.put(`${API_BASE}/admin/users/${householdId}/edit/`, data)
}
export function adminDeleteUser(householdId) {
  return axios.delete(`${API_BASE}/admin/users/${householdId}/delete/`)
}

// ==================== 维修报单 ====================
export function getRepairOrders() {
  return axios.get(`${API_BASE}/repairs/`)
}
export function createRepairOrder(data) {
  return axios.post(`${API_BASE}/repairs/`, data)
}
export function getRepairOrderDetail(orderId) {
  return axios.get(`${API_BASE}/repairs/${orderId}/`)
}
export function rateRepair(orderId, rating) {
  return axios.post(`${API_BASE}/repairs/${orderId}/rate/`, { rating })
}

// ==================== 知识图谱 ====================
export function getKGFullGraph() {
  return axios.get(`${API_BASE}/graph/full/`)
}
export function getUserKG() {
  return axios.get(`${API_BASE}/graph/user/`)
}
export function syncToNeo4j() {
  return axios.post(`${API_BASE}/graph/sync/`)
}

// ==================== 聚类/画像 ====================
export function getClusters() {
  return axios.get(`${API_BASE}/clusters/`)
}
export function getEnhancedProfile() {
  return axios.get(`${API_BASE}/profile/enhanced/`)
}

// ==================== 管理员 ====================
export function getAdminDashboard() {
  return axios.get(`${API_BASE}/admin/stats/`)
}
export function getAdminUsers() {
  return axios.get(`${API_BASE}/admin/users/`)
}
export function getAdminRepairOrders(status) {
  return axios.get(`${API_BASE}/admin/repair-orders/`, { params: status ? { status } : {} })
}
export function assignRepair(orderId, technicianName) {
  return axios.post(`${API_BASE}/admin/repair-orders/${orderId}/assign/`, { technician_name: technicianName })
}
export function completeRepair(orderId, data) {
  return axios.post(`${API_BASE}/admin/repair-orders/${orderId}/complete/`, data)
}
