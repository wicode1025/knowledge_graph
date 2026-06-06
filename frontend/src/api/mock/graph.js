/**
 * Mock Knowledge Graph — 用户中心图谱 + 全量图谱
 * 完全匹配 Django kg/views/neo4j_kg.py 的 JSON 格式
 */
import { getSeed, getCurrentUserId, isAdmin } from './store.js'

// 颜色常量
const deviceColors = { '空气调节': '#5470c6', '厨房电器': '#fac858', '清洁卫生': '#91cc75', '娱乐影音': '#ee6666', '照明设备': '#73c0de', '其他设备': '#fc8452' }
const energyColors = { '节能型': '#67c23a', '普通型': '#5470c6', '摆渡型': '#e6a23c', '高耗能型': '#e74c3c' }

function optLabel(cat, val) {
  if (val === null || val === undefined || val === '') return '--'
  const opts = getSeed('options')
  const items = opts?.options?.[cat] || []
  const found = items.find(o => String(o.item_key) === String(val))
  return found ? found.item_value : String(val)
}

function calcDamagePred(dev, dtype) {
  const prob = parseFloat(dev.damage_probability || 0)
  const years = parseFloat(dev.usage_years || 0)
  const lifespan = dtype?.expected_lifespan_years || 10
  const beta = dtype?.weibull_beta || 2.5
  const bqf = parseFloat(dev.bqf || 1.0)
  const eta = lifespan * 1.2 * bqf
  const next1 = 1 - Math.exp(-Math.pow((years + 1) / eta, beta))
  const next2 = 1 - Math.exp(-Math.pow((years + 2) / eta, beta))
  const remain = Math.max(0, Math.round((lifespan - years) * 10) / 10)
  const est_damage_year = Math.round(lifespan * 1.2 * bqf * Math.pow(-Math.log(1 - 0.8), 1 / beta) * 10) / 10
  return { now: prob, next1: Math.round(next1 * 1000) / 1000, next2: Math.round(next2 * 1000) / 1000, lifespan, remain, est_damage_year }
}

function calcStd(values) {
  if (!values || values.length === 0) return 0
  const avg = values.reduce((s, v) => s + v, 0) / values.length
  const variance = values.reduce((s, v) => s + (v - avg) ** 2, 0) / values.length
  return Math.round(Math.sqrt(variance) * 100) / 100
}

