"""系统月份控制视图"""
from datetime import datetime
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import SystemMonth
from ..monthly_engine import advance_all_households


def _get_user_from_request(request):
    """从请求头获取当前用户"""
    import jwt
    from django.conf import settings
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return User.objects.get(id=payload.get('user_id'))
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return None


@api_view(['GET'])
def get_system_month(request):
    """获取当前系统月份"""
    sm = SystemMonth.get_current()
    return Response({
        'status': 'success',
        'current_year': sm.current_year,
        'current_month': sm.current_month,
        'year_month': sm.year_month,
        'total_months_elapsed': sm.total_months_elapsed,
        'unit_price': float(sm.unit_price),
        'is_processing': sm.is_processing,
    })


@api_view(['POST'])
def advance_system_month(request):
    """管理员执行月度推进"""
    user = _get_user_from_request(request)
    if not user or not user.is_staff:
        return Response({'status': 'error', 'message': '仅管理员可执行此操作'}, status=403)

    try:
        result = advance_all_households()
        return Response({'status': 'success', **result})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)
