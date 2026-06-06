<template>
  <div class="profile-page">
    <div class="page-top">
      <div><h2>用电画像</h2><p class="sub">User Profile</p></div>
      <span class="node-count">{{ visibleNodes }} 个节点 · {{ visibleLinks }} 条关系</span>
    </div>

    <div class="profile-layout">
      <!-- ====== 左侧：用户画像 ====== -->
      <div class="profile-left">
        <!-- 头像区 -->
        <div class="pl-avatar-section">
          <div class="pl-avatar">{{ hh.real_name?.charAt(0) || '?' }}</div>
          <div class="pl-name">{{ hh.real_name || '--' }}</div>
          <div class="pl-tags">
            <span v-if="hh.gender" class="plt">{{ optLabel('gender', hh.gender) }}</span>
            <span v-if="hh.birth_year" class="plt">{{ hh.birth_year }}年</span>
            <span v-if="hh.education_level" class="plt">{{ optLabel('education', hh.education_level) }}</span>
            <span v-if="hh.marital_status" class="plt">{{ optLabel('marital', hh.marital_status) }}</span>
          </div>
        </div>

        <!-- 能耗指标 -->
        <div class="pl-metrics">
          <div class="plm-item">
            <div class="plm-val" :style="{color: elColor(kg?.summary?.energy_level)}">{{ kg?.summary?.energy_level || '--' }}</div>
            <div class="plm-lbl">能耗等级</div>
          </div>
          <div class="plm-item">
            <div class="plm-val">{{ kg?.summary?.avg_monthly_kwh || '--' }}</div>
            <div class="plm-lbl">月均 kWh</div>
          </div>
          <div class="plm-item">
            <div class="plm-val">{{ kg?.summary?.device_count || '--' }}</div>
            <div class="plm-lbl">设备数</div>
          </div>
          <div class="plm-item">
            <div class="plm-val">{{ kg?.summary?.paid_count || 0 }}/{{ kg?.summary?.bill_count || 0 }}</div>
            <div class="plm-lbl">已缴/总账单</div>
          </div>
        </div>

        <!-- 词云 -->
        <div class="pl-wordcloud" id="wc-cloud"></div>

        <!-- 基本信息表 -->
        <div class="pl-table">
          <div class="plt-row"><span>职业</span><span>{{ optLabel('occupation', hh.occupation) }}</span></div>
          <div class="plt-row"><span>城乡</span><span>{{ optLabel('urban', hh.is_urban) }}</span></div>
          <div class="plt-row"><span>作息</span><span>{{ optLabel('schedule', hh.daily_schedule) }}</span></div>
          <div class="plt-row"><span>健康</span><span>{{ optLabel('health', hh.self_health) }}</span></div>
          <div class="plt-row"><span>住房</span><span>{{ optLabel('housing_type', housing?.housing_type) }}</span></div>
          <div class="plt-row"><span>面积</span><span>{{ housing?.housing_area || '--' }} m²</span></div>
          <div class="plt-row"><span>收入</span><span>{{ income?.personal_income ? '¥'+income.personal_income.toLocaleString() : '--' }}</span></div>
        </div>

        <!-- 月度趋势迷你图 -->
        <div class="pl-chart" v-if="kg?.summary" ref="plTrendChart"></div>
      </div>

      <!-- ====== 右侧：知识图谱 ====== -->
      <div class="profile-right">
        <div class="kg-wrap">
          <div class="kg-chart" ref="kgChart"></div>
          <!-- 图例 -->
          <div class="kg-legend">
            <div class="kl-title">图例</div>
            <div class="kl-row"><span class="kl-dot" style="background:#3b82f6"></span>用户</div>
            <div class="kl-row"><span class="kl-square" style="background:#ebf0f5;border:2px solid #c8d6e5"></span>大类</div>
            <div class="kl-row"><span class="kl-dot" style="background:#a8d8ea"></span>空调</div>
            <div class="kl-row"><span class="kl-dot" style="background:#fce4b8"></span>厨房</div>
            <div class="kl-row"><span class="kl-dot" style="background:#f8cecc"></span>清洁</div>
            <div class="kl-row"><span class="kl-dot" style="background:#d5c4e1"></span>影音</div>
            <div class="kl-row"><span class="kl-dot" style="background:#b5d8c3"></span>办公</div>
            <div class="kl-row"><span class="kl-dot" style="background:#f9f3c1"></span>照明</div>
            <div class="kl-row"><span class="kl-dot" style="background:#d4edda"></span>已缴</div>
            <div class="kl-row"><span class="kl-dot" style="background:#fff3cd"></span>未缴</div>
          </div>
        </div>

        <!-- 图谱详情面板 -->
        <div class="kg-panel" :class="{ open: panelOpen }">
          <template v-if="!panelOpen">
            <div class="panel-trigger" @click="panelOpen = true">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
              <span class="ptr-text">详</span><span class="ptr-text">情</span>
            </div>
          </template>
          <template v-else>
            <div class="panel-header">
              <span>节点详情</span>
              <button class="ph-close" @click="panelOpen = false"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
            </div>
            <div class="panel-body" v-if="panelData">
              <!-- ====== 用户中心 ====== -->
              <template v-if="panelData.type === 'user'">
                <h3 class="pb-title">{{ panelData.name }}</h3>
                <span class="pb-badge-s" :style="{background: panelData.energy?.color||'#999'}">{{ panelData.energy?.level||'--' }}</span>
                <div class="pb-sec"><div class="pb-sec-t">基本信息</div>
                  <div class="pb-rows"><div class="pbr"><span>性别</span><span>{{ panelData.info?.gender||'--' }}</span></div><div class="pbr"><span>出生年月</span><span>{{ panelData.info?.birth||'--' }}</span></div><div class="pbr"><span>学历</span><span>{{ panelData.info?.education||'--' }}</span></div><div class="pbr"><span>婚姻状况</span><span>{{ panelData.info?.marital||'--' }}</span></div><div class="pbr"><span>职业</span><span>{{ panelData.info?.occupation||'--' }}</span></div><div class="pbr"><span>工作单位</span><span>{{ panelData.info?.work_unit||'--' }}</span></div><div class="pbr"><span>联系电话</span><span>{{ panelData.info?.phone||'--' }}</span></div><div class="pbr"><span>城乡分类</span><span>{{ panelData.info?.urban||'--' }}</span></div><div class="pbr"><span>日常作息</span><span>{{ panelData.info?.schedule||'--' }}</span></div><div class="pbr"><span>健康自评</span><span>{{ panelData.info?.health||'--' }}</span></div><div class="pbr"><span>详细地址</span><span>{{ panelData.info?.address||'--' }}</span></div></div>
                </div>
                <div class="pb-sec" v-if="panelData.housing"><div class="pb-sec-t">住房信息</div>
                  <div class="pb-rows"><div class="pbr"><span>住房类型</span><span>{{ panelData.housing.type||'--' }}</span></div><div class="pbr"><span>建筑面积</span><span>{{ panelData.housing.area ? panelData.housing.area+' m²' : '--' }}</span></div><div class="pbr"><span>户型</span><span>{{ panelData.housing.bedroom||0 }}室{{ panelData.housing.living||0 }}厅</span></div><div class="pbr"><span>楼层</span><span>{{ panelData.housing.floor||'--' }}/{{ panelData.housing.total_floors||'--' }}层</span></div><div class="pbr"><span>电梯</span><span>{{ panelData.housing.elevator ? '有' : '无' }}</span></div><div class="pbr"><span>供暖方式</span><span>{{ panelData.housing.heating||'--' }}</span></div><div class="pbr"><span>房屋朝向</span><span>{{ panelData.housing.orientation||'--' }}</span></div><div class="pbr"><span>房龄</span><span>{{ panelData.housing.building_age ? panelData.housing.building_age + '年' : '--' }}</span></div></div>
                </div>
                <div class="pb-sec" v-if="panelData.income"><div class="pb-sec-t">收入信息</div>
                  <div class="pb-rows"><div class="pbr"><span>个人年收入</span><span>{{ panelData.income.personal ? '¥'+panelData.income.personal.toLocaleString() : '--' }}</span></div><div class="pbr"><span>家庭年收入</span><span>{{ panelData.income.household ? '¥'+panelData.income.household.toLocaleString() : '--' }}</span></div><div class="pbr"><span>收入来源</span><span>{{ panelData.income.source||'--' }}</span></div><div class="pbr"><span>经济自评</span><span>{{ panelData.income.self_rating ? '★'.repeat(panelData.income.self_rating)+'☆'.repeat(5-panelData.income.self_rating) : '--' }}</span></div></div>
                </div>
                <div class="pb-sec"><div class="pb-sec-t">用电概况</div>
                  <div class="pb-rows"><div class="pbr"><span>能耗等级</span><span :style="{color: panelData.energy?.color}">{{ panelData.energy?.level||'--' }}</span></div><div class="pbr"><span>月均用电</span><span>{{ panelData.energy?.avg_kwh ? panelData.energy.avg_kwh+' kWh' : '--' }}</span></div><div class="pbr"><span>设备总数</span><span>{{ panelData.stats?.devices||0 }} 台</span></div><div class="pbr"><span>正常运行</span><span class="on">{{ panelData.stats?.active||0 }} 台</span></div><div class="pbr"><span>已损坏</span><span class="off">{{ panelData.stats?.damaged||0 }} 台</span></div></div>
                </div>
                <div class="pb-sec"><div class="pb-sec-t">缴费概况</div>
                  <div class="pb-rows"><div class="pbr"><span>账单总数</span><span>{{ panelData.stats?.bills||0 }} 张</span></div><div class="pbr"><span>已缴</span><span class="on">{{ panelData.stats?.paid||0 }} 张</span></div><div class="pbr"><span>未缴</span><span class="off">{{ (panelData.stats?.bills||0)-(panelData.stats?.paid||0) }} 张</span></div></div>
                </div>
                <div class="pb-sec" v-if="panelData.members?.length"><div class="pb-sec-t">家庭成员</div>
                  <div v-for="m in panelData.members" :key="m.name" class="pbr"><span>{{ m.relation||'--' }}</span><span>{{ m.name }}{{ m.cohabit ? '·同住' : '·分居' }}</span></div>
                </div>
              </template>

              <!-- ====== 设备管理大类 ====== -->
              <template v-else-if="panelData.subtype === 'devices'">
                <h3 class="pb-title">设备管理</h3>
                <div class="pb-metrics"><div class="pbm"><div class="pbm-val">{{ panelData.total||0 }}</div><div class="pbm-lbl">总数</div></div><div class="pbm"><div class="pbm-val on">{{ panelData.active||0 }}</div><div class="pbm-lbl">运行中</div></div><div class="pbm"><div class="pbm-val off">{{ panelData.damaged||0 }}</div><div class="pbm-lbl">损坏</div></div></div>
                <div v-if="panelData.pie_data" class="pb-mini-chart" ref="pieChart"></div>
                <div v-if="panelData.high_risk?.length" class="pb-sec"><div class="pb-sec-t">高风险设备</div>
                  <div v-for="r in panelData.high_risk" :key="r.name" class="pbr"><span>{{ r.name }}</span><span :class="r.prob>0.5?'off':r.prob>0.3?'warn':''">{{ (r.prob*100).toFixed(1) }}%</span></div>
                </div>
                <p class="pb-hint mt12">双击展开设备列表</p>
              </template>

              <!-- ====== 用电特征大类 ====== -->
              <template v-else-if="panelData.subtype === 'energy'">
                <h3 class="pb-title">用电特征</h3>
                <span class="pb-badge-s" :style="{background: panelData.level_color||'#999'}">{{ panelData.level||'--' }}</span>
                <div class="pb-sec"><div class="pb-sec-t">用电统计</div>
                  <div class="pb-rows"><div class="pbr"><span>月均用电</span><span>{{ panelData.avg_kwh||0 }} kWh</span></div><div class="pbr"><span>累计用电</span><span>{{ (panelData.total_kwh||0).toLocaleString() }} kWh</span></div><div class="pbr"><span>统计月份</span><span>{{ panelData.months||0 }} 个月</span></div></div>
                </div>
                <div class="pb-sec"><div class="pb-sec-t">波动分析</div>
                  <div class="pb-rows"><div class="pbr"><span>标准差</span><span>{{ panelData.std_kwh||0 }}</span></div><div class="pbr"><span>最大月</span><span>{{ panelData.max_month||0 }} kWh</span></div><div class="pbr"><span>最小月</span><span>{{ panelData.min_month||0 }} kWh</span></div><div class="pbr"><span>峰谷差</span><span>{{ ((panelData.max_month||0)-(panelData.min_month||0)).toFixed(1) }} kWh</span></div></div>
                </div>
                <div v-if="panelData.trend" class="pb-mini-chart" ref="trendChart"></div>
              </template>

              <!-- ====== 账单记录大类 ====== -->
              <template v-else-if="panelData.subtype === 'bills'">
                <h3 class="pb-title">账单记录</h3>
                <div class="pb-metrics"><div class="pbm"><div class="pbm-val">{{ panelData.total||0 }}</div><div class="pbm-lbl">总数</div></div><div class="pbm"><div class="pbm-val on">{{ panelData.paid||0 }}</div><div class="pbm-lbl">已缴</div></div><div class="pbm"><div class="pbm-val off">{{ panelData.unpaid||0 }}</div><div class="pbm-lbl">未缴</div></div></div>
                <div class="pb-sec"><div class="pb-sec-t">费用汇总</div>
                  <div class="pb-rows"><div class="pbr"><span>总费用</span><span>¥{{ panelData.total_cost||0 }}</span></div><div class="pbr"><span>维修费</span><span>¥{{ panelData.repair_cost||0 }}</span></div><div class="pbr"><span>缴费率</span><span>{{ panelData.pay_rate||0 }}%</span></div><div class="pbr"><span>信用状态</span><span :class="panelData.credit==='良好'?'on':'off'">{{ panelData.credit||'--' }}</span></div></div>
                </div>
                <div v-if="panelData.trend?.length" class="pb-sec"><div class="pb-sec-t">近期账单</div>
                  <div v-for="b in panelData.trend" :key="b.month" class="pbr"><span>{{ b.month }}</span><span>{{ b.cost ? '¥'+b.cost : '--' }}<span :class="b.status==='已缴'?'on ml':'off ml'">{{ b.status }}</span></span></div>
                </div>
                <p class="pb-hint mt12">双击展开账单明细</p>
              </template>

              <!-- ====== 家庭信息大类 ====== -->
              <template v-else-if="panelData.subtype === 'family'">
                <h3 class="pb-title">家庭信息</h3>
                <div class="pb-metrics"><div class="pbm"><div class="pbm-val">{{ panelData.members||0 }}</div><div class="pbm-lbl">成员</div></div><div class="pbm"><div class="pbm-val on">{{ panelData.cohabit_count||0 }}</div><div class="pbm-lbl">同住</div></div><div class="pbm"><div class="pbm-val" style="color:#999">{{ panelData.separate_count||0 }}</div><div class="pbm-lbl">分居</div></div></div>
                <div class="pb-sec"><div class="pb-sec-t">住房信息</div>
                  <div class="pb-rows"><div class="pbr"><span>住房类型</span><span>{{ panelData.housing_type||'--' }}</span></div><div class="pbr"><span>建筑面积</span><span>{{ panelData.area ? panelData.area+' m²' : '--' }}</span></div><div class="pbr"><span>卧室</span><span>{{ panelData.bedrooms||0 }} 间</span></div><div class="pbr"><span>客厅</span><span>{{ panelData.living_rooms||0 }} 间</span></div><div class="pbr"><span>厨房</span><span>{{ panelData.kitchen||0 }} 间</span></div><div class="pbr"><span>卫生间</span><span>{{ panelData.bathroom||0 }} 间</span></div><div class="pbr"><span>电梯</span><span>{{ panelData.elevator||'--' }}</span></div><div class="pbr"><span>楼层</span><span>{{ panelData.floor||'--' }}/{{ panelData.total_floors||'--' }}</span></div><div class="pbr"><span>供暖</span><span>{{ panelData.heating||'--' }}</span></div><div class="pbr"><span>朝向</span><span>{{ panelData.orientation||'--' }}</span></div><div class="pbr"><span>房龄</span><span>{{ panelData.building_age ? panelData.building_age+'年' : '--' }}</span></div></div>
                </div>
                <div v-if="panelData.member_list?.length" class="pb-sec"><div class="pb-sec-t">核心成员</div>
                  <div v-for="m in panelData.member_list" :key="m.name" class="pbr"><span>{{ m.relation||'--' }}</span><span>{{ m.name }} · {{ m.cohabit||'--' }}</span></div>
                </div>
              </template>

              <!-- ====== 画像标签大类 ====== -->
              <template v-else-if="panelData.subtype === 'tags'">
                <h3 class="pb-title">画像标签</h3>
                <div class="pb-sec"><div class="pb-sec-t">画像评价</div>
                  <div class="pb-rows"><div class="pbr"><span>能耗等级</span><span :style="{color: panelData.energy_color}">{{ panelData.energy_level||'--' }}</span></div><div class="pbr"><span>缴费信用</span><span :class="panelData.credit==='良好'?'on':'off'">{{ panelData.credit||'--' }}</span></div><div class="pbr"><span>设备规模</span><span>{{ panelData.device_count||0 }} 台</span></div><div class="pbr"><span>家庭规模</span><span>{{ panelData.family_size||0 }} 人</span></div><div class="pbr"><span>收入水平</span><span>{{ panelData.income_level||'--' }}</span></div></div>
                </div>
              </template>

              <!-- ====== 设备节点 ====== -->
              <template v-else-if="panelData.type === 'device'">
                <h3 class="pb-title">{{ panelData.name }}</h3>
                <span class="pb-badge-s" :class="panelData.is_active?'on':'off'">{{ panelData.is_active?'正常运行':'已损坏' }}</span>
                <div class="pb-sec"><div class="pb-sec-t">基本信息</div>
                  <div class="pb-rows"><div class="pbr"><span>设备类别</span><span>{{ panelData.category||'--' }}</span></div><div class="pbr"><span>品牌</span><span>{{ panelData.brand||'--' }}</span></div><div class="pbr"><span>额定功率</span><span>{{ panelData.rated_power||0 }} W</span></div><div class="pbr"><span>有效功率</span><span>{{ panelData.power||0 }} W</span></div></div>
                </div>
                <div class="pb-sec"><div class="pb-sec-t">运行数据</div>
                  <div class="pb-rows"><div class="pbr"><span>使用年限</span><span>{{ panelData.usage_years?.toFixed?.(1)||panelData.usage_years||0 }} 年</span></div><div class="pbr"><span>预期寿命</span><span>{{ panelData.lifespan||10 }} 年</span></div><div class="pbr"><span>剩余寿命</span><span>{{ panelData.damage_pred?.remain||0 }} 年</span></div><div class="pbr"><span>日均时长</span><span>{{ panelData.hours||0 }} 小时</span></div><div class="pbr"><span>使用习惯</span><span>{{ panelData.habit||'--' }}</span></div></div>
                </div>
                <div class="pb-sec"><div class="pb-sec-t">损坏评估</div>
                  <div class="pb-rows"><div class="pbr"><span>当前损坏率</span><span :class="panelData.damage_prob>0.8?'off':panelData.damage_prob>0.5?'warn':''">{{ ((panelData.damage_prob||0)*100).toFixed(1) }}%</span></div><div class="pbr"><span>1年后预测</span><span :class="(panelData.damage_pred?.next1||0)>0.8?'off':(panelData.damage_pred?.next1||0)>0.5?'warn':''">{{ ((panelData.damage_pred?.next1||0)*100).toFixed(1) }}%</span></div><div class="pbr"><span>2年后预测</span><span :class="(panelData.damage_pred?.next2||0)>0.8?'off':(panelData.damage_pred?.next2||0)>0.5?'warn':''">{{ ((panelData.damage_pred?.next2||0)*100).toFixed(1) }}%</span></div><div class="pbr"><span>预计损坏年</span><span>约 {{ panelData.damage_pred?.est_damage_year||'--' }} 年</span></div></div>
                </div>
                <div v-if="panelData.monthly_kwh?.length" class="pb-mini-chart" ref="deviceKwhChart"></div>
              </template>

              <!-- ====== 账单节点 ====== -->
              <template v-else-if="panelData.type === 'bill'">
                <h3 class="pb-title">{{ panelData.month }}</h3>
                <span class="pb-badge-s" :class="panelData.status==='已缴'?'on':'off'">{{ panelData.status }}</span>
                <div class="pb-sec"><div class="pb-sec-t">账单信息</div>
                  <div class="pb-rows"><div class="pbr"><span>用电量</span><span>{{ panelData.kwh||0 }} kWh</span></div><div class="pbr"><span>电价</span><span>¥{{ panelData.unit_price||'0.55' }}/度</span></div><div class="pbr"><span>电费</span><span>¥{{ panelData.elec_cost||0 }}</span></div><div class="pbr"><span>维修费</span><span>¥{{ panelData.repair_cost||0 }}</span></div><div class="pbr total"><span>合计</span><span>¥{{ panelData.total||0 }}</span></div></div>
                </div>
                <div class="pb-sec"><div class="pb-sec-t">缴费状态</div>
                  <div class="pb-rows"><div class="pbr"><span>缴费日期</span><span>{{ panelData.paid_date||'--' }}</span></div><div class="pbr"><span>截止日期</span><span>{{ panelData.due_date||'--' }}</span></div><div class="pbr"><span>欠费警告</span><span :class="panelData.warning?'off':'on'">{{ panelData.warning?'是':'否' }}</span></div></div>
                </div>
              </template>

              <!-- ====== 标签/能耗节点 ====== -->
              <template v-else-if="panelData.type === 'tag'">
                <h3 class="pb-title">{{ panelData.name }}</h3>
                <div class="pb-rows"><div class="pbr"><span>标签值</span><span :style="{color: energyLabelColor(panelData.value)}">{{ panelData.value||'--' }}</span></div><div v-if="panelData.avg_kwh" class="pbr"><span>月均用电</span><span>{{ panelData.avg_kwh }} kWh</span></div></div>
                <div class="pb-sec mt12"><div class="pb-sec-t">等级划分</div>
                  <div class="pbr"><span class="on">节能型</span><span>≤ 100 kWh</span></div>
                  <div class="pbr"><span style="color:#5470c6">普通型</span><span>100 ~ 500 kWh</span></div>
                  <div class="pbr"><span class="off">高耗能型</span><span>> 500 kWh</span></div>
                </div>
              </template>

              <!-- ====== 月度用电节点 ====== -->
              <template v-else-if="panelData.type === 'kwh'">
                <h3 class="pb-title">{{ panelData.name||'用电统计' }}</h3>
                <div class="pb-sec"><div class="pb-sec-t">统计数据</div>
                  <div class="pb-rows"><div v-if="panelData.avg_kwh" class="pbr"><span>月均用电</span><span>{{ panelData.avg_kwh }} kWh</span></div><div v-if="panelData.total_kwh" class="pbr"><span>累计用电</span><span>{{ panelData.total_kwh.toLocaleString() }} kWh</span></div><div v-if="panelData.months" class="pbr"><span>统计月份</span><span>{{ panelData.months }} 个月</span></div><div v-if="panelData.max" class="pbr"><span>最大月</span><span>{{ panelData.max }} kWh</span></div><div v-if="panelData.min" class="pbr"><span>最小月</span><span>{{ panelData.min }} kWh</span></div><div v-if="panelData.month" class="pbr"><span>月份</span><span>{{ panelData.month }}</span></div><div v-if="panelData.value" class="pbr"><span>用电量</span><span>{{ panelData.value }} kWh</span></div></div>
                </div>
                <div v-if="panelData.trend" class="pb-mini-chart" ref="trendChart"></div>
              </template>

              <!-- ====== 家庭成员节点 ====== -->
              <template v-else-if="panelData.type === 'member'">
                <h3 class="pb-title">{{ panelData.name }}</h3>
                <div class="pb-sec"><div class="pb-sec-t">基本信息</div>
                  <div class="pb-rows"><div class="pbr"><span>关系</span><span>{{ panelData.relation||'--' }}</span></div><div class="pbr"><span>同住状态</span><span>{{ panelData.cohabit||'--' }}</span></div><div class="pbr"><span>职业</span><span>{{ panelData.occupation||'--' }}</span></div><div class="pbr"><span>学历</span><span>{{ panelData.education||'--' }}</span></div><div class="pbr"><span>年龄</span><span>{{ panelData.age ? panelData.age + '岁' : '--' }}</span></div><div class="pbr"><span>性别</span><span>{{ panelData.gender||'--' }}</span></div></div>
                </div>
              </template>

              <!-- ====== 旧 housing/member 兼容 ====== -->
              <template v-else-if="panelData.type === 'housing'">
                <h3 class="pb-title">住房</h3>
                <div class="pb-rows"><div class="pbr"><span>类型</span><span>{{ panelData.housing_type }}</span></div><div class="pbr"><span>面积</span><span>{{ panelData.area }} m²</span></div><div class="pbr"><span>楼层</span><span>{{ panelData.floor }}/{{ panelData.total_floors }}</span></div><div class="pbr"><span>供暖</span><span>{{ panelData.heating }}</span></div></div>
              </template>
              <template v-else-if="panelData.type === 'income'">
                <h3 class="pb-title">收入</h3>
                <div class="pb-rows"><div class="pbr"><span>个人</span><span>{{ panelData.personal?'¥'+panelData.personal.toLocaleString():'--' }}</span></div><div class="pbr"><span>家庭</span><span>{{ panelData.household?'¥'+panelData.household.toLocaleString():'--' }}</span></div></div>
              </template>
              <template v-else>
                <div class="pb-rows"><div v-for="(v,k) in panelData" :key="k" v-show="k!=='type'&&v!==undefined&&v!==null" class="pbr"><span>{{ k }}</span><span>{{ v }}</span></div></div>
              </template>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getMyHousehold, getUserKG, getOptions } from '../api'

