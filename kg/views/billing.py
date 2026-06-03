"""缴费管理视图"""
import jwt
from datetime import date
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Household, Bill, SystemMonth


def _get_user_from_request(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return User.objects.get(id=payload.get('user_id'))
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return None


@api_view(['GET'])
def get_my_bills(request):
    """获取当前用户的账单列表"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)

    try:
        household = user.household
    except Household.DoesNotExist:
        return Response({'status': 'error', 'message': '未绑定'}, status=404)

    bills = Bill.objects.filter(household=household).order_by('-bill_month')

    return Response({
        'status': 'success',
        'bills': [{
            'bill_id': b.bill_id,
            'bill_month': b.bill_month,
            'total_kwh': float(b.total_kwh),
            'electricity_cost': float(b.electricity_cost),
            'repair_cost': float(b.repair_cost),
            'total_amount': float(b.total_amount),
            'status': b.status,
            'status_text': {1: '未缴', 2: '已缴', 3: '逾期'}.get(b.status, '未知'),
            'warning_flag': b.warning_flag,
            'warning_message': b.warning_message,
            'due_date': str(b.due_date) if b.due_date else None,
            'paid_date': str(b.paid_date) if b.paid_date else None,
        } for b in bills]
    })


@api_view(['GET'])
def get_current_bill(request):
    """获取当月账单"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)

    try:
        household = user.household
    except Household.DoesNotExist:
        return Response({'status': 'error', 'message': '未绑定'}, status=404)

    latest = Bill.objects.filter(household=household).order_by('-bill_month').first()
    if not latest:
        return Response({'status': 'success', 'bill': None, 'message': '暂无账单（需管理员推进月份后生成）'})
    b = latest

    items = b.items.all()
    return Response({
        'status': 'success',
        'bill': {
            'bill_id': b.bill_id,
            'bill_month': b.bill_month,
            'total_kwh': float(b.total_kwh),
            'electricity_cost': float(b.electricity_cost),
            'repair_cost': float(b.repair_cost),
            'total_amount': float(b.total_amount),
            'status': b.status,
            'status_text': {1: '未缴', 2: '已缴', 3: '逾期'}.get(b.status, '未知'),
            'warning_flag': b.warning_flag,
            'warning_message': b.warning_message,
            'due_date': str(b.due_date) if b.due_date else None,
            'items': [{
                'item_type': i.item_type,
                'item_desc': i.item_desc,
                'amount': float(i.amount),
            } for i in items],
        }
    })


@api_view(['GET'])
def get_bill_detail(request, bill_id):
    """获取账单详情"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)

    try:
        b = Bill.objects.get(bill_id=bill_id)
    except Bill.DoesNotExist:
        return Response({'status': 'error', 'message': '账单不存在'}, status=404)

    items = b.items.all()
    return Response({
        'status': 'success',
        'bill': {
            'bill_id': b.bill_id,
            'bill_month': b.bill_month,
            'total_kwh': float(b.total_kwh),
            'electricity_cost': float(b.electricity_cost),
            'repair_cost': float(b.repair_cost),
            'total_amount': float(b.total_amount),
            'status': b.status,
            'due_date': str(b.due_date) if b.due_date else None,
            'paid_date': str(b.paid_date) if b.paid_date else None,
            'warning_flag': b.warning_flag,
            'warning_message': b.warning_message,
            'items': [{
                'item_type': i.item_type,
                'item_desc': i.item_desc,
                'amount': float(i.amount),
            } for i in items],
        }
    })


@api_view(['POST'])
def pay_bill(request, bill_id):
    """支付账单"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)

    try:
        b = Bill.objects.get(bill_id=bill_id)
    except Bill.DoesNotExist:
        return Response({'status': 'error', 'message': '账单不存在'}, status=404)

    if b.status == 2:
        return Response({'status': 'error', 'message': '该账单已支付'}, status=400)

    b.status = 2
    b.paid_amount = b.total_amount
    b.paid_date = date.today()
    b.warning_flag = 0
    b.warning_message = None
    b.save()

    return Response({'status': 'success', 'message': '缴费成功'})


@api_view(['GET'])
def get_notices(request):
    """获取缴费通知列表"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)
    try:
        household = user.household
    except Household.DoesNotExist:
        return Response({'status': 'error', 'message': '未绑定'}, status=404)

    from ..models import Notice
    notices = Notice.objects.filter(household=household).order_by('-is_pinned', '-created_at')

    return Response({
        'status': 'success',
        'notices': [{
            'id': n.id,
            'notice_type': n.notice_type,
            'title': n.title,
            'content': n.content,
            'is_read': n.is_read,
            'is_pinned': n.is_pinned,
            'bill_month': n.bill_month,
            'bill_id': n.bill.bill_id if n.bill else None,
            'created_at': str(n.created_at),
        } for n in notices]
    })
