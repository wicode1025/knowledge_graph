/**
 * 数据存储引擎 — 加载种子数据 + 管理 localStorage 读写
 * 替换 Django ORM + MySQL
 */
const SEED_FILES = [
  'users.json',
  'system.json',
  'options.json',
  'device_types.json',
  'devices.json',
  'bills.json',
  'repair_orders.json',
  'announcements.json',
  'messages.json',
  'electricity_records.json'
]

const CACHE_KEY_PREFIX = 'kg_seed_'

// 从 public/data/ 加载种子JSON
async function loadSeedFile(filename) {
  const resp = await fetch(`/data/${filename}`)
  if (!resp.ok) throw new Error(`Failed to load ${filename}: ${resp.status}`)
  return resp.json()
}

// 初始化：加载所有种子数据到 localStorage（幂等调用）
export async function initStore(force = false) {
  for (const file of SEED_FILES) {
    const key = CACHE_KEY_PREFIX + file.replace('.json', '')
    if (!force && localStorage.getItem(key)) continue
    try {
      const data = await loadSeedFile(file)
      localStorage.setItem(key, JSON.stringify(data))
    } catch (e) {
      console.error(`[store] load failed: ${file}`, e)
    }
  }
  if (!localStorage.getItem('kg_user_writes')) {
    localStorage.setItem('kg_user_writes', JSON.stringify({}))
  }
}

// 读取种子数据
export function getSeed(key) {
  try {
    const raw = localStorage.getItem(CACHE_KEY_PREFIX + key)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

// 写入种子数据 (用于更新种子，如月度推进后)
export function setSeed(key, data) {
  localStorage.setItem(CACHE_KEY_PREFIX + key, JSON.stringify(data))
}

// 读取用户写入层
export function getUserWrites(userId) {
  try {
    const raw = localStorage.getItem('kg_user_writes')
    const all = raw ? JSON.parse(raw) : {}
    if (userId) return all[userId] || {}
    return all
  } catch {
    return {}
  }
}

// 写入用户写入层
export function setUserWrites(userId, writes) {
  const all = getUserWrites()
  all[userId] = writes
  localStorage.setItem('kg_user_writes', JSON.stringify(all))
}

// 合并种子数据和用户写入 (种子为基础，用户写入覆盖)
export function getMergedData(seed, userId) {
  const writes = getUserWrites(userId)
  return { ...seed, ...writes }
}

// 获取当前登录用户
export function getCurrentUser() {
  try {
    const raw = localStorage.getItem('user')
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

// 获取当前用户 household_id
export function getCurrentUserId() {
  return localStorage.getItem('elec_user_id')
}

// 检查是否管理员
export function isAdmin() {
  return localStorage.getItem('role') === 'admin'
}

// 生成ID
export function genId(prefix, existingIds) {
  let seq = 1
  while (existingIds.includes(`${prefix}_${String(seq).padStart(4, '0')}`)) {
    seq++
  }
  return `${prefix}_${String(seq).padStart(4, '0')}`
}

// 深拷贝
export function clone(obj) {
  return JSON.parse(JSON.stringify(obj))
}