const hh = reactive({})
const kg = ref(null)
const housing = ref({})
const income = ref({})
const options = reactive({})
const kgChart = ref(null)
const plTrendChart = ref(null)
const pieChart = ref(null)
const trendChart = ref(null)
const radarChart = ref(null)
const deviceKwhChart = ref(null)
const panelOpen = ref(false)
const panelData = ref(null)
const visibleNodes = ref(0)
const visibleLinks = ref(0)
let chartInstance = null
const expandedGroups = new Set()

function optLabel(cat, val) {
  if (!val && val !== 0) return '--'
  const opts = options[cat]; if (!opts) return String(val)
  const found = opts.find(o => String(o.item_key) === String(val))
  return found ? found.item_value : String(val)
}
function elColor(lv) { return {'节能型':'#67c23a','普通型':'#5470c6','摆渡型':'#e6a23c','高耗能型':'#e74c3c'}[lv]||'#999' }
function energyLabelColor(v) { return {'节能型':'#67c23a','普通型':'#5470c6','高耗能型':'#e74c3c'}[v]||'#999' }

onMounted(async () => {
  try {
    const [hRes, kgRes, oRes] = await Promise.all([getMyHousehold(), getUserKG(), getOptions()])
    Object.assign(hh, hRes.data.household)
    housing.value = hRes.data.housing || {}
    income.value = hRes.data.income || {}
    Object.assign(options, oRes.data.options || {})
    kg.value = kgRes.data
    await nextTick()
    renderKG()
    renderProfileCharts()
    renderPersonaCloud()
  } catch (e) { console.error(e) }
})

