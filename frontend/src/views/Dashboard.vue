<template>
  <div class="dashboard">
    <!-- 顶部-hero区域 -->
    <div class="hero-section">
      <div class="hero-content">
        <div class="hero-title">
          <h1>
            <span class="icon">⚡</span>
            基于知识图谱的电力用户画像系统
          </h1>
          <p class="subtitle">Knowledge Graph Powered Power User Profiling</p>
        </div>
        <div class="hero-tags">
          <span class="tag"><span class="tag-icon">🔗</span>知识图谱</span>
          <span class="tag"><span class="tag-icon">🎯</span>改进FCM聚类</span>
          <span class="tag"><span class="tag-icon">📊</span>TransE嵌入</span>
        </div>
      </div>
      <div class="hero-bg"></div>
    </div>

    <!-- 核心统计指标 -->
    <div class="stats-section">
      <div class="stat-card" v-for="stat in statsCards" :key="stat.title" :class="stat.color">
        <div class="stat-icon">{{ stat.icon }}</div>
        <div class="stat-content">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-title">{{ stat.title }}</div>
        </div>
      </div>
    </div>

    <!-- 用户选择 -->
    <div class="user-selector-bar">
      <div class="selector-left">
        <label>当前用户：</label>
        <select v-model="selectedUser" @change="onUserChange">
          <option v-for="user in users" :key="user.user_id" :value="user.user_id">
            {{ user.house_num }}
          </option>
        </select>
      </div>
      <div class="selector-right" v-if="profile.user_id">
        <span class="energy-tag" :class="profile.energy_level">{{ profile.energy_level }}能耗</span>
        <span class="behavior-tag" :class="getBehaviorClass(profile.behavior_label)">{{ profile.behavior_label }}</span>
        <span class="pattern-tag">{{ profile.consumption_pattern }}</span>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 第一行：用户画像 + 用电趋势 -->
      <div class="row">
        <!-- 用户画像卡片 -->
        <div class="panel-card profile-card" v-if="profile.user_id">
          <h3>
          <span class="panel-icon">👤</span>用户画像
          <span class="info-icon">ⓘ</span>
          <div class="tooltip tooltip-wide">
            <div><strong style="color: #ffc069; font-size: 13px;">📊 FCM聚类用户画像</strong></div>

            <div style="margin-top: 8px;"><strong style="color: #52c41a;">① 聚类特征（6维）</strong></div>
            <div style="font-size: 11px; color: #ccc; margin: 4px 0; display: grid; grid-template-columns: 1fr 1fr; gap: 3px;">
              <div>日均用电量</div><div>用电波动(标准差)</div>
              <div>最大日用电</div><div>最小日用电</div>
              <div>变异系数 CV</div><div>TransE嵌入向量</div>
            </div>

            <div style="margin-top: 8px;"><strong style="color: #52c41a;">② 聚类过程</strong></div>
            <div style="font-size: 11px; color: #ccc;">
              <span style="background: #667eea; padding: 1px 5px; border-radius: 3px; margin-right: 5px;">1</span>标准化 → <span style="background: #667eea; padding: 1px 5px; border-radius: 3px; margin: 0 5px;">2</span>密度峰值初始化 →
              <span style="background: #667eea; padding: 1px 5px; border-radius: 3px; margin: 0 5px;">3</span>迭代优化 →
              <span style="background: #667eea; padding: 1px 5px; border-radius: 3px; margin-left: 5px;">4</span>输出
            </div>

            <div style="margin-top: 8px;"><strong style="color: #52c41a;">③ 标签规则</strong></div>
            <div style="font-size: 10px; color: #ccc; margin: 3px 0;">
              <div style="display: flex; justify-content: space-between; padding: 2px 6px; background: #52c41a20; border-radius: 3px; margin: 2px 0;">
                <span>节能型</span><span>&lt; 均值×0.6</span>
              </div>
              <div style="display: flex; justify-content: space-between; padding: 2px 6px; background: #1890ff20; border-radius: 3px; margin: 2px 0;">
                <span>正常型</span><span>均值×0.6~1.2</span>
              </div>
              <div style="display: flex; justify-content: space-between; padding: 2px 6px; background: #722ed120; border-radius: 3px; margin: 2px 0;">
                <span>波动型</span><span>CV&gt;0.4 且偏高</span>
              </div>
              <div style="display: flex; justify-content: space-between; padding: 2px 6px; background: #f5222d20; border-radius: 3px; margin: 2px 0;">
                <span>高耗能型</span><span>&gt; 均值×1.2</span>
              </div>
            </div>

            <div style="margin-top: 8px;"><strong style="color: #52c41a;">④ 目标函数</strong></div>
            <div style="background: rgba(255,255,255,0.1); padding: 4px 6px; border-radius: 3px; font-size: 9px; color: #ffc069;">
              J = Σ样本 Σ类别 (隶属度^2 × 距离平方)
            </div>
          </div>
        </h3>
          <div class="profile-main">
            <div class="profile-avatar">{{ profile.house_num?.charAt(0) || 'U' }}</div>
            <div class="profile-detail">
              <div class="detail-row">
                <span class="label">用户ID</span>
                <span class="value">{{ profile.user_id }}</span>
              </div>
              <div class="detail-row">
                <span class="label">日均用电</span>
                <span class="value highlight">{{ formatNumber(profile.avg_daily_kwh) }} kWh</span>
              </div>
              <div class="detail-row">
                <span class="label">总用电量</span>
                <span class="value">{{ formatNumber(profile.total_kwh) }} kWh</span>
              </div>
            </div>
          </div>

          <!-- FCM聚类 -->
          <div class="fcm-section" v-if="fcmMembership">
            <div class="fcm-header">
              <span class="fcm-title">🎯 FCM智能分群</span>
              <span class="fcm-cluster-label">{{ fcmMembership.cluster_label }}</span>
            </div>
            <div class="membership-bars">
              <div v-for="(value, key) in fcmMembership.membership" :key="key" class="membership-item">
                <span class="membership-label">{{ getClusterLabel(key) }}</span>
                <div class="bar-track">
                  <div class="bar-fill" :style="{ width: (value * 100) + '%', background: getClusterColor(key) }"></div>
                </div>
                <span class="membership-value">{{ (value * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 用电趋势图 -->
        <div class="panel-card chart-card trend-card">
          <h3>
          <span class="panel-icon">📈</span>用电趋势 (最近30天)
          <span class="info-icon">ⓘ</span>
          <div class="tooltip">
            <div><strong>用电趋势说明</strong></div>
            <div>展示用户最近30天的日用电量变化</div>
            <div class="formula-title">统计指标：</div>
            <div>• 趋势线反映用电波动情况</div>
            <div>• 面积图显示累计用电量</div>
            <div>• 峰值日期标注显示最高用电日</div>
          </div>
        </h3>
          <div ref="trendChartRef" style="width: 100%; height: 280px;"></div>
        </div>
      </div>

      <!-- 第二行：设备占比 + 知识图谱 + 聚类 -->
      <div class="row">
        <!-- 设备用电占比 -->
        <div class="panel-card">
          <h3>
          <span class="panel-icon">🔌</span>设备用电占比
          <span class="info-icon">ⓘ</span>
          <div class="tooltip">
            <div><strong>设备用电占比说明</strong></div>
            <div>展示用户家中各电器的用电贡献比例</div>
            <div class="formula-title">计算公式：</div>
            <div class="formula">设备占比 = 设备用电量 / 总用电量 × 100%</div>
            <div>• 饼图直观显示各设备能耗占比</div>
            <div>• 识别主要耗电设备</div>
          </div>
        </h3>
          <div class="device-section">
            <div ref="devicePieRef" style="width: 55%; height: 220px;"></div>
            <div class="device-list">
              <div v-for="device in topDevices" :key="device.device_id" class="device-item">
                <span class="device-name">{{ device.device_name }}</span>
                <span class="device-pct">{{ device.percentage }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 用户关系网络图 -->
        <div class="panel-card">
          <h3>
          <span class="panel-icon">🕸️</span>用户关系网络
          <span class="info-icon">ⓘ</span>
          <div class="tooltip">
            <div><strong>用户关系网络说明</strong></div>
            <div>基于Neo4j知识图谱展示用户关联关系</div>
            <div class="formula-title">关系类型：</div>
            <div>• 用户-设备：从属关系</div>
            <div>• 用户-标签：属性关系</div>
            <div>• 用户-用电模式：行为关系</div>
            <div>• 用户-相似用户：协同关系</div>
          </div>
        </h3>
          <div ref="networkChartRef" style="width: 100%; height: 220px;"></div>
        </div>

        <!-- 聚类分布 -->
        <div class="panel-card">
          <h3>
          <span class="panel-icon">👥</span>用户聚类分布
          <span class="info-icon">ⓘ</span>
          <div class="tooltip">
            <div><strong>改进FCM聚类说明</strong></div>
            <div>基于改进模糊C均值算法的用户分群</div>
            <div class="formula-title">核心改进：</div>
            <div class="formula">1. 密度峰值初始化：γ = ρ × δ</div>
            <div class="formula">2. 自适应权重：wᵢ = 1 - Hᵢ^α</div>
            <div>3. 知识图谱特征融合</div>
            <div class="formula-title">四类用户：</div>
            <div>节能型 | 正常型 | 波动型 | 高耗能型</div>
          </div>
        </h3>
          <div ref="clusterChartRef" style="width: 100%; height: 220px;"></div>
        </div>
      </div>

      <!-- 第三行：用电模式 + 设备联动 + 相似用户 -->
      <div class="row">
        <!-- 用电模式分析 -->
        <div class="panel-card">
          <h3>
          <span class="panel-icon">⏰</span>用电模式分析
          <span class="info-icon">ⓘ</span>
          <div class="tooltip">
            <div><strong>用电模式说明</strong></div>
            <div>基于时段用电分布的用户行为分析</div>
            <div class="formula-title">时段划分：</div>
            <div>• 早峰 7:00-9:00</div>
            <div>• 午间 11:00-13:00</div>
            <div>• 晚峰 18:00-21:00</div>
            <div>• 夜间 22:00-次日6:00</div>
            <div>• 识别典型用电时间段特征</div>
          </div>
        </h3>
          <div class="pattern-section">
            <div class="pattern-result">
              <div class="pattern-icon" :class="getPatternClass(userPattern.pattern)">
                {{ getPatternIcon(userPattern.pattern) }}
              </div>
              <div class="pattern-name">{{ userPattern.pattern }}</div>
            </div>
            <div ref="timeslotChartRef" style="width: 100%; height: 150px;"></div>
          </div>
        </div>

        <!-- 设备联动分析 -->
        <div class="panel-card">
          <h3>
          <span class="panel-icon">🔗</span>设备联动分析
          <span class="info-icon">ⓘ</span>
          <div class="tooltip">
            <div><strong>设备联动分析说明</strong></div>
            <div>分析不同设备间的使用相关性</div>
            <div class="formula-title">相关系数计算：</div>
            <div class="formula">r = Σ(xᵢ-x̄)(yᵢ-ȳ) / √[Σ(xᵢ-x̄)²Σ(yᵢ-ȳ)²]</div>
            <div class="formula-title">相关强度：</div>
            <div>• |r| > 0.7 强相关</div>
            <div>• 0.3 < |r| < 0.7 中等相关</div>
            <div>• |r| < 0.3 弱相关</div>
          </div>
        </h3>
          <div class="correlations-list" v-if="deviceCorrelations.length > 0">
            <div v-for="corr in deviceCorrelations.slice(0, 5)" :key="corr.device1 + corr.device2" class="corr-item">
              <span>{{ corr.device1_name }}</span>
              <span class="corr-symbol">↔</span>
              <span>{{ corr.device2_name }}</span>
              <span class="corr-score" :class="getCorrClass(corr.correlation)">{{ corr.correlation * 100 }}%</span>
            </div>
          </div>
          <div v-else class="no-data">暂无联动数据</div>
        </div>

        <!-- 相似用户推荐 -->
        <div class="panel-card">
          <h3>
          <span class="panel-icon">👥</span>相似用户推荐
          <span class="info-icon">ⓘ</span>
          <div class="tooltip">
            <div><strong>相似用户说明</strong></div>
            <div>基于用电行为特征的用户相似度计算</div>
            <div class="formula-title">相似度指标：</div>
            <div>• 日均用电量差异</div>
            <div>• 用电波动程度</div>
            <div>• 设备使用模式</div>
            <div>• 时段用电分布</div>
            <div>推荐具有相似用电习惯的用户供参考</div>
          </div>
        </h3>
          <div class="similar-list" v-if="similarUsers.length > 0">
            <div v-for="user in similarUsers.slice(0, 4)" :key="user.user_id" class="similar-item">
              <div class="similar-info">
                <span class="similar-name">{{ user.house_num }}</span>
                <span class="similar-energy">{{ user.avg_daily_kwh }} kWh/天</span>
              </div>
              <span class="similar-score">{{ user.similarity }}%</span>
            </div>
          </div>
          <div v-else class="no-data">暂无相似用户</div>
        </div>
      </div>

      <!-- 第四行：特征向量雷达图 + 节能建议 -->
      <div class="row">
        <!-- TransE特征向量雷达图 -->
        <div class="panel-card">
          <h3>
          <span class="panel-icon">🧠</span>TransE用户特征向量
          <span class="info-icon">ⓘ</span>
          <div class="tooltip">
            <div><strong>TransE图嵌入说明</strong></div>
            <div>基于知识图谱的语义特征提取算法</div>
            <div class="formula-title">TransE核心思想：</div>
            <div class="formula">h + r ≈ t</div>
            <div>头实体 + 关系 ≈ 尾实体</div>
            <div class="formula-title">嵌入训练：</div>
            <div class="formula">L = Σ[γ + d(h+r,t) - d(h'+r,t')]₊</div>
            <div>• 学习用户的语义表示</div>
            <div>• 捕捉用户间隐含关系</div>
            <div>• 增强FCM聚类效果</div>
          </div>
        </h3>
          <div ref="embeddingRadarRef" class="radar-chart"></div>
          <div class="embedding-info" v-if="userEmbedding">
            <div class="emb-dim">维度: {{ userEmbedding.length }}</div>
            <div class="emb-tip">基于知识图谱TransE算法提取的用户语义特征</div>
          </div>
          <!-- 向量相似用户（懒加载） -->
          <div class="feature-item" @click="toggleSimilarUsers" style="margin-top: 12px;">
            <div class="feature-icon">🔗</div>
            <div class="feature-info">
              <div class="feature-title">基于嵌入的相似用户</div>
              <div class="feature-desc">点击查看与该用户用电行为最相似的用户</div>
            </div>
            <span class="feature-arrow">{{ showEmbeddingSimilar ? '▼' : '▶' }}</span>
          </div>

          <!-- 相似用户列表 -->
          <div v-if="showEmbeddingSimilar" class="feature-panel">
            <div v-if="embeddingSimilarUsers.length > 0" class="similar-list-mini">
              <div v-for="user in embeddingSimilarUsers" :key="user.user_id" class="similar-item-mini">
                <span class="name">{{ user.house_num }}</span>
                <div class="score-bar">
                  <div class="bar-fill" :style="{ width: (user.similarity * 100) + '%' }"></div>
                </div>
                <span class="score">{{ (user.similarity * 100).toFixed(1) }}%</span>
              </div>
            </div>
            <div v-else class="no-data">加载中...</div>
          </div>
        </div>

        <!-- 节能建议 -->
        <div class="panel-card tips-card">
          <h3>
          <span class="panel-icon">💡</span>智能节能建议
          <span class="info-icon">ⓘ</span>
          <div class="tooltip">
            <div><strong>节能建议说明</strong></div>
            <div>基于用户画像特征的个性化建议</div>
            <div class="formula-title">建议生成策略：</div>
            <div>• 对比同类用户平均用电</div>
            <div>• 分析设备能效占比</div>
            <div>• 识别异常用电时段</div>
            <div>• 考虑季节特性影响</div>
            <div>• 评估节能潜力空间</div>
          </div>
        </h3>
          <div class="tips-list" v-if="savingTips.length > 0">
            <div v-for="tip in savingTips.slice(0, 3)" :key="tip.title" class="tip-item" :class="tip.type">
              <div class="tip-title">{{ tip.title }}</div>
              <div class="tip-desc">{{ tip.description }}</div>
              <div class="tip-saving" v-if="tip.potential_saving > 0">
                预计节约: {{ tip.potential_saving }} kWh/天
              </div>
            </div>
          </div>
          <div v-else class="no-data">暂无建议</div>
          <div class="total-saving" v-if="totalSaving > 0">
            总节能潜力: {{ totalSaving }} kWh/天
          </div>
        </div>

        <!-- 季节特性分析 -->
        <div class="panel-card season-card" v-if="seasonAdaptation">
          <h3>
          <span class="panel-icon">🌡️</span>季节特性分析
          <span class="info-icon">ⓘ</span>
          <div class="tooltip">
            <div><strong>季节特性说明</strong></div>
            <div>基于论文《考虑负荷季节特性的电力用户用电行为画像》</div>
            <div class="formula-title">季节因子计算：</div>
            <div class="formula">Sf = (1/n) × Σ(Pi / Pavg)</div>
            <div class="formula-title">季节适应性分类：</div>
            <div>• 夏季敏感型：空调负荷高</div>
            <div>• 冬季敏感型：取暖负荷高</div>
            <div>• 平稳型：季节变化小</div>
            <div>• 均衡型：各季用电平衡</div>
          </div>
        </h3>
          <div class="season-info">
            <div class="season-label">
              <span class="label-name">季节适应性:</span>
              <span class="label-value">{{ seasonAdaptation.label }}</span>
            </div>
            <div class="season-desc">{{ seasonAdaptation.description }}</div>
            <div class="season-ratios">
              <div class="ratio-item" v-for="(ratio, season) in seasonAdaptation.ratios_cn" :key="season">
                <span class="season-name">{{ season }}</span>
                <div class="ratio-bar">
                  <div class="bar-fill" :style="{ width: (ratio * 100) + '%' }"></div>
                </div>
                <span class="ratio-value">{{ (ratio * 100).toFixed(1) }}%</span>
              </div>
            </div>
            <div class="season-index">
              季节性指数: <span class="highlight">{{ (seasonAdaptation.seasonality_index * 100).toFixed(1) }}%</span>
              <span class="index-desc">(差异越大说明季节性越明显)</span>
            </div>
          </div>
        </div>

        <!-- 负荷复杂性分析 -->
        <div class="panel-card complexity-card" v-if="complexityFeatures">
          <h3>
          <span class="panel-icon">📊</span>负荷复杂性分析
          <span class="info-icon">ⓘ</span>
          <div class="tooltip">
            <div><strong>负荷复杂性说明</strong></div>
            <div>基于VMD分解和多维特征提取</div>
            <div class="formula-title">模糊熵(FE)：</div>
            <div class="formula">FE = ln(φm / φm+1)</div>
            <div>表征负荷序列的随机性和复杂性</div>
            <div class="formula-title">统计特征：</div>
            <div>• 变异系数：标准差/均值</div>
            <div>• 负荷率：平均/最大负荷</div>
            <div>• 峰谷差：最大-最小用电</div>
          </div>
        </h3>
          <div class="complexity-info">
            <div class="complexity-item">
              <span class="item-label">模糊熵:</span>
              <span class="item-value">{{ complexityFeatures.fuzzy_entropy?.toFixed(4) || 'N/A' }}</span>
              <span class="item-desc">表征负荷序列随机性</span>
            </div>
            <div class="complexity-item">
              <span class="item-label">样本熵:</span>
              <span class="item-value">{{ complexityFeatures.sample_entropy?.toFixed(4) || 'N/A' }}</span>
              <span class="item-desc">衡量复杂度</span>
            </div>
            <div class="complexity-item">
              <span class="item-label">排列熵:</span>
              <span class="item-value">{{ complexityFeatures.permutation_entropy?.toFixed(4) || 'N/A' }}</span>
              <span class="item-desc">时间序列规律性</span>
            </div>
            <div class="complexity-item">
              <span class="item-label">VMD分解:</span>
              <span class="item-value">{{ complexityFeatures.num_imf_components }} 个分量</span>
              <span class="item-desc">变分模态分解数量</span>
            </div>
          </div>
        </div>

        <!-- 典型用电日 -->
        <div class="panel-card typical-card" v-if="typicalDays && typicalDays.typical_days">
          <h3>
          <span class="panel-icon">📅</span>典型用电日
          <span class="info-icon">ⓘ</span>
          <div class="tooltip">
            <div><strong>典型用电日说明</strong></div>
            <div>基于DTW动态时间规整的K-means聚类</div>
            <div class="formula-title">DTW距离：</div>
            <div class="formula">DTW(i,j) = |xi-yj| + min(DTW(i-1,j),DTW(i,j-1),DTW(i-1,j-1))</div>
            <div>衡量两个日负荷曲线的相似性</div>
            <div class="formula-title">提取流程：</div>
            <div>1. 使用DTW距离进行K-means++聚类</div>
            <div>2. 每类选取距离中心最近的日为代表日</div>
            <div>3. 识别低谷日/平稳日/高峰日</div>
          </div>
        </h3>
          <div class="typical-info">
            <div class="typical-item" v-for="(day, idx) in typicalDays.typical_days" :key="idx">
              <div class="typical-header">
                <span class="typical-type">{{ ['低谷日', '平稳日', '高峰日'][idx] || '类型' + idx }}</span>
                <span class="typical-count">{{ day.count }} 天</span>
              </div>
              <div class="typical-load">
                平均负荷: {{ day.avg_load?.toFixed(2) || 'N/A' }} kWh
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import * as echarts from 'echarts'
import {
  getUserList,
  getUserStatistics,
  getDeviceStatistics,
  getDailyConsumption,
  getUserProfile,
  getUserProfileGraph,
  getUserNetwork,
  getUserPattern,
  getUserFCMMembership,
  getUserEmbedding,
  getProfileSimilarUsers,
  getSavingTips,
  getDeviceCorrelation,
  getFCMClusters,
  getEmbeddingSimilarity,
  getUserSeasonAdaptation,
  getUserTypicalDays,
  getUserComplexityFeatures
} from '../api'

const users = ref([])
const selectedUser = ref('')
const profile = ref({})
const statistics = ref({})
const deviceStats = ref({})
const fcmMembership = ref(null)
const userEmbedding = ref(null)
const similarUsers = ref([])
const savingTips = ref([])
const fcmClusters = ref([])
const topDevices = ref([])
const userPattern = ref({})
const deviceCorrelations = ref([])

const trendChartRef = ref(null)
const devicePieRef = ref(null)
const networkChartRef = ref(null)
const clusterChartRef = ref(null)
const timeslotChartRef = ref(null)
const embeddingRadarRef = ref(null)

const showEmbeddingSimilar = ref(false)
const embeddingSimilarUsers = ref([])

// 季节性特征
const seasonAdaptation = ref(null)
const typicalDays = ref(null)
const complexityFeatures = ref(null)

const totalSaving = computed(() => {
  return savingTips.value.reduce((sum, tip) => sum + (tip.potential_saving || 0), 0).toFixed(2)
})

function formatNumber(num) {
  if (num === undefined || num === null) return '0'
  return Number(num).toFixed(2)
}

function getBehaviorClass(label) {
  const map = { '节能型': 'green', '正常型': 'blue', '高耗能型': 'red' }
  return map[label] || 'blue'
}

function getClusterLabel(key) {
  const labels = ['节能型', '普通型', '波动型', '高耗能型']
  return labels[key] || `类型${key}`
}

function getClusterColor(key) {
  const colors = ['#52c41a', '#1890ff', '#fa8c16', '#f5222d']
  return colors[key] || '#999'
}

function getPatternClass(pattern) {
  const map = { '早峰型': 'morning', '晚峰型': 'evening', '均匀型': 'uniform', '间歇型': 'irregular' }
  return map[pattern] || 'unknown'
}

function getPatternIcon(pattern) {
  const map = { '早峰型': '🌅', '晚峰型': '🌆', '均匀型': '📊', '间歇型': '📈' }
  return map[pattern] || '❓'
}

function getCorrClass(corr) {
  if (corr > 0.7) return 'high'
  if (corr > 0.5) return 'medium'
  return 'low'
}

const statsCards = ref([
  { title: '用户总数', value: 0, icon: '👥', color: 'blue' },
  { title: '总能耗(kWh)', value: 0, icon: '⚡', color: 'orange' },
  { title: '日均能耗(kWh)', value: 0, icon: '📊', color: 'green' },
  { title: '设备总数', value: 0, icon: '🔌', color: 'purple' }
])

async function loadData() {
  try {
    // 获取用户列表
    const usersRes = await getUserList()
    users.value = usersRes.data.users || []
    if (users.value.length > 0 && !selectedUser.value) {
      selectedUser.value = users.value[0].user_id
    }

    // 获取统计数据
    const statsRes = await getUserStatistics()
    statistics.value = statsRes.data
    statsCards.value[0].value = statistics.value.total_users || 0
    statsCards.value[1].value = formatNumber(statistics.value.total_energy_kwh)
    statsCards.value[2].value = formatNumber(statistics.value.avg_daily_kwh)

    // 获取设备统计
    const deviceRes = await getDeviceStatistics()
    deviceStats.value = deviceRes.data
    statsCards.value[3].value = deviceStats.value.total_devices || 0

    // 获取聚类
    const fcmRes = await getFCMClusters()
    fcmClusters.value = fcmRes.data.clusters || []

    // 加载用户数据
    await loadUserData()

    await nextTick()
    initCharts()
  } catch (error) {
    console.error('Error loading data:', error)
  }
}

async function loadUserData() {
  try {
    // 并行请求（不包含相似用户，懒加载）
    const [profileRes, graphRes, patternRes, fcmRes, embRes, similarRes, tipsRes, corrRes, seasonRes, typicalRes, complexityRes] = await Promise.all([
      getUserProfile(selectedUser.value),
      getUserProfileGraph(selectedUser.value),
      getUserPattern(selectedUser.value),
      getUserFCMMembership(selectedUser.value),
      getUserEmbedding(selectedUser.value),
      getProfileSimilarUsers(selectedUser.value),
      getSavingTips(selectedUser.value),
      getDeviceCorrelation(selectedUser.value),
      getUserSeasonAdaptation(selectedUser.value),
      getUserTypicalDays(selectedUser.value, 3),
      getUserComplexityFeatures(selectedUser.value)
    ])

    profile.value = profileRes.data
    userPattern.value = {
      pattern: patternRes.data.pattern || '未知',
      timeslot_distribution: patternRes.data.timeslot_distribution || []
    }
    fcmMembership.value = fcmRes.data.membership || null
    userEmbedding.value = embRes.data.embedding || null
    similarUsers.value = similarRes.data.similar_users || []
    // 不再初始加载相似用户，改为懒加载
    embeddingSimilarUsers.value = []
    savingTips.value = tipsRes.data.tips || []
    deviceCorrelations.value = corrRes.data.correlations || []

    // 季节性特征
    seasonAdaptation.value = seasonRes.data.season_adaptation || null
    typicalDays.value = typicalRes.data.typical_days || null
    complexityFeatures.value = complexityRes.data.complexity_features || null

    // 处理设备数据
    const graphData = graphRes.data.graph || {}
    const devices = (graphData.devices || [])
      .filter(d => d.device_name !== '总用电' && d.total_kwh > 0)
      .sort((a, b) => b.total_kwh - a.total_kwh)
      .slice(0, 5)

    const total = devices.reduce((sum, d) => sum + d.total_kwh, 0)
    topDevices.value = devices.map(d => ({
      ...d,
      percentage: total > 0 ? ((d.total_kwh / total) * 100).toFixed(1) : 0
    }))
  } catch (error) {
    console.error('Error loading user data:', error)
  }
}

async function toggleSimilarUsers() {
  showEmbeddingSimilar.value = !showEmbeddingSimilar.value
  // 懒加载相似用户
  if (showEmbeddingSimilar.value && embeddingSimilarUsers.value.length === 0) {
    try {
      const res = await getEmbeddingSimilarity(selectedUser.value, 5)
      embeddingSimilarUsers.value = res.data.similar_users || []
    } catch (error) {
      console.error('Error loading similar users:', error)
    }
  }
}

function onUserChange() {
  loadUserData().then(() => nextTick(() => initCharts()))
}

function initCharts() {
  initTrendChart()
  initDevicePieChart()
  initNetworkChart()
  initClusterChart()
  initTimeslotChart()
  initEmbeddingRadar()
}

function initTrendChart() {
  if (!trendChartRef.value) return
  let chart = echarts.getInstanceByDom(trendChartRef.value)
  if (chart) chart.dispose()
  chart = echarts.init(trendChartRef.value)

  getDailyConsumption(selectedUser.value, 30).then(res => {
    const data = (res.data || []).reverse()
    const dates = data.map(item => item.date?.slice(5) || '')
    const values = data.map(item => item.total_kwh || 0)

    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: dates, axisLabel: { rotate: 30 } },
      yAxis: { type: 'value', name: 'kWh' },
      series: [{
        name: '用电量',
        type: 'line',
        data: values,
        smooth: true,
        itemStyle: { color: '#722ed1' },
        areaStyle: { color: 'rgba(114, 46, 209, 0.2)' }
      }]
    })
  })
}

function initDevicePieChart() {
  if (!devicePieRef.value || topDevices.value.length === 0) return
  let chart = echarts.getInstanceByDom(devicePieRef.value)
  if (chart) chart.dispose()
  chart = echarts.init(devicePieRef.value)

  const colors = ['#722ed1', '#13c2c2', '#faad14', '#52c41a', '#1890ff']
  chart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
    series: [{
      type: 'pie',
      radius: ['30%', '70%'],
      label: { show: true, formatter: '{b}' },
      data: topDevices.value.map((d, i) => ({
        name: d.device_name,
        value: d.total_kwh,
        itemStyle: { color: colors[i % colors.length] }
      }))
    }]
  })
}

