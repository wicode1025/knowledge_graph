import axios from 'axios'

const API_BASE = '/api/kg'

// ============================================================
// 用户相关API
// ============================================================

// 获取用户列表
export function getUserList() {
  return axios.get(`${API_BASE}/users/`)
}

// 获取指定用户画像
export function getUserProfile(userId = '') {
  const url = userId ? `${API_BASE}/profile/?user_id=${userId}` : `${API_BASE}/profile/`
  return axios.get(url)
}

// 获取用户统计数据
export function getUserStatistics() {
  return axios.get(`${API_BASE}/statistics/`)
}

// 获取用户对比数据
export function getComparison(userIds = []) {
  const ids = userIds.join(',')
  return axios.get(`${API_BASE}/comparison/?user_ids=${ids}`)
}

// 获取相似用户
export function getSimilarUsers(userId, topN = 5) {
  return axios.get(`${API_BASE}/similarity/?user_id=${userId}&top_n=${topN}`)
}

// ============================================================
// 用户分群API
// ============================================================

// 获取用户分群结果
export function getUserClusters() {
  return axios.get(`${API_BASE}/clusters/`)
}

// 获取指定分群的用户列表
export function getClusterUsers(clusterId) {
  return axios.get(`${API_BASE}/clusters/users/?cluster_id=${clusterId}`)
}

// 获取与指定用户相似的用户
export function getSimilarUsersFromCluster(userId, topN = 5) {
  return axios.get(`${API_BASE}/clusters/similar/?user_id=${userId}&top_n=${topN}`)
}

// 导出用户分群到Neo4j
export function exportClustersToNeo4j() {
  return axios.post(`${API_BASE}/clusters/export/`)
}

// ============================================================
// 设备相关API
// ============================================================

// 获取设备列表
export function getDevices(userId = '') {
  const url = userId ? `${API_BASE}/devices/?user_id=${userId}` : `${API_BASE}/devices/`
  return axios.get(url)
}

// 获取设备统计数据
export function getDeviceStatistics() {
  return axios.get(`${API_BASE}/device-stats/`)
}

// ============================================================
// 用电数据API
// ============================================================

// 获取每日用电数据
export function getDailyConsumption(userId = 'REFIT_H1', limit = 30) {
  return axios.get(`${API_BASE}/consumption/daily/?user_id=${userId}&limit=${limit}`)
}

// 获取小时级用电数据
export function getHourlyConsumption(userId = 'REFIT_H1', date = '') {
  const url = date
    ? `${API_BASE}/consumption/hourly/?user_id=${userId}&date=${date}`
    : `${API_BASE}/consumption/hourly/?user_id=${userId}`
  return axios.get(url)
}

// 获取月度用电数据
export function getMonthlyConsumption(userId = 'REFIT_H1') {
  return axios.get(`${API_BASE}/consumption/monthly/?user_id=${userId}`)
}

// ============================================================
// 知识图谱API
// ============================================================

// 获取图谱统计信息
export function getKGGraph() {
  return axios.get(`${API_BASE}/graph/`)
}

// 获取完整图谱数据（用于可视化）
export function getKGFullGraph() {
  return axios.get(`${API_BASE}/graph/full/`)
}

// 导入到Neo4j
export function importToNeo4j() {
  return axios.post(`${API_BASE}/import/`)
}

// ============================================================
// 知识图谱增强型用户画像API
// ============================================================

// 获取用户完整画像（图查询）
export function getUserProfileGraph(userId = '') {
  const url = userId ? `${API_BASE}/profile/graph/?user_id=${userId}` : `${API_BASE}/profile/graph/`
  return axios.get(url)
}

// 获取用户关系网络
export function getUserNetwork(userId = '') {
  const url = userId ? `${API_BASE}/profile/network/?user_id=${userId}` : `${API_BASE}/profile/network/`
  return axios.get(url)
}

