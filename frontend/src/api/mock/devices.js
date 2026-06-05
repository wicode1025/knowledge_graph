/**
 * Mock Devices — 设备管理 + Weibull 损坏概率计算
 */
import { getSeed, setSeed, getCurrentUserId, clone, genId } from './store.js'

// ============ 物理计算（从 Python monthly_engine.py 移植） ============

export function calcEffectivePower(ratedPower, usageYears, lifespan, agingRate = 0.15) {
  const ratio = usageYears / lifespan
  return Math.round(ratedPower * (1 + agingRate * ratio * ratio))
}

export function calcDamageProbability(usageYears, lifespan, beta = 2.5, bqf = 1.0) {
  const eta = lifespan * 1.2 * bqf
  return 1 - Math.exp(-Math.pow(usageYears / eta, beta))
}

// ============ API handlers ============

export function mockGetDeviceTypes() {
  const seed = getSeed('device_types')
  const types = seed?.device_types || []
  // 按 category 分组
  const grouped = {}
  for (const t of types) {
    if (!grouped[t.category]) grouped[t.category] = []
    grouped[t.category].push({
      type_id: t.type_code,
      device_name: t.device_name,
      device_type_code: t.type_code,
      default_power: t.default_power,
      power_range: t.power_range,
      expected_lifespan_years: t.expected_lifespan_years,
      is_active: 1
    })
  }
  return { status: 200, data: { categories: Object.keys(grouped), device_types: grouped } }
}

export function mockGetDeviceTypeDetail(typeCode) {
  const seed = getSeed('device_types')
  const type = seed?.device_types?.find(t => t.type_code === typeCode)
  if (!type) return { status: 404, data: { error: '设备类型不存在' } }

  return {
    status: 200,
    data: {
      device_type: {
        type_code: type.type_code,
        device_name: type.device_name,
        category: type.category,
        default_power: type.default_power,
        expected_lifespan_years: type.expected_lifespan_years,
        weibull_beta: type.weibull_beta,
        aging_rate: type.aging_rate,
        typical_daily_hours: type.typical_daily_hours
      },
      brands: [
        { brand_name: '格力', bqf: 1.10 },
        { brand_name: '美的', bqf: 1.05 },
        { brand_name: '海尔', bqf: 1.08 },
        { brand_name: '西门子', bqf: 1.20 },
        { brand_name: '松下', bqf: 1.15 },
        { brand_name: '通用品牌', bqf: 1.00 },
        { brand_name: '经济品牌', bqf: 0.85 }
      ],
      usage_habits: [
        { habit_id: 1, habit_name: '全天运行', habit_code: '1', typical_hours: '24h', seasonal_factor: 1.0 },
        { habit_id: 2, habit_name: '白天使用', habit_code: '2', typical_hours: '6-8h', seasonal_factor: 1.0 },
        { habit_id: 3, habit_name: '夜间使用', habit_code: '3', typical_hours: '4-6h', seasonal_factor: 1.0 },
        { habit_id: 4, habit_name: '偶尔使用', habit_code: '4', typical_hours: '0-1h', seasonal_factor: 0.5 },
        { habit_id: 5, habit_name: '季节性使用', habit_code: '5', typical_hours: '4-6h', seasonal_factor: 0.7 }
      ]
    }
  }
}

export function mockGetMyDevices() {
  const uid = getCurrentUserId()
  const seed = getSeed('devices')
  const devices = (seed?.devices || []).filter(d => d.household_id === uid)

  const habitNames = { '1': '全天运行', '2': '白天使用', '3': '夜间使用', '4': '偶尔使用', '5': '季节性使用' }
  const result = devices.map(d => {
    const typeSeed = getSeed('device_types')
    const dtype = typeSeed?.device_types?.find(t => t.type_code === d.type_code)
    return {
      device_id: d.device_id,
      custom_name: d.custom_name,
      type_code: d.type_code,
      category: dtype?.category || '',
      device_name: dtype?.device_name || d.type_code,
      rated_power: d.rated_power,
      effective_power: d.effective_power,
      brand_choice: d.brand_choice,
      bqf: d.bqf,
      purchase_date: d.purchase_date,
      usage_years: d.usage_years,
      daily_usage_hours: d.daily_usage_hours,
      usage_habit: d.usage_habit,
      usage_habit_name: habitNames[d.usage_habit] || d.usage_habit || '--',
      usage_season: d.usage_season,
      usage_frequency: d.usage_frequency,
      is_active: d.is_active,
      damage_probability: d.damage_probability,
      damage_date: d.damage_date,
      expected_lifespan_years: dtype?.expected_lifespan_years || 10
    }
  })
  return { status: 200, data: { devices: result, count: result.length } }
}

