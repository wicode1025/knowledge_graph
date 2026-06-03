"""
MySQL → Neo4j 知识图谱同步模块
"""
from .neo4j_db import neo4j_conn


def sync_all():
    """全量同步 MySQL 数据到 Neo4j"""
    from .models import (
        Household, Device, DeviceTypeConfig, Bill, HousingInfo
    )

    # 清空现有图谱
    neo4j_conn.execute_query("MATCH (n) DETACH DELETE n")

    # 1. 创建共享节点: 能耗等级
    levels = [
        ('节能型', 0, 100, '月均用电 < 100 kWh'),
        ('普通型', 100, 250, '月均用电 100-250 kWh'),
        ('摆渡型', 250, 500, '月均用电 250-500 kWh'),
        ('高耗能型', 500, 99999, '月均用电 >= 500 kWh'),
    ]
    for lv, lo, hi, desc in levels:
        neo4j_conn.execute_query("""
            CREATE (:EnergyLevel {level: $lv, min_kwh: $lo, max_kwh: $hi, description: $desc})
        """, {'lv': lv, 'lo': lo, 'hi': hi, 'desc': desc})

    # 2. 创建行为模式节点
    patterns = [
        ('早峰型', 7, 11, '用电高峰 7-11点'),
        ('晚峰型', 17, 22, '用电高峰 17-22点'),
        ('均匀型', 0, 24, '全天分布均匀'),
        ('间歇型', 0, 24, '无固定规律'),
    ]
    for name, ps, pe, desc in patterns:
        neo4j_conn.execute_query("""
            CREATE (:BehaviorPattern {name: $name, peak_start: $ps, peak_end: $pe, description: $desc})
        """, {'name': name, 'ps': ps, 'pe': pe, 'desc': desc})

    # 3. 同步用户节点
    households = Household.objects.select_related('housing').all()
    user_count = 0
    for h in households:
        housing = HousingInfo.objects.filter(household=h).first()

        # 计算用户用电统计
        from .models import ElectricityRecord, Bill
        records = ElectricityRecord.objects.filter(household=h)
        bills = Bill.objects.filter(household=h)

        total_kwh = sum(float(r.total_kwh) for r in records)
        months = records.values('year_month').distinct().count()
        avg_kwh = round(total_kwh / months, 1) if months > 0 else 0

        # 能耗等级
        if avg_kwh < 100:
            energy_level = '节能型'
        elif avg_kwh < 250:
            energy_level = '普通型'
        elif avg_kwh < 500:
            energy_level = '摆渡型'
        else:
            energy_level = '高耗能型'

        # 缴费信用
        total_bills = bills.count()
        paid_bills = bills.filter(status=2).count()
        has_warning = bills.filter(warning_flag=1).exists()
        credit = '良好' if not has_warning else ('一般' if paid_bills > 0 else '较差')

        neo4j_conn.execute_query("""
            MERGE (u:User {household_id: $hid})
            SET u.real_name = $name, u.gender = $gender, u.birth_year = $by,
                u.education = $edu, u.occupation = $occ, u.marital_status = $mar,
                u.is_urban = $urban, u.schedule = $sch, u.health = $health,
                u.energy_level = $el, u.behavior_pattern = $bp,
                u.avg_monthly_kwh = $avg, u.device_count = $dc,
                u.payment_credit = $credit, u.total_bills = $tb, u.paid_bills = $pb
        """, {
            'hid': h.household_id, 'name': h.real_name or '',
            'gender': h.gender, 'by': h.birth_year,
            'edu': str(h.education_level), 'occ': h.occupation or '',
            'mar': str(h.marital_status), 'urban': h.is_urban,
            'sch': str(h.daily_schedule), 'health': str(h.self_health),
            'el': energy_level, 'bp': '',
            'avg': avg_kwh, 'dc': Device.objects.filter(household=h).count(),
            'credit': credit, 'tb': total_bills, 'pb': paid_bills,
        })

        # 关联能耗等级
        neo4j_conn.execute_query("""
            MATCH (u:User {household_id: $hid})
            MATCH (el:EnergyLevel {level: $el})
            MERGE (u)-[:HAS_ENERGY {confidence: 0.9}]->(el)
        """, {'hid': h.household_id, 'el': energy_level})

        user_count += 1

    # 4. 同步设备节点 + 设备类型
    devices = Device.objects.select_related('device_type').all()
    for d in devices:
        neo4j_conn.execute_query("""
            MERGE (d:Device {device_id: $did})
            SET d.name = $name, d.type_code = $tc, d.category = $cat,
                d.rated_power = $rp, d.effective_power = $ep,
                d.usage_years = $uy, d.daily_hours = $dh,
                d.damage_probability = $dp, d.is_active = $ia,
                d.brand = $brand, d.bqf = $bqf
        """, {
            'did': d.device_id, 'name': d.custom_name or d.device_type.device_name,
            'tc': d.device_type.device_type_code, 'cat': d.device_type.category,
            'rp': d.rated_power, 'ep': d.effective_power or d.rated_power,
            'uy': float(d.usage_years), 'dh': float(d.daily_usage_hours),
            'dp': float(d.damage_probability), 'ia': d.is_active,
            'brand': d.brand_choice or '', 'bqf': float(d.bqf),
        })

        # OWNS 关系
        neo4j_conn.execute_query("""
            MATCH (u:User {household_id: $hid})
            MATCH (d:Device {device_id: $did})
            MERGE (u)-[:OWNS {daily_hours: $dh, habit: $hcode}]->(d)
        """, {
            'hid': d.household_id, 'did': d.device_id,
            'dh': float(d.daily_usage_hours),
            'hcode': d.usage_habit.habit_code if d.usage_habit else '',
        })

        # TYPE_OF 关系
        neo4j_conn.execute_query("""
            MERGE (dt:DeviceType {type_code: $tc})
            SET dt.name = $name, dt.category = $cat,
                dt.lifespan_years = $ly, dt.default_power = $dp, dt.aging_rate = $ar
        """, {
            'tc': d.device_type.device_type_code,
            'name': d.device_type.device_name,
            'cat': d.device_type.category,
            'ly': d.device_type.expected_lifespan_years,
            'dp': d.device_type.default_power,
            'ar': float(d.device_type.aging_power_increase_percent),
        })
        neo4j_conn.execute_query("""
            MATCH (d:Device {device_id: $did})
            MATCH (dt:DeviceType {type_code: $tc})
            MERGE (d)-[:TYPE_OF]->(dt)
        """, {'did': d.device_id, 'tc': d.device_type.device_type_code})

    # 5. 同步最近6个月的账单
    recent_bills = Bill.objects.order_by('-bill_month')[:6 * households.count()]
    for b in recent_bills:
        neo4j_conn.execute_query("""
            MERGE (bill:Bill {bill_id: $bid})
            SET bill.bill_month = $bm, bill.total_kwh = $kwh,
                bill.electricity_cost = $ec, bill.repair_cost = $rc,
                bill.total_amount = $ta, bill.status = $st,
                bill.is_warning = $warn
        """, {
            'bid': b.bill_id, 'bm': b.bill_month,
            'kwh': float(b.total_kwh), 'ec': float(b.electricity_cost),
            'rc': float(b.repair_cost), 'ta': float(b.total_amount),
            'st': {1: '未缴', 2: '已缴', 3: '逾期'}.get(b.status, '未知'),
            'warn': b.warning_flag == 1,
        })
        neo4j_conn.execute_query("""
            MATCH (u:User {household_id: $hid})
            MATCH (bill:Bill {bill_id: $bid})
            MERGE (u)-[:HAS_BILL]->(bill)
        """, {'hid': b.household_id, 'bid': b.bill_id})

    # 6. 计算并创建设备关联 (DEVICE_CORR)
    from collections import defaultdict
    device_pairs = defaultdict(int)
    for h in households:
        h_devices = list(Device.objects.filter(household=h).values_list('device_id', flat=True))
        for i in range(len(h_devices)):
            for j in range(i + 1, len(h_devices)):
                pair = tuple(sorted([h_devices[i], h_devices[j]]))
                device_pairs[pair] += 1

    max_count = max(device_pairs.values()) if device_pairs else 1
    for (d1, d2), count in device_pairs.items():
        corr = round(count / max_count, 2)
        if corr > 0.3:
            neo4j_conn.execute_query("""
                MATCH (d1:Device {device_id: $d1})
                MATCH (d2:Device {device_id: $d2})
                MERGE (d1)-[:DEVICE_CORR {correlation: $corr}]->(d2)
            """, {'d1': d1, 'd2': d2, 'corr': corr})

    return {
        'users': user_count,
        'devices': devices.count(),
        'bills': recent_bills.count(),
        'device_correlations': len(device_pairs),
    }
