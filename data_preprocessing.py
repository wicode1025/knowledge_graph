"""
电力用户画像系统 - 数据预处理脚本
将原始数据处理成适合知识图谱(Neo4j)和Django+Vue系统使用的格式
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

# 设置路径
DATA_DIR = 'data'
OUTPUT_DIR = 'processed_data'

# 创建输出目录
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_csv(filename):
    """加载CSV文件"""
    filepath = os.path.join(DATA_DIR, filename)
    return pd.read_csv(filepath)


def process_electricity_data():
    """处理电力数据 - 整合各设备用电数据"""
    print("处理电力数据...")

    # 定义电力设备映射
    electricity_files = {
        'CDE': 'Electricity_CDE.csv',    # Clothes Dryer - 干衣机
        'DNE': 'Electricity_DNE.csv',    # Dishwasher - 洗碗机
        'HPE': 'Electricity_HPE.csv',     # HVAC/Heat Pump - 暖通空调
        'WHE': 'Electricity_WHE.csv',     # Water Heater - 热水器
    }

    all_electricity = []

    for device_code, filename in electricity_files.items():
        df = load_csv(filename)
        df['datetime'] = pd.to_datetime(df['unix_ts'], unit='s')
        df['date'] = df['datetime'].dt.date
        df['hour'] = df['datetime'].dt.hour
        df['device'] = device_code

        # 选择关键字段
        device_df = df[['datetime', 'date', 'hour', 'device', 'V', 'I', 'P', 'Q', 'S', 'DPF', 'APF']].copy()
        device_df.columns = ['datetime', 'date', 'hour', 'device', 'voltage', 'current',
                            'active_power', 'reactive_power', 'apparent_power',
                            'displacement_power_factor', 'apparent_power_factor']

        all_electricity.append(device_df)

    # 合并所有电力数据
    electricity_combined = pd.concat(all_electricity, ignore_index=True)

    # 按小时聚合 - 减少数据量
    hourly_electricity = electricity_combined.groupby(
        ['date', 'hour', 'device']
    ).agg({
        'voltage': 'mean',
        'current': 'mean',
        'active_power': 'mean',
        'reactive_power': 'mean',
        'apparent_power': 'mean',
        'displacement_power_factor': 'mean',
        'apparent_power_factor': 'mean'
    }).reset_index()

    # 保存处理后的电力数据
    hourly_electricity.to_csv(
        os.path.join(OUTPUT_DIR, 'hourly_electricity_by_device.csv'),
        index=False
    )

    # 按日期汇总各设备用电量
    daily_electricity = electricity_combined.groupby(['date', 'device']).agg({
        'active_power': 'sum',  # 千瓦时(按分钟采样，需要乘以1/60)
    }).reset_index()
    daily_electricity['energy_kwh'] = daily_electricity['active_power'] / 60

    daily_pivot = daily_electricity.pivot(
        index='date',
        columns='device',
        values='energy_kwh'
    ).reset_index()
    daily_pivot.columns.name = None

    daily_pivot.to_csv(
        os.path.join(OUTPUT_DIR, 'daily_electricity_consumption.csv'),
        index=False
    )

    print(f"  - 每小时电力数据: {len(hourly_electricity)} 条记录")
    print(f"  - 每日用电汇总: {len(daily_pivot)} 条记录")


def process_weather_data():
    """处理天气数据"""
    print("处理天气数据...")

    df = load_csv('Climate_HourlyWeather.csv')

    # 转换时间
    df['datetime'] = pd.to_datetime(df['Date/Time'])
    df['date'] = df['datetime'].dt.date
    df['hour'] = df['datetime'].dt.hour

    # 选择关键字段
    weather_hourly = df[[
        'datetime', 'date', 'hour',
        'Temp (C)', 'Dew Point Temp (C)', 'Rel Hum (%)',
        'Wind Spd (km/h)', 'Visibility (km)', 'Stn Press (kPa)', 'Weather'
    ]].copy()

    weather_hourly.columns = [
        'datetime', 'date', 'hour',
        'temperature', 'dew_point', 'humidity',
        'wind_speed', 'visibility', 'pressure', 'weather_condition'
    ]

    # 按日期聚合 - 日均值
    daily_weather = weather_hourly.groupby('date').agg({
        'temperature': 'mean',
        'dew_point': 'mean',
        'humidity': 'mean',
        'wind_speed': 'mean',
        'visibility': 'mean',
        'pressure': 'mean'
    }).reset_index()

    # 添加天气状况（取最常见）
    daily_weather_cond = weather_hourly.groupby('date')['weather_condition'].agg(
        lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown'
    ).reset_index()
    daily_weather = daily_weather.merge(daily_weather_cond, on='date')

    # 保存
    weather_hourly.to_csv(
        os.path.join(OUTPUT_DIR, 'hourly_weather.csv'),
        index=False
    )
    daily_weather.to_csv(
        os.path.join(OUTPUT_DIR, 'daily_weather.csv'),
        index=False
    )

    print(f"  - 小时天气数据: {len(weather_hourly)} 条记录")
    print(f"  - 日均天气数据: {len(daily_weather)} 条记录")


def process_natural_gas_data():
    """处理天然气数据"""
    print("处理天然气数据...")

    # 月度账单数据
    billing_df = load_csv('NaturalGas_Billing.csv')
    billing_df['From Date'] = pd.to_datetime(billing_df['From Date'])
    billing_df['To Date'] = pd.to_datetime(billing_df['To Date'])
    billing_df['year_month'] = billing_df['From Date'].dt.to_period('M')

    billing_clean = billing_df[[
        'year_month', 'From Date', 'To Date', 'Billing Days',
        'Billed GJ', 'Amount'
    ]].copy()
    billing_clean.columns = [
        'year_month', 'period_start', 'period_end', 'billing_days',
        'consumption_gj', 'amount'
    ]

    billing_clean.to_csv(
        os.path.join(OUTPUT_DIR, 'monthly_gas_billing.csv'),
        index=False
    )

    # 月度消耗数据
    monthly_df = load_csv('NaturalGas_Monthly.csv')
    monthly_df['Month Year'] = pd.to_datetime(monthly_df['Month Year'], format='%b %Y')
    monthly_df['year_month'] = monthly_df['Month Year'].dt.to_period('M')

    monthly_clean = monthly_df[[
        'year_month', 'Net Consumption (GJ)', 'Avg Outside Temp (℃)'
    ]].copy()
    monthly_clean.columns = ['year_month', 'consumption_gj', 'avg_temperature']

    monthly_clean.to_csv(
        os.path.join(OUTPUT_DIR, 'monthly_gas_consumption.csv'),
        index=False
    )

    print(f"  - 天然气账单: {len(billing_clean)} 条记录")
    print(f"  - 月度天然气消耗: {len(monthly_clean)} 条记录")


def process_water_heater_data():
    """处理热水器数据"""
    print("处理热水器数据...")

    df = load_csv('Water_HTW.csv')
    df['datetime'] = pd.to_datetime(df['unix_ts'], unit='s')
    df['date'] = df['datetime'].dt.date
    df['hour'] = df['datetime'].dt.hour

    # Water_HTW.csv 列名: counter, avg_rate, inst_rate
    # 按小时聚合
    hourly_water = df.groupby(['date', 'hour']).agg({
        'counter': 'mean',
        'avg_rate': 'mean',
        'inst_rate': 'mean'
    }).reset_index()
    hourly_water.columns = ['date', 'hour', 'avg_counter', 'avg_rate', 'inst_rate']

    # 每日能耗 (基于counter的变化)
    daily_water = df.groupby('date').agg({
        'counter': 'max',
        'counter': 'min'
    }).reset_index()
    # 简化处理，使用平均rate
    daily_water = df.groupby('date').agg({
        'avg_rate': 'mean',
        'inst_rate': 'mean'
    }).reset_index()
    daily_water['estimated_energy'] = daily_water['avg_rate'] * 24  # 估算

    hourly_water.to_csv(
        os.path.join(OUTPUT_DIR, 'hourly_water_heater.csv'),
        index=False
    )
    daily_water.to_csv(
        os.path.join(OUTPUT_DIR, 'daily_water_heater.csv'),
        index=False
    )

    print(f"  - 小时热水器数据: {len(hourly_water)} 条记录")
    print(f"  - 日热水器数据: {len(daily_water)} 条记录")


def create_user_profile_summary():
    """创建用户画像汇总数据 - 供知识图谱使用"""
    print("创建用户画像汇总...")

    # 读取处理后的数据
    daily_electricity = pd.read_csv(os.path.join(OUTPUT_DIR, 'daily_electricity_consumption.csv'))
    daily_weather = pd.read_csv(os.path.join(OUTPUT_DIR, 'daily_weather.csv'))
    monthly_gas = pd.read_csv(os.path.join(OUTPUT_DIR, 'monthly_gas_consumption.csv'))

    # 计算月度统计特征
    daily_electricity['date'] = pd.to_datetime(daily_electricity['date'])

    # 月度用电汇总
    monthly_electricity = daily_electricity.copy()
    monthly_electricity['year_month'] = monthly_electricity['date'].dt.to_period('M')

    if 'HPE' in monthly_electricity.columns:
        monthly_hpe = monthly_electricity.groupby('year_month')['HPE'].sum().reset_index()
        monthly_hpe.columns = ['year_month', 'hvac_energy_kwh']

    if 'WHE' in monthly_electricity.columns:
        monthly_whe = monthly_electricity.groupby('year_month')['WHE'].sum().reset_index()
        monthly_whe.columns = ['year_month', 'water_heater_energy_kwh']

    # 创建用户画像实体数据
    profile_data = {
        'user_id': ['household_001'],
        'name': ['家庭用户001'],
        'total_months': [len(monthly_gas)],
        'avg_monthly_gas_gj': [monthly_gas['consumption_gj'].mean()],
        'max_monthly_gas_gj': [monthly_gas['consumption_gj'].max()],
        'min_monthly_gas_gj': [monthly_gas['consumption_gj'].min()],
    }

    if 'hvac_energy_kwh' in locals():
        profile_data['avg_monthly_hvac_kwh'] = [monthly_hpe['hvac_energy_kwh'].mean()]
    if 'water_heater_energy_kwh' in locals():
        profile_data['avg_monthly_water_heater_kwh'] = [monthly_whe['water_heater_energy_kwh'].mean()]

    profile_df = pd.DataFrame(profile_data)
    profile_df.to_csv(
        os.path.join(OUTPUT_DIR, 'user_profile.csv'),
        index=False
    )

    print(f"  - 用户画像数据: {len(profile_df)} 条记录")


def create_kg_relationships():
    """创建知识图谱关系数据 - 适合Neo4j导入"""
    print("创建知识图谱关系数据...")

    # 读取处理后的数据
    daily_electricity = pd.read_csv(os.path.join(OUTPUT_DIR, 'daily_electricity_consumption.csv'))
    daily_weather = pd.read_csv(os.path.join(OUTPUT_DIR, 'daily_weather.csv'))

    # 1. 创建 日期-天气 关系
    weather_relations = daily_weather.copy()
    weather_relations['date'] = pd.to_datetime(weather_relations['date']).dt.strftime('%Y-%m-%d')
    weather_relations.to_csv(
        os.path.join(OUTPUT_DIR, 'kg_weather_relations.csv'),
        index=False
    )

    # 2. 创建 设备-能耗 节点和关系
    daily_electricity['date'] = pd.to_datetime(daily_electricity['date']).dt.strftime('%Y-%m-%d')

    # 设备节点数据
    devices = pd.DataFrame({
        'device_id': ['CDE', 'DNE', 'HPE', 'WHE'],
        'device_name': ['干衣机', '洗碗机', '暖通空调', '热水器'],
        'device_type': ['Electronics', 'Electronics', 'HVAC', 'WaterHeating']
    })
    devices.to_csv(
        os.path.join(OUTPUT_DIR, 'kg_device_nodes.csv'),
        index=False
    )

    # 设备每日能耗关系
    energy_relations = []
    for _, row in daily_electricity.iterrows():
        date = row['date']
        for device in ['CDE', 'DNE', 'HPE', 'WHE']:
            if device in row and pd.notna(row[device]):
                energy_relations.append({
                    'date': date,
                    'device_id': device,
                    'energy_kwh': row[device]
                })

    energy_df = pd.DataFrame(energy_relations)
    energy_df.to_csv(
        os.path.join(OUTPUT_DIR, 'kg_device_energy_relations.csv'),
        index=False
    )

    print(f"  - 天气关系: {len(weather_relations)} 条")
    print(f"  - 设备节点: {len(devices)} 条")
    print(f"  - 设备能耗关系: {len(energy_df)} 条")


def main():
    """主函数"""
    print("=" * 50)
    print("电力用户画像系统 - 数据预处理")
    print("=" * 50)

    # 1. 处理电力数据
    process_electricity_data()

    # 2. 处理天气数据
    process_weather_data()

    # 3. 处理天然气数据
    process_natural_gas_data()

    # 4. 处理热水器数据
    process_water_heater_data()

    # 5. 创建用户画像汇总
    create_user_profile_summary()

    # 6. 创建知识图谱数据
    create_kg_relationships()

    print("=" * 50)
    print("数据预处理完成!")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 50)

    # 列出生成的文件
    print("\n生成的文件列表:")
    for f in os.listdir(OUTPUT_DIR):
        filepath = os.path.join(OUTPUT_DIR, f)
        size = os.path.getsize(filepath) / 1024
        print(f"  - {f} ({size:.1f} KB)")


if __name__ == '__main__':
    main()
