<template>
  <div class="login-page">
    <!-- 顶部装饰线 -->
    <div class="top-accent"></div>

    <!-- 左侧装饰区 -->
    <div class="login-wrapper">
      <div class="brand-panel">
        <div class="brand-content">
          <div class="power-icon">
            <svg viewBox="0 0 64 64" width="64" height="64">
              <circle cx="32" cy="32" r="28" fill="none" stroke="#5470c6" stroke-width="1.5" opacity="0.3"/>
              <circle cx="32" cy="32" r="20" fill="none" stroke="#5470c6" stroke-width="1" opacity="0.5"/>
              <polygon points="34,12 24,34 30,34 26,52 40,28 34,28 38,12" fill="#5470c6" opacity="0.85"/>
            </svg>
          </div>
          <h1>Power User Profiling</h1>
          <p class="subtitle">基于知识图谱的电力用户画像系统</p>
          <div class="feature-tags">
            <span class="tag">Knowledge Graph</span>
            <span class="tag">FCM Clustering</span>
            <span class="tag">Neo4j</span>
          </div>
        </div>
      </div>

      <div class="form-panel">
        <div class="form-content">
          <h2>Sign In</h2>
          <p class="form-desc">登录您的账户以查看用电画像</p>

          <div class="role-toggle">
            <button :class="['role-btn',{active:loginRole==='user'}]" @click="loginRole='user'" type="button">家庭用户</button>
            <button :class="['role-btn',{active:loginRole==='admin'}]" @click="loginRole='admin'" type="button">管理员</button>
          </div>

          <div class="demo-links">
            <span @click="fillDemo('admin')" class="demo-link">管理员 Demo</span>
            <span class="demo-sep">|</span>
            <span @click="fillDemo('user')" class="demo-link">用户 Demo</span>
          </div>

          <form @submit.prevent="handleLogin">
            <div class="field">
              <label>Username</label>
              <input
                type="text"
                v-model="form.username"
                placeholder="输入用户名"
                :disabled="loading"
                autocomplete="username"
              />
            </div>
            <div class="field">
              <label>Password</label>
              <input
                type="password"
                v-model="form.password"
                placeholder="输入密码"
                :disabled="loading"
                autocomplete="current-password"
              />
            </div>
            <div class="error-msg" v-if="error">{{ error }}</div>
            <button type="submit" class="submit-btn" :disabled="loading">
              {{ loading ? '登录中...' : '登 录' }}
            </button>
          </form>
          <div class="register-link">
            还没有账户？<router-link to="/register">立即注册</router-link>
            <span class="link-sep">|</span>
            <span class="doc-link" @click="showDoc = true">操作文档</span>
          </div>

        </div>
      </div>
    </div>

    <!-- 操作文档弹窗 — 左目录右内容 -->
    <Teleport to="body">
      <Transition name="pop">
        <div class="doc-overlay" v-if="showDoc" @click.self="showDoc = false">
          <div class="doc-modal">
            <div class="doc-head">
              <h2>系统操作手册</h2>
              <p class="doc-sub">电力用户画像知识图谱系统 · 文档编号 KG-OP-001 · V1.0</p>
              <button class="doc-close" @click="showDoc = false">×</button>
            </div>
            <div class="doc-body">
              <!-- 左侧目录 -->
              <nav class="doc-nav" ref="docNav">
                <a v-for="item in docToc" :key="item.id"
                  :href="'#' + item.id"
                  :class="['doc-nav-item', { active: docActive === item.id }]"
                  :style="{ paddingLeft: (12 + item.level * 12) + 'px' }"
                  @click.prevent="docScrollTo(item.id)">{{ item.label }}</a>
              </nav>
              <!-- 右侧内容 -->
              <div class="doc-main" ref="docMain" @scroll="onDocScroll">

                <section id="s1">
                  <h3>系统概述</h3>

                  <h4>系统简介</h4>
                  <p>电力用户画像知识图谱系统（Knowledge Graph-based Power User Profiling System）是一套基于知识图谱技术的电力用户行为画像分析平台。系统以知识图谱技术为核心，对电力用户的用电行为、设备配置、缴费记录、家庭特征等多维度数据进行可视化建模与分析，帮助用户了解自身用电习惯，辅助管理者进行全局用电调度。</p>
                  <p>系统按角色划分为<b>家庭用户模块</b>和<b>管理员模块</b>两大功能域。家庭用户可管理个人信息、用电设备、缴纳电费、提交维修报修；管理员可通过月度仿真引擎推进系统时间、监控全局知识图谱、审核维修工单、发布公告及管理用户数据。</p>

                  <div class="doc-accounts">
                    <span><b>管理员</b> admin / 123456</span>
                    <span><b>用户1</b> user001 / 123456</span>
                    <span><b>用户2</b> user002 / 123456</span>
                    <span><b>用户3</b> user003 / 123456</span>
                  </div>
                  <p class="doc-note">※ 本系统为纯前端演示版本，数据存储于浏览器 localStorage。清除浏览器缓存或更换浏览器将恢复初始演示数据。</p>

                  <h4>技术特性</h4>
                  <ul>
                    <li><b>知识图谱可视化</b>：基于 ECharts 力导向图引擎，以用户节点为中心，向外辐射五大类节点（设备管理、用电特征、账单记录、家庭信息、画像标签），支持节点点击详查、双击展开折叠、自由拖拽与缩放。设备节点按六大类别以六种颜色区分，节点大小与设备功率成正比。</li>
                    <li><b>威布尔分布设备损坏模型</b>：设备损坏概率采用双参数 Weibull 分布 P(损坏) = 1 - exp(-(t/η)^β) 计算。特征寿命 η 由设备预期寿命、品牌品质系数（BQF）联合决定，形状参数 β 因设备类型而异（1.5~2.8）。</li>
                    <li><b>品牌品质系数</b>：不同品牌对应不同的 BQF 值（格力 1.10、美的 1.05、海尔 1.08、西门子 1.20、松下 1.15、通用 1.00、经济品牌 0.85），影响设备特征寿命，高品质品牌设备损坏概率更低。</li>
                    <li><b>月度模拟引擎</b>：管理员一键触发推进操作，系统自动遍历所有活跃设备计算当月用电量、汇总维修费用生成账单、检测连续欠费（≥2 月）并标记警告、更新设备年限并重算损坏概率、将超 80% 阈值的设备标记为损坏。</li>
                    <li><b>老化功率修正</b>：设备有效功率按二次衰减曲线 P_有效 = P_额定 × (1 + 老化率 × (t/T)²) 动态调整，模拟真实世界中设备随使用年限增加而效率下降的趋势。</li>
                  </ul>

                  <h4>数据规模</h4>
                  <table class="doc-table">
                    <tr><td>演示用户</td><td>4 人（管理员 1 + 家庭用户 3：王建国 / 陈美丽 / 李大爷）</td></tr>
                    <tr><td>预设电器类型</td><td>34 种，覆盖六大类别</td></tr>
                    <tr><td>用电设备</td><td>20 台</td></tr>
                    <tr><td>历史用电记录</td><td>90+ 条，覆盖 6 个月（2025-08 ~ 2026-01）</td></tr>
                    <tr><td>月度账单</td><td>16+ 张</td></tr>
                    <tr><td>选项字典</td><td>19 类（性别/民族/学历/职业/住房类型等）</td></tr>
                  </table>
                </section>

                <section id="s2">
                  <h3>家庭用户操作指南</h3>

                  <h4>登录系统</h4>
                  <ol>
                    <li>打开系统网址，进入登录界面</li>
                    <li>确认左上方角色切换按钮选中<b>「家庭用户」</b>（蓝色高亮状态）</li>
                    <li>输入用户名和密码，或点击<b>「用户 Demo」</b>快速填充演示账号（user001 / 123456）</li>
                    <li>点击<b>「登 录」</b>按钮</li>
                    <li>验证通过后，系统自动跳转至用户首页</li>
                  </ol>
                  <p><b>错误处理</b>：用户名或密码输入错误时，表单下方显示红色错误提示文字。新用户需点击「立即注册」进入六步注册向导创建账号。</p>

                  <h4>首页 — 个人信息维护</h4>
                  <p>用户首页采用左右双栏布局。左侧自上而下依次为：</p>
                  <ul>
                    <li><b>个人画像摘要区</b>：显示用户姓名首字头像、姓名、性别、出生年份、学历、职业等身份标签，以及上月用电量、预估电费、设备数量、累计账单数四项统计指标</li>
                    <li><b>基本信息面板</b>：展示 15 个字段（姓名/性别/出生年月/民族/学历/婚姻状况/政治面貌/宗教信仰/职业/工作单位/联系电话/城乡分类/日常作息/健康自评/详细地址）</li>
                    <li><b>住房信息面板</b>：展示住房类型/建筑面积/户型/楼层/电梯/供暖方式/朝向/房龄</li>
                    <li><b>家庭成员面板</b>：展示全部家庭成员（姓名/关系/同住状态）</li>
                    <li><b>收入信息面板</b>：展示个人年收入/家庭年收入/收入来源/经济自评</li>
                  </ul>
                  <p>右侧为<b>系统公告栏</b>和<b>留言板</b>。</p>
                  <p><b>编辑操作</b>：各面板右上角均有「编辑」按钮。点击进入编辑状态后，下拉选项字段（性别/学历/职业等）均从系统选项字典获取。修改完成后点击「保存」，系统通过 PUT 接口将数据实时更新至存储层，页面数据即时刷新。</p>
                  <p><b>成员管理</b>：点击「管理」按钮可添加新成员（姓名/关系选择/是否同住）或删除已有成员。</p>
                  <p><b>留言操作</b>：点击「写留言」→ 输入内容 → 发送。未回复留言支持撤回，管理员回复后不可撤回。</p>

                  <h4>用电画像 — 知识图谱</h4>
                  <p>系统的核心可视化模块，以力导向知识图谱直观呈现用户的用电行为全貌。页面分为左右两部分：</p>
                  <p><b>左侧画像面板</b>：</p>
                  <ul>
                    <li>头像卡片 + 身份标签（性别/年龄/学历/婚姻）</li>
                    <li>四项核心指标（能耗等级、月均用电 kWh、设备数、已缴/总账单）</li>
                    <li>彩色标签词云（聚合用户多维度信息标签，最多 35 个）</li>
                    <li>基本信息简表（职业/城乡/作息/健康/住房/面积/收入）</li>
                    <li>月度用电趋势迷你折线图</li>
                  </ul>
                  <p><b>右侧知识图谱</b>：</p>
                  <ul>
                    <li>初始状态仅显示中心用户节点（蓝色大圆）和五个大类节点（灰色方框）共 6 个节点、5 条连线</li>
                    <li><b>双击大类节点</b>：展开该类别下所有子节点（设备/账单/标签等），再次双击折叠</li>
                    <li><b>单击任意节点</b>：右侧滑出 300px 详情面板，展示该节点的完整数据信息</li>
                    <li><b>设备节点颜色</b>：蓝色=空气调节 / 黄色=厨房电器 / 绿色=清洁卫生 / 红色=娱乐影音 / 青色=照明设备 / 棕色=其他</li>
                    <li>损坏设备以红色虚线边框标示</li>
                    <li>支持鼠标滚轮缩放、拖拽平移、节点拖拽</li>
                  </ul>

                  <h4>设备管理</h4>
                  <p>以卡片网格展示用户全部用电设备。每张设备卡片包含：设备名称、环形用电进度图（弧线长度对应实际用电占当月最大可能用电的比例）、当前有效功率（W，已考虑老化修正）、使用习惯、已用年限（保留一位小数）、损坏概率（百分比进度条，&lt;50% 蓝 / 50-80% 黄 / &gt;80% 红）、运行状态标记。</p>
                  <p><b>添加设备（四步向导）</b>：</p>
                  <ol>
                    <li><b>选择类别</b>：从六大设备类别中选择</li>
                    <li><b>选择型号</b>：从该类别的 34 种预设电器中选择具体型号（标注额定功率和预期寿命）</li>
                    <li><b>填写参数</b>：选择品牌（影响 BQF 值）、输入已使用年限、日均使用时长，选择使用习惯（全天运行/白天使用/夜间使用/偶尔使用/季节性使用）</li>
                    <li><b>确认添加</b>：汇总展示设备信息，提交后系统自动运用威布尔公式计算有效功率和损坏概率</li>
                  </ol>
                  <p><b>月份切换</b>：页面顶部「查看月份」区域提供前后月份切换，切换后所有卡片环形图更新为该月用电数据。</p>
                  <p><b>删除设备</b>：点击卡片「删除」按钮 → 确认 → 设备及关联用电记录被移除。</p>

                  <h4>电费缴费</h4>
                  <p>左侧列出本月所有待缴电费账单（月份/用电量/金额，欠费警告以红色标签标出）。点击「缴费」进入四步支付向导：</p>
                  <ol><li>账单摘要确认</li><li>选择支付方式（银行卡/微信）</li><li>输入六位数字密码</li><li>系统处理中 → 缴费成功</li></ol>
                  <p>缴费后账单状态变为「已缴」，按钮消失，标注实际缴费日期。下方维修缴费栏单独列出本月维修费用明细。</p>
                  <p>右侧<b>缴费通知栏</b>按月展示通知（蓝色=正常 / 红色=欠费警告），底部<b>缴费历史表格</b>列出全部历史账单，支持按缴费状态和年份下拉筛选。</p>

                  <h4>维修报单</h4>
                  <p>页面展示设备运行状态概览：</p>
                  <ul>
                    <li><b>所有设备正常</b>：绿色提示「所有设备运行正常」，正常设备以折叠列表收纳</li>
                    <li><b>存在损坏设备</b>：红色卡片列出故障设备（名称/类别/功率/年限/损坏概率），每张卡片右侧提供「报修」按钮</li>
                  </ul>
                  <p><b>报修流程（三步向导）</b>：选择故障设备 → 选择故障类型（10 种：无法开机/运行异常/漏电/噪音异常/不制冷不制热/漏水/频繁启停/异味冒烟/显示异常报错/其他）+ 填写描述 + 预约时间 → 确认提交。</p>
                  <p>底部报修记录表展示历次工单（单号/故障类型/状态/费用/评价）。维修完成后用户可对服务评分（1~5 星）。</p>
                </section>

                <section id="s3">
                  <h3>管理员操作指南</h3>

                  <h4>登录与角色识别</h4>
                  <p>管理员登录流程与用户一致。在登录界面将角色切换按钮选中「管理员」，点击「管理员 Demo」快速填充 admin / 123456。登录成功后在侧边栏显示管理员标识（头像「管」、用户名 admin、角色「管理员」），导航菜单包含三个入口：<b>系统概览、知识图谱、数据管理</b>。</p>

                  <h4>系统概览 — 月度推进引擎</h4>
                  <p><b>「推进至下月」</b>是系统的核心管理操作，一键触发全量用户的月度仿真计算。点击按钮并确认后，系统自动执行以下七步流程：</p>
                  <ol>
                    <li>获取当前系统月份（如 2026-01）</li>
                    <li>遍历所有非管理员用户的活跃设备，逐台计算当月用电量：月度 kWh = P_有效(W) × 日均使用小时 × 当月天数 / 1000</li>
                    <li>将每台设备的计算结果作为一条 ElectricityRecord 写入存储</li>
                    <li>汇总每位用户当月已完成的维修费用，与电费合计生成 Bill 月度账单</li>
                    <li>检查每位用户是否连续 ≥2 个月未缴费，若存在则标记 warning_flag=1</li>
                    <li>每台设备 usage_years += 1/12，重新计算有效功率和损坏概率</li>
                    <li>损坏概率 > 80% 的设备标记 is_active=0，记录 damage_date</li>
                  </ol>
                  <p>推进完成后页面显示绿色提示框：「推进完成！Y 条记录，Z 张账单」。</p>

                  <h4>统计仪表盘</h4>
                  <p>六张统计卡片实时展示系统运行数据：用户总数、活跃/总设备数、损坏设备数、账单收缴率（已缴/总账单）、待审核维修工单数、当前电价（元/度）。</p>

                  <h4>系统公告管理</h4>
                  <p>点击「+ 发布」展开公告编辑表单。填写标题（必填）、内容，勾选「置顶」后发布。置顶公告将在所有用户首页公告栏以 📌 标记优先显示。每条公告支持删除操作。</p>

                  <h4>用户留言管理</h4>
                  <p>留言列表以时间倒序排列，展示用户姓名、留言内容和时间。未回复留言点击「回复」展开内联输入框 → 输入内容 → 点击「发送」提交。已回复留言显示回复内容和回复时间。支持删除操作。</p>

                  <h4>知识图谱（管理员视角）</h4>
                  <p>页面顶部右侧提供用户选择下拉框，列出所有家庭用户（格式：「姓名 (户号)」）。选择目标用户后，系统即时加载该用户的个性化知识图谱，展示内容与用户端「用电画像」完全一致：左侧画像面板（头像/指标/词云/趋势图）+ 右侧力导向图 + 详情滑出面板。切换用户后数据即时刷新。</p>

                  <h4>数据管理</h4>
                  <p>五个子标签页的完整功能说明：</p>
                  <table class="doc-table">
                    <tr><td><b>用户管理</b></td><td>表格（户号/用户名/姓名/电话/设备数），支持新增（用户名+姓名+密码）、编辑（姓名/电话/性别/出生/学历/职业/地址弹窗）、查看详情（六区详情弹窗：基本/住房/收入/设备/账单/家庭）、删除（确认后级联删除关联数据）、搜索（按姓名或用户名实时过滤）</td></tr>
                    <tr><td><b>设备管理</b></td><td>全部用户设备表（名称/类别/所属用户/功率/年限/损坏率/状态），支持按名称搜索和按类别下拉筛选，可删除设备</td></tr>
                    <tr><td><b>维修审核</b></td><td>全部维修工单表（单号/用户/设备/故障/状态/费用），支持按状态筛选（全部/待处理/已派单/维修中/已完成），待处理工单可派单（输入维修人员），维修中工单可完成（输入费用金额，费用计入下月账单）</td></tr>
                    <tr><td><b>系统公告</b></td><td>公告发布（标题/内容/置顶）+ 公告列表（按置顶优先+时间倒序），支持删除</td></tr>
                    <tr><td><b>用户留言</b></td><td>全部留言列表（用户/内容/回复状态/日期），点击回复展开内联输入框，支持删除</td></tr>
                  </table>
                </section>

                <section id="s4">
                  <h3>算法与数据说明</h3>

                  <h4>威布尔分布损坏模型</h4>
                  <p>设备损坏概率采用双参数威布尔分布（Weibull Distribution）计算。该分布广泛应用于可靠性工程中模拟设备寿命分布：</p>
                  <p class="doc-formula">P(损坏) = 1 − exp(−(t / η)<sup>β</sup>)</p>
                  <p>其中 t = 已用年限，η = 特征寿命 = 预期寿命 × 1.2 × BQF，β = 形状参数（1.5~2.8，因设备类型而异）。BQF 为品牌品质系数：格力 1.10、美的 1.05、海尔 1.08、西门子 1.20、松下 1.15、通用 1.00、经济品牌 0.85。BQF 越高，设备特征寿命越长，损坏概率越低。</p>

                  <h4>老化功率修正</h4>
                  <p>设备有效功率随使用年限逐步退化，采用二次衰减曲线建模：</p>
                  <p class="doc-formula">P<sub>有效</sub> = P<sub>额定</sub> × (1 + α × (t / T)<sup>2</sup>)</p>
                  <p>其中 α 为老化率（默认 15%，不同设备类型可配置），t 为已用年限，T 为预期寿命。注意：该公式描述的是功率的<b>增加</b>（而非减少），因为老化设备需要消耗更多电力来维持同等输出。</p>

                  <h4>数据存储与持久性</h4>
                  <ul>
                    <li><b>初始加载</b>：首次访问时，系统从 /data/ 目录拉取 10 份 JSON 种子文件，解析后存入 localStorage</li>
                    <li><b>写入操作</b>：所有用户修改操作（编辑信息/添加设备/缴费/留言/管理员操作等）实时写入 localStorage 的种子数据区</li>
                    <li><b>读取策略</b>：数据读取时优先使用 localStorage 中的缓存数据（含用户修改），种子文件仅在缓存不存在时重新加载</li>
                    <li><b>数据恢复</b>：清除浏览器 localStorage 或使用无痕模式将触发重新加载种子数据，恢复为初始演示状态</li>
                    <li><b>数据隔离</b>：不同浏览器、不同设备间的数据完全独立，互不影响</li>
                  </ul>
                </section>

                <section id="s5">
                  <h3>常见问题（FAQ）</h3>
                  <div class="doc-faq">
                    <p class="doc-faq-q">Q1：登录时提示"用户名或密码错误"怎么办？</p>
                    <p class="doc-faq-a">检查角色切换是否正确（管理员≠家庭用户），确认键盘未开启大写锁定。演示账号密码统一为 123456。如仍无法登录，清除浏览器 localStorage 后刷新页面重试。</p>

                    <p class="doc-faq-q">Q2：推进月份后，用户端的"当前月份"为什么没有变化？</p>
                    <p class="doc-faq-a">用户端"当前月份"来自系统月份参数。请确认管理员已成功执行推进操作（页面显示"推进完成！"提示）。如执行后仍显示旧月份，刷新用户页面即可。</p>

                    <p class="doc-faq-q">Q3：推进月份后，在哪里查看新生成的账单？</p>
                    <p class="doc-faq-a">退出管理员账号，以家庭用户身份登录，进入「电费缴费」即可看到新生成的待缴账单。</p>

                    <p class="doc-faq-q">Q4：设备为什么会损坏？损坏概率如何判定？</p>
                    <p class="doc-faq-a">管理员推进月份时，系统根据威布尔分布模型重新计算每台设备的损坏概率。概率超过 80% 阈值时设备被自动标记为损坏（is_active=0），在设备管理卡片上显示为红色状态。</p>

                    <p class="doc-faq-q">Q5：数据会不会丢失？</p>
                    <p class="doc-faq-a">系统数据存储在浏览器 localStorage 中。正常关闭标签页、重启浏览器数据保留。以下操作会触发数据重置：清除浏览器缓存/历史记录、使用无痕/隐私模式、更换浏览器、更换设备。</p>

                    <p class="doc-faq-q">Q6：知识图谱节点太多看不清怎么办？</p>
                    <p class="doc-faq-a">使用鼠标滚轮缩小视图；双击已展开的大类节点折叠子节点；拖拽节点调整布局。图谱已打开的大类节点可通过双击重新折叠。</p>

                    <p class="doc-faq-q">Q7：如何注册新用户？</p>
                    <p class="doc-faq-a">在登录界面点击「立即注册」进入六步向导：①填写用户名和密码 → ②填写个人基本信息 → ③填写住房信息 → ④勾选拥有设备并配置使用参数 → ⑤填写收入信息 → ⑥确认并提交。注册成功后自动登录。</p>

                    <p class="doc-faq-q">Q8：管理员可以同时查看多个用户的知识图谱吗？</p>
                    <p class="doc-faq-a">可以。管理员知识图谱页面顶部有用户选择下拉框，切换用户后图谱即时刷新。每次只能查看一个用户的图谱，但可以快速切换。</p>
                  </div>
                </section>

              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 底部装饰 -->
    <div class="footer-wave">
      <svg viewBox="0 0 1200 60" preserveAspectRatio="none">
        <path d="M0,40 C200,10 400,50 600,30 C800,10 1000,50 1200,20 L1200,60 L0,60 Z" fill="#5470c6" opacity="0.06"/>
        <path d="M0,50 C300,30 600,55 900,40 C1050,32 1150,48 1200,45 L1200,60 L0,60 Z" fill="#5470c6" opacity="0.04"/>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api/index.js'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const loginRole = ref('user')
