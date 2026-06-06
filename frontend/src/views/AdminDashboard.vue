<template>
  <div class="admin-page">
    <div class="page-top"><h2>管理后台</h2></div>

    <!-- ========== 系统概览 ========== -->
    <div v-if="tab === 'dashboard'">
      <div class="advance-section">
        <div class="advance-card">
          <div class="advance-info">
            <span class="current-month-label">当前系统月份</span>
            <span class="current-month-value">{{ sysMonth }}</span>
            <span class="elapsed-label">已运行 {{ stats.total_months_elapsed }} 个月</span>
          </div>
          <button class="advance-btn" @click="handleAdvance" :disabled="advancing">{{ advancing ? '推进中...' : '推进至下月' }}</button>
          <div class="advance-hint">自动计算用电量并生成账单通知</div>
        </div>
        <div class="advance-result" v-if="advanceResult">推进完成！{{ advanceResult.records_created }} 条记录，{{ advanceResult.bills_created }} 张账单</div>
        <div class="advance-error" v-if="advanceError">{{ advanceError }}</div>
      </div>
      <div class="stats-grid">
        <div class="st-card"><div class="st-val">{{ stats.total_users }}</div><div class="st-lbl">用户总数</div></div>
        <div class="st-card"><div class="st-val">{{ stats.active_devices }}/{{ stats.total_devices }}</div><div class="st-lbl">活跃/总设备</div></div>
        <div class="st-card"><div class="st-val">{{ stats.damaged_devices }}</div><div class="st-lbl">损坏设备</div></div>
        <div class="st-card"><div class="st-val">{{ stats.bills_collected }}</div><div class="st-lbl">账单收缴</div></div>
        <div class="st-card"><div class="st-val">{{ stats.pending_repairs }}</div><div class="st-lbl">待审核维修</div></div>
        <div class="st-card"><div class="st-val">{{ stats.unit_price?.toFixed(2) }}/度</div><div class="st-lbl">电价</div></div>
      </div>

      <!-- 公告 -->
      <section class="panel">
        <div class="panel-head"><h3>系统公告</h3><button class="btn-sm" @click="showAnnForm = !showAnnForm">{{ showAnnForm ? '取消' : '+ 发布' }}</button></div>
        <div class="ann-form" v-if="showAnnForm">
          <input v-model="annForm.title" placeholder="标题" class="af-input" />
          <textarea v-model="annForm.content" placeholder="内容" class="af-textarea" rows="2"></textarea>
          <label class="af-check"><input type="checkbox" v-model="annForm.is_pinned"/> 置顶</label>
          <button class="btn-sm primary" @click="submitAnn">发布</button>
        </div>
        <div class="ann-list" v-if="adminAnns.length">
          <div v-for="a in adminAnns" :key="a.id" class="ann-row">
            <div class="ar-info"><span :class="{pinned:a.is_pinned}">{{ a.is_pinned ? '📌 ' : '' }}{{ a.title }}</span><span class="ar-text">{{ a.content.slice(0,50) }}...</span></div>
            <div class="ar-actions"><span class="ar-date">{{ a.created_at?.slice(0,10) }}</span><button class="btn-del" @click="confirmDelAnn(a.id)">删除</button></div>
          </div>
        </div>
        <div class="empty-hint" v-else>暂无公告</div>
      </section>

      <!-- 留言 -->
      <section class="panel">
        <div class="panel-head"><h3>用户留言 ({{ adminMsgs.length }})</h3></div>
        <div class="msg-list" v-if="adminMsgs.length">
          <div v-for="m in adminMsgs" :key="m.id" class="msg-row">
            <div class="mr-left">
              <span class="mr-user">{{ m.household_name }}</span>
              <span class="mr-content">{{ m.content }}</span>
              <span class="mr-date">{{ m.created_at?.slice(0,10) }}</span>
            </div>
            <div class="mr-right">
              <template v-if="m.reply"><span class="mr-replied">已回复: {{ m.reply }}</span></template>
              <template v-else>
                <button v-if="replyForm.id !== m.id" class="btn-sm" @click="replyForm.id=m.id;replyForm.text=''">回复</button>
                <span v-else class="reply-inline"><input v-model="replyForm.text" placeholder="回复" class="af-input s"/><button class="btn-sm primary" @click="doReply(m.id,replyForm.text)">发送</button><button class="btn-sm" @click="replyForm.id=null">取消</button></span>
              </template>
              <button class="btn-del" @click="confirmDelMsg(m.id)">删除</button>
            </div>
          </div>
        </div>
        <div class="empty-hint" v-else>暂无留言</div>
      </section>
    </div>

    <!-- ========== 知识图谱 ========== -->
    <!-- ========== 知识图谱 (用户视角) ========== -->
    <div v-if="tab === 'kg'" class="kg-user-wrap">
      <div class="kg-user-top">
        <span class="kg-count">{{ adminVisibleNodes }} 个节点 · {{ adminVisibleLinks }} 条关系</span>
        <select v-model="adminKgUser" class="kg-user-sel" @change="loadAdminUserKG">
          <option v-for="u in dataUsers" :key="u.household_id" :value="u.household_id">{{ u.real_name }} ({{ u.household_id }})</option>
        </select>
      </div>
      <div class="kg-user-layout">
        <!-- 左侧: 用户画像 -->
        <div class="kg-user-left">
          <div class="kul-avatar-section">
            <div class="kul-avatar">{{ adminKgUserInfo?.real_name?.charAt?.(0) || '?' }}</div>
            <div class="kul-name">{{ adminKgUserInfo?.real_name || '--' }}</div>
            <template v-if="adminKgUserInfo">
            <div class="kul-tags">
              <span v-if="adminKgUserInfo.gender" class="kult">{{ adminKgOptLabel('gender', adminKgUserInfo.gender) }}</span>
              <span v-if="adminKgUserInfo.birth_year" class="kult">{{ adminKgUserInfo.birth_year }}年</span>
              <span v-if="adminKgUserInfo.education_level" class="kult">{{ adminKgOptLabel('education', adminKgUserInfo.education_level) }}</span>
              <span v-if="adminKgUserInfo.marital_status" class="kult">{{ adminKgOptLabel('marital', adminKgUserInfo.marital_status) }}</span>
            </div>
            </template>
          </div>
          <div class="kul-metrics" v-if="adminKgData">
            <div class="kulm-item"><div class="kulm-val" :style="{color: adminKgEnergyColor}">{{ adminKgData.summary?.energy_level || '--' }}</div><div class="kulm-lbl">能耗等级</div></div>
            <div class="kulm-item"><div class="kulm-val">{{ adminKgData.summary?.avg_monthly_kwh || '--' }}</div><div class="kulm-lbl">月均 kWh</div></div>
            <div class="kulm-item"><div class="kulm-val">{{ adminKgData.summary?.device_count || '--' }}</div><div class="kulm-lbl">设备数</div></div>
            <div class="kulm-item"><div class="kulm-val">{{ adminKgData.summary?.paid_count || 0 }}/{{ adminKgData.summary?.bill_count || 0 }}</div><div class="kulm-lbl">已缴/总账单</div></div>
          </div>
          <div class="kul-wordcloud" v-if="adminKgData" ref="adminWordCloud"></div>
          <div class="kul-table" v-if="adminKgUserInfo">
            <div class="kult-row"><span>职业</span><span>{{ adminKgOptLabel('occupation', adminKgUserInfo.occupation) }}</span></div>
            <div class="kult-row"><span>城乡</span><span>{{ adminKgOptLabel('urban', adminKgUserInfo.is_urban) }}</span></div>
            <div class="kult-row"><span>作息</span><span>{{ adminKgOptLabel('schedule', adminKgUserInfo.daily_schedule) }}</span></div>
            <div class="kult-row"><span>健康</span><span>{{ adminKgOptLabel('health', adminKgUserInfo.self_health) }}</span></div>
            <div class="kult-row"><span>住房</span><span>{{ adminKgOptLabel('housing_type', adminKgHousing?.housing_type) }}</span></div>
            <div class="kult-row"><span>面积</span><span>{{ adminKgHousing?.housing_area || '--' }} m²</span></div>
            <div class="kult-row"><span>收入</span><span>{{ adminKgIncome?.personal_income ? '¥'+Number(adminKgIncome.personal_income).toLocaleString() : '--' }}</span></div>
          </div>
          <div class="kul-chart" v-if="adminKgData?.summary" ref="adminTrendChart"></div>
        </div>
        <!-- 右侧: 知识图谱 -->
        <div class="kg-user-right">
          <div class="kur-chart" ref="adminUserKgChart"></div>
          <div class="kur-panel" :class="{open:adminKgPanelOpen}">
            <template v-if="!adminKgPanelOpen">
              <div class="kurp-trigger" @click="adminKgPanelOpen=true"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg><span class="kurp-text">详情</span></div>
            </template>
            <template v-else>
              <div class="kurp-head"><span>节点详情</span><button class="kurp-close" @click="adminKgPanelOpen=false">×</button></div>
              <div class="kurp-body" v-if="adminKgPanelData">
                <!-- ====== 用户中心 ====== -->
                <template v-if="adminKgPanelData.type==='user'">
                  <h4 class="kurp-dname">{{ adminKgPanelData.name }}</h4>
                  <span class="kurp-badge-s" :style="{background: adminKgPanelData.energy?.color||'#999'}">{{ adminKgPanelData.energy?.level||'--' }}</span>
                  <div class="kurp-sec"><div class="kurp-sec-t">基本信息</div>
                    <div class="kurp-rows"><div class="kurpr" v-for="(v,k) in adminKgPanelData.info" :key="k"><span>{{ k }}</span><span>{{ v||'--' }}</span></div></div>
                  </div>
                  <div class="kurp-sec" v-if="adminKgPanelData.housing"><div class="kurp-sec-t">住房信息</div>
                    <div class="kurp-rows"><div class="kurpr"><span>类型</span><span>{{ adminKgPanelData.housing.type||'--' }}</span></div><div class="kurpr"><span>面积</span><span>{{ adminKgPanelData.housing.area ? adminKgPanelData.housing.area+' m²' : '--' }}</span></div><div class="kurpr"><span>户型</span><span>{{ adminKgPanelData.housing.bedroom||0 }}室{{ adminKgPanelData.housing.living||0 }}厅</span></div></div>
                  </div>
                  <div class="kurp-sec" v-if="adminKgPanelData.stats"><div class="kurp-sec-t">概况</div>
                    <div class="kurp-rows"><div class="kurpr"><span>设备</span><span>{{ adminKgPanelData.stats.active||0 }}/{{ adminKgPanelData.stats.devices||0 }} 运行中</span></div><div class="kurpr"><span>账单</span><span>{{ adminKgPanelData.stats.paid||0 }}/{{ adminKgPanelData.stats.bills||0 }} 已缴</span></div></div>
                  </div>
                </template>
                <!-- ====== 设备管理大类 ====== -->
                <template v-else-if="adminKgPanelData.subtype==='devices'">
                  <h4 class="kurp-dname">设备管理</h4>
                  <div class="kurp-metrics"><div class="kurpm"><div class="kurpm-val">{{ adminKgPanelData.total||0 }}</div><div class="kurpm-lbl">总数</div></div><div class="kurpm"><div class="kurpm-val on">{{ adminKgPanelData.active||0 }}</div><div class="kurpm-lbl">运行中</div></div><div class="kurpm"><div class="kurpm-val off">{{ adminKgPanelData.damaged||0 }}</div><div class="kurpm-lbl">损坏</div></div></div>
                  <div v-if="adminKgPanelData.high_risk?.length" class="kurp-sec"><div class="kurp-sec-t">高风险设备</div>
                    <div v-for="r in adminKgPanelData.high_risk" :key="r.name" class="kurpr"><span>{{ r.name }}</span><span :class="r.prob>0.5?'off':r.prob>0.3?'warn':''">{{ (r.prob*100).toFixed(1) }}%</span></div>
                  </div>
                </template>
                <!-- ====== 用电特征大类 ====== -->
                <template v-else-if="adminKgPanelData.subtype==='energy'">
                  <h4 class="kurp-dname">用电特征</h4>
                  <span class="kurp-badge-s" :style="{background: adminKgPanelData.level_color||'#999'}">{{ adminKgPanelData.level||'--' }}</span>
                  <div class="kurp-rows"><div class="kurpr"><span>月均用电</span><span>{{ adminKgPanelData.avg_kwh||0 }} kWh</span></div><div class="kurpr"><span>累计用电</span><span>{{ (adminKgPanelData.total_kwh||0).toLocaleString() }} kWh</span></div><div class="kurpr"><span>统计月份</span><span>{{ adminKgPanelData.months||0 }} 个月</span></div><div class="kurpr"><span>标准差</span><span>{{ adminKgPanelData.std_kwh||0 }}</span></div><div class="kurpr"><span>最大月</span><span>{{ adminKgPanelData.max_month||0 }} kWh</span></div><div class="kurpr"><span>最小月</span><span>{{ adminKgPanelData.min_month||0 }} kWh</span></div></div>
                </template>
                <!-- ====== 账单记录大类 ====== -->
                <template v-else-if="adminKgPanelData.subtype==='bills'">
                  <h4 class="kurp-dname">账单记录</h4>
                  <div class="kurp-metrics"><div class="kurpm"><div class="kurpm-val">{{ adminKgPanelData.total||0 }}</div><div class="kurpm-lbl">总数</div></div><div class="kurpm"><div class="kurpm-val on">{{ adminKgPanelData.paid||0 }}</div><div class="kurpm-lbl">已缴</div></div><div class="kurpm"><div class="kurpm-val off">{{ adminKgPanelData.unpaid||0 }}</div><div class="kurpm-lbl">未缴</div></div></div>
                  <div class="kurp-rows"><div class="kurpr"><span>总费用</span><span>¥{{ adminKgPanelData.total_cost||0 }}</span></div><div class="kurpr"><span>缴费率</span><span>{{ adminKgPanelData.pay_rate||0 }}%</span></div><div class="kurpr"><span>信用</span><span :class="adminKgPanelData.credit==='良好'?'on':'off'">{{ adminKgPanelData.credit||'--' }}</span></div></div>
                </template>
                <!-- ====== 家庭信息大类 ====== -->
                <template v-else-if="adminKgPanelData.subtype==='family'">
                  <h4 class="kurp-dname">家庭信息</h4>
                  <div class="kurp-metrics"><div class="kurpm"><div class="kurpm-val">{{ adminKgPanelData.members||0 }}</div><div class="kurpm-lbl">成员</div></div><div class="kurpm"><div class="kurpm-val on">{{ adminKgPanelData.cohabit_count||0 }}</div><div class="kurpm-lbl">同住</div></div></div>
                  <div class="kurp-rows"><div class="kurpr"><span>住房类型</span><span>{{ adminKgPanelData.housing_type||'--' }}</span></div><div class="kurpr"><span>面积</span><span>{{ adminKgPanelData.area ? adminKgPanelData.area+' m²' : '--' }}</span></div><div class="kurpr"><span>户型</span><span>{{ adminKgPanelData.bedrooms||0 }}室{{ adminKgPanelData.living_rooms||0 }}厅 · {{ adminKgPanelData.kitchen||0 }}厨{{ adminKgPanelData.bathroom||0 }}卫</span></div><div class="kurpr"><span>楼层</span><span>{{ adminKgPanelData.floor||'--' }}/{{ adminKgPanelData.total_floors||'--' }}</span></div><div class="kurpr"><span>电梯</span><span>{{ adminKgPanelData.elevator||'--' }}</span></div><div class="kurpr"><span>供暖</span><span>{{ adminKgPanelData.heating||'--' }}</span></div><div class="kurpr"><span>朝向</span><span>{{ adminKgPanelData.orientation||'--' }}</span></div>
                  </div>
                </template>
                <!-- ====== 画像标签大类 ====== -->
                <template v-else-if="adminKgPanelData.subtype==='tags'">
                  <h4 class="kurp-dname">画像标签</h4>
                  <div class="kurp-rows"><div class="kurpr"><span>能耗等级</span><span :style="{color: adminKgPanelData.energy_color}">{{ adminKgPanelData.energy_level||'--' }}</span></div><div class="kurpr"><span>缴费信用</span><span :class="adminKgPanelData.credit==='良好'?'on':'off'">{{ adminKgPanelData.credit||'--' }}</span></div><div class="kurpr"><span>设备规模</span><span>{{ adminKgPanelData.device_count||0 }} 台</span></div><div class="kurpr"><span>家庭规模</span><span>{{ adminKgPanelData.family_size||0 }} 人</span></div></div>
                </template>
                <!-- ====== 设备节点 ====== -->
                <template v-else-if="adminKgPanelData.type==='device'">
                  <h4 class="kurp-dname">{{ adminKgPanelData.name }}</h4>
                  <span class="kurp-badge-s" :class="adminKgPanelData.is_active?'on':'off'">{{ adminKgPanelData.is_active?'正常运行':'已损坏' }}</span>
                  <div class="kurp-rows"><div class="kurpr"><span>类别</span><span>{{ adminKgPanelData.category||'--' }}</span></div><div class="kurpr"><span>品牌</span><span>{{ adminKgPanelData.brand||'--' }}</span></div><div class="kurpr"><span>功率</span><span>{{ adminKgPanelData.power||0 }} W (额定{{ adminKgPanelData.rated_power||0 }}W)</span></div><div class="kurpr"><span>年限</span><span>{{ adminKgPanelData.usage_years?.toFixed?.(1)||adminKgPanelData.usage_years||0 }} 年</span></div><div class="kurpr"><span>寿命</span><span>{{ adminKgPanelData.lifespan||10 }} 年 · 剩余{{ adminKgPanelData.damage_pred?.remain||0 }}年</span></div><div class="kurpr"><span>使用习惯</span><span>{{ adminKgPanelData.habit||'--' }}</span></div><div class="kurpr"><span>损坏率</span><span :class="(adminKgPanelData.damage_prob||0)>0.8?'off':(adminKgPanelData.damage_prob||0)>0.5?'warn':''">{{ ((adminKgPanelData.damage_prob||0)*100).toFixed(1) }}%</span></div><div class="kurpr"><span>1年后</span><span :class="(adminKgPanelData.damage_pred?.next1||0)>0.8?'off':(adminKgPanelData.damage_pred?.next1||0)>0.5?'warn':''">{{ ((adminKgPanelData.damage_pred?.next1||0)*100).toFixed(1) }}%</span></div></div>
                </template>
                <!-- ====== 账单节点 ====== -->
                <template v-else-if="adminKgPanelData.type==='bill'">
                  <h4 class="kurp-dname">{{ adminKgPanelData.month }}</h4>
                  <span class="kurp-badge-s" :class="adminKgPanelData.status==='已缴'?'on':'off'">{{ adminKgPanelData.status }}</span>
                  <div class="kurp-rows"><div class="kurpr"><span>用电量</span><span>{{ adminKgPanelData.kwh||0 }} kWh</span></div><div class="kurpr"><span>电价</span><span>¥{{ adminKgPanelData.unit_price||'0.55' }}/度</span></div><div class="kurpr"><span>电费</span><span>¥{{ adminKgPanelData.elec_cost||0 }}</span></div><div class="kurpr"><span>维修费</span><span>¥{{ adminKgPanelData.repair_cost||0 }}</span></div><div class="kurpr total"><span>合计</span><span>¥{{ adminKgPanelData.total||0 }}</span></div></div>
                </template>
                <!-- ====== 标签/能耗 ====== -->
                <template v-else-if="adminKgPanelData.type==='tag'">
                  <h4 class="kurp-dname">{{ adminKgPanelData.name }}</h4>
                  <div class="kurp-rows"><div class="kurpr"><span>标签值</span><span>{{ adminKgPanelData.value||'--' }}</span></div></div>
                </template>
                <!-- ====== 月度用电/成员 ====== -->
                <template v-else>
                  <h4 class="kurp-dname">{{ adminKgPanelData.name }}</h4>
                  <div class="kurp-rows">
                    <div v-for="(v,k) in adminKgPanelData" :key="k" class="kurpr"><span>{{ k }}</span><span>{{ typeof v==='object'?'--':v||'--' }}</span></div>
                  </div>
                </template>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- ========== 数据管理 ========== -->
    <div v-if="tab === 'data'">
      <div class="data-subtabs">
        <button :class="['dtab',{active:dataSub==='users'}]" @click="dataSub='users';loadDataTab()">用户管理</button>
        <button :class="['dtab',{active:dataSub==='devices'}]" @click="dataSub='devices';loadDataTab()">设备管理</button>
        <button :class="['dtab',{active:dataSub==='repairs'}]" @click="dataSub='repairs';loadDataTab()">维修审核</button>
        <button :class="['dtab',{active:dataSub==='announcements'}]" @click="dataSub='announcements';loadDataTab()">系统公告</button>
        <button :class="['dtab',{active:dataSub==='messages'}]" @click="dataSub='messages';loadDataTab()">用户留言</button>
      </div>

      <!-- 用户管理 -->
      <div v-if="dataSub==='users'" class="data-table-wrap">
        <div class="dt-toolbar"><button class="btn-sm primary" @click="showUserForm=true;editUserForm={username:'',real_name:'',password:''}">+ 新增用户</button><input v-model="userSearch" placeholder="搜索姓名/用户名..." class="af-input dt-search"/></div>
        <div v-if="showUserForm" class="user-form"><input v-model="editUserForm.username" placeholder="用户名" class="af-input"/><input v-model="editUserForm.real_name" placeholder="姓名" class="af-input"/><input v-model="editUserForm.password" placeholder="密码" class="af-input" type="password"/><button class="btn-sm primary" @click="createUser">创建</button><button class="btn-sm" @click="showUserForm=false">取消</button></div>
        <div v-if="dataLoading" class="empty-hint">加载中...</div>
        <div v-else-if="isEmpty(filteredUsers)" class="empty-hint">暂无用户数据</div>
        <table class="dt" v-else><thead><tr><th>户号</th><th>用户名</th><th>姓名</th><th>电话</th><th>设备</th><th>操作</th></tr></thead>
          <tbody><tr v-for="u in filteredUsers" :key="u.household_id"><td>{{ u.household_id }}</td><td>{{ u.username }}</td><td>{{ u.real_name }}</td><td>{{ u.phone||'-' }}</td><td>{{ u.device_count }}</td><td class="dt-actions"><button class="btn-sm" @click="openUserDetail(u.household_id)">详情</button><button class="btn-sm" @click="openEditForm(u)">编辑</button><button class="btn-sm" @click="deleteUser(u.household_id)">删除</button></td></tr></tbody>
        </table>
      </div>

      <!-- 设备管理 -->
      <div v-if="dataSub==='devices'" class="data-table-wrap">
        <div class="dt-toolbar"><input v-model="deviceSearch" placeholder="搜索设备名..." class="af-input dt-search"/><select v-model="deviceCatFilter" class="kf-sel"><option value="all">全部类别</option><option v-for="c in categories" :key="c" :value="c">{{ c }}</option></select></div>
        <div v-if="dataLoading" class="empty-hint">加载中...</div>
        <div v-else-if="isEmpty(filteredDevices)" class="empty-hint">暂无设备数据</div>
        <table class="dt" v-else><thead><tr><th>设备</th><th>类别</th><th>用户</th><th>功率</th><th>年限</th><th>损坏率</th><th>状态</th><th>操作</th></tr></thead>
          <tbody><tr v-for="d in filteredDevices" :key="d.device_id"><td>{{ d.custom_name||d.device_name }}</td><td>{{ d.category }}</td><td>{{ d.household_name }}</td><td>{{ d.effective_power||d.rated_power }}W</td><td>{{ d.usage_years?.toFixed?.(1)||d.usage_years }}年</td><td :class="d.damage_probability>0.5?'text-red':''">{{ ((d.damage_probability||0)*100).toFixed(1) }}%</td><td><span :class="d.is_active?'stat-ok':'stat-bad'">{{ d.is_active?'正常':'损坏' }}</span></td><td><button class="btn-del" @click="deleteDevice(d.device_id)">删除</button></td></tr></tbody>
        </table>
      </div>

      <!-- 维修审核 -->
      <div v-if="dataSub==='repairs'" class="data-table-wrap">
        <div class="dt-toolbar"><select v-model="repairStatus" class="kf-sel"><option value="all">全部状态</option><option value="1">待处理</option><option value="2">已派单</option><option value="3">维修中</option><option value="4">已完成</option></select></div>
        <div v-if="dataLoading" class="empty-hint">加载中...</div>
        <div v-else-if="isEmpty(filteredRepairs)" class="empty-hint">暂无维修工单</div>
        <table class="dt" v-else><thead><tr><th>单号</th><th>用户</th><th>设备</th><th>故障</th><th>状态</th><th>费用</th><th>操作</th></tr></thead>
          <tbody><tr v-for="o in filteredRepairs" :key="o.order_id"><td class="td-mono">{{ o.order_id?.slice(-8) }}</td><td>{{ o.household_name }}</td><td>{{ o.device_name }}</td><td>{{ o.fault_text }} {{ o.fault_description?.slice(0,20) }}</td><td>{{ o.status_text }}</td><td>{{ o.repair_cost?'¥'+o.repair_cost:'-' }}</td><td class="dt-actions"><button v-if="o.status===1" class="btn-sm" @click="doAssign(o)">派单</button><button v-if="o.status===3" class="btn-sm" @click="doComplete(o)">完成</button></td></tr></tbody>
        </table>
      </div>

      <!-- 系统公告 -->
      <div v-if="dataSub==='announcements'" class="data-table-wrap">
        <div class="ann-form-bar"><input v-model="annForm.title" placeholder="公告标题" class="af-input"/><textarea v-model="annForm.content" placeholder="公告内容" class="af-textarea" rows="2"></textarea><label class="af-check"><input type="checkbox" v-model="annForm.is_pinned"/>置顶</label><button class="btn-sm primary" @click="submitAnn">发布</button></div>
        <div v-if="dataLoading" class="empty-hint">加载中...</div>
        <div v-else-if="isEmpty(sortedAnnouncements)" class="empty-hint">暂无公告</div>
        <table class="dt" v-else><thead><tr><th>标题</th><th>内容</th><th>置顶</th><th>日期</th><th>操作</th></tr></thead><tbody><tr v-for="a in sortedAnnouncements" :key="a.id"><td>{{ a.title }}</td><td class="td-desc">{{ a.content.slice(0,60) }}...</td><td>{{ a.is_pinned?'是':'否' }}</td><td>{{ a.created_at?.slice(0,10) }}</td><td><button class="btn-del" @click="confirmDelAnn(a.id)">删除</button></td></tr></tbody></table>
      </div>

      <!-- 用户留言 -->
      <div v-if="dataSub==='messages'" class="data-table-wrap">
        <div v-if="dataLoading" class="empty-hint">加载中...</div>
        <div v-else-if="isEmpty(dataMessages)" class="empty-hint">暂无留言</div>
        <table class="dt" v-else><thead><tr><th>用户</th><th>内容</th><th>回复</th><th>日期</th><th>操作</th></tr></thead><tbody><template v-for="m in dataMessages" :key="m.id"><tr><td>{{ m.household_name }}</td><td>{{ m.content }}</td><td>{{ m.reply||'未回复' }}</td><td>{{ m.created_at?.slice(0,10) }}</td><td class="dt-actions"><button v-if="!m.reply" class="btn-sm" @click="toggleReply(m)">回复</button><button class="btn-del" @click="confirmDelMsg(m.id)">删除</button></td></tr><tr v-if="replyForm.id===m.id" class="reply-row"><td colspan="5"><div class="reply-inline"><input v-model="replyForm.text" placeholder="输入回复..." class="af-input" style="flex:1"/><button class="btn-sm primary" @click="doReply(replyForm.id,replyForm.text)">确认</button><button class="btn-sm" @click="replyForm.id=null">取消</button></div></td></tr></template></tbody></table>
      </div>

      <!-- 用户详情弹窗 -->
      <Teleport to="body"><Transition name="pop"><div class="pop-overlay" v-if="userDetail" @click.self="userDetail=null"><div class="pop-detail">
        <div class="pd-head"><h3>{{ userDetail.household?.real_name || userDetail.username }}</h3><span class="pd-id">{{ userDetail.household?.household_id }}</span><button class="ph-close" @click="userDetail=null">×</button></div>
        <div class="pd-body" v-if="userDetail.household">
          <div class="pd-sec"><div class="pd-st">基本信息</div><div class="pd-grid"><div class="pdg"><span>性别</span><span>{{ {1:'男',2:'女'}[userDetail.household.gender]||'--' }}</span></div><div class="pdg"><span>出生</span><span>{{ userDetail.household.birth_year||'--' }}年{{ userDetail.household.birth_month||'--' }}月</span></div><div class="pdg"><span>学历</span><span>{{ optLabelShort(userDetail.household.education_level,'education') }}</span></div><div class="pdg"><span>婚姻</span><span>{{ optLabelShort(userDetail.household.marital_status,'marital') }}</span></div><div class="pdg"><span>职业</span><span>{{ optLabelShort(userDetail.household.occupation,'occupation') }}</span></div><div class="pdg"><span>电话</span><span>{{ userDetail.household.phone||'--' }}</span></div><div class="pdg"><span>作息</span><span>{{ optLabelShort(userDetail.household.daily_schedule,'schedule') }}</span></div><div class="pdg"><span>健康</span><span>{{ optLabelShort(userDetail.household.self_health,'health') }}</span></div><div class="pdg full"><span>地址</span><span>{{ userDetail.household.address_detail||'--' }}</span></div></div></div>
          <div class="pd-sec" v-if="userDetail.housing?.housing_type"><div class="pd-st">住房</div><div class="pd-grid"><div class="pdg"><span>类型</span><span>{{ optLabelShort(userDetail.housing.housing_type,'housing_type') }}</span></div><div class="pdg"><span>面积</span><span>{{ userDetail.housing.housing_area||'--' }} m²</span></div><div class="pdg"><span>户型</span><span>{{ userDetail.housing.bedroom_count }}室{{ userDetail.housing.living_room_count }}厅</span></div><div class="pdg"><span>楼层</span><span>{{ userDetail.housing.floor_level||'--' }}/{{ userDetail.housing.total_floors||'--' }}</span></div></div></div>
          <div class="pd-sec" v-if="userDetail.income?.personal_income"><div class="pd-st">收入</div><div class="pd-grid"><div class="pdg"><span>个人</span><span>¥{{ Number(userDetail.income.personal_income).toLocaleString() }}</span></div><div class="pdg"><span>家庭</span><span>¥{{ Number(userDetail.income.household_income).toLocaleString() }}</span></div></div></div>
          <div class="pd-sec"><div class="pd-st">用电</div><div class="pd-device-list" v-if="userDetail.devices?.length"><div v-for="d in userDetail.devices" :key="d.device_id" class="pdd"><span>{{ d.custom_name||d.device_name }}</span><span>{{ d.category }} · {{ d.effective_power||d.rated_power }}W · {{ d.usage_years?.toFixed?.(1)||d.usage_years }}年 <span :class="(d.damage_probability||0)>0.5?'text-red':''">{{ ((d.damage_probability||0)*100).toFixed(1) }}%</span></span></div></div><div v-else class="empty-hint">暂无设备</div></div>
          <div class="pd-sec" v-if="userDetail.bills?.length"><div class="pd-st">账单 (已缴{{ userDetail.total_paid }}/{{ userDetail.bill_count }})</div><div class="pd-grid"><div v-for="b in userDetail.bills" :key="b.bill_id" class="pdg"><span>{{ b.bill_month }}</span><span>{{ b.total_kwh }}kWh · ¥{{ b.total_amount }} · {{ b.status===2?'已缴':'未缴' }}</span></div></div></div>
          <div class="pd-sec" v-if="userDetail.family_members?.length"><div class="pd-st">家庭成员</div><div v-for="m in userDetail.family_members" :key="m.name" class="pbr"><span>{{ {2:'配偶',3:'子女',4:'父母',5:'岳父母/公婆',6:'兄弟姐妹',7:'其他'}[m.relation]||'亲属' }}</span><span>{{ m.name }}</span></div></div>
        </div>
      </div></div></Transition></Teleport>
    </div>

    <!-- 用户编辑弹窗 -->
    <Teleport to="body"><Transition name="pop"><div class="pop-overlay" v-if="showEditForm" @click.self="showEditForm=false"><div class="pop-dialog" style="max-width:480px"><h3>编辑用户</h3>
      <div class="pd-grid"><div class="pdg"><span>姓名</span><input v-model="editForm.real_name" class="af-input s"/></div><div class="pdg"><span>电话</span><input v-model="editForm.phone" class="af-input s"/></div><div class="pdg"><span>性别</span><select v-model="editForm.gender" class="kf-sel"><option value="">--</option><option value="1">男</option><option value="2">女</option></select></div><div class="pdg"><span>出生年</span><input v-model="editForm.birth_year" class="af-input s" placeholder="年份"/></div><div class="pdg"><span>出生月</span><input v-model="editForm.birth_month" class="af-input s" placeholder="月份"/></div><div class="pdg"><span>学历</span><select v-model="editForm.education_level" class="kf-sel"><option value="">--</option><option value="1">小学</option><option value="2">初中</option><option value="3">高中</option><option value="4">大专</option><option value="5">本科</option><option value="6">硕士</option><option value="7">博士</option></select></div><div class="pdg"><span>职业</span><input v-model="editForm.occupation" class="af-input s"/></div><div class="pdg full"><span>地址</span><input v-model="editForm.address_detail" class="af-input" style="width:100%"/></div></div>
      <div class="pop-actions"><button class="btn-sm" @click="showEditForm=false">取消</button><button class="btn-sm primary" @click="doEdit">保存</button></div>
    </div></div></Transition></Teleport>

    <!-- 删除确认弹窗 -->
    <Teleport to="body"><Transition name="pop"><div class="pop-overlay" v-if="delTarget" @click.self="delTarget=null"><div class="pop-dialog"><h3>确认删除</h3><p>删除后不可恢复，确定吗？</p><div class="pop-actions"><button class="btn-sm" @click="delTarget=null">取消</button><button class="btn-sm danger" @click="doDel">确认删除</button></div></div></div></Transition></Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import {
  getAdminDashboard, advanceSystemMonth, getSystemMonth,
  getAdminAnnouncements, createAnnouncement, deleteAnnouncement,
  getAdminMessages, replyMessage, deleteMessage, getAdminUsers,
  getAdminRepairOrders, getAdminUserDetail, getUserKGById, getOptions,
  getMyDevices, assignRepair, completeRepair,
  adminCreateUser, adminDeleteUser, adminEditUser, deleteDevice as apiDeleteDevice,
} from '../api'

