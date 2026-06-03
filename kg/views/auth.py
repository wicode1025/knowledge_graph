"""认证相关视图"""
import json
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Household


def _generate_token(user):
    """生成JWT令牌"""
    payload = {
        'user_id': user.id,
        'username': user.username,
        'is_staff': user.is_staff,
        'exp': datetime.utcnow() + timedelta(days=7),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


def _decode_token(token):
    """解码JWT令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


@api_view(['POST'])
def auth_login(request):
    """用户登录"""
    username = request.data.get('username', '')
    password = request.data.get('password', '')

    if not username or not password:
        return Response({'status': 'error', 'message': '用户名和密码不能为空'}, status=400)

    user = authenticate(username=username, password=password)
    if user is None:
        return Response({'status': 'error', 'message': '用户名或密码错误'}, status=401)

    if not user.is_active:
        return Response({'status': 'error', 'message': '账户已被禁用'}, status=403)

    token = _generate_token(user)
    role = 'admin' if user.is_staff else 'user'

    # 获取绑定的用电账户ID
    elec_user_id = None
    try:
        household = user.household
        elec_user_id = household.household_id
    except Household.DoesNotExist:
        pass

    return Response({
        'status': 'success',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': role,
            'elec_user_id': elec_user_id,
        }
    })


@api_view(['POST'])
def auth_register(request):
    """用户注册"""
    username = request.data.get('username', '')
    password = request.data.get('password', '')
    email = request.data.get('email', '')

    if not username or not password:
        return Response({'status': 'error', 'message': '用户名和密码不能为空'}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({'status': 'error', 'message': '用户名已存在'}, status=400)

    user = User.objects.create_user(username=username, password=password, email=email)
    # 自动创建 Household
    household_id = f"H{user.id:04d}"
    Household.objects.create(
        household_id=household_id,
        user=user,
        real_name=username,
    )

    token = _generate_token(user)
    return Response({
        'status': 'success',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'role': 'user',
            'elec_user_id': household_id,
        }
    })


@api_view(['POST'])
def auth_logout(request):
    """用户登出"""
    return Response({'status': 'success', 'message': '已登出'})


@api_view(['GET'])
def auth_verify(request):
    """验证令牌"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    payload = _decode_token(token)
    if payload:
        return Response({'status': 'success', 'valid': True, 'user': payload})
    return Response({'status': 'error', 'valid': False}, status=401)