function renderPersonaCloud() {
  const colors = ['#3b82f6','#5470c6','#67c23a','#e6a23c','#91cc75','#73c0de','#fc8452','#8b5cf6','#f59e0b','#10b981']
  const d = kg.value
  const allNames = []
  if (d?.nodes) {
    const uNode = d.nodes.find(n => n.group === 'center')
    if (uNode?.detail) {
      const de = uNode.detail
      // 用户画像字段
      if (de.info) Object.entries(de.info).forEach(([k,v]) => { if (v && v!=='--' && v.length<20) allNames.push(v) })
      if (de.energy?.level) allNames.push(de.energy.level)
      if (de.housing) { if (de.housing.type && de.housing.type!=='--') allNames.push(de.housing.type); if (de.housing.heating && de.housing.heating!=='--') allNames.push(de.housing.heating); if (de.housing.orientation && de.housing.orientation!=='--') allNames.push(de.housing.orientation) }
      if (de.members) de.members.forEach(m => { if (m.relation) allNames.push(m.relation) })
    }
    // 所有设备名称 + 类型 + 习惯 + 品牌
    d.nodes.filter(n=>n.category==='device').forEach(nd=>{
      if (nd.name) allNames.push(nd.name)
      if (nd.detail) {
        if (nd.detail.category) allNames.push(nd.detail.category)
        if (nd.detail.habit && nd.detail.habit!=='') allNames.push(nd.detail.habit)
        if (nd.detail.brand && nd.detail.brand!=='') allNames.push(nd.detail.brand)
      }
    })
    // 行为模式标签
    d.nodes.filter(n=>n.category==='sub'&&n.hidden).forEach(nd=>{ if(nd.name&&nd.name.length<15)allNames.push(nd.name) })
    // 能耗等级
    if (d.summary?.energy_level) allNames.push(d.summary.energy_level)
  }
  // 去重
  const unique = [...new Set(allNames)]
  const cloudWords = unique.map(n => ({name:n, w:9+Math.random()*10}))
  const cloudEl = document.getElementById('wc-cloud')
  if (cloudEl) cloudEl.innerHTML = cloudWords.sort(()=>Math.random()-0.5).slice(0,35).map(w=>`<span style="font-size:${w.w}px;color:${colors[Math.floor(Math.random()*colors.length)]};margin:1px 4px;display:inline-block;line-height:1.4">${w.name}</span>`).join('')
}

