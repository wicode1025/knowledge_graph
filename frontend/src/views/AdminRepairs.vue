<template>
  <div class="page"><h2>维修审核</h2>
    <table class="data-table"><thead><tr><th>单号</th><th>用户</th><th>设备</th><th>故障</th><th>状态</th><th>费用</th><th>操作</th></tr></thead>
      <tbody><tr v-for="o in orders" :key="o.order_id">
        <td>{{ o.order_id?.slice(-8) }}</td><td>{{ o.household_name }}</td><td>{{ o.device_name }}</td>
        <td>{{ o.fault_description }}</td><td>{{ o.status_text }}</td>
        <td>{{ o.repair_cost ? '¥'+o.repair_cost : '-' }}</td>
        <td>
          <button v-if="o.status===1" @click="doAssign(o)">派单</button>
          <button v-if="o.status===3" @click="doComplete(o)">完成</button>
        </td>
      </tr></tbody>
    </table>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'; import { getAdminRepairOrders as fetchOrders, assignRepair as apiAssign, completeRepair as apiComplete } from '../api'
const orders = ref([])
const load = async () => { const r = await fetchOrders(); orders.value = r.data.orders || [] }
onMounted(load)
async function doAssign(o) { const name = prompt('维修人员：', '张师傅'); if (name) { await apiAssign(o.order_id, name); load() } }
async function doComplete(o) { const cost = prompt('维修费用(元)：', '100'); if (cost) { await apiComplete(o.order_id, { repair_cost: parseFloat(cost), repair_result: '已修复' }); load() } }
</script>
<style scoped>.page{padding:24px}h2{font-size:16px;margin-bottom:16px}.data-table{width:100%;border-collapse:collapse;font-size:13px;background:#fff;border:1px solid #e5e5e5;border-radius:8px}.data-table th{background:#fafafa;padding:10px;text-align:left;font-weight:500}.data-table td{padding:10px;border-top:1px solid #f5f5f5}button{padding:4px 12px;background:#5470c6;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:12px;margin:2px}</style>
