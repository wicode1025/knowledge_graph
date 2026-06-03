"""
月度模拟引擎 - 核心计算模块
负责推进系统月份时的所有计算逻辑
"""
import math
import calendar
from datetime import date, timedelta
from decimal import Decimal
from django.db import transaction
from .models import (
    Household, Device, DeviceTypeConfig, SystemMonth,
    ElectricityRecord, Bill, BillItem, RepairOrder
)


def calc_effective_power(rated_power, usage_years, lifespan, aging_rate):
    """计算老化后的有效功率
    P_effective = P_rated * (1 + aging_rate * (usage_years / lifespan)^2)
    """
    if lifespan <= 0:
        return rated_power
    ratio = min(1.0, float(usage_years) / lifespan)
    factor = 1 + float(aging_rate) * (ratio ** 2)
    return int(rated_power * factor)


def calc_damage_probability(usage_years, lifespan, weibull_beta, bqf):
    """计算威布尔分布的损坏概率
    P_damage = 1 - exp(-(t / (lifespan * 1.2 * BQF))^beta)
    """
    if lifespan <= 0:
        return 0
    eta = float(lifespan) * 1.2 * float(bqf)
    if eta <= 0:
        return 0
    t = float(usage_years)
    beta = float(weibull_beta)
    return 1 - math.exp(-((t / eta) ** beta))


def calc_monthly_kwh(device, year_month):
    """计算单台设备月用电量
    E_month = P_effective * daily_hours * days_in_month * seasonal_factor / 1000
    """
    year, month = map(int, year_month.split('-'))
    days = calendar.monthrange(year, month)[1]

    config = device.device_type
    daily_hours = float(device.daily_usage_hours or config.typical_daily_hours or 1)

    # 季节系数
    seasonal_factor = 1.0
    if device.usage_habit:
        seasonal_factor = float(device.usage_habit.seasonal_factor)

    # 老化后的有效功率
    effective_power = calc_effective_power(
        device.rated_power,
        float(device.usage_years),
        config.expected_lifespan_years,
        float(config.aging_power_increase_percent)
    )

    kwh = effective_power * daily_hours * days * seasonal_factor / 1000
    return round(kwh, 2), effective_power