function renderProfileCharts() {
  if (!plTrendChart.value || !kg.value?.summary) return
  const c = echarts.init(plTrendChart.value)
  c.setOption({
    grid:{top:8,right:8,bottom:16,left:36},
    xAxis:{type:'category',data:(kg.value.nodes?.find(n=>n.group==='center')?.detail?.trend||[]).map(t=>t.month),axisLabel:{fontSize:8,rotate:30}},
    yAxis:{type:'value',splitLine:{lineStyle:{color:'#f0f0f0'}},axisLabel:{fontSize:9}},
    series:[{type:'line',data:(kg.value.nodes?.find(n=>n.group==='center')?.detail?.trend||[]).map(t=>t.kwh),smooth:true,lineStyle:{color:'#5470c6'},areaStyle:{color:'rgba(84,112,198,0.1)'},symbol:'none'}],
  })
}

function getVisible() {
  if (!kg.value) return {nodes:[],links:[]}
  const allNodes=kg.value.nodes,allLinks=kg.value.links,m=new Set()
  allNodes.forEach(n=>{if(n.group==='center'||n.group==='category')m.add(n.id);if(n.group&&expandedGroups.has(n.group))m.add(n.id)})
  const vn=allNodes.filter(n=>m.has(n.id)),vi=new Set(vn.map(n=>n.id)),vl=allLinks.filter(l=>vi.has(l.source)&&vi.has(l.target))
  visibleNodes.value=vn.length;visibleLinks.value=vl.length
  return {nodes:vn,links:vl}
}

