"""
REFIT数据集预处理脚本
将REFIT Smart Home数据转换为适合知识图谱的格式
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

# 设置路径
INPUT_DIR = 'REFITPowerData'
OUTPUT_DIR = 'kg_refit_data'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 设备列名映射
APPLIANCE_NAMES = {
    'Aggregate': '总用电',
    'Fridge': '冰箱',
    'Freezer': '冰柜',
    'Freezer(1)': '冰柜1',
    'Freezer(2)': '冰柜2',
    'Fridge-Freezer': '冰箱冰柜',
    'Fridge(garage)': '车库冰箱',
    'Freezer(garage)': '车库冰柜',
    'Washer Dryer': '洗干一体机',
    'Washing Machine': '洗衣机',
    'Washing Machine(1)': '洗衣机1',
    'Washing Machine(2)': '洗衣机2',
    'Tumble Dryer': '干衣机',
    'Dishwasher': '洗碗机',
    'Computer': '电脑',
    'Computer Site': '电脑站点',
    'Desktop Computer': '台式电脑',
    'MJY Computer': '电脑',
    'PGM Computer': '电脑',
    'Television Site': '电视站点',
    'Television': '电视',
    'TV/Satellite': '电视卫星',
    'TV Site(Bedroom)': '卧室电视',
    'Microwave': '微波炉',
    'Kettle': '电水壶',
    'Toaster': '烤面包机',
    'Electric Heater': '电暖器',
    'Electric Heater(1)': '电暖器1',
    'Electric Heater(2)': '电暖器2',
    'Hi-Fi': '音响',
    'Overhead Fan': '吊扇',
    'K Mix': '搅拌机',
    'Magimix(Blender)': '搅拌机',
    'Chest Freezer': '冰柜',
    'Router': '路由器',
    'Network Site': '网络设备',
    'Bread-maker': '面包机',
    'Games Console': '游戏机',
    'Food Mixer': '食品搅拌机',
    'Vivarium': '水族箱',
    'Pond Pump': '池塘泵',
    'Dehumidifier': '除湿器',
}


def load_house_data(house_num):
    """加载单个房屋的数据"""
    filename = f'{INPUT_DIR}/House{house_num}.csv'

    # 读取数据，跳过第一行（描述）
    df = pd.read_csv(filename, skiprows=1, header=None)

    # 设置列名 - 第一列是时间戳，第二列是Aggregate，后面是App1-App9
    # 共11列：timestamp + Aggregate + 9 appliances
    cols = ['unix_time', 'Aggregate'] + [f'App{i}' for i in range(1, 10)]
    df.columns = cols

    # 转换时间戳
    df['datetime'] = pd.to_datetime(df['unix_time'], unit='s')
    df['date'] = df['datetime'].dt.date
    df['hour'] = df['datetime'].dt.hour
    df['year_month'] = df['datetime'].dt.to_period('M').astype(str)

    return df


def get_house_appliances(house_num):
    """获取每个房屋的设备列表"""
    # 根据README定义设备
    appliances_map = {
        1: ['Aggregate', 'Fridge', 'Freezer(1)', 'Freezer(2)', 'Washer Dryer',
            'Washing Machine', 'Dishwasher', 'Computer', 'Television Site', 'Electric Heater'],
        2: ['Aggregate', 'Fridge-Freezer', 'Washing Machine', 'Dishwasher', 'Television Site',
            'Microwave', 'Toaster', 'Hi-Fi', 'Kettle', 'Overhead Fan'],
        3: ['Aggregate', 'Toaster', 'Fridge-Freezer', 'Freezer', 'Tumble Dryer',
            'Dishwasher', 'Washing Machine', 'Television Site', 'Microwave', 'Kettle'],
        4: ['Aggregate', 'Fridge', 'Freezer', 'Fridge-Freezer', 'Washing Machine(1)',
            'Washing Machine(2)', 'Desktop Computer', 'Television Site', 'Microwave', 'Kettle'],
        5: ['Aggregate', 'Fridge-Freezer', 'Tumble Dryer', 'Washing Machine', 'Dishwasher',
            'Desktop Computer', 'Television Site', 'Microwave', 'Kettle', 'Toaster'],
        6: ['Aggregate', 'Freezer', 'Washing Machine', 'Dishwasher', 'MJY Computer',
            'TV/Satellite', 'Microwave', 'Kettle', 'Toaster', 'PGM Computer'],
        7: ['Aggregate', 'Fridge', 'Freezer(1)', 'Freezer(2)', 'Tumble Dryer',
            'Washing Machine', 'Dishwasher', 'Television Site', 'Toaster', 'Kettle'],
        8: ['Aggregate', 'Fridge', 'Freezer', 'Washer Dryer', 'Washing Machine',
            'Toaster', 'Computer', 'Television Site', 'Microwave', 'Kettle'],
        9: ['Aggregate', 'Fridge-Freezer', 'Washer Dryer', 'Washing Machine', 'Dishwasher',
            'Television Site', 'Microwave', 'Kettle', 'Hi-Fi', 'Electric Heater'],
        10: ['Aggregate', 'Magimix(Blender)', 'Toaster', 'Chest Freezer', 'Fridge-Freezer',
             'Washing Machine', 'Dishwasher', 'Television Site', 'Microwave', 'K Mix'],
        11: ['Aggregate', 'Fridge', 'Fridge-Freezer', 'Washing Machine', 'Dishwasher',
             'Computer Site', 'Microwave', 'Kettle', 'Router', 'Hi-Fi'],
        12: ['Aggregate', 'Fridge-Freezer', 'Unknown', 'Unknown', 'Computer Site',
             'Microwave', 'Kettle', 'Toaster', 'Television', 'Unknown'],
        13: ['Aggregate', 'Television Site', 'Freezer', 'Washing Machine', 'Dishwasher',
             'Unknown', 'Network Site', 'Microwave', 'Microwave', 'Kettle'],
        15: ['Aggregate', 'Fridge-Freezer', 'Tumble Dryer', 'Washing Machine', 'Dishwasher',
             'Computer Site', 'Television Site', 'Microwave', 'Hi-Fi', 'Toaster'],
        16: ['Aggregate', 'Fridge-Freezer(1)', 'Fridge-Freezer(2)', 'Electric Heater(1)',
             'Electric Heater(2)', 'Washing Machine', 'Dishwasher', 'Computer Site',
             'Television Site', 'Dehumidifier'],
        17: ['Aggregate', 'Freezer', 'Fridge-Freezer', 'Tumble Dryer', 'Washing Machine',
             'Computer Site', 'Television Site', 'Microwave', 'Kettle', 'TV Site(Bedroom)'],
        18: ['Aggregate', 'Fridge(garage)', 'Freezer(garage)', 'Fridge-Freezer', 'Washer Dryer(garage)',
             'Washing Machine', 'Dishwasher', 'Desktop Computer', 'Television Site', 'Microwave'],
        19: ['Aggregate', 'Fridge Freezer', 'Washing Machine', 'Television Site', 'Microwave',
             'Kettle', 'Toaster', 'Bread-maker', 'Games Console', 'Hi-Fi'],
        20: ['Aggregate', 'Fridge', 'Freezer', 'Tumble Dryer', 'Washing Machine', 'Dishwasher',
             'Computer Site', 'Television Site', 'Microwave', 'Kettle'],
        21: ['Aggregate', 'Fridge-Freezer', 'Tumble Dryer', 'Washing Machine', 'Dishwasher',
             'Food Mixer', 'Television', 'Unknown', 'Vivarium', 'Pond Pump'],
    }
    return appliances_map.get(house_num, [])


def process_all_houses():
    """处理所有房屋数据"""
    print("=" * 60)
    print("REFIT数据集预处理")
    print("=" * 60)

    # 房屋列表（跳过14）
    house_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21]

    all_hourly_data = []
    all_daily_data = []
    all_monthly_data = []
    users_info = []
    devices_info = []

    for house_num in house_numbers:
        print(f"\n处理 House {house_num}...")

        # 加载数据
        df = load_house_data(house_num)
        appliances = get_house_appliances(house_num)

        print(f"  数据量: {len(df):,} 条")
        print(f"  时间范围: {df['datetime'].min()} ~ {df['datetime'].max()}")

        # 重要：REFIT数据是累积能耗值（瓦秒），需要计算差值
        # 列名是: unix_time, Aggregate, App1, App2, ..., App9
        app_cols_orig = ['Aggregate'] + [f'App{i}' for i in range(1, 10)]

        # 计算差值（每次观测的能耗增量）
        for col in app_cols_orig:
            df[f'{col}_diff'] = df[col].diff()

        # 时间差（秒）
        df['time_diff'] = df['unix_time'].diff()

        # 将瓦秒转换为kWh (除以3600)
        for col in app_cols_orig:
            df[f'{col}_kwh'] = df[f'{col}_diff'] / 3600

        # 处理负值（可能由于数据重置）
        for col in app_cols_orig:
            df.loc[df[f'{col}_kwh'] < 0, f'{col}_kwh'] = 0

        # 用户信息
        user_id = f"REFIT_H{house_num}"
        users_info.append({
            'user_id': user_id,
            'house_num': house_num,
            'data_start': str(df['datetime'].min().date()),
            'data_end': str(df['datetime'].max().date()),
            'record_count': len(df),
        })

        # 设备信息
        for i, app_name in enumerate(appliances):  # 包含Aggregate
            device_id = f"{user_id}_App{i}"
            devices_info.append({
                'user_id': user_id,
                'device_id': device_id,
                'device_code': f'App{i}',
                'device_name': app_name,
                'device_name_cn': APPLIANCE_NAMES.get(app_name, app_name),
            })

        # 按小时聚合 - 计算每小时的能耗总和（包含Aggregate）
        hourly_agg = df.groupby(['year_month', 'date', 'hour']).agg({
            'Aggregate_kwh': 'sum', **{f'App{i}_kwh': 'sum' for i in range(1, 10)}
        }).reset_index()

        for _, row in hourly_agg.iterrows():
            hour_data = {
                'user_id': user_id,
                'date': str(row['date']),
                'hour': row['hour'],
                'year_month': str(row['year_month']),
            }

            hour_data['Aggregate'] = row['Aggregate_kwh']
            for i in range(1, 10):
                app_name = appliances[i] if i < len(appliances) else f'App{i}'
                col = f'App{i}_kwh'
                if col in row:
                    hour_data[app_name.replace(' ', '_')] = row[col]

            all_hourly_data.append(hour_data)

        # 按天聚合
        daily_agg = df.groupby(['year_month', 'date']).agg({
            'Aggregate_kwh': 'sum', **{f'App{i}_kwh': 'sum' for i in range(1, 10)}
        }).reset_index()

        for _, row in daily_agg.iterrows():
            daily_data = {
                'user_id': user_id,
                'date': str(row['date']),
                'year_month': str(row['year_month']),
            }

            daily_data['Aggregate'] = row['Aggregate_kwh']
            for i in range(1, 10):
                app_name = appliances[i] if i < len(appliances) else f'App{i}'
                col = f'App{i}_kwh'
                if col in row:
                    daily_data[app_name.replace(' ', '_')] = row[col]

            daily_data['total_kwh'] = row['Aggregate_kwh']
            all_daily_data.append(daily_data)

        # 按月聚合
        monthly_agg = df.groupby('year_month').agg({
            'Aggregate_kwh': 'sum', **{f'App{i}_kwh': 'sum' for i in range(1, 10)}
        }).reset_index()

        for _, row in monthly_agg.iterrows():
            monthly_data = {
                'user_id': user_id,
                'year_month': str(row['year_month']),
            }

            monthly_data['Aggregate'] = row['Aggregate_kwh']
            for i in range(1, 10):
                app_name = appliances[i] if i < len(appliances) else f'App{i}'
                col = f'App{i}_kwh'
                if col in row:
                    monthly_data[app_name.replace(' ', '_')] = row[col]

            monthly_data['total_kwh'] = row['Aggregate_kwh']
            all_monthly_data.append(monthly_data)

    # 保存用户信息
    users_df = pd.DataFrame(users_info)
    users_df.to_csv(f'{OUTPUT_DIR}/users.csv', index=False, encoding='utf-8-sig')
    print(f"\n保存用户信息: {len(users_df)} 条")

    # 保存设备信息
    devices_df = pd.DataFrame(devices_info)
    devices_df.to_csv(f'{OUTPUT_DIR}/devices.csv', index=False, encoding='utf-8-sig')
    print(f"保存设备信息: {len(devices_df)} 条")

    # 保存小时数据
    hourly_df = pd.DataFrame(all_hourly_data)
    hourly_df.to_csv(f'{OUTPUT_DIR}/hourly_consumption.csv', index=False, encoding='utf-8-sig')
    print(f"保存小时数据: {len(hourly_df)} 条")

    # 保存日数据
    daily_df = pd.DataFrame(all_daily_data)
    daily_df.to_csv(f'{OUTPUT_DIR}/daily_consumption.csv', index=False, encoding='utf-8-sig')
    print(f"保存日数据: {len(daily_df)} 条")

    # 保存月数据
    monthly_df = pd.DataFrame(all_monthly_data)
    monthly_df.to_csv(f'{OUTPUT_DIR}/monthly_consumption.csv', index=False, encoding='utf-8-sig')
    print(f"保存月数据: {len(monthly_df)} 条")

    return users_df, devices_df, hourly_df, daily_df, monthly_df


def generate_user_profiles(users_df, daily_df):
    """生成用户画像特征"""
    print("\n生成用户画像...")

    profiles = []

    for user_id in users_df['user_id']:
        user_daily = daily_df[daily_df['user_id'] == user_id]

        if len(user_daily) == 0:
            continue

        # 计算基本统计
        total_kwh = user_daily['total_kwh'].sum()
        avg_daily_kwh = user_daily['total_kwh'].mean()
        max_daily_kwh = user_daily['total_kwh'].max()
        min_daily_kwh = user_daily['total_kwh'].min()
        std_daily_kwh = user_daily['total_kwh'].std()

        # 计算时段分布（早上6-9，晚间18-24）
        user_daily_copy = user_daily.copy()
        # 这里简化处理，用hourly数据会更准确

        # 根据用电量分类 (英国用电较高，因为使用电暖气)
        # 低: < 30 kWh/天, 中: 30-60, 高: 60-100, 极高: > 100
        if avg_daily_kwh < 30:
            energy_level = '低'
            behavior_label = '节能型'
        elif avg_daily_kwh < 60:
            energy_level = '中'
            behavior_label = '正常型'
        elif avg_daily_kwh < 100:
            energy_level = '高'
            behavior_label = '正常型'
        else:
            energy_level = '极高'
            behavior_label = '高耗能型'

        # 用电稳定性
        if std_daily_kwh / avg_daily_kwh < 0.3:
            consumption_pattern = '稳定型'
        elif std_daily_kwh / avg_daily_kwh < 0.5:
            consumption_pattern = '波动型'
        else:
            consumption_pattern = '不稳定型'

        profiles.append({
            'user_id': user_id,
            'house_num': user_id.split('_')[1],
            'total_kwh': round(total_kwh, 2),
            'avg_daily_kwh': round(avg_daily_kwh, 2),
            'max_daily_kwh': round(max_daily_kwh, 2),
            'min_daily_kwh': round(min_daily_kwh, 2),
            'std_daily_kwh': round(std_daily_kwh, 2),
            'energy_level': energy_level,
            'behavior_label': behavior_label,
            'consumption_pattern': consumption_pattern,
            'data_days': len(user_daily),
        })

    profiles_df = pd.DataFrame(profiles)
    profiles_df.to_csv(f'{OUTPUT_DIR}/user_profiles.csv', index=False, encoding='utf-8-sig')
    print(f"保存用户画像: {len(profiles_df)} 条")

    return profiles_df


def generate_kg_nodes_edges(users_df, devices_df, profiles_df):
    """生成Neo4j节点和关系"""
    print("\n生成Neo4j导入数据...")

    # 节点
    nodes = []

    # 用户节点
    for _, user in profiles_df.iterrows():
        nodes.append({
            'type': 'User',
            'id': user['user_id'],
            'props': f"house_num:{user['house_num']},energy_level:'{user['energy_level']}',behavior_label:'{user['behavior_label']}',consumption_pattern:'{user['consumption_pattern']}',avg_daily_kwh:{user['avg_daily_kwh']}"
        })

    # 设备节点（去重）
    seen_devices = set()
    for _, dev in devices_df.iterrows():
        if dev['device_id'] not in seen_devices:
            seen_devices.add(dev['device_id'])
            nodes.append({
                'type': 'Device',
                'id': dev['device_id'],
                'props': f"device_name:'{dev['device_name_cn']}',device_code:'{dev['device_code']}'"
            })

    # 能耗等级节点
    energy_levels = profiles_df['energy_level'].unique()
    for el in energy_levels:
        nodes.append({
            'type': 'EnergyLevel',
            'id': el,
            'props': f"name:'{el}'"
        })

    # 行为标签节点
    behavior_labels = profiles_df['behavior_label'].unique()
    for bl in behavior_labels:
        nodes.append({
            'type': 'BehaviorLabel',
            'id': bl,
            'props': f"name:'{bl}'"
        })

    # 用电模式节点
    patterns = profiles_df['consumption_pattern'].unique()
    for p in patterns:
        nodes.append({
            'type': 'ConsumptionPattern',
            'id': p,
            'props': f"name:'{p}'"
        })

    # 月份节点
    months = set()
    for _, row in profiles_df.iterrows():
        months.add(row['house_num'])

    # 保存节点
    nodes_df = pd.DataFrame(nodes)
    nodes_df.to_csv(f'{OUTPUT_DIR}/neo4j_nodes.csv', index=False, encoding='utf-8-sig')
    print(f"  保存节点: {len(nodes_df)} 条")

    # 关系
    relations = []

    # 用户-设备 拥有关系
    for _, dev in devices_df.iterrows():
        relations.append({
            'source': dev['user_id'],
            'target': dev['device_id'],
            'type': 'OWNS',
            'props': ''
        })

    # 用户-能耗等级
    for _, user in profiles_df.iterrows():
        relations.append({
            'source': user['user_id'],
            'target': user['energy_level'],
            'type': 'HAS_ENERGY_LEVEL',
            'props': ''
        })

    # 用户-行为标签
    for _, user in profiles_df.iterrows():
        relations.append({
            'source': user['user_id'],
            'target': user['behavior_label'],
            'type': 'HAS_BEHAVIOR_LABEL',
            'props': ''
        })

    # 用户-用电模式
    for _, user in profiles_df.iterrows():
        relations.append({
            'source': user['user_id'],
            'target': user['consumption_pattern'],
            'type': 'FOLLOWS_PATTERN',
            'props': ''
        })

    # 保存关系
    rels_df = pd.DataFrame(relations)
    rels_df.to_csv(f'{OUTPUT_DIR}/neo4j_relations.csv', index=False, encoding='utf-8-sig')
    print(f"  保存关系: {len(rels_df)} 条")

    return nodes_df, rels_df


def main():
    """主函数"""
    print("开始处理REFIT数据集...")
    print(f"输入目录: {INPUT_DIR}")
    print(f"输出目录: {OUTPUT_DIR}")

    # 1. 处理所有房屋数据
    users_df, devices_df, hourly_df, daily_df, monthly_df = process_all_houses()

    # 2. 生成用户画像
    profiles_df = generate_user_profiles(users_df, daily_df)

    # 3. 生成Neo4j数据
    nodes_df, rels_df = generate_kg_nodes_edges(users_df, devices_df, profiles_df)

    print("\n" + "=" * 60)
    print("处理完成!")
    print("=" * 60)

    # 打印用户画像统计
    print("\n用户画像统计:")
    print(profiles_df[['user_id', 'avg_daily_kwh', 'energy_level', 'behavior_label', 'consumption_pattern']].to_string())


if __name__ == '__main__':
    main()
