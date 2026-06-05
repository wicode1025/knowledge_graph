/**
 * Mock Household — 用户资料、家庭成员、住房、收入、选项字典
 */
import { getSeed, setSeed, getCurrentUserId, clone } from './store.js'

function findUser(householdId) {
  const seed = getSeed('users')
  return seed?.users?.find(u => u.household.household_id === householdId)
}

export function mockGetMyHousehold() {
  const uid = getCurrentUserId()
  const user = findUser(uid)
  if (!user) return { status: 404, data: { error: '用户不存在' } }

  return {
    status: 200,
    data: {
      household: clone(user.household),
      members: clone(user.family_members || []),
      housing: clone(user.housing || {}),
      income: clone(user.income || {}),
      username: user.username,
      email: user.email
    }
  }
}

export function mockUpdateHousehold(data) {
  const uid = getCurrentUserId()
  const seed = getSeed('users')
  const user = seed?.users?.find(u => u.household.household_id === uid)
  if (!user) return { status: 404, data: { error: '用户不存在' } }

  Object.assign(user.household, data)
  setSeed('users', seed)
  return { status: 200, data: { message: '更新成功' } }
}

export function mockUpdateHousing(data) {
  const uid = getCurrentUserId()
  const seed = getSeed('users')
  const user = seed?.users?.find(u => u.household.household_id === uid)
  if (!user) return { status: 404, data: { error: '用户不存在' } }

  user.housing = { ...user.housing, ...data }
  setSeed('users', seed)
  return { status: 200, data: { message: '住房信息更新成功' } }
}

export function mockUpdateIncome(data) {
  const uid = getCurrentUserId()
  const seed = getSeed('users')
  const user = seed?.users?.find(u => u.household.household_id === uid)
  if (!user) return { status: 404, data: { error: '用户不存在' } }

  user.income = { ...user.income, ...data }
  setSeed('users', seed)
  return { status: 200, data: { message: '收入信息更新成功' } }
}

export function mockGetMembers() {
  const uid = getCurrentUserId()
  const user = findUser(uid)
  if (!user) return { status: 404, data: { error: '用户不存在' } }

  return { status: 200, data: { members: clone(user.family_members || []) } }
}

export function mockAddMember(data) {
  const uid = getCurrentUserId()
  const seed = getSeed('users')
  const user = seed?.users?.find(u => u.household.household_id === uid)
  if (!user) return { status: 404, data: { error: '用户不存在' } }

  const members = user.family_members || []
  const maxSeq = members.reduce((m, mbr) => Math.max(m, mbr.member_seq), 0)
  const newMember = {
    member_seq: maxSeq + 1,
    relation: data.relation,
    name: data.name,
    gender: data.gender || null,
    birth_year: data.birth_year || null,
    occupation: data.occupation || '',
    is_cohabit: data.is_cohabit || 1
  }
  members.push(newMember)
  user.family_members = members
  setSeed('users', seed)
  return { status: 201, data: { member_id: newMember.member_seq } }
}

export function mockUpdateMember(id, data) {
  const uid = getCurrentUserId()
  const seed = getSeed('users')
  const user = seed?.users?.find(u => u.household.household_id === uid)
  if (!user) return { status: 404, data: { error: '用户不存在' } }

  const member = user.family_members?.find(m => m.member_seq === parseInt(id))
  if (!member) return { status: 404, data: { error: '成员不存在' } }
  Object.assign(member, data)
  setSeed('users', seed)
  return { status: 200, data: { message: '更新成功' } }
}

export function mockDeleteMember(id) {
  const uid = getCurrentUserId()
  const seed = getSeed('users')
  const user = seed?.users?.find(u => u.household.household_id === uid)
  if (!user) return { status: 404, data: { error: '用户不存在' } }

  user.family_members = (user.family_members || []).filter(m => m.member_seq !== parseInt(id))
  setSeed('users', seed)
  return { status: 200, data: { message: '删除成功' } }
}

export function mockGetOptions() {
  const seed = getSeed('options')
  return { status: 200, data: seed || {} }
}

export function mockGetAnnouncements() {
  const seed = getSeed('announcements')
  const active = (seed?.announcements || [])
    .filter(a => a.is_active === 1)
    .sort((a, b) => {
      if (a.is_pinned !== b.is_pinned) return b.is_pinned - a.is_pinned
      return new Date(b.created_at) - new Date(a.created_at)
    })
    .slice(0, 5)
  return { status: 200, data: { announcements: active } }
}

export function mockGetMessages() {
  const uid = getCurrentUserId()
  const seed = getSeed('messages')
  const msgs = (seed?.messages || [])
    .filter(m => m.household_id === uid)
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 20)
  return { status: 200, data: { messages: msgs } }
}

export function mockSendMessage(data) {
  const uid = getCurrentUserId()
  const seed = getSeed('messages')
  const msg = {
    id: seed.next_id,
    household_id: uid,
    content: data.content,
    is_read: 0,
    reply: null,
    replied_at: null,
    created_at: new Date().toISOString()
  }
  seed.messages.push(msg)
  seed.next_id++
  setSeed('messages', seed)
  return { status: 201, data: { id: msg.id } }
}

export function mockWithdrawMessage(id) {
  const uid = getCurrentUserId()
  const seed = getSeed('messages')
  const idx = seed.messages.findIndex(m => m.id === parseInt(id) && m.household_id === uid)
  if (idx === -1) return { status: 404, data: { error: '留言不存在' } }
  if (seed.messages[idx].reply) return { status: 400, data: { error: '已回复的留言不可撤回' } }
  seed.messages.splice(idx, 1)
  setSeed('messages', seed)
  return { status: 200, data: { message: '撤回成功' } }
}