// 获取用户用电模式分析
export function getUserPattern(userId = '') {
  const url = userId ? `${API_BASE}/profile/pattern/?user_id=${userId}` : `${API_BASE}/profile/pattern/`
  return axios.get(url)
}

// 获取相似用户及相似原因
export function getProfileSimilarUsers(userId = '') {
  const url = userId ? `${API_BASE}/profile/similar/?user_id=${userId}` : `${API_BASE}/profile/similar/`
  return axios.get(url)
}

// 获取节能建议
export function getSavingTips(userId = '') {
  const url = userId ? `${API_BASE}/profile/saving-tips/?user_id=${userId}` : `${API_BASE}/profile/saving-tips/`
  return axios.get(url)
}

// 获取设备联动分析
export function getDeviceCorrelation(userId = '') {
  const url = userId ? `${API_BASE}/profile/device-correlation/?user_id=${userId}` : `${API_BASE}/profile/device-correlation/`
  return axios.get(url)
}

// ============================================================
// 新增：基于改进FCM和TransE嵌入的用户画像API
// ============================================================

// 获取FCM聚类结果
export function getFCMClusters() {
  return axios.get(`${API_BASE}/fcm-clusters/`)
}

// 获取用户FCM隶属度
export function getUserFCMMembership(userId = '') {
  const url = userId ? `${API_BASE}/fcm-membership/?user_id=${userId}` : `${API_BASE}/fcm-membership/`
  return axios.get(url)
}

// 获取用户图嵌入向量
export function getUserEmbedding(userId = '') {
  const url = userId ? `${API_BASE}/embedding/?user_id=${userId}` : `${API_BASE}/embedding/`
  return axios.get(url)
}

// 获取所有用户嵌入向量
export function getAllEmbeddings() {
  return axios.get(`${API_BASE}/embeddings/all/`)
}

// 获取增强版用户画像
export function getEnhancedProfile(userId = '') {
  const url = userId ? `${API_BASE}/profile/enhanced/?user_id=${userId}` : `${API_BASE}/profile/enhanced/`
  return axios.get(url)
}

// 获取基于图嵌入的用户相似度
export function getEmbeddingSimilarity(userId = '', topN = 5) {
  const url = userId ? `${API_BASE}/profile/embedding-similarity/?user_id=${userId}&top_n=${topN}` : `${API_BASE}/profile/embedding-similarity/`
  return axios.get(url)
}

// 获取气象因素影响分析
export function getWeatherImpact(userId = '') {
  const url = userId ? `${API_BASE}/profile/weather-impact/?user_id=${userId}` : `${API_BASE}/profile/weather-impact/`
  return axios.get(url)
}

// 训练嵌入向量
export function trainEmbeddings(embeddingDim = 32) {
  return axios.post(`${API_BASE}/embeddings/train/`, { embedding_dim: embeddingDim })
}

// ==================== 基于论文的季节性特征API ====================

// 获取用户季节性特征（完整版）
export function getUserSeasonalFeatures(userId = '') {
  const url = userId ? `${API_BASE}/profile/seasonal/?user_id=${userId}` : `${API_BASE}/profile/seasonal/`
  return axios.get(url)
}

// 获取用户季节适应性分析
export function getUserSeasonAdaptation(userId = '') {
  const url = userId ? `${API_BASE}/profile/season-adaptation/?user_id=${userId}` : `${API_BASE}/profile/season-adaptation/`
  return axios.get(url)
}

// 获取用户典型用电日
export function getUserTypicalDays(userId = '', nClusters = 3) {
  const url = userId ? `${API_BASE}/profile/typical-days/?user_id=${userId}&n_clusters=${nClusters}` : `${API_BASE}/profile/typical-days/`
  return axios.get(url)
}

// 获取用户负荷复杂性特征
export function getUserComplexityFeatures(userId = '') {
  const url = userId ? `${API_BASE}/profile/complexity/?user_id=${userId}` : `${API_BASE}/profile/complexity/`
  return axios.get(url)
}
