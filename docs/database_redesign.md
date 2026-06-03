# 数据库结构重新设计稿

## 一、设计背景

基于CGSS2023（中国综合社会调查）数据结构，结合现有电力用户画像系统需求，重新设计数据库架构。

**CGSS2023数据概况**：
- 样本量：11,326条记录
- 变量数：436个字段
- 涵盖模块：基本信息、家庭信息、教育信息、工作信息、收入财产、健康信息、住房信息、社会态度、价值观等

## 二、设计原则

1. **标准化**：遵循数据库第三范式（3NF），消除数据冗余
2. **模块化**：按业务主题划分表结构，便于维护和扩展
3. **可追溯**：保留原始字段编码，便于与CGSS编码表对照
4. **扩展性**：预留字段便于后续功能扩展

## 三、表结构设计

### 3.1 核心表清单

| 序号 | 表名 | 中文名称 | 说明 |
|------|------|---------|------|
| 1 | respondent | 受访者基本信息表 | 存储受访者核心信息 |
| 2 | family_member | 家庭成员信息表 | 存储家庭成员关系 |
| 3 | education | 教育经历表 | 存储教育背景信息 |
| 4 | work_experience | 工作经历表 | 存储就业和工作信息 |
| 5 | income | 收入信息表 | 存储各类收入数据 |
| 6 | property | 财产信息表 | 存储房产、车辆等财产 |
| 7 | health | 健康信息表 | 存储健康和医疗信息 |
| 8 | housing | 住房信息表 | 存储住房基本情况 |
| 9 | social_attitude | 社会态度表 | 存储社会信任、幸福感等 |
| 10 | media_usage | 媒体使用表 | 存储媒体接触和行为 |
| 11 | value_belief | 价值观表 | 存储价值观念信息 |
| 12 | survey_record | 调查记录表 | 存储调查过程信息 |

---

### 3.2 详细表结构

---

#### 表1：respondent（受访者基本信息表）

存储受访者的核心基本信息，是整个数据库的主表。

| 字段名 | 数据类型 | 长度 | 约束 | 描述 |
|--------|----------|------|------|------|
| respondent_id | VARCHAR | 50 | PRIMARY KEY | 受访者唯一标识（原id） |
| survey_date | DATETIME | - | - | 调查日期（原a00） |
| province_code | INT | - | - | 省份编码（原s41） |
| city_code | INT | - | - | 城市编码（原s42） |
| district_code | INT | - | - | 地区编码（原s43） |
| is_urban | TINYINT | - | - | 城乡分类：1=城市，2=农村（原isurban） |
| gender | TINYINT | - | - | 性别：1=男，2=女（原a2） |
| birth_year | INT | - | - | 出生年份（原a3a） |
| birth_month | TINYINT | - | - | 出生月份（原a3b） |
| ethnicity | TINYINT | - | - | 民族编码（原a3c） |
| education_level | TINYINT | - | - | 受教育程度编码（原a4） |
| education_years | INT | - | - | 受教育年限（原a5） |
| marital_status | TINYINT | - | - | 婚姻状况（原a6） |
| political_status | TINYINT | - | - | 政治面貌（原a7a） |
| religion | TINYINT | - | - | 宗教信仰（原a7b） |
| household_size | INT | - | - | 家庭人口数（原a11） |
| self_health | TINYINT | - | - | 自评健康状况（原c2） |
| survey_weight1 | DECIMAL | 10,6 | - | 权重1（原weight1） |
| survey_weight2 | DECIMAL | 10,6 | - | 权重2（原weight2） |
| created_at | DATETIME | - | - | 创建时间 |

---

#### 表2：family_member（家庭成员信息表）

存储受访者家庭成员的基本信息和与受访者的关系。

| 字段名 | 数据类型 | 长度 | 约束 | 描述 |
|--------|----------|------|------|------|
| id | BIGINT | - | PRIMARY KEY, AUTO_INCREMENT | 主键 |
| respondent_id | VARCHAR | 50 | FOREIGN KEY, INDEX | 受访者ID |
| member_seq | INT | - | - | 成员序号（1-15） |
| relation_code | INT | - | - | 与受访者关系编码（原a01102系列） |
| cohabit_status | TINYINT | - | - | 是否同住（原a01202系列） |
| cohabit_remark | VARCHAR | 200 | - | 同住情况备注（原a01202a系列） |
| current_residence | TINYINT | - | - | 目前是否住在一起（原a01302系列） |
| created_at | DATETIME | - | - | 创建时间 |

**说明**：每个受访者最多存储15位家庭成员信息（member_seq 1-15）。

---

#### 表3：education（教育经历表）

存储受访者的教育背景信息。