export function mockGetAllDevices() {
  const seed = getSeed('devices')
  const typeSeed = getSeed('device_types')
  const userSeed = getSeed('users')
  const devices = (seed?.devices || []).filter(d => {
    const owner = userSeed?.users?.find(u => u.household.household_id === d.household_id)
    return owner && !owner.is_staff
  })
  const habitNames = { '1': '全天运行', '2': '白天使用', '3': '夜间使用', '4': '偶尔使用', '5': '季节性使用' }
  const result = devices.map(d => {
    const dtype = typeSeed?.device_types?.find(t => t.type_code === d.type_code)
    const owner = userSeed?.users?.find(u => u.household.household_id === d.household_id)
    return {
      device_id: d.device_id,
      custom_name: d.custom_name,
      device_name: dtype?.device_name || d.type_code,
      type_code: d.type_code,
      category: dtype?.category || '',
      household_id: d.household_id,
      household_name: owner?.household?.real_name || d.household_id,
      rated_power: d.rated_power,
      effective_power: d.effective_power,
      usage_years: d.usage_years,
      usage_habit_name: habitNames[d.usage_habit] || '--',
      is_active: d.is_active,
      damage_probability: d.damage_probability
    }
  })
  return { status: 200, data: { devices: result, count: result.length } }
}

export function mockAddDevice(data) {
  const uid = getCurrentUserId()
  const seed = getSeed('devices')
  const typeSeed = getSeed('device_types')
  const dtype = typeSeed?.device_types?.find(t => t.type_code === data.type_code)
  if (!dtype) return { status: 400, data: { error: '设备类型不存在' } }

  const existingIds = (seed.devices || []).map(d => d.device_id)
  const deviceId = genId(`DEV_${uid}`, existingIds)

  const usageYears = parseFloat(data.usage_years || 0)
  const ratedPower = data.rated_power || dtype.default_power
  const lifespan = dtype.expected_lifespan_years
  const beta = dtype.weibull_beta
  const bqf = parseFloat(data.bqf || 1.0)
  const agingRate = (dtype.aging_rate || 15) / 100

  const effectivePower = calcEffectivePower(ratedPower, usageYears, lifespan, agingRate)
  const damageProb = calcDamageProbability(usageYears, lifespan, beta, bqf)

  const device = {
    device_id: deviceId,
    household_id: uid,
    type_code: data.type_code,
    custom_name: data.custom_name || dtype.device_name,
    rated_power: ratedPower,
    brand_choice: data.brand_choice || '',
    bqf: bqf,
    purchase_date: data.purchase_date || null,
    usage_years: usageYears,
    daily_usage_hours: parseFloat(data.daily_usage_hours || dtype.typical_daily_hours || 1),
    usage_habit: data.usage_habit || '2',
    usage_season: data.usage_season || '1',
    usage_frequency: data.usage_frequency || 1,
    is_active: 1,
    damage_probability: Math.round(damageProb * 10000) / 10000,
    effective_power: effectivePower
  }
  seed.devices.push(device)
  setSeed('devices', seed)
  return { status: 201, data: { device_id: deviceId, message: '设备添加成功' } }
}

export function mockDeleteDevice(deviceId) {
  const uid = getCurrentUserId()
  const seed = getSeed('devices')
  const idx = seed.devices.findIndex(d => d.device_id === deviceId && d.household_id === uid)
  if (idx === -1) return { status: 404, data: { error: '设备不存在' } }
  seed.devices.splice(idx, 1)
  setSeed('devices', seed)
  return { status: 200, data: { message: '设备已删除' } }
}

export function mockGetDeviceHistory(deviceId) {
  const seed = getSeed('electricity_records')
  const records = (seed?.records || [])
    .filter(r => r.device_id === deviceId)
    .sort((a, b) => b.year_month.localeCompare(a.year_month))
    .slice(0, 12)
    .map(r => ({
      year_month: r.year_month,
      total_kwh: parseFloat(r.total_kwh),
      avg_daily_kwh: parseFloat(r.avg_daily_kwh),
      peak_power: parseFloat(r.peak_power),
      hours_used: parseFloat(r.hours_used)
    }))
  return { status: 200, data: { records, count: records.length } }
}
