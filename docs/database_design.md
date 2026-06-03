# 电力用户画像系统 - 数据库架构设计

## 概述

采用 **MySQL + Neo4j** 混合存储架构，结合关系型数据库和图数据库的优势。

---

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      应用层 (Django + Vue)                    │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                                 ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│        MySQL            │     │        Neo4j             │
│  (结构化数据存储)        │     │   (图数据存储)           │
├─────────────────────────┤     ├─────────────────────────┤
│ • 用户基本信息           │     │ • 用户关系网络          │
│ • 用电记录(秒/分/时/日) │     │ • 相似用户关系          │
│ • 设备信息              │     │ • 设备联动关系          │
│ • 电价/气象/空气质量    │     │ • 用电模式图谱          │
│ • 统计汇总数据          │     │ • 聚类关系图            │
└─────────────────────────┘     └─────────────────────────┘
```

---

## MySQL 表结构

### 1. 用户表 (users)
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(20) UNIQUE NOT NULL,
    user_type ENUM('residential', 'enterprise') NOT NULL,
    house_num VARCHAR(50),
    -- 居民用户字段
    house_type VARCHAR(20),
    family_type VARCHAR(20),
    family_members INT,
    area DECIMAL(10,2),
    -- 企业用户字段
    enterprise_type VARCHAR(30),
    industry VARCHAR(30),
    power_type VARCHAR(30),
    employees INT,
    voltage_level VARCHAR(20),
    -- 公共字段
    province VARCHAR(20),
    city VARCHAR(20),
    district VARCHAR(20),
    energy_level VARCHAR(10),
    behavior_label VARCHAR(20),
    consumption_pattern VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. 日用电数据表 (daily_consumption)
```sql
CREATE TABLE daily_consumption (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    year_month VARCHAR(7),
    weekday TINYINT,
    total_kwh DECIMAL(10,2),
    is_holiday TINYINT DEFAULT 0,
    INDEX idx_user_date (user_id, date),
    INDEX idx_date (date)
);
```

### 3. 小时用电数据表 (hourly_consumption)
```sql
CREATE TABLE hourly_consumption (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    hour TINYINT NOT NULL,
    kwh DECIMAL(10,4),
    INDEX idx_user_date (user_id, date, hour)
);
```

### 4. 设备表 (devices)
```sql
CREATE TABLE devices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    device_id VARCHAR(30) UNIQUE,
    user_id VARCHAR(20),
    device_code VARCHAR(20),
    device_name VARCHAR(50),
    rated_power INT,
    daily_use_hours DECIMAL(4,1),
    INDEX idx_user (user_id)
);
```

### 5. 气象数据表 (weather)
```sql
CREATE TABLE weather (
    id INT PRIMARY KEY AUTO_INCREMENT,
    date DATE UNIQUE,
    temperature DECIMAL(5,1),
    temperature_min DECIMAL(5,1),
    temperature_max DECIMAL(5,1),
    humidity DECIMAL(5,1),
    wind_speed DECIMAL(5,1),
    weather VARCHAR(20)
);
```

### 6. 空气质量表 (air_quality)
```sql
CREATE TABLE air_quality (
    id INT PRIMARY KEY AUTO_INCREMENT,
    date DATE UNIQUE,
    aqi INT,
    pm25 INT,
    pm10 INT,
    so2 INT,
    no2 INT,
    co DECIMAL(4,1),
    o3 INT,
    level VARCHAR(20)
);
```

### 7. 电价表 (electricity_price)
```sql
CREATE TABLE electricity_price (
    id INT PRIMARY KEY AUTO_INCREMENT,
    price_type VARCHAR(30),
    month TINYINT,
    base_price DECIMAL(6,3),
    peak_price DECIMAL(6,3),
    valley_price DECIMAL(6,3)
);
```

---

## Neo4j 图模型

### 节点类型

1. **User** - 用户节点
   - 属性: user_id, user_type, energy_level, avg_daily_kwh

2. **Device** - 设备节点
   - 属性: device_id, device_name, rated_power

3. **TimeSlot** - 时段节点
   - 属性: slot_name, hours

4. **Season** - 季节节点
   - 属性: season_name

### 关系类型

1. **USES** - 用户使用设备
   - 属性: usage_ratio

2. **SIMILAR_TO** - 用户相似关系
   - 属性: similarity, based_on (用电模式/设备/能耗)

3. **SAME_CLUSTER** - 同聚类关系
   - 属性: cluster_id, algorithm

4. **CORRELATES_WITH** - 设备联动关系
   - 属性: correlation_coefficient

5. **AFFECTED_BY** - 用电受天气影响
   - 属性: correlation

---

## 数据同步策略

### 1. 写入策略
- **MySQL**: 实时写入用电数据
- **Neo4j**: 定期同步用户关系（每日/每周）

### 2. 查询优化
- **统计查询**: MySQL (聚合函数优化)
- **关系查询**: Neo4j (图遍历优化)
- **混合查询**: 根据场景选择

### 3. 数据量估算
- 用户数: 280+
- 日用电数据: 102,200条/天
- 小时用电数据: 72,000条/天
- 设备数: 2,000+

---

## 实现步骤

1. **安装MySQL和Neo4j**
2. **创建数据库和表**
3. **编写数据导入脚本**
4. **修改Django配置连接MySQL**
5. **更新Neo4j连接**
6. **测试数据读写性能**