| 字段名 | 数据类型 | 长度 | 约束 | 描述 |
|--------|----------|------|------|------|
| id | BIGINT | - | PRIMARY KEY, AUTO_INCREMENT | 主键 |
| respondent_id | VARCHAR | 50 | FOREIGN KEY, INDEX | 受访者ID |
| education_level | TINYINT | - | - | 最高学历编码（原a4） |
| education_remark | VARCHAR | 200 | - | 学历备注（原a4a） |
| political_course | TINYINT | - | - | 思想政治课程（原a7c） |
| graduation_year | INT | - | - | 毕业年份（原a7c相关） |
| created_at | DATETIME | - | - | 创建时间 |

---

#### 表4：work_experience（工作经历表）

存储受访者的就业和工作经历信息。

| 字段名 | 数据类型 | 长度 | 约束 | 描述 |
|--------|----------|------|------|------|
| id | BIGINT | - | PRIMARY KEY, AUTO_INCREMENT | 主键 |
| respondent_id | VARCHAR | 50 | FOREIGN KEY, INDEX | 受访者ID |
| has_work | TINYINT | - | - | 是否有工作（原a6） |
| work_years | INT | - | - | 工作年限（原a7a） |
| work_remark | VARCHAR | 200 | - | 工作备注（原a7aa） |
| employment_type | TINYINT | - | - | 就业类型（原a7b） |
| is_employed | TINYINT | - | - | 目前是否在业（原a10） |
| work_status_remark | VARCHAR | 200 | - | 不在业原因备注（原a10a） |
| hukou_location | VARCHAR | 100 | - | 户口登记地（原a11） |
| hukou_type | TINYINT | - | - | 户口类型（原a25a） |
| job_change_times | INT | - | - | 工作变换次数（原a14） |
| industry_code | INT | - | - | 行业编码（原a19） |
| occupation_code | INT | - | - | 职业编码（原a20） |
| isco08_code | INT | - | - | ISCO08职业编码（原isco08a59d/isco08a60d） |
| employer_type | TINYINT | - | - | 单位类型（原a21） |
| created_at | DATETIME | - | - | 创建时间 |

---

#### 表5：income（收入信息表）

存储受访者及其家庭的各种收入数据。

| 字段名 | 数据类型 | 长度 | 约束 | 描述 |
|--------|----------|------|------|------|
| id | BIGINT | - | PRIMARY KEY, AUTO_INCREMENT | 主键 |
| respondent_id | VARCHAR | 50 | FOREIGN KEY, INDEX | 受访者ID |
| personal_income_lastyear | DECIMAL | 12,2 | - | 去年个人总收入（原a8a） |
| household_income_lastyear | DECIMAL | 12,2 | - | 去年家庭总收入（原a8b） |
| income_source | TINYINT | - | - | 收入来源（原a9） |
| first_income_year | INT | - | - | 首次获得收入年份（原a9a） |
| unemployment_reason | TINYINT | - | - | 失业原因（原a54） |
| unemployment_remark | VARCHAR | 200 | - | 失业原因备注（原a54a） |
| unemployment_weeks | INT | - | - | 失业周数（原a55） |
| created_at | DATETIME | - | - | 创建时间 |

---

#### 表6：property（财产信息表）

存储受访者及其家庭的财产状况，包括房产、车辆等。

| 字段名 | 数据类型 | 长度 | 约束 | 描述 |
|--------|----------|------|------|------|
| id | BIGINT | - | PRIMARY KEY, AUTO_INCREMENT | 主键 |
| respondent_id | VARCHAR | 50 | FOREIGN KEY, INDEX | 受访者ID |
| has_house_property | TINYINT | - | - | 是否拥有房产（原a12a） |
| has_savings | TINYINT | - | - | 是否有存款（原a12b） |
| house_property_num | INT | - | - | 拥有房产数量（原a12c1a等） |
| car_num | INT | - | - | 拥有汽车数量（原a67系列） |
| mobile_phone_num | INT | - | - | 手机数量（原a30a） |
| self_evaluated_wealth | TINYINT | - | - | 自评财产等级（原a64） |
| total_property_value | DECIMAL | 14,2 | - | 财产总估值（原a62） |
| created_at | DATETIME | - | - | 创建时间 |

---

#### 表7：health（健康信息表）

存储受访者的健康状况和医疗信息。

