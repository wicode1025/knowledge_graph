/**
 * Mock Router — 请求分发器
 * 根据 URL path 和 HTTP method 将拦截的 API 请求路由到对应 mock 函数
 */
import { initStore } from './store.js'
import { mockLogin, mockRegister, mockLogout, mockVerify } from './auth.js'
import * as household from './household.js'
import * as devices from './devices.js'
import * as billing from './billing.js'
import * as repair from './repair.js'
import * as system from './system.js'
import * as admin from './admin.js'
import * as graph from './graph.js'

const API_PREFIX = '/api/kg'

function parseBody(data) {
  if (typeof data === 'string') {
    try { return JSON.parse(data) } catch { return {} }
  }
  return data || {}
}

/**
 * 核心分发函数 — 匹配 URL 和 method，调用对应 mock 函数
 */
export async function mockDispatch(method, url, body, params) {
  await initStore()
  const data = parseBody(body)
  const path = url.replace(API_PREFIX, '')

  // ============ AUTH ============
  if (path === '/auth/login/' && method === 'post') return mockLogin(data)
  if (path === '/auth/register/' && method === 'post') return mockRegister(data)
  if (path === '/auth/logout/' && method === 'post') return mockLogout()
  if (path === '/auth/verify/' && method === 'get') return mockVerify()

  // ============ SYSTEM ============
  if (path === '/system/month/' && method === 'get') return system.mockGetSystemMonth()
  if (path === '/system/month/advance/' && method === 'post') return system.mockAdvanceMonth()

  // ============ HOUSEHOLD ============
  if (path === '/household/mine/' && method === 'get') return household.mockGetMyHousehold()
  if (path === '/household/mine/update/' && method === 'put') return household.mockUpdateHousehold(data)
  if (path === '/household/housing/update/' && method === 'put') return household.mockUpdateHousing(data)
  if (path === '/household/income/update/' && method === 'put') return household.mockUpdateIncome(data)
  if (path === '/household/members/' && method === 'get') return household.mockGetMembers()
  if (path === '/household/members/' && method === 'post') return household.mockAddMember(data)

  // 家庭成员 CRUD (带 ID)
  const memberMatch = path.match(/^\/household\/members\/(\d+)\/$/)
  if (memberMatch) {
    const memberId = memberMatch[1]
    if (method === 'put') return household.mockUpdateMember(memberId, data)
    if (method === 'delete') return household.mockDeleteMember(memberId)
  }

  // ============ OPTIONS ============
  if (path === '/options/' && method === 'get') return household.mockGetOptions()
  if (path === '/announcements/' && method === 'get') return household.mockGetAnnouncements()
  if (path === '/messages/' && method === 'get') return household.mockGetMessages()
  if (path === '/messages/' && method === 'post') return household.mockSendMessage(data)

  const msgWithdrawMatch = path.match(/^\/messages\/(\d+)\/withdraw\/$/)
  if (msgWithdrawMatch && method === 'delete') return household.mockWithdrawMessage(msgWithdrawMatch[1])

  // ============ DEVICES ============
  if (path === '/device-types/' && method === 'get') return devices.mockGetDeviceTypes()
  const dtMatch = path.match(/^\/device-types\/([^/]+)\/$/)
  if (dtMatch && method === 'get') return devices.mockGetDeviceTypeDetail(dtMatch[1])

  if (path === '/devices/' && method === 'get') {
    // admin sees all devices, users see only their own
    const role = (() => { try { return localStorage.getItem('role') } catch { return 'user' } })()
    if (role === 'admin') return devices.mockGetAllDevices()
    return devices.mockGetMyDevices()
  }
  if (path === '/devices/' && method === 'post') return devices.mockAddDevice(data)

  const devMatch = path.match(/^\/devices\/([^/]+)\/$/)
  if (devMatch) {
    const devId = devMatch[1]
    if (method === 'delete') return devices.mockDeleteDevice(devId)
  }
  const devHistMatch = path.match(/^\/devices\/([^/]+)\/history\/$/)
  if (devHistMatch && method === 'get') return devices.mockGetDeviceHistory(devHistMatch[1])

  // ============ CONSUMPTION ============
  if (path === '/consumption/monthly/' && method === 'get') {
    const { getSeed, getCurrentUserId: uid } = await import('./store.js')
    const elecSeed = getSeed('electricity_records')
    const deviceSeed = getSeed('devices')
    const typeSeed = getSeed('device_types')
    const helpId = uid()
    const allRecords = (elecSeed?.records || []).filter(r => r.household_id === helpId)
    const hDevices = (deviceSeed?.devices || []).filter(d => d.household_id === helpId)
    const monthlyData = {}
    for (const r of allRecords) {
      if (!monthlyData[r.year_month]) {
        monthlyData[r.year_month] = { year_month: r.year_month, total_kwh: 0, devices: [] }
      }
      const dev = hDevices.find(d => d.device_id === r.device_id)
      const dtype = typeSeed?.device_types?.find(t => t.type_code === dev?.type_code)
      monthlyData[r.year_month].total_kwh = Math.round((monthlyData[r.year_month].total_kwh + r.total_kwh) * 100) / 100
      monthlyData[r.year_month].devices.push({
        device_id: r.device_id,
        device_name: dev?.custom_name || dtype?.device_name || r.device_id,
        kwh: r.total_kwh
      })
    }
    return { status: 200, data: { status: 'success', data: Object.values(monthlyData) } }
  }
  if (path === '/consumption/summary/' && method === 'get') {
    // 从用电记录生成摘要
    const { getSeed, getCurrentUserId } = await import('./store.js')
    const uid = getCurrentUserId()
    const elecSeed = getSeed('electricity_records')
    const deviceSeed = getSeed('devices')
    const typeSeed = getSeed('device_types')
    const records = (elecSeed?.records || []).filter(r => r.household_id === uid)
    const devices = (deviceSeed?.devices || []).filter(d => d.household_id === uid)

    const sysSeed = getSeed('system')
    const yearMonth = sysSeed?.system?.year_month || '2026-01'
    const monthRecords = records.filter(r => r.year_month === yearMonth)
    const totalKwh = Math.round(monthRecords.reduce((s, r) => s + r.total_kwh, 0) * 100) / 100

    const breakdown = []
    for (const d of devices) {
      const drec = monthRecords.find(r => r.device_id === d.device_id)
      if (drec) {
        const dtype = typeSeed?.device_types?.find(t => t.type_code === d.type_code)
        breakdown.push({
          device_id: d.device_id,
          device_name: d.custom_name || dtype?.device_name || d.type_code,
          category: dtype?.category || '',
          kwh: drec.total_kwh,
          percentage: totalKwh > 0 ? Math.round(drec.total_kwh / totalKwh * 10000) / 100 : 0
        })
      }
    }
    return { status: 200, data: { total_kwh: totalKwh, device_count: devices.length, breakdown, month: yearMonth } }
  }
  if (path === '/consumption/trends/' && method === 'get') {
    const { getSeed, getCurrentUserId } = await import('./store.js')
    const uid = getCurrentUserId()
    const elecSeed = getSeed('electricity_records')
    const records = (elecSeed?.records || []).filter(r => r.household_id === uid)
    const monthly = {}
    for (const r of records) {
      monthly[r.year_month] = (monthly[r.year_month] || 0) + r.total_kwh
    }
    const months = Object.keys(monthly).sort()
    const recent = months.slice(-12)
    const values = recent.map(m => Math.round(monthly[m] * 100) / 100)
    return { status: 200, data: { months: recent, values } }
  }

  // ============ BILLING ============
  if (path === '/bills/' && method === 'get') return billing.mockGetMyBills()
  if (path === '/bills/current/' && method === 'get') return billing.mockGetCurrentBill()

  const billMatch = path.match(/^\/bills\/([^/]+)\/$/)
  const billPayMatch = path.match(/^\/bills\/([^/]+)\/pay\/$/)
  if (billPayMatch && method === 'post') return billing.mockPayBill(billPayMatch[1])
  if (billMatch && method === 'get') return billing.mockGetCurrentBill() // 简化：返回最新账单

  if (path === '/notices/' && method === 'get') return billing.mockGetNotices()

  // ============ REPAIR ============
  if (path === '/repairs/' && method === 'get') return repair.mockGetRepairOrders()
  if (path === '/repairs/' && method === 'post') return repair.mockCreateRepairOrder(data)

  const repairRateMatch = path.match(/^\/repairs\/([^/]+)\/rate\/$/)
  if (repairRateMatch && method === 'post') return repair.mockRateRepair(repairRateMatch[1], data)

  // ============ GRAPH ============
  if (path === '/graph/full/' && method === 'get') return graph.mockGetFullGraph()
  if (path === '/graph/user/' && method === 'get') {
    const hid = params?.household_id || null
    return graph.mockGetUserKG(hid)
  }
  if (path === '/graph/sync/' && method === 'post') return graph.mockSyncGraph()

  // ============ CLUSTERING / PROFILE ============
  if (path === '/clusters/' && method === 'get') {
    return { status: 200, data: { current_month: new Date().toISOString().slice(0, 7), total_households: 3 } }
  }
  if (path === '/profile/enhanced/' && method === 'get') {
    const { getSeed, getCurrentUserId } = await import('./store.js')
    const uid = getCurrentUserId()
    const elecSeed = getSeed('electricity_records')
    const records = (elecSeed?.records || []).filter(r => r.household_id === uid)
    const monthly = {}
    for (const r of records) { monthly[r.year_month] = (monthly[r.year_month] || 0) + r.total_kwh }
    const vals = Object.values(monthly)
    const avgKwh = vals.length > 0 ? Math.round(vals.reduce((s, v) => s + v, 0) / vals.length * 100) / 100 : 0
    let energyLevel = '普通型'
    if (avgKwh <= 100) energyLevel = '节能型'
    else if (avgKwh > 500) energyLevel = '高耗能型'
    const months = Object.keys(monthly).sort().slice(-6)
    const trendValues = months.map(m => Math.round(monthly[m] * 100) / 100)
    return { status: 200, data: { energy_level: energyLevel, avg_monthly_kwh: avgKwh, device_count: 0, monthly_trend: { months, values: trendValues } } }
  }

  // ============ ADMIN ============
  if (path === '/admin/stats/' && method === 'get') return admin.mockGetAdminStats()
  if (path === '/admin/users/' && method === 'get') return admin.mockGetAdminUsers()
  if (path === '/admin/users/create/' && method === 'post') return admin.mockAdminCreateUser(data)

  const adminUserMatch = path.match(/^\/admin\/users\/([^/]+)\/$/)
  const adminUserEditMatch = path.match(/^\/admin\/users\/([^/]+)\/edit\/$/)
  const adminUserDeleteMatch = path.match(/^\/admin\/users\/([^/]+)\/delete\/$/)
  if (adminUserEditMatch && method === 'put') return admin.mockAdminEditUser(adminUserEditMatch[1], data)
  if (adminUserDeleteMatch && method === 'delete') return admin.mockAdminDeleteUser(adminUserDeleteMatch[1])
  if (adminUserMatch && method === 'get') return admin.mockAdminGetUserDetail(adminUserMatch[1])

  if (path === '/admin/repair-orders/' && method === 'get') return admin.mockGetAdminRepairOrders()

  const assignMatch = path.match(/^\/admin\/repair-orders\/([^/]+)\/assign\/$/)
  if (assignMatch && method === 'post') return admin.mockAssignRepair(assignMatch[1], data)
  const completeMatch = path.match(/^\/admin\/repair-orders\/([^/]+)\/complete\/$/)
  if (completeMatch && method === 'post') return admin.mockCompleteRepair(completeMatch[1], data)

  if (path === '/admin/announcements/' && method === 'get') return admin.mockGetAdminAnnouncements()
  if (path === '/admin/announcements/' && method === 'post') return admin.mockCreateAnnouncement(data)

  const annDeleteMatch = path.match(/^\/admin\/announcements\/(\d+)\/$/)
  if (annDeleteMatch && method === 'delete') return admin.mockDeleteAnnouncement(annDeleteMatch[1])

  if (path === '/admin/messages/' && method === 'get') return admin.mockGetAdminMessages()

  const replyMatch = path.match(/^\/admin\/messages\/(\d+)\/reply\/$/)
  if (replyMatch && method === 'post') return admin.mockReplyMessage(replyMatch[1], data)
  const delMsgMatch = path.match(/^\/admin\/messages\/(\d+)\/delete\/$/)
  if (delMsgMatch && method === 'delete') return admin.mockDeleteMessage(delMsgMatch[1])

  // ============ FALLBACK ============
  console.warn(`[mock] Unmatched: ${method.toUpperCase()} ${path}`)
  return { status: 404, data: { error: `Mock not found: ${method.toUpperCase()} ${path}` } }
}