function renderKG() {
  if (!kgChart.value || !kg.value) return
  if (chartInstance) chartInstance.dispose()
  chartInstance = echarts.init(kgChart.value)
  const cats = [
    {name:'user',itemStyle:{color:'#3b82f6'}},
    {name:'category',itemStyle:{color:'#ebf0f5',borderColor:'#c8d6e5',borderWidth:2}},
    {name:'device',itemStyle:{color:'#a8d8ea'}},
    {name:'sub',itemStyle:{color:'#91c7ae'}},
  ]
  const userNode = kg.value.nodes.find(n => n.group === 'center')
  if (userNode?.detail) { panelData.value = userNode.detail; panelOpen.value = true }

  function doRender(){
    const {nodes,links}=getVisible()
    chartInstance.setOption({
      tooltip:{trigger:'item',formatter:p=>p.dataType==='node'?`<b>${p.name}</b>`:''},
      series:[{type:'graph',layout:'force',roam:true,draggable:true,force:{repulsion:180,edgeLength:[60,140],gravity:0.15,friction:0.4},data:nodes,links:links,categories:cats,label:{show:true,fontSize:12,color:'#444'},lineStyle:{color:'#bcc4d0',curveness:0.15,opacity:0.7,width:2},emphasis:{focus:'adjacency',lineStyle:{width:4,color:'#5b8def'},itemStyle:{shadowBlur:30},label:{fontSize:14,fontWeight:600}},animationDurationUpdate:600}],
    },true)
  }
  doRender()
  let ct=null
  chartInstance.off('click').on('click',p=>{
    if(p.dataType==='node'&&p.data?.detail){if(ct){clearTimeout(ct);ct=null;return};ct=setTimeout(()=>{panelData.value=p.data.detail;panelOpen.value=true;setTimeout(renderMiniCharts,300);ct=null},300)}
  })
  chartInstance.off('dblclick').on('dblclick',p=>{if(ct){clearTimeout(ct);ct=null};if(p.dataType==='node'&&p.data.group==='category'){const g=p.data.id;expandedGroups.has(g)?expandedGroups.delete(g):expandedGroups.add(g);doRender()}})
  new ResizeObserver(()=>chartInstance?.resize()).observe(kgChart.value)
}

