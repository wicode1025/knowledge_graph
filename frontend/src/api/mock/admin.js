/**
 * Mock Admin — 管理员统计、用户管理、维修审核、公告和留言管理
 */
import { getSeed, setSeed, clone, genId, isAdmin } from './store.js'

function checkAdmin() {
  if (!isAdmin()) return { status: 403, data: { error: '需要管理员权限' } }
  return null
}

export function mockGetAdminStats() {
  const err = checkAdmin(); if (err) return err
  const userSeed = getSeed('users')
  const deviceSeed = getSeed('devices')
  const billSeed = getSeed('bills')
  const repairSeed = getSeed('repair_orders')
  const sysSeed = getSeed('system')

  const users = (userSeed?.users || []).filter(u => !u.is_staff)
  const devices = deviceSeed?.devices || []
  const bills = billSeed?.bills || []
  const repairs = repairSeed?.repair_orders || []

  return {
    status: 200,
    data: {
      stats: {
        total_users: users.length,
        total_devices: devices.length,
        active_devices: devices.filter(d => d.is_active).length,
        damaged_devices: devices.filter(d => !d.is_active).length,
        bills_collected: `${bills.filter(b => b.status === 2).length}/${bills.length}`,
        total_months_elapsed: sysSeed?.system?.total_months_elapsed || 0,
        pending_repairs: repairs.filter(r => r.status === 1).length,
        unit_price: parseFloat(sysSeed?.system?.unit_price || 0.55)
      }
    }
  }
}

export function mockGetAdminUsers() {
  const err = checkAdmin(); if (err) return err
  const userSeed = getSeed('users')
  const deviceSeed = getSeed('devices')
  const users = (userSeed?.users || []).filter(u => !u.is_staff).map(u => {
    const deviceCount = deviceSeed.devices.filter(d => d.household_id === u.household.household_id).length
    return {
      household_id: u.household.household_id,
      real_name: u.household.real_name,
      username: u.username,
      gender: u.household.gender,
      phone: u.household.phone,
      address_detail: u.household.address_detail,
      device_count: deviceCount
    }
  })
  return { status: 200, data: { users } }
}

export function mockAdminCreateUser(data) {
  const err = checkAdmin(); if (err) return err
  const userSeed = getSeed('users')
  if (userSeed.users.find(u => u.username === data.username)) {
    return { status: 400, data: { error: '用户名已存在' } }
  }
  const newId = userSeed.users.length + 1
  const householdId = `H${String(newId).padStart(4, '0')}`
  userSeed.users.push({
    id: newId, username: data.username, password: data.password || '123456',
    email: data.email || '', is_staff: false,
    household: { household_id: householdId, real_name: data.real_name || data.username, gender: null, phone: data.phone || null },
    housing: {}, income: {}, family_members: []
  })
  setSeed('users', userSeed)
  return { status: 201, data: { household_id: householdId, message: '用户创建成功' } }
}

export function mockAdminGetUserDetail(householdId) {
  const err = checkAdmin(); if (err) return err
  const userSeed = getSeed('users')
  const user = userSeed?.users?.find(u => u.household.household_id === householdId && !u.is_staff)
  if (!user) return { status: 404, data: { error: '用户不存在' } }

  const deviceSeed = getSeed('devices')
  const billSeed = getSeed('bills')
  const repairSeed = getSeed('repair_orders')
  const elecSeed = getSeed('electricity_records')

  const devices = deviceSeed.devices.filter(d => d.household_id === householdId)
  const bills = billSeed.bills.filter(b => b.household_id === householdId).sort((a, b) => b.bill_month.localeCompare(a.bill_month))
  const repairs = repairSeed.repair_orders.filter(r => r.household_id === householdId)
  const records = elecSeed.records.filter(r => r.household_id === householdId)

  return {
    status: 200,
    data: {
      household: clone(user.household),
      housing: clone(user.housing || {}),
      income: clone(user.income || {}),
      family_members: clone(user.family_members || []),
      devices: clone(devices.slice(0, 12)),
      bills: clone(bills.slice(0, 12)),
      repairs: clone(repairs.slice(0, 5)),
      electricity_records: clone(records.slice(0, 24)),
      username: user.username,
      device_count: devices.length,
      bill_count: bills.length,
      total_paid: Math.round(bills.filter(b => b.status === 2).reduce((s, b) => s + parseFloat(b.total_amount), 0) * 100) / 100
    }
  }
}

export function mockAdminEditUser(householdId, data) {
  const err = checkAdmin(); if (err) return err
  const userSeed = getSeed('users')
  const user = userSeed?.users?.find(u => u.household.household_id === householdId)
  if (!user) return { status: 404, data: { error: '用户不存在' } }
  Object.assign(user.household, data)
  setSeed('users', userSeed)
  return { status: 200, data: { message: '用户信息更新成功' } }
}

