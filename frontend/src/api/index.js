import { mockDispatch } from './mock/router.js'

const API_BASE = '/api/kg'

// ==================== Mock HTTP Client (纯前端模式) ====================
// 封装 axios 风格的 API 调用，将所有请求路由到本地 mock 服务
const api = {
  async _mockCall(method, url, data, params) {
    const fullUrl = url.startsWith('/') ? url : `${API_BASE}${url}`
    const result = await mockDispatch(method, fullUrl, data, params)
    if (result.status >= 200 && result.status < 300) {
      return { data: result.data }
    }
    throw { response: { status: result.status, data: result.data } }
  },
  get(url, params) { return this._mockCall('get', url, null, params) },
  post(url, data) { return this._mockCall('post', url, data) },
  put(url, data) { return this._mockCall('put', url, data) },
  delete(url) { return this._mockCall('delete', url, null) }
}

// ==================== 认证 ====================
export function login(username, password) {
  return api.post(`${API_BASE}/auth/login/`, { username, password })
}
export function register(username, password, email) {
  return api.post(`${API_BASE}/auth/register/`, { username, password, email })
}
export function logout() {
  return api.post(`${API_BASE}/auth/logout/`)
}
export function verifyToken() {
  return api.get(`${API_BASE}/auth/verify/`)
}

// ==================== 系统月份 ====================
export function getSystemMonth() {
  return api.get(`${API_BASE}/system/month/`)
}
export function advanceSystemMonth() {
  return api.post(`${API_BASE}/system/month/advance/`)
}

// ==================== 用户信息 ====================
export function getMyHousehold() {
  return api.get(`${API_BASE}/household/mine/`)
}
export function updateMyHousehold(data) {
  return api.put(`${API_BASE}/household/mine/update/`, data)
}
export function updateHousingInfo(data) {
  return api.put(`${API_BASE}/household/housing/update/`, data)
}
export function updateIncomeInfo(data) {
  return api.put(`${API_BASE}/household/income/update/`, data)
}
export function getFamilyMembers() {
  return api.get(`${API_BASE}/household/members/`)
}
export function addFamilyMember(data) {
  return api.post(`${API_BASE}/household/members/`, data)
}
export function updateFamilyMember(id, data) {
  return api.put(`${API_BASE}/household/members/${id}/`, data)
}
export function deleteFamilyMember(id) {
  return api.delete(`${API_BASE}/household/members/${id}/`)
}

export function getOptions() {
  return api.get(`${API_BASE}/options/`)
}

// ==================== 设备管理 ====================
export function getDeviceTypes() {
  return api.get(`${API_BASE}/device-types/`)
}
export function getDeviceTypeDetail(typeCode) {
  return api.get(`${API_BASE}/device-types/${typeCode}/`)
}
export function getMyDevices() {
  return api.get(`${API_BASE}/devices/`)
}
export function addDevice(data) {
  return api.post(`${API_BASE}/devices/`, data)
}
export function updateDevice(deviceId, data) {
  return api.put(`${API_BASE}/devices/${deviceId}/`, data)
}
export function deleteDevice(deviceId) {
  return api.delete(`${API_BASE}/devices/${deviceId}/`)
}
export function getDeviceHistory(deviceId) {
  return api.get(`${API_BASE}/devices/${deviceId}/history/`)
}

// ==================== 用电记录 ====================
export function getMonthlyConsumption(params) {
  return api.get(`${API_BASE}/consumption/monthly/`, { params })
}
export function getConsumptionSummary() {
  return api.get(`${API_BASE}/consumption/summary/`)
}
export function getConsumptionTrends() {
  return api.get(`${API_BASE}/consumption/trends/`)
}