const form = reactive({ username: '', password: '' })
const showDoc = ref(false)

// ========== 操作文档 — 目录与滚动联动 ==========
const docMain = ref(null)
const docActive = ref('s1')

const docToc = [
  { id: 's1', label: '系统概述', level: 0 },
  { id: 's2', label: '家庭用户操作指南', level: 0 },
  { id: 's3', label: '管理员操作指南', level: 0 },
  { id: 's4', label: '算法与数据说明', level: 0 },
  { id: 's5', label: '常见问题（FAQ）', level: 0 },
]

function docScrollTo(id) {
  docActive.value = id
  const el = document.getElementById(id)
  if (el && docMain.value) {
    docMain.value.scrollTo({ top: el.offsetTop - 24, behavior: 'smooth' })
  }
}

function onDocScroll() {
  if (!docMain.value) return
  const scrollTop = docMain.value.scrollTop + 80
  let active = docToc[0].id
  for (const item of docToc) {
    const el = document.getElementById(item.id)
    if (el && el.offsetTop <= scrollTop) active = item.id
  }
  docActive.value = active
}

function fillDemo(role) {
  loginRole.value = role
  const accounts = { admin: 'admin', user: 'user001' }
  form.username = accounts[role]
  form.password = '123456'
}

async function handleLogin() {
  error.value = ''
  if (!form.username || !form.password) {
    error.value = '请输入用户名和密码'
    return
  }
  loading.value = true
  try {
    const res = await login(form.username, form.password)
    if (res.data.status === 'success') {
      const { token, user } = res.data
      // 验证角色是否匹配
      if (loginRole.value === 'admin' && user.role !== 'admin') {
        error.value = '该账号不是管理员，请使用管理员账号登录'; loading.value = false; return
      }
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('role', user.role)
      localStorage.setItem('elec_user_id', user.elec_user_id || '')
      // 用 location.replace 避免浏览器缓存导致的导航栏角色错乱
      window.location.replace(user.role === 'admin' ? '/#/admin' : '/#/')
    }
  } catch (err) {
    error.value = err.response?.data?.message || '用户名或密码错误'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
* { box-sizing: border-box; }

.login-page {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafbfc;
  overflow: hidden;
}

/* 顶部细线 */
.top-accent {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, #5470c6, #91cc75, #5470c6);
}

/* 主布局 */
.login-wrapper {
  display: flex;
  width: 820px;
  max-width: calc(100vw - 40px);
  background: #fff;
  border: 1px solid #e8ecf0;
  border-radius: 2px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 8px 40px rgba(0,0,0,0.06);
  overflow: hidden;
  z-index: 1;
}

/* 左侧品牌区 */
.brand-panel {
  width: 400px;
  background: #f8f9fb;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  border-right: 1px solid #eef0f4;
}

.brand-content {
  text-align: center;
}

.power-icon {
  margin-bottom: 24px;
}

.brand-panel h1 {
  font-size: 18px;
  font-weight: 500;
  color: #2c3e50;
  margin: 0 0 8px;
  letter-spacing: 0.5px;
}

.subtitle {
  font-size: 13px;
  color: #8c9aa8;
  margin: 0 0 28px;
  font-weight: 300;
}

.feature-tags {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}

.tag {
  font-size: 11px;
  padding: 4px 10px;
  border: 1px solid #dde3ea;
  border-radius: 2px;
  color: #7c8a98;
  font-weight: 300;
}

/* 右侧表单区 */
.form-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 48px;
}

.form-content {
  width: 100%;
  max-width: 280px;
}

.form-content h2 {
  font-size: 20px;
  font-weight: 400;
  color: #333;
  margin: 0 0 6px;
}

.form-desc {
  font-size: 12px;
  color: #999;
  margin: 0 0 20px;
  font-weight: 300;
}

.role-toggle { display: flex; margin-bottom: 20px; border: 1px solid #e0e0e0; border-radius: 6px; overflow: hidden; }
.role-btn { flex: 1; padding: 8px 0; background: #fff; border: none; font-size: 12px; color: #999; cursor: pointer; transition: all 0.15s; }
.role-btn.active { background: #2c3e50; color: #fff; }

.demo-links { text-align: center; margin-bottom: 18px; font-size: 11px; color: #ccc; }
.demo-link { color: #999; cursor: pointer; transition: color 0.15s; }
.demo-link:hover { color: #5470c6; }
.demo-sep { margin: 0 8px; color: #ddd; }

.field {
  margin-bottom: 20px;
}

.field label {
  display: block;
  font-size: 12px;
  color: #999;
  margin-bottom: 6px;
  font-weight: 300;
}

.field input {
  width: 100%;
  padding: 10px 0;
  border: none;
  border-bottom: 1px solid #e0e0e0;
  font-size: 14px;
  color: #333;
  outline: none;
  background: transparent;
  transition: border-color 0.2s;
}

.field input:focus {
  border-bottom-color: #5470c6;
}

.field input::placeholder {
  color: #ccc;
  font-weight: 300;
}

.field input:disabled {
  opacity: 0.5;
}

.error-msg {
  color: #c0392b;
  font-size: 12px;
  text-align: center;
  margin-bottom: 16px;
  padding: 8px 0;
}

.submit-btn {
  width: 100%;
  padding: 12px 0;
  background: #2c3e50;
  color: #fff;
  border: none;
  font-size: 13px;
  cursor: pointer;
  letter-spacing: 1px;
  transition: background 0.2s;
}

.submit-btn:hover {
  background: #5470c6;
}

.submit-btn:disabled {
  background: #bbb;
  cursor: not-allowed;
}

.register-link { text-align: center; margin-top: 20px; font-size: 12px; color: #aaa; }
.register-link a { color: #5470c6; text-decoration: none; font-weight: 500; }
.register-link a:hover { text-decoration: underline; }
.link-sep { margin: 0 8px; color: #ddd; }
.doc-link { color: #5470c6; cursor: pointer; font-weight: 500; }
.doc-link:hover { text-decoration: underline; }

/* 操作文档弹窗 — 左目录右内容 */
.doc-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 2000;
  display: flex; align-items: center; justify-content: center;
}
.doc-modal {
  background: #fff; border-radius: 14px; width: 960px; max-height: 90vh;
  display: flex; flex-direction: column; position: relative;
  box-shadow: 0 24px 80px rgba(0,0,0,0.2);
}
.doc-head {
  padding: 24px 32px 16px; border-bottom: 1px solid #edf0f4;
  flex-shrink: 0; position: relative;
}
.doc-head h2 { font-size: 20px; color: #1a1a2e; margin: 0; font-weight: 700; }
.doc-head .doc-sub { font-size: 11px; color: #999; margin: 3px 0 0; }
.doc-close {
  position: absolute; top: 20px; right: 24px;
  width: 32px; height: 32px; background: #f5f5f5; border: none; border-radius: 50%;
  font-size: 18px; color: #999; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all .15s;
}
.doc-close:hover { background: #e8e8e8; color: #333; }
.doc-body {
  flex: 1; display: flex; overflow: hidden; min-height: 0;
}
.doc-nav {
  width: 220px; flex-shrink: 0; border-right: 1px solid #edf0f4;
  padding: 16px 0; overflow-y: auto; background: #fafbfc;
}
.doc-nav-item {
  display: block; padding: 9px 20px; font-size: 12px; color: #666;
  text-decoration: none; cursor: pointer; transition: all .15s;
  line-height: 1.4; border-left: 3px solid transparent;
  font-weight: 400;
}
.doc-nav-item:hover { color: #2c3e50; background: #f0f2f5; }
.doc-nav-item.active {
  color: #5470c6; font-weight: 600; background: #eef2ff;
  border-left-color: #5470c6;
}
.doc-main {
  flex: 1; padding: 24px 32px 40px; overflow-y: auto;
  font-size: 13px; color: #555; line-height: 1.85;
}
.doc-main h3 { font-size: 17px; color: #1a1a2e; margin: 32px 0 16px; padding-bottom: 10px; border-bottom: 2px solid #5470c6; }
.doc-main h3:first-child { margin-top: 0; }
.doc-main h4 { font-size: 14px; color: #2c3e50; margin: 20px 0 8px; font-weight: 600; }
.doc-main p { margin: 4px 0 14px; }
.doc-main b { color: #2c3e50; }
.doc-main ul, .doc-main ol { margin: 8px 0 16px; padding-left: 22px; }
.doc-main li { margin: 5px 0; }
.doc-note { font-size: 12px; color: #999; padding: 8px 14px; background: #fffbe6; border-radius: 6px; border-left: 3px solid #f5d23e; }
.doc-accounts {
  display: flex; gap: 16px; flex-wrap: wrap; margin: 12px 0; padding: 12px 18px;
  background: #f7f9fc; border-radius: 8px; font-size: 12px; border: 1px solid #edf0f4;
}
.doc-accounts span { color: #555; }
.doc-table {
  width: 100%; border-collapse: collapse; margin: 10px 0 16px; font-size: 12px;
}
.doc-table td { padding: 8px 12px; border-bottom: 1px solid #f0f2f5; }
.doc-table td:first-child { font-weight: 600; color: #2c3e50; width: 120px; white-space: nowrap; background: #fafbfc; }
.doc-formula {
  text-align: center; font-size: 15px; color: #5470c6; padding: 12px 0;
  font-weight: 600; font-style: italic; font-family: Georgia, serif;
}
.doc-faq-q { font-weight: 600; color: #2c3e50; margin-bottom: 2px; }
.doc-faq-a { margin-left: 14px; padding-left: 10px; border-left: 2px solid #d0d5dd; color: #666; margin-bottom: 18px; }

/* 弹窗动画 */
.pop-enter-active, .pop-leave-active { transition: opacity 0.25s; }
.pop-enter-active .doc-modal, .pop-leave-active .doc-modal { transition: transform 0.25s; }
.pop-enter-from, .pop-leave-to { opacity: 0; }
.pop-enter-from .doc-modal { transform: scale(0.95) translateY(12px); }
.pop-leave-to .doc-modal { transform: scale(0.95) translateY(12px); }

/* 底部波浪 */
.footer-wave {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 60px;
}

/* 响应式 */
@media (max-width: 780px) {
  .login-wrapper {
    flex-direction: column;
    max-width: 380px;
  }
  .brand-panel {
    width: 100%;
    padding: 32px 24px;
    border-right: none;
    border-bottom: 1px solid #eef0f4;
  }
  .power-icon { margin-bottom: 16px; }
  .power-icon svg { width: 40px; height: 40px; }
  .brand-panel h1 { font-size: 15px; }
  .subtitle { margin-bottom: 16px; }
  .form-panel { padding: 32px 28px; }
  .form-desc { margin-bottom: 24px; }
}

@media (max-height: 700px) {
  .brand-panel { padding: 30px 24px; }
  .form-panel { padding: 30px 28px; }
  .field { margin-bottom: 14px; }
  .power-icon svg { width: 40px; height: 40px; }
}
</style>