const route = useRoute()
const tab = computed(() => {
  if (route.path === '/admin/kg') return 'kg'
  if (route.path === '/admin/data') return 'data'
  return 'dashboard'
})

// 概览
const stats = reactive({ total_users:0,total_devices:0,active_devices:0,damaged_devices:0,pending_repairs:0,bills_collected:'0/0',total_months_elapsed:0,unit_price:0 })
const sysMonth = ref(''); const advancing = ref(false); const advanceResult = ref(null); const advanceError = ref('')
const adminAnns = ref([]); const showAnnForm = ref(false); const annForm = reactive({title:'',content:'',is_pinned:false})
const adminMsgs = ref([]); const replyForm = reactive({id:null,text:''}); const delTarget = ref(null); const delType = ref('')

async function loadOverview() {
  const [a,s,ann,msg,oRes] = await Promise.all([getAdminDashboard(),getSystemMonth(),getAdminAnnouncements(),getAdminMessages(),getOptions()])
  Object.assign(stats,a.data.stats); sysMonth.value=s.data.year_month; adminAnns.value=ann.data.announcements||[]; adminMsgs.value=msg.data.messages||[]
  adminOptions.value = oRes.data.options || {}
}
onMounted(loadOverview)

async function handleAdvance() { if(!confirm('确定推进至下月？'))return; advancing.value=true; try{const r=await advanceSystemMonth();advanceResult.value=r.data;await loadOverview()}catch(e){advanceError.value=e.response?.data?.message||'失败'}finally{advancing.value=false} }
async function submitAnn() { if(!annForm.title.trim())return; await createAnnouncement(annForm); showAnnForm.value=false; annForm.title='';annForm.content='';annForm.is_pinned=false; const r=await getAdminAnnouncements();adminAnns.value=r.data.announcements||[] }
function confirmDelAnn(id) { delTarget.value=id; delType.value='ann' }
function confirmDelMsg(id) { delTarget.value=id; delType.value='msg' }
async function doDel() {
  if(delType.value==='ann'){await deleteAnnouncement(delTarget.value);const r=await getAdminAnnouncements();adminAnns.value=r.data.announcements||[]}
  else if(delType.value==='msg'){await deleteMessage(delTarget.value);const r=await getAdminMessages();adminMsgs.value=r.data.messages||[]}
  delTarget.value=null;delType.value=''
}
async function doReply(id,text) { await replyMessage(id,text); const r=await getAdminMessages();adminMsgs.value=r.data.messages||[]; replyForm.id=null;replyForm.text='' }