// ==================== 缴费管理 ====================
export function getMyBills() {
  return api.get(`${API_BASE}/bills/`)
}
export function getCurrentBill() {
  return api.get(`${API_BASE}/bills/current/`)
}
export function getBillDetail(billId) {
  return api.get(`${API_BASE}/bills/${billId}/`)
}
export function payBill(billId) {
  return api.post(`${API_BASE}/bills/${billId}/pay/`)
}
export function getNotices() {
  return api.get(`${API_BASE}/notices/`)
}

// 公告
export function getAnnouncements() {
  return api.get(`${API_BASE}/announcements/`)
}
export function getAdminAnnouncements() {
  return api.get(`${API_BASE}/admin/announcements/`)
}
export function createAnnouncement(data) {
  return api.post(`${API_BASE}/admin/announcements/`, data)
}
export function updateAnnouncement(id, data) {
  return api.put(`${API_BASE}/admin/announcements/${id}/`, data)
}
export function deleteAnnouncement(id) {
  return api.delete(`${API_BASE}/admin/announcements/${id}/`)
}

// 留言
export function getMessages() {
  return api.get(`${API_BASE}/messages/`)
}
export function sendMessage(content) {
  return api.post(`${API_BASE}/messages/`, { content })
}
export function withdrawMessage(msgId) {
  return api.delete(`${API_BASE}/messages/${msgId}/withdraw/`)
}
export function getAdminMessages() {
  return api.get(`${API_BASE}/admin/messages/`)
}
export function replyMessage(id, reply) {
  return api.post(`${API_BASE}/admin/messages/${id}/reply/`, { reply })
}
export function deleteMessage(id) {
  return api.delete(`${API_BASE}/admin/messages/${id}/delete/`)
}
export function getAdminUserDetail(householdId) {
  return api.get(`${API_BASE}/admin/users/${householdId}/`)
}
export function adminCreateUser(data) {
  return api.post(`${API_BASE}/admin/users/create/`, data)
}
export function adminEditUser(householdId, data) {
  return api.put(`${API_BASE}/admin/users/${householdId}/edit/`, data)
}
export function adminDeleteUser(householdId) {
  return api.delete(`${API_BASE}/admin/users/${householdId}/delete/`)
}

// ==================== 维修报单 ====================
export function getRepairOrders() {
  return api.get(`${API_BASE}/repairs/`)
}
export function createRepairOrder(data) {
  return api.post(`${API_BASE}/repairs/`, data)
}
export function getRepairOrderDetail(orderId) {
  return api.get(`${API_BASE}/repairs/${orderId}/`)
}
export function rateRepair(orderId, rating) {
  return api.post(`${API_BASE}/repairs/${orderId}/rate/`, { rating })
}

// ==================== 知识图谱 ====================
export function getKGFullGraph() {
  return api.get(`${API_BASE}/graph/full/`)
}
export function getUserKG() {
  return api.get(`${API_BASE}/graph/user/`)
}
export function getUserKGById(householdId) {
  return api.get(`${API_BASE}/graph/user/`, { household_id: householdId })
}
export function syncToNeo4j() {
  return api.post(`${API_BASE}/graph/sync/`)
}

// ==================== 聚类/画像 ====================
export function getClusters() {
  return api.get(`${API_BASE}/clusters/`)
}
export function getEnhancedProfile() {
  return api.get(`${API_BASE}/profile/enhanced/`)
}

// ==================== 管理员 ====================
export function getAdminDashboard() {
  return api.get(`${API_BASE}/admin/stats/`)
}
export function getAdminUsers() {
  return api.get(`${API_BASE}/admin/users/`)
}
export function getAdminRepairOrders(status) {
  return api.get(`${API_BASE}/admin/repair-orders/`, { params: status ? { status } : {} })
}
export function assignRepair(orderId, technicianName) {
  return api.post(`${API_BASE}/admin/repair-orders/${orderId}/assign/`, { technician_name: technicianName })
}
export function completeRepair(orderId, data) {
  return api.post(`${API_BASE}/admin/repair-orders/${orderId}/complete/`, data)
}