@transaction.atomic
def advance_all_households():
    """推进所有用户到下一个月 - 核心流程
    1. 计算每个设备的月用电量
    2. 汇总未计入账单的维修费
    3. 为每个用户生成账单
    4. 更新设备年限和损坏概率
    5. 推进系统月份
    """
    sys_month = SystemMonth.get_current()

    if sys_month.is_processing:
        raise Exception("系统正在执行月度推进，请稍后再试")

    sys_month.is_processing = 1
    sys_month.save()

    try:
        year_month = sys_month.year_month
        year, month = sys_month.current_year, sys_month.current_month

        # 步骤1: 计算每个活跃设备的月用电量
        active_devices = Device.objects.filter(is_active=1).select_related(
            'household', 'device_type', 'usage_habit'
        )

        records_created = 0
        for device in active_devices:
            try:
                kwh, effective_power = calc_monthly_kwh(device, year_month)

                ElectricityRecord.objects.update_or_create(
                    household=device.household,
                    device=device,
                    year_month=year_month,
                    defaults={
                        'total_kwh': Decimal(str(kwh)),
                        'avg_daily_kwh': Decimal(str(round(kwh / calendar.monthrange(year, month)[1], 2))),
                        'peak_power': Decimal(str(effective_power)),
                        'hours_used': Decimal(str(float(device.daily_usage_hours) * calendar.monthrange(year, month)[1])),
                    }
                )
                records_created += 1
            except Exception as e:
                print(f"Error calculating for device {device.device_id}: {e}")

        # 步骤2: 汇总未计入账单的维修费
        completed_repairs = RepairOrder.objects.filter(
            status=4, is_billed=0
        ).select_related('household')

        repair_by_household = {}
        for repair in completed_repairs:
            hid = repair.household.household_id
            if hid not in repair_by_household:
                repair_by_household[hid] = []
            repair_by_household[hid].append(repair)

        # 步骤3: 为每个家庭用户生成账单
        households = Household.objects.all()
        unit_price = float(sys_month.unit_price)
        bills_created = 0

        for household in households:
            # 计算本月电费
            records = ElectricityRecord.objects.filter(
                household=household, year_month=year_month
            )
            total_kwh = float(sum(r.total_kwh for r in records))
            electricity_cost = round(total_kwh * unit_price, 2)

            # 维修费
            repair_total = Decimal('0')
            repairs = repair_by_household.get(household.household_id, [])
            for repair in repairs:
                repair_total += repair.repair_cost or Decimal('0')

            # 检查上月缴费情况
            prev_month = _prev_year_month(year, month)
            last_bill = Bill.objects.filter(
                household=household, bill_month=prev_month
            ).first()

            consecutive_unpaid = 0
            if last_bill and last_bill.status != 2:  # 上月未缴费
                consecutive_unpaid = last_bill.consecutive_unpaid_months + 1
            elif last_bill and last_bill.status == 2:
                consecutive_unpaid = 0

            # 生成账单
            total_amount = Decimal(str(electricity_cost)) + repair_total
            bill_id = f"BILL_{household.household_id}_{year_month}"

            due_day = 15
            if month == 12:
                due_date = date(year + 1, 1, due_day)
            else:
                due_date = date(year, month + 1, due_day)

            bill, created = Bill.objects.update_or_create(
                bill_id=bill_id,
                defaults={
                    'household': household,
                    'bill_month': year_month,
                    'total_kwh': Decimal(str(round(total_kwh, 2))),
                    'electricity_cost': Decimal(str(electricity_cost)),
                    'unit_price': Decimal(str(unit_price)),
                    'repair_cost': repair_total,
                    'total_amount': total_amount,
                    'consecutive_unpaid_months': consecutive_unpaid,
                    'warning_flag': 1 if consecutive_unpaid >= 2 else 0,
                    'warning_message': f'您已连续{consecutive_unpaid}个月未缴纳电费，请尽快缴费！' if consecutive_unpaid >= 2 else None,
                    'due_date': due_date,
                    'status': 1,
                }
            )

            if created or bill.items.count() == 0:
                # 电费明细
                BillItem.objects.create(
                    bill=bill, item_type=1,
                    item_desc=f'{total_kwh:.1f}kWh × ¥{unit_price}/度',
                    amount=Decimal(str(electricity_cost))
                )
                # 维修费明细
                for repair in repairs:
                    BillItem.objects.create(
                        bill=bill, item_type=2,
                        item_desc=f'维修: {repair.device.device_type.device_name}',
                        amount=repair.repair_cost,
                        ref_id=repair.order_id
                    )
                    repair.is_billed = 1
                    repair.status = 5
                    repair.save()

            bills_created += 1

            # 生成缴费通知
            from .models import Notice
            is_warning = bill.warning_flag == 1
            rep = bill.repair_cost or 0
            msg = (
                f'尊敬的用户，您{year_month}电费账单已生成。用电量 {total_kwh:.0f} kWh，'
                f'电费 ¥{electricity_cost}。'
                + (f'另有维修费 ¥{rep}。' if rep > 0 else '')
                + f'请于 {due_date} 前完成缴费，逾期将影响信用记录。'
            )
            Notice.objects.create(
                household=household, bill=bill,
                notice_type=2 if is_warning else 1,
                title=f'{"⚠ " if is_warning else ""}{year_month} 电费账单',
                content=msg,
                is_pinned=1 if is_warning else 0,
                bill_month=year_month
            )
            # 每个用户保留最近10条通知
            old = Notice.objects.filter(household=household).order_by('-created_at')[10:]
            for n in old: n.delete()

        # 步骤4: 更新所有设备年限和损坏概率
        devices_updated = 0
        devices_damaged = 0
        for device in Device.objects.filter(is_active=1):
            config = device.device_type
            # 增加使用年限
            device.usage_years = Decimal(str(float(device.usage_years) + 1.0 / 12.0))

            # 重新计算有效功率
            device.effective_power = calc_effective_power(
                device.rated_power,
                float(device.usage_years),
                config.expected_lifespan_years,
                float(config.aging_power_increase_percent)
            )

            # 重新计算损坏概率
            device.damage_probability = Decimal(str(round(
                calc_damage_probability(
                    float(device.usage_years),
                    config.expected_lifespan_years,
                    float(config.weibull_beta),
                    float(device.bqf)
                ), 4
            )))

            # 损坏概率 > 0.8 自动标记为损坏
            if float(device.damage_probability) > 0.8:
                device.is_active = 0
                device.damage_date = date.today()
                devices_damaged += 1

            device.save()
            devices_updated += 1

        # 步骤5: 推进系统月份
        if month == 12:
            sys_month.current_year = year + 1
            sys_month.current_month = 1
        else:
            sys_month.current_month = month + 1
        sys_month.total_months_elapsed += 1
        sys_month.is_processing = 0
        sys_month.last_advance_time = date.today()
        sys_month.save()

        return {
            'success': True,
            'records_created': records_created,
            'bills_created': bills_created,
            'devices_updated': devices_updated,
            'devices_damaged': devices_damaged,
            'repairs_billed': sum(len(v) for v in repair_by_household.values()),
            'new_month': sys_month.year_month,
        }

    except Exception as e:
        sys_month.is_processing = 0
        sys_month.save()
        raise e


def _prev_year_month(year, month):
    """计算上一个月"""
    if month == 1:
        return f"{year - 1}-12"
    return f"{year}-{month - 1:02d}"