// ============ 用户中心图谱 ============
export function mockGetUserKG(overrideUid) {
  const uid = overrideUid || getCurrentUserId()
  const userSeed = getSeed('users')
  const deviceSeed = getSeed('devices')
  const billSeed = getSeed('bills')
  const typeSeed = getSeed('device_types')
  const elecSeed = getSeed('electricity_records')

  const user = userSeed?.users?.find(u => u.household.household_id === uid)
  if (!user) return { status: 404, data: { error: '用户不存在' } }

  const hid = uid
  const household = user.household
  const hDevices = (deviceSeed?.devices || []).filter(d => d.household_id === uid)
  const allBills = (billSeed?.bills || []).filter(b => b.household_id === uid).sort((a, b) => b.bill_month.localeCompare(a.bill_month))
  const bills = allBills.slice(0, 6)
  const records = (elecSeed?.records || []).filter(r => r.household_id === uid)
  const housing = user.housing || null
  const income = user.income || null
  const familyMembers = user.family_members || []

  // 月度用电汇总
  const ymTotals = {}
  for (const r of records) {
    ymTotals[r.year_month] = (ymTotals[r.year_month] || 0) + r.total_kwh
  }
  const sortedMonths = Object.keys(ymTotals).sort()
  const months = sortedMonths.slice(-12)
  const totalKwh = Object.values(ymTotals).reduce((s, v) => s + v, 0)
  const avgKwh = months.length > 0 ? Math.round(totalKwh / months.length * 100) / 100 : 0
  const monthlyTrend = months.map(m => ({ month: m, kwh: Math.round((ymTotals[m] || 0) * 100) / 100 }))

  // 能耗等级
  let elLv = '普通型'
  if (avgKwh <= 100) elLv = '节能型'
  else if (avgKwh > 500) elLv = '高耗能型'
  const elColor = energyColors[elLv] || '#999'

  const activeDevices = hDevices.filter(d => d.is_active)
  const damagedDevices = hDevices.filter(d => !d.is_active && d.damage_date)
  const deviceCount = hDevices.length
  const activeCount = activeDevices.length
  const damagedCount = damagedDevices.length

  const totalBills = allBills.length
  const paidCount = allBills.filter(b => b.status === 2).length

  const nodes = []
  const links = []

  // 设备饼图数据
  const catKwhMap = {}
  const devicePie = []
  for (const d of hDevices) {
    const dtype = typeSeed?.device_types?.find(t => t.type_code === d.type_code)
    const cat = dtype?.category || '其他'
    const drecs = records.filter(r => r.device_id === d.device_id)
    const dkwh = drecs.reduce((s, r) => s + r.total_kwh, 0)
    catKwhMap[cat] = (catKwhMap[cat] || 0) + dkwh
  }
  for (const [cat, kwh] of Object.entries(catKwhMap)) {
    if (kwh > 0) devicePie.push({ name: cat, value: Math.round(kwh * 100) / 100 })
  }

  // 高风险设备
  const highRisk = hDevices
    .filter(d => parseFloat(d.damage_probability) > 0.3)
    .sort((a, b) => parseFloat(b.damage_probability) - parseFloat(a.damage_probability))
    .slice(0, 5)

  // 账单趋势
  const recentBills = allBills.slice(0, 6).reverse()
  const billTrend = recentBills.map(b => ({
    month: b.bill_month,
    kwh: parseFloat(b.total_kwh || 0),
    cost: parseFloat(b.total_amount || 0),
    status: b.status === 2 ? '已缴' : '未缴'
  }))

  // === 用户中心节点 ===
  const userInfo = {
    gender: optLabel('gender', household.gender),
    birth: household.birth_year ? `${household.birth_year}年${household.birth_month || ''}月` : '--',
    education: optLabel('education', household.education_level),
    marital: optLabel('marital', household.marital_status),
    occupation: optLabel('occupation', household.occupation),
    urban: optLabel('urban', household.is_urban),
    schedule: optLabel('schedule', household.daily_schedule),
    health: optLabel('health', household.self_health),
    political: optLabel('political', household.political_status),
    religion: optLabel('religion', household.religion),
    phone: household.phone || '--',
    work_unit: household.work_unit || '--',
    address: household.address_detail || '--',
  }

  nodes.push({
    id: hid, name: household.real_name, category: 'user',
    symbolSize: 70, group: 'center',
    itemStyle: { color: '#3b82f6' },
    detail: {
      type: 'user', name: household.real_name,
      info: userInfo,
      energy: { level: elLv, avg_kwh: avgKwh, color: elColor },
      trend: monthlyTrend,
      housing: housing ? {
        type: optLabel('housing_type', housing.housing_type),
        area: parseFloat(housing.housing_area) || null,
        bedroom: housing.bedroom_count || 0,
        living: housing.living_room_count || 0,
        kitchen: housing.kitchen_count || 0,
        bathroom: housing.bathroom_count || 0,
        floor: housing.floor_level || null,
        total_floors: housing.total_floors || null,
        elevator: housing.has_elevator || 0,
        heating: optLabel('heating', housing.heating_type),
        orientation: optLabel('orientation', housing.orientation),
        building_age: housing.building_age || null,
      } : null,
      income: income ? {
        personal: parseFloat(income.personal_income) || null,
        household: parseFloat(income.household_income) || null,
        source: optLabel('income_source', income.income_source),
        self_rating: income.self_evaluated_wealth || null,
      } : null,
      members: familyMembers.map(m => ({
        name: m.name,
        relation: { 2: '配偶', 3: '子女', 4: '父母', 5: '岳父母/公婆', 6: '兄弟姐妹', 7: '其他' }[m.relation] || '',
        cohabit: m.is_cohabit
      })),
      stats: { devices: deviceCount, active: activeCount, damaged: damagedCount, bills: totalBills, paid: paidCount },
    },
  })

  // === L1: 设备管理大类 ===
  const cdId = `${hid}_devices`
  nodes.push({
    id: cdId, name: `设备管理 (${deviceCount}台)`, category: 'category',
    symbolSize: 56, group: 'category',
    itemStyle: { color: '#ebf0f5', borderColor: '#c8d6e5', borderWidth: 2, borderRadius: 8 },
    detail: {
      type: 'category', subtype: 'devices', name: '设备管理',
      total: deviceCount, active: activeCount, damaged: damagedCount,
      pie_data: devicePie,
      high_risk: highRisk.map(d => ({ name: d.custom_name, prob: parseFloat(d.damage_probability || 0) })),
    },
  })
  links.push({ source: hid, target: cdId, value: '' })

  for (const d of hDevices) {
    const did = d.device_id
    const dtype = typeSeed?.device_types?.find(t => t.type_code === d.type_code)
    const cat = dtype?.category || ''
    const pwr = d.effective_power || d.rated_power || 0
    const dRecords = records.filter(r => r.device_id === did).sort((a, b) => b.year_month.localeCompare(a.year_month)).slice(0, 6).reverse()
    const devKwh = dRecords.map(r => ({ month: r.year_month, kwh: parseFloat(r.total_kwh) }))
    nodes.push({
      id: did, name: (d.custom_name || dtype?.device_name || d.type_code),
      category: 'device', symbolSize: Math.min(24 + pwr / 50, 44), group: cdId, hidden: true,
      itemStyle: { color: deviceColors[cat] || '#ccc' },
      detail: {
        type: 'device', name: d.custom_name || dtype?.device_name || d.type_code,
        category: cat, power: pwr, rated_power: d.rated_power,
        usage_years: parseFloat(d.usage_years || 0), hours: parseFloat(d.daily_usage_hours || 0),
        damage_prob: parseFloat(d.damage_probability || 0), is_active: d.is_active,
        brand: d.brand_choice, lifespan: dtype?.expected_lifespan_years || 10,
        habit: d.usage_habit || '',
        monthly_kwh: devKwh,
        damage_pred: calcDamagePred(d, dtype),
      },
    })
    links.push({ source: cdId, target: did, value: '' })
  }

  // === L1: 用电特征大类 ===
  const ceId = `${hid}_energy`
  nodes.push({
    id: ceId, name: '用电特征', category: 'category',
    symbolSize: 56, group: 'category',
    itemStyle: { color: '#ebf0f5', borderColor: '#c8d6e5', borderWidth: 2, borderRadius: 8 },
    detail: {
      type: 'category', subtype: 'energy', name: '用电特征',
      level: elLv, avg_kwh: avgKwh, total_kwh: Math.round(totalKwh * 100) / 100,
      months: months.length, level_color: elColor,
      trend: monthlyTrend,
      max_month: Math.max(...Object.values(ymTotals)) || 0,
      min_month: Math.min(...Object.values(ymTotals)) || 0,
      std_kwh: calcStd(Object.values(ymTotals)),
    },
  })
  links.push({ source: hid, target: ceId, value: '' })

  const elNodeId = `${hid}_el`
  nodes.push({
    id: elNodeId, name: `能耗: ${elLv}`, category: 'sub',
    symbolSize: 26, group: ceId, hidden: true,
    itemStyle: { color: elColor },
    detail: { type: 'tag', name: '能耗等级', value: elLv, avg_kwh: avgKwh },
  })
  links.push({ source: ceId, target: elNodeId, value: '' })

  const kwhNodeId = `${hid}_kwh`
  nodes.push({
    id: kwhNodeId, name: `月均 ${avgKwh} kWh`, category: 'sub',
    symbolSize: 26, group: ceId, hidden: true,
    itemStyle: { color: '#91c7ae' },
    detail: { type: 'kwh', name: '月均用电', avg_kwh: avgKwh, total_kwh: Math.round(totalKwh * 100) / 100, months: months.length, trend: monthlyTrend, max: Math.max(...Object.values(ymTotals)) || 0, min: Math.min(...Object.values(ymTotals)) || 0 },
  })
  links.push({ source: ceId, target: kwhNodeId, value: '' })

  if (monthlyTrend.length > 0) {
    const last = monthlyTrend[monthlyTrend.length - 1]
    const lastId = `${hid}_last_kwh`
    nodes.push({
      id: lastId, name: `上月 ${last.kwh} kWh`, category: 'sub',
      symbolSize: 26, group: ceId, hidden: true,
      itemStyle: { color: '#d5c4e1' },
      detail: { type: 'kwh', name: '上月用电', value: last.kwh, month: last.month },
    })
    links.push({ source: ceId, target: lastId, value: '' })
  }

  // === L1: 账单记录大类 ===
  const cbId = `${hid}_bills`
  const totalCost = Math.round(allBills.reduce((s, b) => s + parseFloat(b.total_amount || 0), 0) * 100) / 100
  const repairCost = Math.round(allBills.reduce((s, b) => s + parseFloat(b.repair_cost || 0), 0) * 100) / 100
  nodes.push({
    id: cbId, name: `账单记录 (${totalBills}条)`, category: 'category',
    symbolSize: 56, group: 'category',
    itemStyle: { color: '#ebf0f5', borderColor: '#c8d6e5', borderWidth: 2, borderRadius: 8 },
    detail: {
      type: 'category', subtype: 'bills', name: '账单记录',
      total: totalBills, paid: paidCount, unpaid: totalBills - paidCount,
      total_cost: totalCost, repair_cost: repairCost,
      pay_rate: totalBills > 0 ? Math.round(paidCount / totalBills * 1000) / 10 : 0,
      credit: allBills.some(b => b.warning_flag === 1) ? '较差' : '良好',
      trend: billTrend,
    },
  })
  links.push({ source: hid, target: cbId, value: '' })

  for (const b of bills) {
    const bid = `bill_${(b.bill_id || '').slice(-8)}`
    const paid = b.status === 2
    nodes.push({
      id: bid, name: `${b.bill_month} ¥${parseFloat(b.total_amount || 0).toFixed(0)}`,
      category: 'sub', symbolSize: 24, group: cbId, hidden: true,
      itemStyle: { color: paid ? '#d4edda' : '#fff3cd' },
      detail: {
        type: 'bill', month: b.bill_month,
        kwh: parseFloat(b.total_kwh || 0), elec_cost: parseFloat(b.electricity_cost || 0),
        repair_cost: parseFloat(b.repair_cost || 0), total: parseFloat(b.total_amount || 0),
        unit_price: parseFloat(b.unit_price || 0.55), status: paid ? '已缴' : '未缴',
        paid_date: b.paid_date || null, due_date: b.due_date || null,
        warning: b.warning_flag === 1,
      },
    })
    links.push({ source: cbId, target: bid, value: '' })
  }

  // === L1: 家庭信息大类 ===
  const cfId = `${hid}_family`
  nodes.push({
    id: cfId, name: '家庭信息', category: 'category',
    symbolSize: 56, group: 'category',
    itemStyle: { color: '#ebf0f5', borderColor: '#c8d6e5', borderWidth: 2, borderRadius: 8 },
    detail: {
      type: 'category', subtype: 'family', name: '家庭信息',
      members: familyMembers.length,
      cohabit_count: familyMembers.filter(m => m.is_cohabit).length,
      separate_count: familyMembers.filter(m => !m.is_cohabit).length,
      housing_type: housing ? optLabel('housing_type', housing.housing_type) : '--',
      area: housing ? parseFloat(housing.housing_area) : null,
      bedrooms: housing?.bedroom_count || 0,
      living_rooms: housing?.living_room_count || 0,
      kitchen: housing?.kitchen_count || 0,
      bathroom: housing?.bathroom_count || 0,
      floor: housing?.floor_level || null,
      total_floors: housing?.total_floors || null,
      elevator: housing?.has_elevator ? '有' : '无',
      heating: housing ? optLabel('heating', housing.heating_type) : '--',
      orientation: housing ? optLabel('orientation', housing.orientation) : '--',
      building_age: housing?.building_age || null,
      member_list: familyMembers.map(m => ({ name: m.name, relation: { 2: '配偶', 3: '子女', 4: '父母', 5: '岳父母/公婆', 6: '兄弟姐妹', 7: '其他' }[m.relation] || '', cohabit: m.is_cohabit ? '同住' : '分居' })),
    },
  })
  links.push({ source: hid, target: cfId, value: '' })

  for (const m of familyMembers) {
    const mid = `${hid}_member_${m.member_seq}`
    nodes.push({
      id: mid, name: m.name, category: 'sub',
      symbolSize: 22, group: cfId, hidden: true,
      itemStyle: { color: '#ee6666' },
      detail: {
        type: 'member', name: m.name,
        relation: { 2: '配偶', 3: '子女', 4: '父母', 5: '岳父母/公婆', 6: '兄弟姐妹', 7: '其他' }[m.relation] || '',
        cohabit: m.is_cohabit ? '同住' : '分居',
        occupation: m.occupation ? optLabel('occupation', m.occupation) : '--',
        education: m.education ? optLabel('education', m.education) : '--',
        age: m.birth_year ? (new Date().getFullYear() - m.birth_year) : null,
        gender: m.gender ? { 1: '男', 2: '女' }[m.gender] : '--',
      },
    })
    links.push({ source: cfId, target: mid, value: '' })
  }

  // === L1: 画像标签大类 ===
  const ctId = `${hid}_tags`
  nodes.push({
    id: ctId, name: '画像标签', category: 'category',
    symbolSize: 56, group: 'category',
    itemStyle: { color: '#ebf0f5', borderColor: '#c8d6e5', borderWidth: 2, borderRadius: 8 },
    detail: {
      type: 'category', subtype: 'tags', name: '画像标签',
      energy_level: elLv, energy_color: elColor,
      credit: allBills.some(b => b.warning_flag === 1) ? '较差' : '良好',
      device_count: deviceCount, family_size: familyMembers.length,
      income_level: income ? (parseFloat(income.personal_income) > 200000 ? '高收入' : parseFloat(income.personal_income) > 100000 ? '中等收入' : '低收入') : '--',
    },
  })
  links.push({ source: hid, target: ctId, value: '' })

  const tags = [
    { name: '能耗等级', value: elLv },
    { name: '缴费信用', value: allBills.some(b => b.warning_flag === 1) ? '较差' : '良好' },
    { name: '设备数', value: `${deviceCount}台` },
  ]
  for (const tag of tags) {
    const tid = `${hid}_tag_${tag.name}`
    nodes.push({
      id: tid, name: tag.value, category: 'sub',
      symbolSize: 22, group: ctId, hidden: true,
      itemStyle: { color: '#73c0de' },
      detail: { type: 'tag', name: tag.name, value: tag.value },
    })
    links.push({ source: ctId, target: tid, value: '' })
  }

  // 雷达图数据
  let radar = null
  if (months.length > 0) {
    const indicators = [
      { name: '月均用电', max: Math.max(1000, avgKwh * 2) },
      { name: '设备数量', max: 20 },
      { name: '缴费率', max: 100 },
      { name: '用电波动', max: Math.max(500, calcStd(Object.values(ymTotals)) * 2) },
      { name: '能耗水平', max: 1000 },
    ]
    const userValues = [
      Math.round(avgKwh),
      deviceCount,
      totalBills > 0 ? Math.round(paidCount / totalBills * 100) : 0,
      calcStd(Object.values(ymTotals)),
      Math.round(avgKwh),
    ]
    radar = { indicator: indicators, user_values: userValues, avg_values: [350, 10, 85, 200, 350] }
  }

  return {
    status: 200,
    data: {
      nodes, links,
      summary: {
        user: { name: household.real_name, id: hid },
        energy_level: elLv, avg_monthly_kwh: avgKwh, device_count: deviceCount,
        bill_count: totalBills, paid_count: paidCount, total_cost: totalCost,
        has_warning: allBills.some(b => b.warning_flag === 1),
        tags,
        energy_trend: monthlyTrend.length > 0 ? { months: months, values: monthlyTrend.map(t => t.kwh) } : null,
        radar,
        stats: { devices: deviceCount, active: activeCount, damaged: damagedCount, bills: totalBills, paid: paidCount },
      }
    }
  }
}

