"""用电记录视图"""
import jwt
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Household, ElectricityRecord


def _get_user_from_request(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return User.objects.get(id=payload.get('user_id'))
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return None


@api_view(['GET'])
def get_monthly_consumption(request):
    """获取月度用电记录"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)

    try:
        household = user.household
    except Household.DoesNotExist:
        return Response({'status': 'error', 'message': '未绑定'}, status=404)

    year_month = request.query_params.get('year_month')

    records = ElectricityRecord.objects.filter(household=household)
    if year_month:
        records = records.filter(year_month=year_month)
    records = records.select_related('device', 'device__device_type').order_by('-year_month')

    # 按月聚合
    monthly_data = {}
    for r in records:
        if r.year_month not in monthly_data:
            monthly_data[r.year_month] = {'year_month': r.year_month, 'total_kwh': 0, 'devices': []}
        monthly_data[r.year_month]['total_kwh'] += float(r.total_kwh)
        monthly_data[r.year_month]['devices'].append({
            'device_id': r.device.device_id,
            'device_name': r.device.custom_name or r.device.device_type.device_name,
            'kwh': float(r.total_kwh),
        })

    return Response({'status': 'success', 'data': list(monthly_data.values())})


@api_view(['GET'])
def get_consumption_summary(request):
    """获取用电概览"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)

    try:
        household = user.household
    except Household.DoesNotExist:
        return Response({'status': 'error', 'message': '未绑定'}, status=404)

    # 使用最新有数据的月份（上月）
    records_all = ElectricityRecord.objects.filter(
        household=household
    ).order_by('-year_month')
    if not records_all.exists():
        return Response({'status': 'success', 'total_kwh': 0, 'device_count': 0, 'device_breakdown': [], 'year_month': ''})

    latest_ym = records_all[0].year_month
    records = records_all.filter(year_month=latest_ym).select_related('device__device_type')

    total_kwh = sum(float(r.total_kwh) for r in records)

    # 设备用电占比
    device_breakdown = []
    for r in records:
        device_breakdown.append({
            'device_name': r.device.custom_name or r.device.device_type.device_name,
            'kwh': float(r.total_kwh),
            'percentage': round(float(r.total_kwh) / total_kwh * 100, 1) if total_kwh > 0 else 0,
        })
    device_breakdown.sort(key=lambda x: x['kwh'], reverse=True)

    return Response({
        'status': 'success',
        'year_month': latest_ym,
        'total_kwh': round(total_kwh, 2),
        'device_count': len(records),
        'device_breakdown': device_breakdown,
    })


@api_view(['GET'])
def get_consumption_trends(request):
    """获取近12月用电趋势"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)

    try:
        household = user.household
    except Household.DoesNotExist:
        return Response({'status': 'error', 'message': '未绑定'}, status=404)

    records = ElectricityRecord.objects.filter(
        household=household
    ).values('year_month').order_by('-year_month')[:12]

    # 按月聚合
    monthly_totals = {}
    for r in records:
        ym = r['year_month']
        if ym not in monthly_totals:
            monthly_totals[ym] = 0

    detailed = ElectricityRecord.objects.filter(
        household=household,
        year_month__in=list(monthly_totals.keys())
    ).values('year_month', 'total_kwh')

    for d in detailed:
        monthly_totals[d['year_month']] += float(d['total_kwh'])

    trends = [{'year_month': k, 'total_kwh': round(v, 2)} for k, v in sorted(monthly_totals.items())]

    return Response({'status': 'success', 'trends': trends})