| 字段名 | 数据类型 | 长度 | 约束 | 描述 |
|--------|----------|------|------|------|
| id | BIGINT | - | PRIMARY KEY, AUTO_INCREMENT | 主键 |
| respondent_id | VARCHAR | 50 | FOREIGN KEY, INDEX | 受访者ID |
| self_health | TINYINT | - | - | 自评健康状况（原c2） |
| chronic_illness | TINYINT | - | - | 是否患有慢性病（原c3） |
| exercise_frequency | TINYINT | - | - | 锻炼频率（原c4） |
| smoke_status | TINYINT | - | - | 吸烟状况（原c5） |
| drink_status | TINYINT | - | - | 饮酒状况（原c6） |
| sleep_hours | DECIMAL | 4,1 | - | 平均睡眠时长（原c7） |
| health_change | TINYINT | - | - | 健康变化（原c8） |
| medical_expense_lastyear | DECIMAL | 10,2 | - | 去年医疗支出（原c16a/b/c） |
| insurance_type1 | TINYINT | - | - | 医疗保险类型1（原c11a） |
| insurance_type2 | TINYINT | - | - | 医疗保险类型2（原c11b） |
| insurance_type3 | TINYINT | - | - | 医疗保险类型3（原c11c） |
| created_at | DATETIME | - | - | 创建时间 |

---

#### 表8：housing（住房信息表）

存储受访者当前住房的基本情况。

| 字段名 | 数据类型 | 长度 | 约束 | 描述 |
|--------|----------|------|------|------|
| id | BIGINT | - | PRIMARY KEY, AUTO_INCREMENT | 主键 |
| respondent_id | VARCHAR | 50 | FOREIGN KEY, INDEX | 受访者ID |
| housing_type | TINYINT | - | - | 住房类型（原a18） |
| housing_remark | VARCHAR | 200 | - | 住房类型备注（原a18a） |
| housing_area | DECIMAL | 10,2 | - | 住房建筑面积（原a13） |
| room_num | INT | - | - | 房间数（原a14） |
| purchase_year | INT | - | - | 购房年份（原a25） |
| property_right | TINYINT | - | - | 产权情况（原a25a） |
| renovation_year | INT | - | - | 最近一次装修年份（原a19） |
| renovation_type | TINYINT | - | - | 装修情况（原a19a） |
| created_at | DATETIME | - | - | 创建时间 |

---

#### 表9：social_attitude（社会态度表）

存储受访者对社会事务的态度和看法。

| 字段名 | 数据类型 | 长度 | 约束 | 描述 |
|--------|----------|------|------|------|
| id | BIGINT | - | PRIMARY KEY, AUTO_INCREMENT | 主键 |
| respondent_id | VARCHAR | 50 | FOREIGN KEY, INDEX | 受访者ID |
| trust_family | TINYINT | - | - | 对家人信任度（原a32） |
| trust_neighbor | TINYINT | - | - | 对邻居信任度（原a33） |
| trust_stranger | TINYINT | - | - | 对陌生人信任度（原a34） |
| happiness | TINYINT | - | - | 幸福感（原a35） |
| life_satisfaction | TINYINT | - | - | 生活满意度（原a36） |
| social_mobility | TINYINT | - | - | 社会流动感知（原a38-a40） |
| gender_equality | TINYINT | - | - | 性别平等态度（原a421-a425） |
| class_perception | TINYINT | - | - | 主观社会阶层（原a43a-e） |
| election_participation | TINYINT | - | - | 是否参加选举投票（原a44） |
| party_member | TINYINT | - | - | 是否党员（原a45） |
| created_at | DATETIME | - | - | 创建时间 |

---

#### 表10：media_usage（媒体使用表）

存储受访者的媒体接触和使用习惯。

| 字段名 | 数据类型 | 长度 | 约束 | 描述 |
|--------|----------|------|------|------|
| id | BIGINT | - | PRIMARY KEY, AUTO_INCREMENT | 主键 |
| respondent_id | VARCHAR | 50 | FOREIGN KEY, INDEX | 受访者ID |
| newspaper_freq | TINYINT | - | - | 报纸阅读频率（原a281） |
| magazine_freq | TINYINT | - | - | 杂志阅读频率（原a282） |
| tv_freq | TINYINT | - | - | 电视观看频率（原a283） |
| radio_freq | TINYINT | - | - | 广播收听频率（原a284） |
| internet_freq | TINYINT | - | - | 网络使用频率（原a285） |
| internet_usage | TINYINT | - | - | 主要网络用途（原a29） |
| social_media_active | TINYINT | - | - | 社交媒体活跃度（原a3001-a3012） |
| has_smartphone | TINYINT | - | - | 是否拥有智能手机（原a30a） |
| smartphone_num | INT | - | - | 智能手机数量（原a30d） |
| chinese_level | TINYINT | - | - | 中文水平（原a49-50） |
| english_level | TINYINT | - | - | 英语水平（原a51-52） |
| volunteer_activity | TINYINT | - | - | 是否参与志愿活动（原a311-a313） |
| created_at | DATETIME | - | - | 创建时间 |