function renderMiniCharts(){
  nextTick(()=>{
    if(panelData.value?.pie_data?.length&&pieChart.value){const c=echarts.init(pieChart.value);c.setOption({series:[{type:'pie',radius:['45%','75%'],data:panelData.value.pie_data,label:{fontSize:9}}]})}
    if(panelData.value?.trend?.length&&trendChart.value){const c=echarts.init(trendChart.value);c.setOption({grid:{top:8,right:8,bottom:16,left:36},xAxis:{type:'category',data:panelData.value.trend.map(t=>t.month),axisLabel:{fontSize:8,rotate:30}},yAxis:{type:'value',axisLabel:{fontSize:9}},series:[{type:'line',data:panelData.value.trend.map(t=>t.kwh),smooth:true,lineStyle:{color:'#5470c6'},areaStyle:{color:'rgba(84,112,198,0.1)'},symbol:'none'}]})}
    if(panelData.value?.radar&&radarChart.value){const c=echarts.init(radarChart.value);c.setOption({radar:{indicator:panelData.value.radar.indicator,center:['50%','55%'],radius:'60%'},series:[{type:'radar',data:[{value:panelData.value.radar.user_values,name:'您',areaStyle:{color:'rgba(84,112,198,0.2)'}},{value:panelData.value.radar.avg_values,name:'均值',areaStyle:{color:'rgba(204,204,204,0.15)'}}]}]})}
    if(panelData.value?.monthly_kwh?.length&&deviceKwhChart.value){const c=echarts.init(deviceKwhChart.value);c.setOption({grid:{top:8,right:8,bottom:16,left:36},xAxis:{type:'category',data:panelData.value.monthly_kwh.map(m=>m.month),axisLabel:{fontSize:8,rotate:30}},yAxis:{type:'value',axisLabel:{fontSize:9}},series:[{type:'bar',data:panelData.value.monthly_kwh.map(m=>m.kwh),itemStyle:{color:'#a8d8ea',borderRadius:[4,4,0,0]}}]})}
  })
}
</script>

