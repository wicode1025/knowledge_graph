<template>
  <div class="register-page">
    <div class="reg-container">
      <!-- 左侧品牌区 -->
      <div class="reg-brand">
        <div class="rb-logo">
          <svg viewBox="0 0 64 64" width="48" height="48">
            <circle cx="32" cy="32" r="28" fill="none" stroke="rgba(255,255,255,0.4)" stroke-width="1.5"/>
            <polygon points="34,12 24,34 30,34 26,52 40,28 34,28 38,12" fill="rgba(255,255,255,0.9)"/>
          </svg>
        </div>
        <h2>Power User Profiling</h2>
        <p>创建您的用电画像账户</p>

        <!-- 步骤指示器 -->
        <div class="rb-steps">
          <div v-for="(s,i) in steps" :key="i" :class="['rbs',{active:i===step,done:i<step}]">
            <div class="rbs-num">{{ i<step?'✓':i+1 }}</div>
            <div class="rbs-label">{{ s }}</div>
          </div>
        </div>
      </div>

      <!-- 右侧表单区 -->
      <div class="reg-form">
        <div class="rf-header">
          <h3>{{ steps[step] }}</h3>
          <div class="rf-progress"><div class="rfp-fill" :style="{width:(step+1)/steps.length*100+'%'}"></div></div>
        </div>

        <div class="rf-body">
          <!-- 步骤1: 账户信息 -->
          <div v-if="step===0" class="rf-step">
            <div class="rf-field"><label>用户名</label><input v-model="form.username" placeholder="用于登录系统" class="rf-input"/></div>
            <div class="rf-field"><label>密码</label><input v-model="form.password" type="password" placeholder="至少6位" class="rf-input"/></div>
            <div class="rf-field"><label>确认密码</label><input v-model="form.password2" type="password" placeholder="再次输入密码" class="rf-input"/></div>
            <div class="rf-field"><label>姓名</label><input v-model="form.real_name" placeholder="真实姓名" class="rf-input"/></div>
          </div>

          <!-- 步骤2: 基本信息 -->
          <div v-if="step===1" class="rf-step">
            <div class="rf-row">
              <div class="rf-field half"><label>性别</label><select v-model="form.gender" class="rf-input"><option value="">请选择</option><option v-for="o in opts.gender" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></div>
              <div class="rf-field half"><label>出生年份</label><input v-model="form.birth_year" type="number" placeholder="如1990" class="rf-input"/></div>
            </div>
            <div class="rf-row">
              <div class="rf-field half"><label>学历</label><select v-model="form.education_level" class="rf-input"><option value="">请选择</option><option v-for="o in opts.education" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></div>
              <div class="rf-field half"><label>婚姻状况</label><select v-model="form.marital_status" class="rf-input"><option value="">请选择</option><option v-for="o in opts.marital" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></div>
            </div>
            <div class="rf-field"><label>职业</label><select v-model="form.occupation" class="rf-input"><option value="">请选择</option><option v-for="o in opts.occupation" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></div>
            <div class="rf-field"><label>联系电话</label><input v-model="form.phone" placeholder="手机号" class="rf-input"/></div>
            <div class="rf-row">
              <div class="rf-field half"><label>城乡</label><select v-model="form.is_urban" class="rf-input"><option value="">请选择</option><option v-for="o in opts.urban" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></div>
              <div class="rf-field half"><label>作息</label><select v-model="form.daily_schedule" class="rf-input"><option value="">请选择</option><option v-for="o in opts.schedule" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></div>
            </div>
          </div>

          <!-- 步骤3: 住房信息 -->
          <div v-if="step===2" class="rf-step">
            <div class="rf-row">
              <div class="rf-field half"><label>住房类型</label><select v-model="form.housing_type" class="rf-input"><option value="">请选择</option><option v-for="o in opts.housing_type" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></div>
              <div class="rf-field half"><label>建筑面积(m²)</label><input v-model="form.housing_area" type="number" placeholder="如120" class="rf-input"/></div>
            </div>
            <div class="rf-row">
              <div class="rf-field half"><label>卧室数</label><input v-model="form.bedroom_count" type="number" placeholder="间" class="rf-input"/></div>
              <div class="rf-field half"><label>客厅数</label><input v-model="form.living_room_count" type="number" placeholder="间" class="rf-input"/></div>
            </div>
            <div class="rf-field"><label>详细地址</label><input v-model="form.address_detail" placeholder="如回龙观北农路二号" class="rf-input"/></div>
          </div>

          <!-- 步骤4: 添加设备 -->
          <div v-if="step===3" class="rf-step">
            <p class="rf-desc">选择您家中常用的电器设备，可稍后在设备管理中添加更多</p>
            <div class="rf-device-grid">
              <div v-for="dt in deviceTypes" :key="dt.type_code" :class="['rfd-item',{selected:selectedDevices.includes(dt.type_code)}]" @click="toggleDevice(dt.type_code)">
                <span class="rfd-name">{{ dt.device_name }}</span>
                <span class="rfd-power">{{ dt.default_power }}W</span>
              </div>
            </div>
            <p class="rf-count">已选 {{ selectedDevices.length }} 台设备</p>
          </div>

          <!-- 步骤5: 收入 -->
          <div v-if="step===4" class="rf-step">
            <div class="rf-field"><label>个人年收入(¥)</label><input v-model="form.personal_income" type="number" placeholder="如120000" class="rf-input"/></div>
            <div class="rf-field"><label>家庭年收入(¥)</label><input v-model="form.household_income" type="number" placeholder="如250000" class="rf-input"/></div>
            <div class="rf-field"><label>收入来源</label><select v-model="form.income_source" class="rf-input"><option value="">请选择</option><option v-for="o in opts.income_source" :key="o.item_key" :value="o.item_key">{{ o.item_value }}</option></select></div>
            <div class="rf-field"><label>经济自评</label>
              <div class="rf-stars"><span v-for="i in 5" :key="i" @click="form.self_rating=i" :class="{active:i<=form.self_rating}">★</span></div>
            </div>
          </div>

          <!-- 步骤6: 完成 -->
          <div v-if="step===5" class="rf-step rf-done">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#67c23a" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            <h3>注册完成</h3>
            <p>账户已创建，即将跳转到首页...</p>
          </div>
        </div>

        <div class="rf-footer">
          <button v-if="step>0&&step<5" class="rf-btn back" @click="step--">上一步</button>
          <button v-if="step<4" class="rf-btn next" @click="nextStep">下一步</button>
          <button v-if="step===4" class="rf-btn next" @click="submitRegister" :disabled="registering">{{ registering?'注册中...':'完成注册' }}</button>
          <div class="rf-error" v-if="error">{{ error }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { getOptions, getDeviceTypes, addDevice } from '../api'

const router = useRouter()
const step = ref(0)
const error = ref('')
const registering = ref(false)
const steps = ['账户信息','基本信息','住房信息','添加设备','收入信息','完成']
const opts = reactive({})
const deviceTypes = ref([])
const selectedDevices = ref([])

const form = reactive({
  username:'',password:'',password2:'',real_name:'',
  gender:'',birth_year:null,education_level:'',marital_status:'',
  occupation:'',phone:'',is_urban:'',daily_schedule:'',
  housing_type:'',housing_area:null,bedroom_count:null,living_room_count:null,address_detail:'',
  personal_income:null,household_income:null,income_source:'',self_rating:3,
})

onMounted(async ()=>{
  const [o,d]=await Promise.all([getOptions(),getDeviceTypes()])
  Object.assign(opts,o.data.options||{})
  const allTypes=[]
  Object.values(d.data.categories||{}).forEach(v=>allTypes.push(...v))
  deviceTypes.value=allTypes.sort((a,b)=>b.default_power-a.default_power).slice(0,24)
})

function toggleDevice(code){const i=selectedDevices.value.indexOf(code);i>-1?selectedDevices.value.splice(i,1):selectedDevices.value.push(code)}

function nextStep(){
  error.value=''
  if(step.value===0){if(!form.username||!form.password||form.password!==form.password2){error.value='请检查用户名和密码';return};if(form.password.length<6){error.value='密码至少6位';return}}
  if(step.value===1){if(!form.gender){error.value='请选择性别';return}}
  if(step.value===2){if(!form.housing_type){error.value='请选择住房类型';return}}
  step.value++
  if(step.value===5) submitRegister()
}

async function submitRegister(){
  registering.value=true;error.value=''
  try {
    const regRes = await axios.post('/api/kg/auth/register/',{username:form.username,password:form.password,email:''})
    const token=regRes.data.token; const hid=regRes.data.user.elec_user_id
    // 更新基本信息
    await axios.put('/api/kg/household/mine/update/',{
      real_name:form.real_name,gender:form.gender,birth_year:form.birth_year,
      education_level:form.education_level,marital_status:form.marital_status,
      occupation:form.occupation,phone:form.phone,is_urban:form.is_urban,
      daily_schedule:form.daily_schedule,address_detail:form.address_detail||'',
    },{headers:{Authorization:`Bearer ${token}`}})
    // 住房
    await axios.put('/api/kg/household/housing/update/',{
      housing_type:form.housing_type,housing_area:form.housing_area,
      bedroom_count:form.bedroom_count,living_room_count:form.living_room_count,
    },{headers:{Authorization:`Bearer ${token}`}})
    // 收入
    await axios.put('/api/kg/household/income/update/',{
      year:2026,personal_income:form.personal_income,
      household_income:form.household_income,income_source:form.income_source,
      self_evaluated_wealth:form.self_rating,
    },{headers:{Authorization:`Bearer ${token}`}})
    // 添加设备
    for(const tc of selectedDevices.value){
      const dt=deviceTypes.value.find(d=>d.type_code===tc)
      if(dt){
        await axios.post('/api/kg/devices/',{
          device_type_code:tc,rated_power:dt.default_power,
          daily_usage_hours:dt.typical_daily_hours||1,brand_choice:'普通品牌',usage_years:0,
        },{headers:{Authorization:`Bearer ${token}`}})
      }
    }
    localStorage.setItem('token',token)
    localStorage.setItem('user',JSON.stringify(regRes.data.user))
    localStorage.setItem('role','user')
    localStorage.setItem('elec_user_id',hid||'')
    setTimeout(()=>router.push('/'),1500)
  } catch(e){error.value=e.response?.data?.message||'注册失败，请重试'}
  finally{registering.value=false}
}
</script>

<style scoped>
.register-page{position:fixed;top:0;left:0;right:0;bottom:0;display:flex;align-items:center;justify-content:center;background:#f0f2f5}
.reg-container{display:flex;width:820px;max-width:92vw;height:560px;max-height:90vh;background:#fff;border-radius:12px;box-shadow:0 8px 40px rgba(0,0,0,0.12);overflow:hidden}

/* 左侧 */
.reg-brand{width:300px;background:linear-gradient(160deg,#1a2332,#2c3e50);color:#fff;display:flex;flex-direction:column;align-items:center;padding:40px 30px;text-align:center}
.rb-logo{margin-bottom:20px}
.reg-brand h2{font-size:16px;font-weight:500;margin:0 0 6px}
.reg-brand p{font-size:12px;opacity:0.6;margin:0}
.rb-steps{margin-top:auto;width:100%;display:flex;flex-direction:column;gap:14px}
.rbs{display:flex;align-items:center;gap:10px;opacity:0.4;transition:opacity 0.3s}
.rbs.active,.rbs.done{opacity:1}
.rbs-num{width:26px;height:26px;border-radius:50%;border:2px solid rgba(255,255,255,0.4);display:flex;align-items:center;justify-content:center;font-size:12px;flex-shrink:0}
.rbs.done .rbs-num{background:#67c23a;border-color:#67c23a}
.rbs.active .rbs-num{border-color:#fff}
.rbs-label{font-size:12px}

/* 右侧 */
.reg-form{flex:1;display:flex;flex-direction:column;overflow:hidden}
.rf-header{padding:20px 28px 0}
.rf-header h3{font-size:20px;font-weight:500;color:#2c3e50;margin:0 0 12px}
.rf-progress{height:3px;background:#edf0f4;border-radius:2px}
.rfp-fill{height:100%;background:#2c3e50;border-radius:2px;transition:width 0.4s ease}
.rf-body{flex:1;overflow-y:auto;padding:20px 28px}
.rf-step{display:flex;flex-direction:column;gap:14px}
.rf-field{display:flex;flex-direction:column;gap:4px}
.rf-field label{font-size:11px;color:#999}
.rf-input{width:100%;padding:9px 12px;border:1px solid #e0e0e0;border-radius:6px;font-size:13px;outline:none;font-family:inherit;box-sizing:border-box;transition:border-color 0.15s}
.rf-input:focus{border-color:#5470c6}
select.rf-input{cursor:pointer;appearance:none;background:#fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12'%3E%3Cpath d='M3 5l3 3 3-3' fill='none' stroke='%23999' stroke-width='1.5'/%3E%3C/svg%3E") no-repeat right 10px center;padding-right:30px}
.rf-row{display:flex;gap:14px}
.rf-field.half{flex:1}
.rf-desc{font-size:12px;color:#999;margin:0}
.rf-device-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px}
.rfd-item{padding:8px 10px;border:1px solid #e0e0e0;border-radius:6px;cursor:pointer;text-align:center;transition:all 0.15s;font-size:12px}
.rfd-item:hover{border-color:#5470c6}
.rfd-item.selected{background:#2c3e50;color:#fff;border-color:#2c3e50}
.rfd-name{display:block}
.rfd-power{display:block;font-size:10px;opacity:0.6;margin-top:2px}
.rf-count{font-size:11px;color:#888;text-align:center;margin:0}
.rf-stars{display:flex;gap:4px;font-size:22px;color:#ddd;cursor:pointer}
.rf-stars span.active{color:#e6a23c}
.rf-done{text-align:center;padding:40px 0;align-items:center}
.rf-done h3{font-size:18px;color:#2c3e50;margin:12px 0 6px}
.rf-done p{font-size:13px;color:#888}
.rf-footer{display:flex;align-items:center;gap:10px;padding:16px 28px;border-top:1px solid #f0f2f5}
.rf-btn{padding:10px 28px;border-radius:6px;font-size:13px;cursor:pointer;font-family:inherit;transition:all 0.15s}
.rf-btn.back{background:#fff;border:1px solid #e0e0e0;color:#666}
.rf-btn.back:hover{border-color:#5470c6;color:#5470c6}
.rf-btn.next{margin-left:auto;background:#2c3e50;color:#fff;border:none}
.rf-btn.next:hover{background:#5470c6}
.rf-btn:disabled{opacity:0.5;cursor:not-allowed}
.rf-error{font-size:12px;color:#e74c3c}

@media(max-width:700px){.reg-container{flex-direction:column;height:auto}.reg-brand{width:100%;padding:24px 20px}.rb-steps{flex-direction:row;gap:8px;margin-top:16px}.rbs-label{display:none}}
</style>
