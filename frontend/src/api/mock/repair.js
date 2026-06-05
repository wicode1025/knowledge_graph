/**
 * Mock Repair — 维修报单
 */
import { getSeed, setSeed, getCurrentUserId, clone, genId } from './store.js'

export function mockGetRepairOrders() {
  const uid = getCurrentUserId()
  const seed = getSeed('repair_orders')
  const orders = (seed?.repair_orders || [])
    .filter(o => o.household_id === uid)
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .map(o => ({
      ...clone(o),
      status_text: { 1: '待处理', 2: '已派单', 3: '维修中', 4: '已完成', 5: '已取消' }[o.status] || '未知'
    }))
  return { status: 200, data: { orders } }
}

export function mockCreateRepairOrder(data) {
  const uid = getCurrentUserId()
  const seed = getSeed('repair_orders')
  const existingIds = (seed.repair_orders || []).map(o => o.order_id)
  const orderId = genId(`REP_${uid}`, existingIds)

  const order = {
    order_id: orderId,
    household_id: uid,
    device_id: data.device_id,
    fault_type: data.fault_type,
    fault_description: data.fault_description,
    contact_name: data.contact_name || '',
    contact_phone: data.contact_phone || '',
    appointment_date: data.appointment_date || null,
    appointment_time: data.appointment_time || null,
    status: 1,
    repair_result: null,
    repair_cost: null,
    technician_name: null,
    completed_date: null,
    rating: null,
    is_billed: 0,
    created_at: new Date().toISOString()
  }
  seed.repair_orders.push(order)
  setSeed('repair_orders', seed)
  return { status: 201, data: { order_id: orderId, message: '报修成功' } }
}

export function mockRateRepair(orderId, data) {
  const uid = getCurrentUserId()
  const seed = getSeed('repair_orders')
  const order = seed.repair_orders.find(o => o.order_id === orderId && o.household_id === uid)
  if (!order) return { status: 404, data: { error: '工单不存在' } }
  order.rating = data.rating
  setSeed('repair_orders', seed)
  return { status: 200, data: { message: '评价成功' } }
}
