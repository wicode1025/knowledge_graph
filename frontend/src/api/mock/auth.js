/**
 * Mock Auth — 登录、注册、登出、验证
 */
import { getSeed, setSeed, genId, clone } from './store.js'

export function mockLogin(data) {
  const seed = getSeed('users')
  const users = seed?.users || []
  const user = users.find(u => u.username === data.username)

  if (!user) {
    return { status: 401, data: { error: '用户名或密码错误' } }
  }
  if (user.password !== data.password) {
    return { status: 401, data: { error: '用户名或密码错误' } }
  }

  // 生成模拟 JWT payload
  const payload = {
    user_id: user.id,
    username: user.username,
    is_staff: !!user.is_staff,
    exp: Date.now() + 7 * 24 * 3600 * 1000
  }
  const token = 'mock_jwt_' + btoa(JSON.stringify(payload))
  const role = user.is_staff ? 'admin' : 'user'
  const elec_user_id = user.household.household_id

  const responseData = {
    status: 'success',
    token,
    user: {
      id: user.id,
      username: user.username,
      email: user.email,
      role,
      is_staff: !!user.is_staff,
      elec_user_id
    },
    role,
    elec_user_id,
    message: '登录成功'
  }

  return { status: 200, data: responseData }
}

export function mockRegister(data) {
  const seed = getSeed('users')
  const users = seed?.users || []

  if (users.find(u => u.username === data.username)) {
    return { status: 400, data: { error: '用户名已存在' } }
  }

  const newId = users.length + 1
  const householdId = `H${String(newId).padStart(4, '0')}`
  const newUser = {
    id: newId,
    username: data.username,
    password: data.password,
    email: data.email || '',
    is_staff: false,
    household: {
      household_id: householdId,
      real_name: data.real_name || data.username,
      gender: null, birth_year: null, birth_month: null,
      education_level: null, marital_status: null,
      phone: null, is_urban: null, address_detail: ''
    },
    housing: {},
    income: {},
    family_members: []
  }

  users.push(newUser)
  seed.users = users
  setSeed('users', seed)

  const payload = { user_id: newId, username: data.username, is_staff: false, exp: Date.now() + 7 * 24 * 3600 * 1000 }
  const token = 'mock_jwt_' + btoa(JSON.stringify(payload))

  return {
    status: 201,
    data: {
      status: 'success',
      token,
      user: {
        id: newId,
        username: data.username,
        email: data.email || '',
        role: 'user',
        is_staff: false,
        elec_user_id: householdId
      },
      role: 'user',
      elec_user_id: householdId,
      message: '注册成功'
    }
  }
}

export function mockLogout() {
  return { status: 200, data: { message: '已登出' } }
}

export function mockVerify() {
  const token = localStorage.getItem('token')
  if (!token || !token.startsWith('mock_jwt_')) {
    return { status: 401, data: { valid: false } }
  }
  try {
    const payload = JSON.parse(atob(token.replace('mock_jwt_', '')))
    if (payload.exp < Date.now()) {
      return { status: 401, data: { valid: false, error: '令牌已过期' } }
    }
    return { status: 200, data: { valid: true, user: payload } }
  } catch {
    return { status: 401, data: { valid: false } }
  }
}