<style scoped>
.profile-page{padding:12px 16px 0;width:100%;box-sizing:border-box;height:calc(100vh - 52px);display:flex;flex-direction:column}
.page-top{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:10px;flex-shrink:0}
.page-top h2{font-size:18px;font-weight:500;margin:0;color:#2c3e50}
.sub{font-size:11px;color:#999;margin-top:2px}
.node-count{font-size:11px;color:#aaa}

.profile-layout{flex:1;display:flex;gap:14px;overflow:hidden;min-height:0}

/* ====== 左侧画像 ====== */
.profile-left{width:280px;flex-shrink:0;overflow-y:auto;display:flex;flex-direction:column;gap:12px}
.pl-avatar-section{background:#fff;border:1px solid #edf0f4;border-radius:10px;padding:20px;text-align:center}
.pl-avatar{width:56px;height:56px;border-radius:50%;background:#f0f2f5;color:#999;display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:500;margin:0 auto 10px}
.pl-name{font-size:17px;font-weight:600;color:#2c3e50;margin-bottom:8px}
.pl-tags{display:flex;gap:4px;flex-wrap:wrap;justify-content:center}
.plt{font-size:10px;padding:2px 7px;background:#f0f2f5;color:#888;border-radius:4px}

.pl-metrics{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.plm-item{background:#fff;border:1px solid #edf0f4;border-radius:8px;padding:12px 8px;text-align:center}
.plm-val{font-size:18px;font-weight:700;color:#2c3e50}
.plm-lbl{font-size:10px;color:#bbb;margin-top:2px}

/* 词云 */
.pl-wordcloud{background:#fff;border:1px solid #edf0f4;border-radius:10px;padding:10px 12px;display:flex;flex-wrap:wrap;align-items:flex-start;align-content:flex-start;justify-content:center;gap:1px 5px;line-height:1.3;height:160px;overflow-y:auto;overflow-x:hidden}

.pl-table{background:#fff;border:1px solid #edf0f4;border-radius:10px;padding:12px 16px}
.plt-row{display:flex;justify-content:space-between;padding:5px 0;font-size:11px;border-bottom:1px solid #fafafa}
.plt-row span:first-child{color:#aaa}
.plt-row span:last-child{color:#555}

.pl-chart{width:100%;height:160px;background:#fff;border:1px solid #edf0f4;border-radius:10px}

/* ====== 右侧图谱 ====== */
.profile-right{flex:1;display:flex;gap:0;overflow:hidden;min-width:0}
.kg-wrap{flex:1;background:#fafbfc;border:1px solid #edf0f4;border-radius:8px;overflow:hidden;position:relative}
.kg-chart{width:100%;height:100%}
.kg-legend{position:absolute;top:10px;left:10px;background:rgba(255,255,255,0.95);border:1px solid #edf0f4;border-radius:8px;padding:6px 10px;font-size:10px;z-index:10}
.kl-title{font-size:10px;font-weight:600;color:#888;margin-bottom:3px}
.kl-row{display:flex;align-items:center;gap:4px;padding:1px 0;color:#666}
.kl-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.kl-square{width:8px;height:8px;border-radius:2px;flex-shrink:0}

/* 图谱面板 */
.kg-panel{flex-shrink:0;background:#fff;border:1px solid #edf0f4;border-left:none;border-radius:0 8px 8px 0;transition:width .25s ease;overflow:hidden;display:flex;flex-direction:column}
.kg-panel:not(.open){width:44px}
.kg-panel.open{width:280px}
.panel-trigger{display:flex;flex-direction:column;align-items:center;gap:4px;padding:14px 8px;cursor:pointer;color:#999;transition:color .15s}
.panel-trigger:hover{color:#5470c6;background:#f8f9fb}
.ptr-text{font-size:11px;writing-mode:vertical-rl;letter-spacing:2px}
.panel-header{display:flex;justify-content:space-between;align-items:center;padding:12px 14px;border-bottom:1px solid #f0f2f5;font-size:12px;font-weight:600;color:#888}
.ph-close{background:none;border:none;cursor:pointer;color:#ccc;padding:2px}
.panel-body{flex:1;overflow-y:auto;padding:14px}
.pb-title{font-size:14px;font-weight:600;color:#2c3e50;margin:0 0 8px}
.pb-badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:10px;margin-bottom:8px}
.pb-badge.on{background:#e8f5e9;color:#52c41a}
.pb-badge.off{background:#fde8e8;color:#ff4d4f}
.pb-hint{font-size:10px;color:#ddd}.mt12{margin-top:12px}
.pb-metrics{display:flex;gap:6px;margin-bottom:8px}
.pbm{flex:1;text-align:center;padding:6px 4px;background:#f8f9fb;border-radius:6px}
.pbm-val{font-size:14px;font-weight:700;color:#2c3e50}
.pbm-val.on{color:#52c41a}
.pbm-lbl{font-size:9px;color:#bbb;margin-top:1px}
.pb-rows{display:flex;flex-direction:column}
.pbr{display:flex;justify-content:space-between;padding:4px 0;font-size:11px;border-bottom:1px solid #fafafa}
.pbr span:first-child{color:#aaa;min-width:40px}
.pbr span:last-child{color:#555}
.pbr.total{font-weight:600}
.text-red{color:#ff4d4f!important}
.pb-mini-chart{width:100%;height:90px}
/* 节点详情面板增强 */
.pb-sec{margin-top:14px}
.pb-sec-t{font-size:10px;color:#888;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px;padding-bottom:4px;border-bottom:1px solid #f0f2f5}
.pb-badge-s{display:inline-block;padding:2px 10px;border-radius:10px;font-size:10px;color:#fff;margin-bottom:10px}
.pb-badge-s.on{background:#67c23a}.pb-badge-s.off{background:#e74c3c}
.pbr span.on{color:#67c23a}.pbr span.off{color:#e74c3c}.pbr span.warn{color:#e6a23c}
.pbr span.ml{margin-left:8px}
</style>