// ========== 知识图谱 (用户视角) ==========
const adminKgUser = ref('')
const adminKgData = ref(null)
const adminKgUserInfo = ref(null)
const adminKgHousing = ref(null)
const adminKgIncome = ref(null)
const adminKgPanelOpen = ref(true)
const adminKgPanelData = ref(null)
const adminVisibleNodes = ref(0)
const adminVisibleLinks = ref(0)
const adminUserKgChart = ref(null)
const adminTrendChart = ref(null)
const adminWordCloud = ref(null)
let adminKgInstance = null
const adminExpandedGroups = new Set()
const adminOptions = ref({})
const adminKgEnergyColor = ref('#999')

function adminKgOptLabel(cat, val) {
  if (val === null || val === undefined || val === '') return '--'
  const opts = adminOptions.value[cat]
  if (!opts) return String(val)
  const found = opts.find(o => String(o.item_key) === String(val))
  return found ? found.item_value : String(val)
}

async function loadAdminUserKG() {
  if (!adminKgUser.value || !adminUserKgChart.value) return
  try {
    const hid = adminKgUser.value
    const [kgRes, hRes, oRes] = await Promise.all([
      getUserKGById(hid),
      getAdminUserDetail(hid),
      getOptions()
    ])
    adminKgData.value = kgRes.data
    adminKgUserInfo.value = hRes.data.household || hRes.data.user || {}
    adminKgHousing.value = hRes.data.housing || {}
    adminKgIncome.value = hRes.data.income || {}
    adminOptions.value = oRes.data.options || {}

    const el = adminKgData.value.summary?.energy_level
    adminKgEnergyColor.value = { '节能型': '#67c23a', '普通型': '#5470c6', '摆渡型': '#e6a23c', '高耗能型': '#e74c3c' }[el] || '#999'

    adminExpandedGroups.clear()
    await nextTick()
    renderAdminKG()
    renderAdminTrend()
    renderAdminWordCloud()
  } catch(e) { console.error(e) }
}

