/**
 * Mock System — 系统月份管理 + 月度推进引擎 (JS 移植)
 */
import { getSeed, setSeed, clone } from './store.js'
import { calcEffectivePower, calcDamageProbability } from './devices.js'

export function mockGetSystemMonth() {
  const seed = getSeed('system')
  const sys = seed?.system || { current_year: 2026, current_month: 1, total_months_elapsed: 0, unit_price: 0.55, is_processing: 0 }
  return {
    status: 200,
    data: {
      current_year: sys.current_year,
      current_month: sys.current_month,
      year_month: `${sys.current_year}-${String(sys.current_month).padStart(2, '0')}`,
      total_months_elapsed: sys.total_months_elapsed,
      unit_price: parseFloat(sys.unit_price),
      is_processing: sys.is_processing
    }
  }
}

export function mockAdvanceMonth() {
  const sysSeed = getSeed('system')
  const sys = sysSeed.system
  const yearMonth = `${sys.current_year}-${String(sys.current_month).padStart(2, '0')}`

  const deviceSeed = getSeed('devices')
  const devices = deviceSeed.devices || []
  const typeSeed = getSeed('device_types')
  const elecSeed = getSeed('electricity_records')

  let recordsCreated = 0

  // 为每台活跃设备生成本月用电记录
  const daysInMonth = new Date(sys.current_year, sys.current_month, 0).getDate()
  for (const dev of devices) {
    if (!dev.is_active) continue
    const dtype = typeSeed.device_types.find(t => t.type_code === dev.type_code)
    if (!dtype) continue

    const ratedPower = dev.rated_power || dtype.default_power
    const usageYears = dev.usage_years
    const lifespan = dtype.expected_lifespan_years
    const agingRate = (dtype.aging_rate || 15) / 100
    const beta = dtype.weibull_beta

    const effPower = calcEffectivePower(ratedPower, usageYears, lifespan, agingRate)
    const dailyHours = dev.daily_usage_hours || dtype.typical_daily_hours || 1
    const monthlyKwh = (effPower * dailyHours * daysInMonth) / 1000

    // 生成用电记录
    const record = {
      record_id: elecSeed.next_record_id++,
      household_id: dev.household_id,
      device_id: dev.device_id,
      year_month: yearMonth,
      total_kwh: Math.round(monthlyKwh * 100) / 100,
      avg_daily_kwh: Math.round(monthlyKwh / daysInMonth * 100) / 100,
      peak_power: effPower,
      hours_used: Math.round(dailyHours * daysInMonth * 10) / 10
    }
    elecSeed.records.push(record)
    recordsCreated++

    // 更新设备状态
    dev.usage_years = Math.round((parseFloat(dev.usage_years) + 1 / 12) * 100) / 100
    dev.effective_power = effPower
    dev.damage_probability = Math.round(calcDamageProbability(dev.usage_years, lifespan, beta, dev.bqf) * 10000) / 10000

    // 损坏检测 (概率 > 0.8 则触发损坏)
    if (dev.damage_probability > 0.8 && !dev.damage_date) {
      dev.is_active = 0
      dev.damage_date = new Date(sys.current_year, sys.current_month - 1, 15).toISOString().slice(0, 10)
    }
  }
  setSeed('electricity_records', elecSeed)

  // 为每个用户生成账单
  const userSeed = getSeed('users')
  const billSeed = getSeed('bills')
  let billsCreated = 0

  const households = [...new Set(devices.map(d => d.household_id))]
  for (const hid of households) {
    const user = userSeed.users.find(u => u.household.household_id === hid)
    if (!user || user.is_staff) continue

    const hRecords = elecSeed.records.filter(r => r.household_id === hid && r.year_month === yearMonth)
    const totalKwh = Math.round(hRecords.reduce((s, r) => s + r.total_kwh, 0) * 100) / 100
    const unitPrice = parseFloat(sys.unit_price)
    const electricityCost = Math.round(totalKwh * unitPrice * 100) / 100

    // 查询本月已完成的维修费用
    const repairSeed = getSeed('repair_orders')
    let repairCost = 0
    const completedRepairs = repairSeed.repair_orders.filter(
      o => o.household_id === hid && o.status === 4 && !o.is_billed
    )
    for (const r of completedRepairs) {
      repairCost += parseFloat(r.repair_cost || 0)
      r.is_billed = 1
    }
    setSeed('repair_orders', repairSeed)

    const totalAmount = electricityCost + repairCost
    const billId = `BILL_${hid}_${yearMonth.replace('-', '')}`

    // 检查连续欠费
    const prevBills = billSeed.bills
      .filter(b => b.household_id === hid)
      .sort((a, b) => b.bill_month.localeCompare(a.bill_month))
    let consecutiveUnpaid = 0
    if (prevBills.length > 0 && prevBills[0].status !== 2) {
      consecutiveUnpaid = (prevBills[0].consecutive_unpaid_months || 0) + 1
    }

    const bill = {
      bill_id: billId,
      household_id: hid,
      bill_month: yearMonth,
      total_kwh: totalKwh,
      electricity_cost: electricityCost,
      unit_price: unitPrice,
      repair_cost: repairCost,
      total_amount: totalAmount,
      paid_amount: 0,
      status: 1,
      consecutive_unpaid_months: consecutiveUnpaid,
      warning_flag: consecutiveUnpaid >= 2 ? 1 : 0,
      due_date: `${sys.current_year}-${String(sys.current_month + 1).padStart(2, '0')}-15`,
      paid_date: null,
      items: [
        { item_type: 1, item_desc: `电费 ${totalKwh} kWh × ¥${unitPrice}`, amount: electricityCost, ref_id: null },
        ...completedRepairs.map(r => ({ item_type: 2, item_desc: '维修费', amount: parseFloat(r.repair_cost || 0), ref_id: r.order_id }))
      ]
    }
    billSeed.bills.push(bill)
    billsCreated++
  }
  setSeed('bills', billSeed)

  // 推进月份
  sys.current_month++
  if (sys.current_month > 12) {
    sys.current_month = 1
    sys.current_year++
  }
  sys.total_months_elapsed++
  sys.is_processing = 0
  setSeed('system', sysSeed)

  return {
    status: 200,
    data: {
      message: '月份推进完成',
      records_created: recordsCreated,
      bills_created: billsCreated,
      new_month: { current_year: sys.current_year, current_month: sys.current_month, total_months_elapsed: sys.total_months_elapsed }
    }
  }
}