export function mockAdminDeleteUser(householdId) {
  const err = checkAdmin(); if (err) return err
  const userSeed = getSeed('users')
  const idx = userSeed.users.findIndex(u => u.household.household_id === householdId && !u.is_staff)
  if (idx === -1) return { status: 404, data: { error: '用户不存在' } }
  userSeed.users.splice(idx, 1)
  // 同时删除关联数据
  const deviceSeed = getSeed('devices')
  deviceSeed.devices = deviceSeed.devices.filter(d => d.household_id !== householdId)
  setSeed('devices', deviceSeed)
  const billSeed = getSeed('bills')
  billSeed.bills = billSeed.bills.filter(b => b.household_id !== householdId)
  setSeed('bills', billSeed)
  setSeed('users', userSeed)
  return { status: 200, data: { message: '用户已删除' } }
}

export function mockGetAdminRepairOrders() {
  const err = checkAdmin(); if (err) return err
  const seed = getSeed('repair_orders')
  const orders = (seed?.repair_orders || [])
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .map(o => ({ ...clone(o), status_text: { 1: '待处理', 2: '已派单', 3: '维修中', 4: '已完成', 5: '已取消' }[o.status] || '未知' }))
  return { status: 200, data: { orders } }
}

export function mockAssignRepair(orderId, data) {
  const err = checkAdmin(); if (err) return err
  const seed = getSeed('repair_orders')
  const order = seed.repair_orders.find(o => o.order_id === orderId)
  if (!order) return { status: 404, data: { error: '工单不存在' } }
  order.technician_name = data.technician_name
  order.status = 2
  setSeed('repair_orders', seed)
  return { status: 200, data: { message: '派单成功' } }
}

export function mockCompleteRepair(orderId, data) {
  const err = checkAdmin(); if (err) return err
  const seed = getSeed('repair_orders')
  const order = seed.repair_orders.find(o => o.order_id === orderId)
  if (!order) return { status: 404, data: { error: '工单不存在' } }
  order.repair_result = data.repair_result
  order.repair_cost = parseFloat(data.repair_cost) || 0
  order.completed_date = new Date().toISOString().slice(0, 10)
  order.status = 4
  setSeed('repair_orders', seed)
  return { status: 200, data: { message: '维修已完成，费用将计入下月账单' } }
}

// ============ 公告管理 ============

export function mockGetAdminAnnouncements() {
  const err = checkAdmin(); if (err) return err
  const seed = getSeed('announcements')
  return { status: 200, data: { announcements: clone(seed?.announcements || []) } }
}

export function mockCreateAnnouncement(data) {
  const err = checkAdmin(); if (err) return err
  const seed = getSeed('announcements')
  const ann = {
    id: seed.next_id++,
    title: data.title,
    content: data.content,
    is_pinned: data.is_pinned || 0,
    is_active: 1,
    created_at: new Date().toISOString()
  }
  seed.announcements.push(ann)
  setSeed('announcements', seed)
  return { status: 201, data: { id: ann.id, message: '公告发布成功' } }
}

export function mockDeleteAnnouncement(id) {
  const err = checkAdmin(); if (err) return err
  const seed = getSeed('announcements')
  seed.announcements = seed.announcements.filter(a => a.id !== parseInt(id))
  setSeed('announcements', seed)
  return { status: 200, data: { message: '公告已删除' } }
}

// ============ 留言管理 ============

export function mockGetAdminMessages() {
  const err = checkAdmin(); if (err) return err
  const seed = getSeed('messages')
  const userSeed = getSeed('users')
  const msg = (seed?.messages || [])
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 50)
    .map(m => {
      const user = userSeed?.users?.find(u => u.household.household_id === m.household_id)
      return { ...m, household_name: user?.household?.real_name || m.household_id }
    })
  return { status: 200, data: { messages: msg } }
}

export function mockReplyMessage(id, data) {
  const err = checkAdmin(); if (err) return err
  const seed = getSeed('messages')
  const msg = seed.messages.find(m => m.id === parseInt(id))
  if (!msg) return { status: 404, data: { error: '留言不存在' } }
  msg.reply = data.reply
  msg.replied_at = new Date().toISOString()
  msg.is_read = 1
  setSeed('messages', seed)
  return { status: 200, data: { message: '回复成功' } }
}

export function mockDeleteMessage(id) {
  const err = checkAdmin(); if (err) return err
  const seed = getSeed('messages')
  seed.messages = seed.messages.filter(m => m.id !== parseInt(id))
  setSeed('messages', seed)
  return { status: 200, data: { message: '留言已删除' } }
}
