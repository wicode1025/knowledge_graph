"""维修报单视图"""
import uuid
import jwt
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Household, Device, RepairOrder


def _get_user_from_request(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return User.objects.get(id=payload.get('user_id'))
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return None


@api_view(['GET', 'POST'])
def repair_orders(request):
    """获取/创建报修单"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)

    try:
        household = user.household
    except Household.DoesNotExist:
        return Response({'status': 'error', 'message': '未绑定'}, status=404)

    if request.method == 'GET':
        orders = RepairOrder.objects.filter(
            household=household
        ).select_related('device', 'device__device_type').order_by('-created_at')

        status_map = {1: '待审核', 2: '已派单', 3: '维修中', 4: '已完成(待缴费)', 5: '已完成(已缴费)', 6: '已取消'}
        fault_map = {1: '无法开机', 2: '运行异常', 3: '漏电', 4: '噪音异常', 5: '制冷/热失效', 6: '漏水', 7: '其他'}

        return Response({
            'status': 'success',
            'orders': [{
                'order_id': o.order_id,
                'device_name': o.device.custom_name or o.device.device_type.device_name,
                'fault_type': o.fault_type,
                'fault_text': fault_map.get(o.fault_type, '未知'),
                'fault_description': o.fault_description,
                'status': o.status,
                'status_text': status_map.get(o.status, '未知'),
                'repair_cost': float(o.repair_cost) if o.repair_cost else None,
                'technician_name': o.technician_name,
                'appointment_date': str(o.appointment_date) if o.appointment_date else None,
                'rating': o.rating,
                'created_at': str(o.created_at),
            } for o in orders]
        })

    elif request.method == 'POST':
        device_id = request.data.get('device_id')
        if not device_id:
            return Response({'status': 'error', 'message': '请选择设备'}, status=400)

        try:
            device = Device.objects.get(device_id=device_id, household=household)
        except Device.DoesNotExist:
            return Response({'status': 'error', 'message': '设备不存在'}, status=404)

        order_id = f"REP_{household.household_id}_{uuid.uuid4().hex[:6]}"
        order = RepairOrder.objects.create(
            order_id=order_id,
            household=household,
            device=device,
            fault_type=request.data.get('fault_type', 7),
            fault_description=request.data.get('fault_description', ''),
            contact_name=request.data.get('contact_name', household.real_name),
            contact_phone=request.data.get('contact_phone', household.phone or ''),
            appointment_date=request.data.get('appointment_date'),
            appointment_time=request.data.get('appointment_time', 1),
        )

        return Response({'status': 'success', 'order_id': order.order_id})


@api_view(['GET'])
def repair_order_detail(request, order_id):
    """获取报修单详情"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)

    try:
        o = RepairOrder.objects.get(order_id=order_id)
    except RepairOrder.DoesNotExist:
        return Response({'status': 'error', 'message': '报修单不存在'}, status=404)

    status_map = {1: '待审核', 2: '已派单', 3: '维修中', 4: '已完成(待缴费)', 5: '已完成(已缴费)', 6: '已取消'}
    return Response({
        'status': 'success',
        'order': {
            'order_id': o.order_id,
            'device_name': o.device.custom_name or o.device.device_type.device_name,
            'fault_type': o.fault_type,
            'fault_description': o.fault_description,
            'contact_name': o.contact_name,
            'contact_phone': o.contact_phone,
            'appointment_date': str(o.appointment_date) if o.appointment_date else None,
            'status': o.status,
            'status_text': status_map.get(o.status, '未知'),
            'repair_result': o.repair_result,
            'repair_cost': float(o.repair_cost) if o.repair_cost else None,
            'technician_name': o.technician_name,
            'completed_date': str(o.completed_date) if o.completed_date else None,
            'rating': o.rating,
            'is_billed': o.is_billed,
        }
    })


@api_view(['POST'])
def rate_repair(request, order_id):
    """评价维修服务"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)

    try:
        o = RepairOrder.objects.get(order_id=order_id, household=user.household)
    except RepairOrder.DoesNotExist:
        return Response({'status': 'error', 'message': '报修单不存在'}, status=404)

    if o.status not in [4, 5]:
        return Response({'status': 'error', 'message': '只能评价已完成的维修'}, status=400)

    rating = request.data.get('rating', 5)
    if rating < 1 or rating > 5:
        return Response({'status': 'error', 'message': '评分需在1-5之间'}, status=400)

    o.rating = rating
    o.save()
    return Response({'status': 'success', 'message': '评价已提交'})