function getAdminVisible() {
  if (!adminKgData.value) return { nodes: [], links: [] }
  const allNodes = adminKgData.value.nodes
  const allLinks = adminKgData.value.links
  const m = new Set()
  allNodes.forEach(n => {
    if (n.group === 'center' || n.group === 'category') m.add(n.id)
    if (n.group && adminExpandedGroups.has(n.group)) m.add(n.id)
  })
  const vn = allNodes.filter(n => m.has(n.id))
  const vi = new Set(vn.map(n => n.id))
  const vl = allLinks.filter(l => vi.has(l.source) && vi.has(l.target))
  adminVisibleNodes.value = vn.length
  adminVisibleLinks.value = vl.length
  return { nodes: vn, links: vl }
}

function renderAdminKG() {
  if (!adminUserKgChart.value || !adminKgData.value) return
  if (adminKgInstance) adminKgInstance.dispose()
  adminKgInstance = echarts.init(adminUserKgChart.value)
  const cats = [
    { name: 'user', itemStyle: { color: '#3b82f6' } },
    { name: 'category', itemStyle: { color: '#ebf0f5', borderColor: '#c8d6e5', borderWidth: 2 } },
    { name: 'device', itemStyle: { color: '#a8d8ea' } },
    { name: 'sub', itemStyle: { color: '#91c7ae' } },
  ]
  const userNode = adminKgData.value.nodes.find(n => n.group === 'center')
  if (userNode?.detail) { adminKgPanelData.value = userNode.detail; adminKgPanelOpen.value = true }

  function doRender() {
    const { nodes, links } = getAdminVisible()
    adminKgInstance.setOption({
      tooltip: { trigger: 'item', formatter: p => p.dataType === 'node' ? `<b>${p.name}</b>` : '' },
      series: [{
        type: 'graph', layout: 'force', roam: true, draggable: true,
        force: { repulsion: 180, edgeLength: [60, 140], gravity: 0.15, friction: 0.4 },
        data: nodes, links, categories: cats,
        label: { show: true, fontSize: 12, color: '#444' },
        lineStyle: { color: '#bcc4d0', curveness: 0.15, opacity: 0.7, width: 2 },
        emphasis: { focus: 'adjacency', lineStyle: { width: 4, color: '#5b8def' }, itemStyle: { shadowBlur: 30 }, label: { fontSize: 14, fontWeight: 600 } },
        animationDurationUpdate: 600,
      }],
    }, true)
  }
  doRender()
  let ct = null
  adminKgInstance.off('click').on('click', p => {
    if (p.dataType === 'node' && p.data?.detail) {
      if (ct) { clearTimeout(ct); ct = null; return }
      ct = setTimeout(() => { adminKgPanelData.value = p.data.detail; adminKgPanelOpen.value = true; ct = null }, 300)
    }
  })
  adminKgInstance.off('dblclick').on('dblclick', p => {
    if (ct) { clearTimeout(ct); ct = null }
    if (p.dataType === 'node' && p.data.group === 'category') {
      const g = p.data.id
      adminExpandedGroups.has(g) ? adminExpandedGroups.delete(g) : adminExpandedGroups.add(g)
      doRender()
    }
  })
  new ResizeObserver(() => adminKgInstance?.resize()).observe(adminUserKgChart.value)
}

