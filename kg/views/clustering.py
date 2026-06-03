"""聚类/用户画像视图"""
import jwt
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Household, Device, ElectricityRecord, Bill, SystemMonth


def _get_user_from_request(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return User.objects.get(id=payload.get('user_id'))
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return None


@api_view(['GET'])
def get_clusters(request):
    """获取用户分群结果（简化版）"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)

    sm = SystemMonth.get_current()
    all_records = ElectricityRecord.objects.filter(year_month=sm.year_month).values('household_id')

    return Response({
        'status': 'success',
        'message': '聚类分析将在积累足够数据后自动生成',
        'current_month': sm.year_month,
        'total_households': Household.objects.count(),
    })


@api_view(['GET'])
def get_enhanced_profile(request):
    """获取增强用户画像"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)

    try:
        household = user.household
    except Household.DoesNotExist:
        return Response({'status': 'error', 'message': '未绑定'}, status=404)

    sm = SystemMonth.get_current()

    # 设备统计
    devices = Device.objects.filter(household=household)
    total_devices = devices.count()
    active_devices = devices.filter(is_active=1).count()
    damaged = devices.filter(is_active=0).count()

    # 用电统计
    records = ElectricityRecord.objects.filter(household=household).order_by('-year_month')[:12]
    monthly_data = {}
    for r in records:
        ym = r.year_month
        monthly_data[ym] = monthly_data.get(ym, 0) + float(r.total_kwh)
    avg_monthly = round(sum(monthly_data.values()) / len(monthly_data), 2) if monthly_data else 0

    # 账单统计
    all_bills = Bill.objects.filter(household=household)
    bill_count = all_bills.count()
    paid_count = all_bills.filter(status=2).count()
    has_warning = all_bills.filter(warning_flag=1).exists()

    # 能耗等级判断
    if avg_monthly < 100:
        energy_level = '节能型'
    elif avg_monthly < 250:
        energy_level = '普通型'
    elif avg_monthly < 500:
        energy_level = '摆渡型'
    else:
        energy_level = '高耗能型'

    return Response({
        'status': 'success',
        'profile': {
            'household_id': household.household_id,
            'real_name': household.real_name,
            'energy_level': energy_level,
            'total_devices': total_devices,
            'active_devices': active_devices,
            'damaged_devices': damaged,
            'avg_monthly_kwh': round(avg_monthly, 2),
            'bills_paid': paid_count,
            'bills_total': bill_count,
            'has_warning': has_warning,
            'monthly_trend': [{'month': str(k), 'kwh': float(v)} for k, v in sorted(monthly_data.items())],
        }
    })
