<template>
  <div class="page"><h2>用户管理</h2>
    <table class="data-table"><thead><tr><th>户号</th><th>用户名</th><th>姓名</th><th>电话</th><th>学历</th><th>职业</th><th>设备数</th></tr></thead>
      <tbody><tr v-for="u in users" :key="u.household_id"><td>{{ u.household_id }}</td><td>{{ u.username }}</td><td>{{ u.real_name }}</td><td>{{ u.phone || '-' }}</td><td>{{ u.education_level || '-' }}</td><td>{{ u.occupation || '-' }}</td><td>{{ u.device_count }}</td></tr></tbody>
    </table>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'; import { getAdminUsers } from '../api'
const users = ref([])
onMounted(async () => { const r = await getAdminUsers(); users.value = r.data.users || [] })
</script>
<style scoped>.page{padding:24px}h2{font-size:16px;margin-bottom:16px}.data-table{width:100%;border-collapse:collapse;font-size:13px;background:#fff;border:1px solid #e5e5e5;border-radius:8px}.data-table th{background:#fafafa;padding:10px;text-align:left;font-weight:500}.data-table td{padding:10px;border-top:1px solid #f5f5f5}</style>