function renderAdminTrend() {
  if (!adminTrendChart.value || !adminKgData.value?.summary) return
  const c = echarts.init(adminTrendChart.value)
  const trend = adminKgData.value.nodes?.find(n => n.group === 'center')?.detail?.trend || []
  c.setOption({
    grid: { top: 8, right: 8, bottom: 16, left: 36 },
    xAxis: { type: 'category', data: trend.map(t => t.month), axisLabel: { fontSize: 8, rotate: 30 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#f0f0f0' } }, axisLabel: { fontSize: 9 } },
    series: [{ type: 'line', data: trend.map(t => t.kwh), smooth: true, lineStyle: { color: '#5470c6' }, areaStyle: { color: 'rgba(84,112,198,0.1)' }, symbol: 'none' }],
  })
}

function renderAdminWordCloud() {
  if (!adminWordCloud.value || !adminKgData.value) return
  const d = adminKgData.value
  const colors = ['#3b82f6', '#5470c6', '#67c23a', '#e6a23c', '#91cc75', '#73c0de', '#fc8452', '#8b5cf6', '#f59e0b', '#10b981']
  const allNames = []
  const uNode = d.nodes?.find(n => n.group === 'center')
  if (uNode?.detail) {
    const de = uNode.detail
    if (de.info) Object.entries(de.info).forEach(([k, v]) => { if (v && v !== '--' && v.length < 20) allNames.push(v) })
    if (de.energy?.level) allNames.push(de.energy.level)
    if (de.housing) {
      if (de.housing.type && de.housing.type !== '--') allNames.push(de.housing.type)
      if (de.housing.heating && de.housing.heating !== '--') allNames.push(de.housing.heating)
      if (de.housing.orientation && de.housing.orientation !== '--') allNames.push(de.housing.orientation)
    }
    if (de.members) de.members.forEach(m => { if (m.relation) allNames.push(m.relation) })
  }
  d.nodes?.filter(n => n.category === 'device').forEach(nd => {
    if (nd.name) allNames.push(nd.name)
    if (nd.detail?.category) allNames.push(nd.detail.category)
    if (nd.detail?.brand && nd.detail.brand !== '') allNames.push(nd.detail.brand)
    if (nd.detail?.habit && nd.detail.habit !== '') allNames.push(nd.detail.habit)
  })
  d.nodes?.filter(n => n.category === 'sub' && n.hidden).forEach(nd => {
    if (nd.name && nd.name.length < 15) allNames.push(nd.name)
  })
  if (d.summary?.energy_level) allNames.push(d.summary.energy_level)
  const unique = [...new Set(allNames)]
  const cloudWords = unique.map(n => ({ name: n, w: 9 + Math.random() * 10 }))
  adminWordCloud.value.innerHTML = cloudWords.sort(() => Math.random() - 0.5).slice(0, 35).map(w =>
    `<span style="font-size:${w.w}px;color:${colors[Math.floor(Math.random()*colors.length)]};margin:1px 4px;display:inline-block;line-height:1.4">${w.name}</span>`
  ).join('')
}

const dataSub=ref('users')
const dataUsers=ref([]);const dataDevices=ref([]);const dataRepairs=ref([]);const dataAnnouncements=ref([]);const dataMessages=ref([])
const userDetail=ref(null)
const showUserForm=ref(false);const editUserForm=reactive({username:'',real_name:'',password:''})
const dataLoading=ref(false)
// 搜索和筛选
const userSearch=ref('')
const deviceSearch=ref('');const deviceCatFilter=ref('all')
const repairStatus=ref('all')
// 用户编辑
const showEditForm=ref(false);const editForm=reactive({household_id:'',real_name:'',phone:'',gender:'',birth_year:'',birth_month:'',education_level:'',occupation:'',address_detail:''})

// 选项标签简写
function optLabelShort(val, cat) {
  if (val === null || val === undefined || val === '') return '--'
  const map = adminOptions.value[cat]
  if (!map) return String(val)
  const found = map.find(o => String(o.item_key) === String(val))
  return found ? found.item_value : String(val)
}

function toggleReply(m) { replyForm.id = m.id; replyForm.text = '' }

function openEditForm(u) {
  const h = u._household || u
  editForm.household_id = u.household_id
  editForm.real_name = h.real_name || u.real_name || ''
  editForm.phone = h.phone || u.phone || ''
  editForm.gender = h.gender || ''
  editForm.birth_year = h.birth_year || ''
  editForm.birth_month = h.birth_month || ''
  editForm.education_level = h.education_level || ''
  editForm.occupation = h.occupation || ''
  editForm.address_detail = h.address_detail || ''
  showEditForm.value = true
}

async function doEdit() {
  if (!editForm.household_id) return
  await adminEditUser(editForm.household_id, { ...editForm })
  showEditForm.value = false
  loadDataTab()
}

// 筛选后的数据
const filteredUsers = computed(() => {
  if (!userSearch.value) return dataUsers.value
  const q = userSearch.value.toLowerCase()
  return dataUsers.value.filter(u => (u.username||'').toLowerCase().includes(q) || (u.real_name||'').toLowerCase().includes(q))
})
const filteredDevices = computed(() => {
  let arr = dataDevices.value
  if (deviceSearch.value) {
    const q = deviceSearch.value.toLowerCase()
    arr = arr.filter(d => (d.custom_name||d.device_name||'').toLowerCase().includes(q))
  }
  if (deviceCatFilter.value !== 'all') {
    arr = arr.filter(d => d.category === deviceCatFilter.value)
  }
  return arr
})
const categories = computed(() => [...new Set(dataDevices.value.map(d=>d.category).filter(Boolean))])
const filteredRepairs = computed(() => {
  if (repairStatus.value === 'all') return dataRepairs.value
  return dataRepairs.value.filter(r => r.status === parseInt(repairStatus.value))
})
const sortedAnnouncements = computed(() => {
  return [...dataAnnouncements.value].sort((a,b) => {
    if (a.is_pinned !== b.is_pinned) return b.is_pinned - a.is_pinned
    return (b.created_at||'').localeCompare(a.created_at||'')
  })
})

function isEmpty(arr) { return !arr || arr.length === 0 }

async function loadDataTab() {
  dataLoading.value = true
  try {
    if(dataSub.value==='users'){const r=await getAdminUsers();dataUsers.value=r.data.users||[]}
    if(dataSub.value==='devices'){const r=await getMyDevices();dataDevices.value=r.data.devices||[]}
    if(dataSub.value==='repairs'){const r=await getAdminRepairOrders();dataRepairs.value=r.data.orders||[]}
    if(dataSub.value==='announcements'){const r=await getAdminAnnouncements();dataAnnouncements.value=r.data.announcements||[]}
    if(dataSub.value==='messages'){const r=await getAdminMessages();dataMessages.value=r.data.messages||[]}
  } finally { dataLoading.value = false }
}
watch(tab,(v)=>{if(v==='kg'){loadDataTab().then(()=>{if(dataUsers.value.length){if(!adminKgUser.value)adminKgUser.value=dataUsers.value[0]?.household_id||'';setTimeout(()=>loadAdminUserKG(),200)}})}; if(v==='data')loadDataTab()},{immediate:true})

async function openUserDetail(hid){const r=await getAdminUserDetail(hid);userDetail.value=r.data}
async function doAssign(o){const n=prompt('维修人员：','张师傅');if(n){await assignRepair(o.order_id,n);loadDataTab()}}
async function doComplete(o){const c=prompt('费用(元)：','100');if(c){await completeRepair(o.order_id,{repair_cost:parseFloat(c),repair_result:'已修复'});loadDataTab()}}

async function createUser(){if(!editUserForm.username)return;await adminCreateUser(editUserForm);showUserForm.value=false;loadDataTab()}
async function deleteUser(hid){if(!confirm('确定删除用户 '+hid+' ？'))return;await adminDeleteUser(hid);loadDataTab()}
async function deleteDevice(did){if(!confirm('确定删除？'))return;await apiDeleteDevice(did);loadDataTab()}
async function deleteRepair(oid){if(!confirm('确定删除？'))return;await deleteMessage(oid);loadDataTab()}
</script>

<style scoped>
.admin-page{padding:20px 24px;width:100%;box-sizing:border-box}
.page-top{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:18px}
.page-top h2{font-size:18px;font-weight:500;color:#2c3e50;margin:0}

/* 统计 */
.stats-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px}
.st-card{background:#fff;border:1px solid #edf0f4;border-radius:8px;padding:18px;text-align:center}
.st-val{font-size:24px;font-weight:600;color:#2c3e50}
.st-lbl{font-size:11px;color:#999;margin-top:4px}

.advance-section{margin-bottom:16px}
.advance-card{background:linear-gradient(135deg,#5470c6,#3b82f6);border-radius:10px;padding:20px;text-align:center;color:#fff}
.current-month-value{font-size:32px;font-weight:700;display:block}
.current-month-label{font-size:12px;opacity:.8}
.elapsed-label{font-size:11px;opacity:.6;display:block;margin-top:4px}
.advance-btn{padding:10px 36px;background:#fff;color:#5470c6;border:none;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;margin-top:12px;font-family:inherit}
.advance-btn:disabled{opacity:.6}
.advance-result{background:#ecf8e8;border:1px solid #91cc75;border-radius:6px;padding:10px 14px;margin-top:10px;font-size:12px}
.advance-error{background:#fde8e8;border:1px solid #ee6666;border-radius:6px;padding:10px 14px;margin-top:10px;font-size:12px;color:#c33}
.advance-hint{font-size:11px;opacity:.7;margin-top:6px}

/* 面板 */
.panel{background:#fff;border:1px solid #edf0f4;border-radius:8px;margin-bottom:14px;overflow:hidden}
.panel-head{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-bottom:1px solid #f0f2f5}
.panel-head h3{font-size:13px;font-weight:600;color:#555;margin:0}

.ann-form{padding:12px 16px;display:flex;gap:8px;align-items:center;flex-wrap:wrap;border-bottom:1px solid #f0f2f5}
.af-input{padding:6px 10px;border:1px solid #e0e0e0;border-radius:4px;font-size:12px;outline:none;font-family:inherit}
.af-textarea{padding:6px 10px;border:1px solid #e0e0e0;border-radius:4px;font-size:12px;outline:none;resize:vertical;font-family:inherit}
.af-input.s{width:100px}
.af-check{font-size:11px;color:#888;display:flex;align-items:center;gap:4px}
.ann-list{padding:4px 10px}
.ann-row,.msg-row{display:flex;justify-content:space-between;align-items:center;padding:8px 6px;border-bottom:1px solid #f8f9fb;gap:10px}
.ann-row:last-child,.msg-row:last-child{border-bottom:none}
.ar-info{display:flex;flex-direction:column;gap:2px}
.ar-info span{font-size:12px;color:#333}.ar-info span.pinned{color:#e6a23c}
.ar-text{font-size:10px;color:#999}
.ar-actions,.mr-right{display:flex;align-items:center;gap:8px;flex-shrink:0}
.ar-date{font-size:10px;color:#ccc}
.mr-left{display:flex;flex-direction:column;gap:2px;flex:1}
.mr-user{font-size:12px;font-weight:600;color:#2c3e50}
.mr-content{font-size:11px;color:#555}
.mr-date{font-size:10px;color:#ccc}
.mr-replied{font-size:11px;color:#67c23a}
.reply-inline{display:flex;gap:4px;align-items:center}
.btn-sm{padding:4px 12px;border:1px solid #e0e0e0;border-radius:4px;background:#fff;font-size:11px;color:#666;cursor:pointer;font-family:inherit}
.btn-sm.primary{background:#2c3e50;color:#fff;border-color:#2c3e50}
.btn-sm:hover{border-color:#5470c6;color:#5470c6}
.btn-sm.primary:hover{background:#5470c6}
.btn-del{font-size:11px;padding:3px 8px;border:1px solid #e0e0e0;background:#fff;color:#e74c3c;border-radius:4px;cursor:pointer;font-family:inherit}
.btn-del:hover{background:#fde8e8}
.empty-hint{text-align:center;padding:20px;color:#ccc;font-size:12px}

/* KG */
/* KG user view */
.kg-user-wrap{display:flex;flex-direction:column;height:calc(100vh - 130px)}
.kg-user-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-shrink:0}
.kg-count{font-size:11px;color:#aaa}
.kg-user-sel{padding:6px 12px;border:1px solid #d0d0d0;border-radius:6px;font-size:12px;color:#333;background:#fff;outline:none;cursor:pointer;font-family:inherit}
.kg-user-layout{flex:1;display:flex;gap:12px;overflow:hidden;min-height:0}
.kg-user-left{width:260px;flex-shrink:0;display:flex;flex-direction:column;gap:8px;overflow-y:auto;padding-right:4px}
.kg-user-right{flex:1;display:flex;gap:0;overflow:hidden;min-height:0}
.kur-chart{flex:1;background:#fafbfc;border:1px solid #edf0f4;border-radius:8px 0 0 8px;overflow:hidden}
.kur-panel{flex-shrink:0;background:#fff;border:1px solid #edf0f4;border-left:none;border-radius:0 8px 8px 0;display:flex;flex-direction:column;transition:width .25s;overflow:hidden;width:44px}
.kur-panel.open{width:300px}
.kurp-trigger{display:flex;flex-direction:column;align-items:center;gap:6px;padding:18px 10px;cursor:pointer;color:#999;user-select:none}
.kurp-text{font-size:10px;writing-mode:vertical-rl}
.kurp-head{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;font-size:13px;font-weight:600;color:#555;border-bottom:1px solid #f0f2f5;background:#fafbfc}
.kurp-close{background:none;border:none;font-size:16px;color:#999;cursor:pointer}
.kurp-body{padding:12px 14px;overflow-y:auto;flex:1}
.kurp-dname{font-size:14px;font-weight:600;color:#2c3e50;margin:0 0 8px}
.kurp-rows{display:flex;flex-direction:column;gap:6px}
.kurpr{display:flex;justify-content:space-between;font-size:11px;color:#888;padding:3px 0}
.kurpr span:first-child{color:#aaa}
.kurpr.total{font-weight:600;color:#555}
.kurpr span.on{color:#67c23a}.kurpr span.off{color:#e74c3c}.kurpr span.warn{color:#e6a23c}
.c-on{color:#67c23a}.c-off{color:#e74c3c}.c-red{color:#e74c3c}
/* admin panel enhanced */
.kurp-sec{margin-top:12px}
.kurp-sec-t{font-size:10px;color:#888;margin-bottom:4px;padding-bottom:3px;border-bottom:1px solid #f0f2f5}
.kurp-badge-s{display:inline-block;padding:2px 10px;border-radius:10px;font-size:10px;color:#fff;margin-bottom:8px}
.kurp-metrics{display:flex;gap:6px;margin-bottom:10px}
.kurpm{flex:1;text-align:center;padding:6px 4px;background:#f8f9fb;border-radius:6px}
.kurpm-val{font-size:14px;font-weight:700;color:#2c3e50}
.kurpm-val.on{color:#67c23a}.kurpm-val.off{color:#e74c3c}
.kurpm-lbl{font-size:9px;color:#bbb;margin-top:1px}
/* left card */
.kul-avatar-section{background:#fff;border:1px solid #edf0f4;border-radius:8px;padding:12px;text-align:center}
.kul-avatar{width:44px;height:44px;border-radius:50%;background:#5470c6;color:#fff;font-size:20px;font-weight:600;line-height:44px;margin:0 auto 6px}
.kul-name{font-size:15px;font-weight:600;color:#2c3e50}
.kul-tags{display:flex;flex-wrap:wrap;justify-content:center;gap:4px;margin-top:6px}
.kult{font-size:10px;background:#f0f2f5;color:#666;padding:1px 7px;border-radius:8px}
.kul-metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}
.kulm-item{background:#fff;border:1px solid #edf0f4;border-radius:8px;padding:10px 6px;text-align:center}
.kulm-val{font-size:16px;font-weight:700;color:#2c3e50}
.kulm-lbl{font-size:9px;color:#999;margin-top:2px}
.kul-wordcloud{background:#fff;border:1px solid #edf0f4;border-radius:8px;padding:8px;max-height:160px;overflow-y:auto;line-height:1.5}
.kul-table{background:#fff;border:1px solid #edf0f4;border-radius:8px;padding:8px 12px}
.kult-row{display:flex;justify-content:space-between;font-size:11px;padding:3px 0;border-bottom:1px solid #f8f9fb}
.kult-row:last-child{border-bottom:none}
.kult-row span:first-child{color:#999}
.kult-row span:last-child{color:#333}
.kul-chart{width:100%;height:120px;background:#fff;border:1px solid #edf0f4;border-radius:8px}
.text-red{color:#ff4d4f!important}
.stat-ok{color:#52c41a}.stat-bad{color:#ff4d4f}

/* 数据管理 */
.data-table-wrap{overflow-x:auto}
.dt-toolbar{margin-bottom:10px;display:flex;gap:8px;align-items:center}
.dt-search{width:180px}
.dt-actions{display:flex;gap:4px}
.user-form{display:flex;gap:8px;align-items:center;margin-bottom:12px;flex-wrap:wrap}
.td-mono{font-family:monospace;font-size:11px;color:#999}
.td-desc{max-width:200px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ann-form-bar{display:flex;gap:8px;align-items:center;padding:10px 0;flex-wrap:wrap}
.reply-row td{padding:8px 10px;background:#fafbfc}
.reply-inline{display:flex;gap:6px;align-items:center}

/* 详情弹窗 */
.pop-detail{background:#fff;border-radius:10px;width:620px;max-width:94vw;max-height:85vh;overflow-y:auto}
.pd-head{display:flex;align-items:center;gap:10px;padding:16px 20px;border-bottom:1px solid #f0f2f5;position:sticky;top:0;background:#fff;z-index:1}
.pd-head h3{font-size:16px;font-weight:600;color:#2c3e50;margin:0}
.pd-id{font-size:11px;color:#ccc;font-family:monospace}
.pd-body{padding:16px 20px}
.pd-sec{margin-bottom:16px}
.pd-st{font-size:10px;color:#bbb;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px;padding-bottom:4px;border-bottom:1px solid #f5f5f5}
.pd-grid{display:grid;grid-template-columns:1fr 1fr;gap:4px 16px}
.pdg{display:flex;justify-content:space-between;padding:4px 0;font-size:11px;border-bottom:1px solid #fafafa}
.pdg span:first-child{color:#aaa}
.pdg span:last-child{color:#555}
.pdg.full{grid-column:span 2}
.pd-device-list{display:flex;flex-direction:column;gap:4px}
.pdd{display:flex;justify-content:space-between;padding:4px 0;font-size:11px;border-bottom:1px solid #fafafa}
.pbr{display:flex;justify-content:space-between;padding:4px 0;font-size:11px;border-bottom:1px solid #fafafa}

/* 数据标签 */
.data-subtabs{display:flex;gap:4px;margin-bottom:14px}
.dtab{padding:6px 16px;border:1px solid #e0e0e0;border-radius:6px;background:#fff;font-size:12px;color:#888;cursor:pointer;font-family:inherit}
.dtab.active{background:#2c3e50;color:#fff;border-color:#2c3e50}
.dt{width:100%;border-collapse:collapse;font-size:12px;background:#fff;border:1px solid #edf0f4;border-radius:8px;overflow:hidden}
.dt th{padding:10px 14px;text-align:left;font-size:10px;color:#aaa;text-transform:uppercase;font-weight:500;background:#fafbfc}
.dt td{padding:10px 14px;border-top:1px solid #f5f5f5}

/* 弹窗 */
.pop-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.3);z-index:3000;display:flex;align-items:center;justify-content:center}
.pop-dialog{background:#fff;border-radius:10px;padding:28px 32px;width:360px;text-align:center}
.pop-dialog h3{font-size:15px;color:#2c3e50;margin:0 0 8px}
.pop-dialog p{font-size:12px;color:#888;margin:0 0 20px}
.pop-actions{display:flex;gap:10px;justify-content:center}
.btn-sm.danger{background:#e74c3c;color:#fff;border-color:#e74c3c}
.pop-enter-active,.pop-leave-active{transition:opacity .2s}
.pop-enter-from,.pop-leave-to{opacity:0}
</style>