function initNetworkChart() {
  if (!networkChartRef.value) return
  let chart = echarts.getInstanceByDom(networkChartRef.value)
  if (chart) chart.dispose()
  chart = echarts.init(networkChartRef.value)

  getUserNetwork(selectedUser.value).then(res => {
    const nodes = (res.data.nodes || []).slice(0, 15)
    const links = (res.data.links || []).slice(0, 20)
    const categories = [{ name: '用户' }, { name: '设备' }, { name: '能耗等级' }, { name: '行为标签' }]

    chart.setOption({
      tooltip: {},
      series: [{
        type: 'graph',
        layout: 'force',
        data: nodes.map(n => ({
          ...n,
          category: n.category === 'user' ? 0 : n.category === 'device' ? 1 : n.category === 'energy_level' ? 2 : 3,
          symbolSize: n.category === 'user' ? 25 : 12
        })),
        links: links,
        categories: categories,
        roam: true,
        label: { show: true, position: 'right', formatter: '{b}', fontSize: 9 },
        force: { repulsion: 80, edgeLength: 40 },
        lineStyle: { color: 'source', curveness: 0.1 }
      }]
    })
  })
}

function initClusterChart() {
  if (!clusterChartRef.value) return
  let chart = echarts.getInstanceByDom(clusterChartRef.value)
  if (chart) chart.dispose()
  chart = echarts.init(clusterChartRef.value)

  const data = fcmClusters.value.map(c => ({ name: c.cluster_label, value: c.user_count }))
  const colors = ['#52c41a', '#1890ff', '#fa8c16', '#f5222d']

  chart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: data.map((d, i) => ({ ...d, itemStyle: { color: colors[i % colors.length] } })),
      label: { show: true, formatter: '{b}: {c}' }
    }]
  })
}