---

#### 表11：value_belief（价值观表）

存储受访者的价值观、信念和态度信息。

| 字段名 | 数据类型 | 长度 | 约束 | 描述 |
|--------|----------|------|------|------|
| id | BIGINT | - | PRIMARY KEY, AUTO_INCREMENT | 主键 |
| respondent_id | VARCHAR | 50 | FOREIGN KEY, INDEX | 受访者ID |
| attitude_toward_society | TINYINT | - | - | 对社会态度（原a38） |
| attitude_toward_others | TINYINT | - | - | 对他人态度（原a39） |
| attitude_toward_self | TINYINT | - | - | 对自己态度（原a40） |
| attitude_toward_women | TINYINT | - | - | 对女性态度（原a41） |
| view_on_education | TINYINT | - | - | 教育观念（原a46-a48） |
| view_on_work | TINYINT | - | - | 工作观念（原a72-a74a） |
| life_goal_1 | VARCHAR | 200 | - | 人生目标1（原a56系列） |
| life_goal_2 | VARCHAR | 200 | - | 人生目标2（原a57系列） |
| created_at | DATETIME | - | - | 创建时间 |

---

#### 表12：survey_record（调查记录表）

存储调查过程的管理信息。

| 字段名 | 数据类型 | 长度 | 约束 | 描述 |
|--------|----------|------|------|------|
| id | BIGINT | - | PRIMARY KEY, AUTO_INCREMENT | 主键 |
| respondent_id | VARCHAR | 50 | FOREIGN KEY, UNIQUE | 受访者ID |
| interview_start_time | DATETIME | - | - | 访问开始时间（原a00） |
| interview_end_time | DATETIME | - | - | 访问结束时间（原z00） |
| survey_type | TINYINT | - | - | 调查方式（原a1） |
| data_source | TINYINT | - | - | 数据来源（原dsource） |
| created_at | DATETIME | - | - | 创建时间 |

---

## 四、表关系ER图设计

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   respondent     │       │family_member    │       │   education      │
│ (受访者基本信息)  │1───N──│  (家庭成员)     │       │   (教育信息)     │
└────────┬────────┘       └─────────────────┘       └────────┬────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│work_experience  │       │    income       │       │   property      │
│   (工作经历)     │       │   (收入信息)    │       │   (财产信息)    │
└────────┬────────┘       └─────────────────┘       └────────┬────────┘
         │                                                 │
         │                                                 │
         ▼                                                 │
┌─────────────────┐       ┌─────────────────┐              │
│    housing      │       │    health       │              │
│   (住房信息)     │       │   (健康信息)    │              │
└────────┬────────┘       └────────┬────────┘              │
         │                         │                       │
         │                         │                       │
         ▼                         ▼                       │
┌─────────────────┐       ┌─────────────────┐              │
│ social_attitude │       │  media_usage    │              │
│  (社会态度)      │       │  (媒体使用)     │              │
└────────┬────────┘       └────────┬────────┘              │
         │                         │                       │
         │                         │                       │
         ▼                         ▼                       │
┌─────────────────┐       ┌─────────────────┐              │
│  value_belief  │       │ survey_record  │              │
│   (价值观)      │       │  (调查记录)     │              │
└─────────────────┘       └─────────────────┘              │
```

---

## 五、设计说明

### 5.1 命名规范

- 表名：使用英文单数形式，如`respondent`而非`respondents`
- 字段名：使用小写加下划线，如`respondent_id`
- 保留原始字段编码：在备注中标注原始CGSS字段编码，便于对照

### 5.2 索引设计

- 主表`respondent`的`respondent_id`建立主键索引
- 所有外键字段建立普通索引，加速关联查询
- 常用查询条件字段（如`province_code`、`is_urban`）建立索引

### 5.3 与现有系统兼容

- `respondent_id`可与现有的`household_id`建立映射关系
- 现有`electricity_record`表可通过`respondent_id`关联到新表
- 保持`weight1`、`weight2`字段用于统计分析

### 5.4 数据迁移说明

1. 首先创建新表结构
2. 从CGSS2023原始数据提取对应字段导入
3. 建立与现有`household`表的映射关系
4. 保留原始数据文件作为备份

---

## 六、预期效果

| 指标 | 原有设计 | 新设计 |
|------|----------|--------|
| 表数量 | 7表 | 12表 |
| 字段数量 | 约30字段 | 约120字段 |
| 数据冗余 | 高 | 低 |
| 查询效率 | 一般 | 优 |
| 可维护性 | 一般 | 优 |
| CGSS兼容性 | 无 | 完全兼容 |

---

**文档版本**：V1.0
**创建日期**：2026-05-08
**状态**：设计稿，待评审