// ============ 全量图谱（管理员） ============
export function mockGetFullGraph() {
  if (!isAdmin()) return { status: 403, data: { error: '需要管理员权限' } }
  // 简化版全量图谱：使用与 Django 相同的格式
  const userSeed = getSeed('users')
  const deviceSeed = getSeed('devices')
  const billSeed = getSeed('bills')
  const users = (userSeed?.users || []).filter(u => !u.is_staff)
  const allDevices = deviceSeed?.devices || []
  const allBills = billSeed?.bills || []

  const nodes = []
  const links = []

  const energyDist = {}
  let totalPaid = 0
  let totalUnpaid = 0
  let warningUsers = 0
  const catDist = {}
  const highRisk = []

  for (const user of users) {
    const hid = user.household.household_id
    const uDevices = allDevices.filter(d => d.household_id === hid)
    const uBills = allBills.filter(b => b.household_id === hid)
    const totalKwh = uBills.reduce((s, b) => s + parseFloat(b.total_kwh || 0), 0)
    const avgKwh = uBills.length > 0 ? Math.round(totalKwh / uBills.length) : 0

    let el = '普通型'
    if (avgKwh <= 100) el = '节能型'
    else if (avgKwh > 500) el = '高耗能型'
    energyDist[el] = (energyDist[el] || 0) + 1

    const nodeColor = energyColors[el] || '#999'
    const size = Math.max(25, Math.min(65, 25 + avgKwh / 10))

    nodes.push({
      id: hid, name: user.household.real_name, category: 'user',
      symbolSize: size, group: 'center',
      itemStyle: { color: nodeColor },
      detail: {
        type: 'user', name: user.household.real_name,
        avg_monthly_kwh: avgKwh,
        device_count: uDevices.length,
        bills: uBills.length,
      },
    })

    for (const d of uDevices) {
      const did = d.device_id
      const dtype = (getSeed('device_types')?.device_types || []).find(t => t.type_code === d.type_code)
      const cat = dtype?.category || '其他'
      catDist[cat] = (catDist[cat] || 0) + 1
      const prob = parseFloat(d.damage_probability || 0)
      if (prob > 0.5) highRisk.push({ device_id: did, name: d.custom_name, prob, household_id: hid })

      nodes.push({
        id: did, name: d.custom_name || dtype?.device_name || d.type_code,
        category: 'device', symbolSize: 15, group: hid,
        itemStyle: { color: deviceColors[cat] || '#ccc' },
        detail: { type: 'device', category: cat, power: d.rated_power, usage_years: parseFloat(d.usage_years || 0), damage_prob: prob }
      })
      links.push({ source: hid, target: did, value: '' })
    }

    const paid = uBills.filter(b => b.status === 2).length
    const unpaid = uBills.filter(b => b.status !== 2).length
    totalPaid += paid
    totalUnpaid += unpaid
    if (uBills.some(b => b.warning_flag === 1)) warningUsers++
  }

  return {
    status: 200,
    data: {
      nodes, links,
      stats: {
        total_users: users.length, total_devices: allDevices.length, total_bills: allBills.length,
        paid_bills: totalPaid, unpaid_bills: totalUnpaid, warning_users: warningUsers,
        energy_dist: energyDist,
        device_cat_dist: Object.fromEntries(Object.entries(catDist).sort((a, b) => b[1] - a[1])),
        high_risk: highRisk.sort((a, b) => b.prob - a.prob).slice(0, 5),
      }
    }
  }
}

export function mockSyncGraph() {
  if (!isAdmin()) return { status: 403, data: { error: '需要管理员权限' } }
  return { status: 200, data: { message: '知识图谱已同步（静态模式下无需同步）', nodes_synced: 0 } }
}