function initTimeslotChart() {
  if (!timeslotChartRef.value || !userPattern.value.timeslot_distribution) return
  let chart = echarts.getInstanceByDom(timeslotChartRef.value)
  if (chart) chart.dispose()
  chart = echarts.init(timeslotChartRef.value)

  const data = userPattern.value.timeslot_distribution
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
    yAxis: { type: 'category', data: data.map(d => d.timeslot) },
    series: [{
      type: 'bar',
      data: data.map(d => ({
        value: d.percentage,
        itemStyle: { color: d.percentage > 40 ? '#f5222d' : d.percentage > 25 ? '#fa8c16' : '#52c41a' }
      })),
      label: { show: true, position: 'right', formatter: '{c}%' }
    }]
  })
}

function initEmbeddingRadar() {
  if (!embeddingRadarRef.value) return
  let chart = echarts.getInstanceByDom(embeddingRadarRef.value)
  if (chart) chart.dispose()
  chart = echarts.init(embeddingRadarRef.value)

  let emb = userEmbedding.value
  if (!emb || emb.length === 0) emb = Array(64).fill(0).map(() => Math.random() * 0.2)

  const dim = emb.length
  const numGroups = 8
  const groupSize = Math.max(1, Math.floor(dim / numGroups))
  const indicators = []
  const values = []

  for (let i = 0; i < numGroups; i++) {
    const start = i * groupSize
    const end = Math.min(start + groupSize, dim)
    let sum = 0
    for (let j = start; j < end; j++) sum += Math.abs(emb[j])
    const avg = sum / (end - start)
    indicators.push({ name: `维度${i+1}`, max: Math.max(avg * 1.5, 0.2) })
    values.push(parseFloat(avg.toFixed(4)))
  }

  chart.setOption({
    tooltip: {},
    radar: { indicator: indicators, radius: '55%' },
    series: [{
      type: 'radar',
      data: [{
        value: values,
        name: '特征强度',
        areaStyle: { color: 'rgba(114, 46, 209, 0.4)' },
        lineStyle: { color: '#722ed1' },
        itemStyle: { color: '#722ed1' }
      }]
    }]
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  min-height: 100vh;
}

/* Hero Section */
.hero-section {
  position: relative;
  padding: 35px 40px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  color: #fff;
  overflow: hidden;
}

.hero-content { position: relative; z-index: 2; }

.hero-title h1 {
  font-size: 28px;
  margin: 0 0 8px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.hero-title .icon { font-size: 36px; }
.subtitle { font-size: 14px; opacity: 0.8; margin: 0; }

.hero-tags {
  display: flex;
  gap: 12px;
  margin-top: 15px;
}

.hero-tags .tag {
  background: rgba(255,255,255,0.15);
  padding: 6px 14px;
  border-radius: 15px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.hero-bg {
  position: absolute;
  top: 0;
  right: 0;
  width: 45%;
  height: 100%;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="0.5"/><circle cx="50" cy="50" r="30" fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="0.5"/><circle cx="50" cy="50" r="20" fill="none" stroke="rgba(255,255,255,0.02)" stroke-width="0.5"/></svg>');
  background-size: contain;
  background-repeat: no-repeat;
  background-position: right center;
}

/* Stats Section */
.stats-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  padding: 15px 40px;
  margin-top: -25px;
  position: relative;
  z-index: 10;
}

.stat-card {
  background: #fff;
  border-radius: 10px;
  padding: 15px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 3px 15px rgba(0,0,0,0.08);
  transition: transform 0.3s;
}

.stat-card:hover { transform: translateY(-3px); }

.stat-icon {
  font-size: 30px;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
}

.stat-card.blue .stat-icon { background: linear-gradient(135deg, #e6f7ff, #bae7ff); }
.stat-card.orange .stat-icon { background: linear-gradient(135deg, #fff7e6, #ffd591); }
.stat-card.green .stat-icon { background: linear-gradient(135deg, #f6ffed, #b7eb8f); }
.stat-card.purple .stat-icon { background: linear-gradient(135deg, #f9f0ff, #d3adf7); }

.stat-value { font-size: 24px; font-weight: bold; color: #1a1a2e; }
.stat-title { font-size: 12px; color: #666; margin-top: 3px; }

/* User Selector Bar */
.user-selector-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 40px;
  background: #fff;
  margin: 15px 40px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.selector-left { display: flex; align-items: center; gap: 10px; }

.selector-left label { font-weight: 500; color: #333; }

.selector-left select {
  padding: 8px 15px;
  border: 2px solid #e8e8e8;
  border-radius: 6px;
  font-size: 14px;
  min-width: 200px;
  cursor: pointer;
}

.selector-left select:focus { outline: none; border-color: #722ed1; }

.selector-right { display: flex; gap: 10px; }

.selector-right .energy-tag,
.selector-right .behavior-tag,
.selector-right .pattern-tag {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
}

.energy-tag.低 { background: #f6ffed; color: #52c41a; }
.energy-tag.中 { background: #e6f7ff; color: #1890ff; }
.energy-tag.高 { background: #fff7e6; color: #fa8c16; }
.energy-tag.极高 { background: #fff1f0; color: #f5222d; }

.behavior-tag.green { background: #f6ffed; color: #52c41a; }
.behavior-tag.blue { background: #e6f7ff; color: #1890ff; }
.behavior-tag.red { background: #fff1f0; color: #f5222d; }

.pattern-tag { background: #f9f0ff; color: #722ed1; }

/* Radar Chart */
.radar-chart {
  width: 100%;
  height: 220px;
}

.embedding-info {
  text-align: center;
  margin-top: 8px;
}

.emb-dim {
  font-size: 13px;
  color: #722ed1;
  font-weight: 500;
}

.emb-tip {
  font-size: 11px;
  color: #999;
  margin-top: 4px;
}

/* Feature Item */
.feature-item {
  display: flex;
  align-items: center;
  padding: 10px;
  background: #fafafa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.feature-item:hover {
  background: #f0f0f0;
}

.feature-icon {
  font-size: 20px;
  margin-right: 10px;
}

.feature-info {
  flex: 1;
}

.feature-title {
  font-size: 13px;
  font-weight: 500;
  color: #333;
}

.feature-desc {
  font-size: 11px;
  color: #999;
  margin-top: 2px;
}

.feature-arrow {
  color: #999;
  font-size: 12px;
}

.feature-panel {
  margin-top: 10px;
  padding: 10px;
  background: #fafafa;
  border-radius: 8px;
}

.similar-list-mini {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.similar-item-mini {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  background: #fff;
  border-radius: 6px;
}

.similar-item-mini .name {
  font-size: 12px;
  color: #333;
  width: 60px;
}

.similar-item-mini .score-bar {
  flex: 1;
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
}

.similar-item-mini .bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #722ed1, #9254de);
  border-radius: 3px;
}

.similar-item-mini .score {
  font-size: 11px;
  color: #722ed1;
  width: 40px;
  text-align: right;
}

/* Main Content */
.main-content { padding: 0 40px 40px; }

.row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 15px;
}

.panel-card {
  background: #fff;
  border-radius: 10px;
  padding: 18px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.panel-card h3 {
  font-size: 15px;
  margin: 0 0 15px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1a1a2e;
  position: relative;
  cursor: help;
}

.panel-card h3 .info-icon {
  font-size: 12px;
  color: #999;
  margin-left: 4px;
  cursor: help;
  transition: color 0.2s;
}

.panel-card h3:hover .info-icon {
  color: #722ed1;
}

/* Tooltip styles */
.panel-card h3 .tooltip {
  visibility: hidden;
  opacity: 0;
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  width: 320px;
  max-width: 90vw;
  margin: 0 auto 8px auto;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: #fff;
  padding: 12px;
  border-radius: 8px;
  font-size: 12px;
  line-height: 1.6;
  z-index: 100;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  transition: all 0.3s ease;
  pointer-events: none;
  text-align: left;
}

.panel-card h3 .tooltip-wide {
  width: 260px;
  left: 0;
  right: auto;
  margin: 0;
}

.panel-card h3 .tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-top-color: #16213e;
}

.panel-card h3:hover .tooltip {
  visibility: visible;
  opacity: 1;
}

.panel-card h3 .tooltip .formula {
  background: rgba(255,255,255,0.1);
  padding: 6px 8px;
  border-radius: 4px;
  margin: 6px 0;
  font-family: 'Courier New', monospace;
  font-size: 11px;
  color: #ffc069;
  overflow-x: auto;
}

.panel-card h3 .tooltip .formula-title {
  color: #52c41a;
  font-weight: 500;
}

.panel-icon { font-size: 16px; }

.badge {
  font-size: 10px;
  background: #722ed1;
  color: #fff;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: auto;
}

/* Profile Card */
.profile-card .profile-main {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.profile-avatar {
  width: 55px;
  height: 55px;
  border-radius: 50%;
  background: linear-gradient(135deg, #722ed1, #9254de);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  flex-shrink: 0;
}

.profile-detail { flex: 1; }

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-row .label { color: #999; font-size: 13px; }
.detail-row .value { font-weight: 500; font-size: 13px; }
.detail-row .value.highlight { color: #722ed1; font-size: 15px; }

/* FCM Section */
.fcm-section {
  background: #fafafa;
  border-radius: 8px;
  padding: 12px;
}

.fcm-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.fcm-title { font-size: 13px; font-weight: 500; }
.fcm-cluster-label {
  font-size: 12px;
  background: #722ed1;
  color: #fff;
  padding: 2px 8px;
  border-radius: 10px;
}

.membership-bars { display: flex; flex-direction: column; gap: 6px; }

.membership-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.membership-label { width: 45px; font-size: 11px; color: #666; }

.bar-track {
  flex: 1;
  height: 8px;
  background: #e8e8e8;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill { height: 100%; border-radius: 4px; }

.membership-value { width: 40px; text-align: right; font-size: 11px; color: #666; }

/* Trend Card */
.trend-card { grid-column: span 2; }

/* Device Section */
.device-section {
  display: flex;
  gap: 15px;
}

.device-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.device-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 10px;
  background: #fafafa;
  border-radius: 6px;
  font-size: 12px;
}

.device-name { color: #333; }
.device-pct { color: #722ed1; font-weight: bold; }

/* Pattern Section */
.pattern-section { display: flex; gap: 15px; }

.pattern-result {
  width: 70px;
  text-align: center;
}

.pattern-icon {
  font-size: 32px;
  margin-bottom: 5px;
}

.pattern-name { font-size: 13px; font-weight: 500; }

/* Correlations */
.correlations-list { display: flex; flex-direction: column; gap: 8px; }

.corr-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: #fafafa;
  border-radius: 6px;
  font-size: 12px;
}

.corr-symbol { color: #999; }
.corr-score { margin-left: auto; font-weight: 500; }
.corr-score.high { color: #f5222d; }
.corr-score.medium { color: #fa8c16; }
.corr-score.low { color: #1890ff; }

/* Similar List */
.similar-list { display: flex; flex-direction: column; gap: 8px; }

.similar-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 10px;
  background: #fafafa;
  border-radius: 6px;
}

.similar-name { font-weight: 500; font-size: 13px; }
.similar-energy { font-size: 11px; color: #999; margin-left: 8px; }
.similar-score { color: #52c41a; font-weight: bold; font-size: 13px; }

/* Embedding Section */
.embedding-section { display: flex; gap: 15px; }

.embedding-info { flex: 1; display: flex; flex-direction: column; justify-content: center; }

.dim-display {
  background: #fafafa;
  padding: 10px;
  border-radius: 8px;
  text-align: center;
  margin-bottom: 10px;
}

.dim-label { display: block; font-size: 11px; color: #999; }
.dim-value { font-size: 28px; font-weight: bold; color: #722ed1; }

.embedding-desc {
  font-size: 12px;
  color: #666;
  line-height: 1.5;
}

/* Tips */
.tips-list { display: flex; flex-direction: column; gap: 10px; }

.tip-item {
  padding: 12px;
  border-radius: 8px;
  border-left: 3px solid;
}

.tip-item.reduce_level, .tip-item.high_energy { background: #fff7e6; border-color: #fa8c16; }
.tip-item.follow_example { background: #e6f7ff; border-color: #1890ff; }
.tip-item.general { background: #fafafa; border-color: #d9d9d9; }

.tip-title { font-weight: 500; font-size: 13px; margin-bottom: 5px; }
.tip-desc { font-size: 11px; color: #666; margin-bottom: 5px; }
.tip-saving { font-size: 12px; color: #52c41a; font-weight: 500; }

.total-saving {
  margin-top: 12px;
  padding: 10px;
  background: #f6ffed;
  border-radius: 8px;
  text-align: center;
  color: #52c41a;
  font-weight: 500;
}

.no-data {
  text-align: center;
  padding: 30px;
  color: #999;
  font-size: 13px;
}

/* 季节特性分析 */
.season-card {
  border-left: 4px solid #fa8c16;
}

.season-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.season-label {
  display: flex;
  align-items: center;
  gap: 10px;
}

.label-name {
  color: #666;
  font-size: 14px;
}

.label-value {
  background: linear-gradient(135deg, #fa8c16, #ffc069);
  color: white;
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 14px;
  font-weight: 500;
}

.season-desc {
  color: #666;
  font-size: 13px;
  line-height: 1.5;
}

.season-ratios {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-top: 8px;
}

.ratio-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.season-name {
  font-size: 13px;
  color: #333;
  font-weight: 500;
}

.ratio-bar {
  width: 100%;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.ratio-bar .bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #fa8c16, #ffc069);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.ratio-value {
  font-size: 12px;
  color: #666;
}

.season-index {
  margin-top: 8px;
  font-size: 13px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 8px;
}

.season-index .highlight {
  color: #fa8c16;
  font-weight: 600;
  font-size: 16px;
}

.index-desc {
  color: #999;
  font-size: 12px;
}

/* 负荷复杂性分析 */
.complexity-card {
  border-left: 4px solid #13c2c2;
}

.complexity-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.complexity-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 8px;
}

.item-label {
  font-size: 13px;
  color: #333;
  font-weight: 500;
}

.item-value {
  font-size: 18px;
  color: #13c2c2;
  font-weight: 600;
}

.item-desc {
  font-size: 11px;
  color: #999;
}

/* 典型用电日 */
.typical-card {
  border-left: 4px solid #722ed1;
}

.typical-info {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.typical-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 8px;
  text-align: center;
}

.typical-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.typical-type {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.typical-count {
  font-size: 12px;
  color: #722ed1;
  background: rgba(114, 46, 209, 0.1);
  padding: 2px 8px;
  border-radius: 10px;
}

.typical-load {
  font-size: 13px;
  color: #666;
}

/* Responsive */
@media (max-width: 1200px) {
  .row { grid-template-columns: repeat(2, 1fr); }
  .trend-card { grid-column: span 1; }
}

@media (max-width: 768px) {
  .stats-section { grid-template-columns: repeat(2, 1fr); }
  .row { grid-template-columns: 1fr; }
  .user-selector-bar { flex-direction: column; gap: 10px; }
}
</style>
