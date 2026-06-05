/**
 * Mock Billing — 账单列表、缴费、通知
 */
import { getSeed, setSeed, getCurrentUserId, clone } from './store.js'

export function mockGetMyBills() {
  const uid = getCurrentUserId()
  const seed = getSeed('bills')
  const bills = (seed?.bills || [])
    .filter(b => b.household_id === uid)
    .sort((a, b) => b.bill_month.localeCompare(a.bill_month))
    .map(b => ({
      ...clone(b),
      items: b.items || [],
      total_kwh: parseFloat(b.total_kwh),
      electricity_cost: parseFloat(b.electricity_cost),
      total_amount: parseFloat(b.total_amount),
      repair_cost: parseFloat(b.repair_cost || 0),
      status_text: b.status === 2 ? '已缴' : '未缴'
    }))
  return { status: 200, data: { bills } }
}

export function mockGetCurrentBill() {
  const uid = getCurrentUserId()
  const seed = getSeed('bills')
  const bills = (seed?.bills || [])
    .filter(b => b.household_id === uid)
    .sort((a, b) => b.bill_month.localeCompare(a.bill_month))
  const latest = bills[0]
  if (!latest) return { status: 200, data: { bill: null } }
  return {
    status: 200,
    data: {
      bill: {
        ...clone(latest),
        items: latest.items || [],
        total_kwh: parseFloat(latest.total_kwh),
        electricity_cost: parseFloat(latest.electricity_cost),
        total_amount: parseFloat(latest.total_amount),
        repair_cost: parseFloat(latest.repair_cost || 0),
        status_text: latest.status === 2 ? '已缴' : '未缴'
      }
    }
  }
}

export function mockPayBill(billId) {
  const uid = getCurrentUserId()
  const seed = getSeed('bills')
  const bill = seed.bills.find(b => b.bill_id === billId && b.household_id === uid)
  if (!bill) return { status: 404, data: { error: '账单不存在' } }
  if (bill.status === 2) return { status: 400, data: { error: '该账单已缴费' } }

  bill.status = 2
  bill.paid_date = new Date().toISOString().slice(0, 10)
  bill.paid_amount = bill.total_amount
  bill.warning_flag = 0
  bill.consecutive_unpaid_months = 0
  setSeed('bills', seed)
  return { status: 200, data: { message: '缴费成功' } }
}

export function mockGetNotices() {
  const uid = getCurrentUserId()
  const seed = getSeed('bills')
  const bills = (seed?.bills || [])
    .filter(b => b.household_id === uid)
    .sort((a, b) => b.bill_month.localeCompare(a.bill_month))

  const notices = bills.map((b, i) => ({
    id: 1000 + i,
    title: `${b.bill_month} 电费账单`,
    content: b.warning_flag
      ? `您${b.bill_month}月份电费账单¥${b.total_amount}已逾期，请尽快缴费，以免影响信用。`
      : `您${b.bill_month}月份电费账单已生成，应缴¥${b.total_amount}（电费¥${b.electricity_cost}${b.repair_cost > 0 ? ' + 维修费¥' + b.repair_cost : ''}），请于${b.due_date}前完成缴费。`,
    is_read: b.status === 2 ? 1 : 0,
    is_pinned: b.warning_flag ? 1 : 0,
    bill_month: b.bill_month,
    created_at: b.bill_month + '-01T00:00:00'
  }))
  return { status: 200, data: { notices } }
}
