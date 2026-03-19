"""
电力用户画像知识图谱 - 多用户数据生成器
基于真实数据模式，生成适合知识图谱的多用户数据
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# 设置随机种子，保证可复现
np.random.seed(42)
random.seed(42)

# 输出目录
OUTPUT_DIR = 'kg_data'
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# 1. 用户类型定义（基于真实用户画像研究）
# ============================================================

USER_TYPES = {
    '节约型家庭': {
        'weight': 0.20,
        'family_size': [3, 4, 5],
        'house_area': [80, 120],  # 平方米
        'consumption_pattern': '均匀型',
        'energy_level': '低',
        'behavior_label': '节能型',
        'sensitivity': '一般型',
        'devices': ['HPE', 'WHE', 'DNE', 'CDE'],  # 全部有
        'evening_peak_ratio': 0.4,  # 晚间用电占比
    },
    '普通家庭': {
        'weight': 0.30,
        'family_size': [3, 4],
        'house_area': [90, 130],
        'consumption_pattern': '晚峰型',
        'energy_level': '中',
        'behavior_label': '正常型',
        'sensitivity': '一般型',
        'devices': ['HPE', 'WHE', 'DNE'],
        'evening_peak_ratio': 0.6,
    },
    '高耗能家庭': {
        'weight': 0.15,
        'family_size': [4, 5, 6],
        'house_area': [130, 180],
        'consumption_pattern': '双峰型',
        'energy_level': '极高',
        'behavior_label': '浪费型',
        'sensitivity': '天气敏感型',
        'devices': ['HPE', 'WPE', 'WHE', 'DNE', 'CDE'],  # WPE=壁挂炉
        'evening_peak_ratio': 0.5,
    },
    '单身青年': {
        'weight': 0.20,
        'family_size': [1, 2],
        'house_area': [40, 70],
        'consumption_pattern': '间歇型',
        'energy_level': '低',
        'behavior_label': '正常型',
        'sensitivity': '不敏感型',
        'devices': ['HPE', 'WHE'],
        'evening_peak_ratio': 0.7,
    },
    '老年家庭': {
        'weight': 0.15,
        'family_size': [2, 3],
        'house_area': [70, 100],
        'consumption_pattern': '早峰型',
        'energy_level': '低',
        'behavior_label': '节能型',
        'sensitivity': '天气敏感型',
        'devices': ['HPE', 'WHE', 'DNE'],
        'evening_peak_ratio': 0.3,
    },
}

# 设备信息
DEVICE_INFO = {
    'HPE': {'name': '暖通空调', 'type': 'HVAC', 'base_power': 2500, 'max_power': 3500},
    'WHE': {'name': '热水器', 'type': 'WaterHeating', 'base_power': 1500, 'max_power': 2000},
    'DNE': {'name': '洗碗机', 'type': 'Electronics', 'base_power': 1200, 'max_power': 1800},
    'CDE': {'name': '干衣机', 'type': 'Electronics', 'base_power': 2500, "max_power": 3000},
    'WPE': {'name': '壁挂炉', 'type': 'Heating', 'base_power': 8000, 'max_power': 12000},
}

# 地区
DISTRICTS = ['朝阳区', '海淀区', '西城区', '东城区', '丰台区', '石景山区', '通州区', '昌平区']


# ============================================================
# 2. 辅助函数
# ============================================================

def weighted_choice(choices_dict):
    """根据权重随机选择"""
    items = list(choices_dict.items())
    weights = [item[1]['weight'] for item in items]
    selected = random.choices(items, weights=weights, k=1)[0]
    return selected


def generate_user_id(index):
    """生成用户ID"""
    return f"HU{str(index).zfill(4)}"


def generate_date_range():
    """生成日期范围（与原始数据时间对应）"""
    start = datetime(2013, 1, 1)
    end = datetime(2014, 12, 31)
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)
    return dates


# ============================================================
# 3. 数据生成主函数
# ============================================================

def generate_users(num_users=50):
    """生成用户基础信息"""
    print(f"生成 {num_users} 个用户...")
    users = []

    for i in range(1, num_users + 1):
        # 选择用户类型
        user_type_name, user_type = weighted_choice(USER_TYPES)

        # 随机选择家庭人口
        family_size = random.choice(user_type['family_size'])

        # 随机选择房屋面积
        house_area = random.randint(user_type['house_area'][0], user_type['house_area'][1])

        # 生成用户
        user = {
            'user_id': generate_user_id(i),
            'user_type': user_type_name,
            'family_size': family_size,
            'house_area': house_area,
            'house_type': random.choice(['商品房', '经济适用房', '老旧小区']),
            'district': random.choice(DISTRICTS),
            'construction_year': random.randint(2000, 2020),
            'consumption_pattern': user_type['consumption_pattern'],
            'energy_level': user_type['energy_level'],
            'behavior_label': user_type['behavior_label'],
            'sensitivity': user_type['sensitivity'],
            'evening_peak_ratio': user_type['evening_peak_ratio'],
            'has_solar': random.random() < 0.1,  # 10%用户有太阳能
            'has_electric_car': random.random() < 0.05,  # 5%用户有电动汽车
        }

        # 为用户分配设备
        user_devices = []
        for device_code in user_type['devices']:
            device = DEVICE_INFO[device_code].copy()
            device['device_id'] = f"{user['user_id']}_{device_code}"
            device['device_code'] = device_code
            device['purchase_year'] = random.randint(2015, 2023)
            device['energy_rating'] = random.choice(['一级', '二级', '三级'])
            user_devices.append(device)

        user['devices'] = user_devices
        users.append(user)

    return users


def generate_hourly_consumption(user, date, weather_data):
    """为用户生成某天的逐小时用电数据"""
    hour_consumption = []

    # 基础负荷（每户基本用电）
    base_load = 0.5  # kWh

    # 获取用户属性
    evening_ratio = user['evening_peak_ratio']
    is_sensitive = user['sensitivity'] == '天气敏感型'

    # 天气影响因子
    if is_sensitive and date in weather_data:
        temp = weather_data[date]['temperature']
        if temp < 5 or temp > 30:
            weather_factor = 1.5
        elif temp < 10 or temp > 28:
            weather_factor = 1.3
        else:
            weather_factor = 1.0
    else:
        weather_factor = 1.0

    # 周末因子（周末用电更多）
    is_weekend = date.weekday() >= 5
    weekend_factor = 1.2 if is_weekend else 1.0

    # 季节因子
    month = date.month
    if month in [12, 1, 2]:  # 冬季
        season_factor = 1.4
    elif month in [6, 7, 8]:  # 夏季
        season_factor = 1.3
    else:  # 春秋季
        season_factor = 1.0

    for hour in range(24):
        # 基础时段分布
        if 6 <= hour < 9:  # 早高峰
            time_factor = 1.2
        elif 9 <= hour < 17:  # 工作时间
            time_factor = 0.6
        elif 17 <= hour < 22:  # 晚高峰
            time_factor = 1.0 + evening_ratio
        else:  # 夜间
            time_factor = 0.4

        # 计算总用电量
        total_kwh = base_load * time_factor * weather_factor * weekend_factor * season_factor

        # 按设备分配用电量
        hourly_devices = []
        for device in user['devices']:
            if hour >= 22 or hour < 6:  # 夜间
                device_active = device['device_code'] == 'WHE'  # 只有热水器可能夜间开
            elif device['device_code'] == 'HPE':
                device_active = weather_factor > 1.2  # 空调根据天气
            elif device['device_code'] == 'WHE':
                device_active = hour >= 20 or hour < 7  # 热水器晚上开
            elif device['device_code'] in ['DNE', 'CDE']:
                device_active = hour >= 19 and hour < 22  # 饭后使用
            else:
                device_active = random.random() < 0.3

            if device_active:
                # 设备实际功率使用（不是满功率）
                power_factor = random.uniform(0.5, 1.0)
                device_kwh = total_kwh * power_factor * random.uniform(0.1, 0.4)
            else:
                device_kwh = 0

            hourly_devices.append({
                'device_id': device['device_id'],
                'device_code': device['device_code'],
                'device_name': device['name'],
                'hour': hour,
                'power_kw': device_kwh,
                'energy_kwh': device_kwh,
            })

        hour_consumption.append({
            'date': date.strftime('%Y-%m-%d'),
            'hour': hour,
            'total_kwh': sum(d['energy_kwh'] for d in hourly_devices),
            'devices': hourly_devices,
            'temperature': weather_data.get(date, {}).get('temperature', 20),
            'weather': weather_data.get(date, {}).get('weather', 'Unknown'),
        })

    return hour_consumption


def generate_monthly_summary(user, dates):
    """生成月度用能总结"""
    monthly_data = {}

    for date in dates:
        year_month = date.strftime('%Y-%m')

        if year_month not in monthly_data:
            monthly_data[year_month] = {
                'year_month': year_month,
                'total_kwh': 0,
                'peak_daily_kwh': 0,
                'cost': 0,
                'days': 0,
            }

        # 简化计算
        daily_avg = random.uniform(8, 25) * user.get('energy_level_factor', 1.0)
        monthly_data[year_month]['total_kwh'] += daily_avg
        monthly_data[year_month]['peak_daily_kwh'] = max(
            monthly_data[year_month]['peak_daily_kwh'],
            daily_avg * random.uniform(1.2, 1.5)
        )
        monthly_data[year_month]['days'] += 1
        monthly_data[year_month]['cost'] += daily_avg * 0.6  # 电价

    return list(monthly_data.values())


def load_weather_from_existing():
    """从现有数据加载天气模式"""
    try:
        df = pd.read_csv('processed_data/daily_weather.csv')
        weather = {}
        for _, row in df.iterrows():
            date = pd.to_datetime(row['date']).date()
            weather[date] = {
                'temperature': row['temperature'],
                'humidity': row['humidity'],
                'wind_speed': row['wind_speed'],
                'weather': row.get('weather_condition', 'Unknown'),
            }
        return weather
    except:
        # 生成典型天气数据
        print("使用默认天气数据...")
        weather = {}
        base_date = datetime(2013, 1, 1)
        for i in range(730):  # 2年
            date = (base_date + timedelta(days=i)).date()
            month = date.month
            # 季节性温度
            if month in [12, 1, 2]:
                temp = random.uniform(-5, 10)
            elif month in [3, 4, 5]:
                temp = random.uniform(10, 25)
            elif month in [6, 7, 8]:
                temp = random.uniform(20, 35)
            else:
                temp = random.uniform(10, 25)

            weather_conditions = ['晴天', '多云', '阴天', '小雨', '大雨']
            weather[date] = {
                'temperature': temp,
                'humidity': random.uniform(30, 90),
                'wind_speed': random.uniform(0, 20),
                'weather': random.choice(weather_conditions),
            }
        return weather


def generate_all_data(num_users=50):
    """生成所有数据"""
    print("=" * 60)
    print("电力用户画像知识图谱 - 数据生成器")
    print("=" * 60)

    # 1. 生成用户信息
    users = generate_users(num_users)

    # 2. 加载天气数据
    weather_data = load_weather_from_existing()

    # 3. 生成用电数据
    dates = generate_date_range()

    print(f"\n生成用电数据 ({len(dates)} 天 x {num_users} 用户)...")

    all_hourly_data = []
    all_daily_data = []
    all_monthly_data = []

    for idx, user in enumerate(users):
        if (idx + 1) % 10 == 0:
            print(f"  处理用户 {idx + 1}/{num_users}...")

        # 用户级别的用能因子
        energy_level_factors = {'极低': 0.5, '低': 0.7, '中': 1.0, '高': 1.3, '极高': 1.6}
        user['energy_level_factor'] = energy_level_factors.get(user['energy_level'], 1.0)

        # 每日数据
        daily_totals = {}

        for date in dates:
            hourly_data = generate_hourly_consumption(user, date, weather_data)

            # 汇总每小时数据
            for hour_record in hourly_data:
                for device_record in hour_record['devices']:
                    all_hourly_data.append({
                        'user_id': user['user_id'],
                        'user_type': user['user_type'],
                        'date': hour_record['date'],
                        'hour': hour_record['hour'],
                        'device_id': device_record['device_id'],
                        'device_code': device_record['device_code'],
                        'device_name': device_record['device_name'],
                        'power_kw': device_record['power_kw'],
                        'energy_kwh': device_record['energy_kwh'],
                        'temperature': hour_record['temperature'],
                        'weather': hour_record['weather'],
                    })

            # 每日汇总
            daily_total = sum(h['total_kwh'] for h in hourly_data)
            date_str = date.strftime('%Y-%m-%d')
            if date_str not in daily_totals:
                daily_totals[date_str] = {
                    'user_id': user['user_id'],
                    'user_type': user['user_type'],
                    'date': date_str,
                    'total_energy_kwh': 0,
                    'peak_power_kw': 0,
                    'temperature': hourly_data[12]['temperature'],  # 中午温度
                    'is_weekend': date.weekday() >= 5,
                }
            daily_totals[date_str]['total_energy_kwh'] += daily_total
            daily_totals[date_str]['peak_power_kw'] = max(
                daily_totals[date_str]['peak_power_kw'],
                daily_total * 2  # 峰值功率估算
            )

        all_daily_data.extend(list(daily_totals.values()))

        # 月度汇总
        monthly = generate_monthly_summary(user, dates)
        for m in monthly:
            m['user_id'] = user['user_id']
            m['user_type'] = user['user_type']
            m['behavior_label'] = user['behavior_label']
            all_monthly_data.append(m)

    # 4. 保存数据
    print("\n保存数据...")

    # 用户信息
    user_df = pd.DataFrame([{
        'user_id': u['user_id'],
        'user_type': u['user_type'],
        'family_size': u['family_size'],
        'house_area': u['house_area'],
        'house_type': u['house_type'],
        'district': u['district'],
        'construction_year': u['construction_year'],
        'consumption_pattern': u['consumption_pattern'],
        'energy_level': u['energy_level'],
        'behavior_label': u['behavior_label'],
        'sensitivity': u['sensitivity'],
        'has_solar': u['has_solar'],
        'has_electric_car': u['has_electric_car'],
    } for u in users])
    user_df.to_csv(f'{OUTPUT_DIR}/kg_users.csv', index=False, encoding='utf-8-sig')
    print(f"  - 用户信息: {len(user_df)} 条")

    # 用户设备
    device_rows = []
    for u in users:
        for d in u['devices']:
            device_rows.append({
                'user_id': u['user_id'],
                'device_id': d['device_id'],
                'device_code': d['device_code'],
                'device_name': d['name'],
                'device_type': d['type'],
                'purchase_year': d['purchase_year'],
                'energy_rating': d['energy_rating'],
            })
    device_df = pd.DataFrame(device_rows)
    device_df.to_csv(f'{OUTPUT_DIR}/kg_devices.csv', index=False, encoding='utf-8-sig')
    print(f"  - 用户设备: {len(device_df)} 条")

    # 小时用电数据
    hourly_df = pd.DataFrame(all_hourly_data)
    hourly_df.to_csv(f'{OUTPUT_DIR}/kg_hourly_consumption.csv', index=False, encoding='utf-8-sig')
    print(f"  - 小时用电: {len(hourly_df)} 条")

    # 每日用电数据
    daily_df = pd.DataFrame(all_daily_data)
    daily_df.to_csv(f'{OUTPUT_DIR}/kg_daily_consumption.csv', index=False, encoding='utf-8-sig')
    print(f"  - 每日用电: {len(daily_df)} 条")

    # 月度用能总结
    monthly_df = pd.DataFrame(all_monthly_data)
    monthly_df.to_csv(f'{OUTPUT_DIR}/kg_monthly_summary.csv', index=False, encoding='utf-8-sig')
    print(f"  - 月度总结: {len(monthly_df)} 条")

    # 天气数据
    weather_rows = []
    for date, w in weather_data.items():
        weather_rows.append({
            'date': date.strftime('%Y-%m-%d') if isinstance(date, datetime) else str(date),
            'temperature': w['temperature'],
            'humidity': w['humidity'],
            'wind_speed': w['wind_speed'],
            'weather_condition': w['weather'],
        })
    weather_df = pd.DataFrame(weather_rows)
    weather_df.to_csv(f'{OUTPUT_DIR}/kg_weather.csv', index=False, encoding='utf-8-sig')
    print(f"  - 天气数据: {len(weather_df)} 条")

    # 5. 生成Neo4j导入格式
    print("\n生成Neo4j导入格式...")

    # 节点
    nodes = []

    # 用户节点
    for u in users:
        nodes.append({
            'type': 'User',
            'id': u['user_id'],
            'props': f"user_type:'{u['user_type']}',family_size:{u['family_size']},house_area:{u['house_area']},consumption_pattern:'{u['consumption_pattern']}',behavior_label:'{u['behavior_label']}',energy_level:'{u['energy_level']}'"
        })

    # 设备节点（去重）
    device_ids = set()
    for d in device_rows:
        if d['device_id'] not in device_ids:
            device_ids.add(d['device_id'])
            nodes.append({
                'type': 'Device',
                'id': d['device_id'],
                'props': f"device_name:'{d['device_name']}',device_type:'{d['device_type']}',energy_rating:'{d['energy_rating']}'"
            })

    # 用户类型节点
    user_types = set(u['user_type'] for u in users)
    for ut in user_types:
        nodes.append({
            'type': 'UserType',
            'id': ut,
            'props': f"name:'{ut}'"
        })

    # 行为标签节点
    behavior_labels = set(u['behavior_label'] for u in users)
    for bl in behavior_labels:
        nodes.append({
            'type': 'BehaviorLabel',
            'id': bl,
            'props': f"name:'{bl}'"
        })

    # 时间节点（月份）
    months = set(d['date'][:7] for d in all_daily_data)
    for m in months:
        season = '冬季' if m[5:7] in ['12', '01', '02'] else ('夏季' if m[5:7] in ['06', '07', '08'] else '过渡季')
        nodes.append({
            'type': 'Month',
            'id': m,
            'props': f"year_month:'{m}',season:'{season}'"
        })

    # 用电模式节点
    patterns = set(u['consumption_pattern'] for u in users)
    for p in patterns:
        nodes.append({
            'type': 'ConsumptionPattern',
            'id': p,
            'props': f"name:'{p}'"
        })

    # 保存节点
    nodes_df = pd.DataFrame(nodes)
    nodes_df.to_csv(f'{OUTPUT_DIR}/neo4j_nodes.csv', index=False, encoding='utf-8-sig')
    print(f"  - Neo4j节点: {len(nodes_df)} 条")

    # 关系
    relations = []

    # 用户-设备 关系
    for d in device_rows:
        relations.append({
            'source': d['user_id'],
            'target': d['device_id'],
            'type': 'OWNS',
            'props': ''
        })

    # 用户-类型 关系
    for u in users:
        relations.append({
            'source': u['user_id'],
            'target': u['user_type'],
            'type': 'IS_TYPE',
            'props': ''
        })

    # 用户-行为标签 关系
    for u in users:
        relations.append({
            'source': u['user_id'],
            'target': u['behavior_label'],
            'type': 'HAS_LABEL',
            'props': ''
        })

    # 用户-用电模式 关系
    for u in users:
        relations.append({
            'source': u['user_id'],
            'target': u['consumption_pattern'],
            'type': 'FOLLOWS',
            'props': ''
        })

    # 用户-月份 关系（用能）
    monthly_user_month = set()
    for m in all_monthly_data:
        key = (m['user_id'], m['year_month'])
        if key not in monthly_user_month:
            monthly_user_month.add(key)
            relations.append({
                'source': m['user_id'],
                'target': m['year_month'],
                'type': 'CONSUMES_IN',
                'props': f"total_kwh:{m['total_kwh']:.1f},cost:{m['cost']:.1f}"
            })

    # 保存关系
    rels_df = pd.DataFrame(relations)
    rels_df.to_csv(f'{OUTPUT_DIR}/neo4j_relations.csv', index=False, encoding='utf-8-sig')
    print(f"  - Neo4j关系: {len(rels_df)} 条")

    print("\n" + "=" * 60)
    print("数据生成完成!")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 60)

    return users


if __name__ == '__main__':
    users = generate_all_data(num_users=50)
