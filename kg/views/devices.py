"""设备管理视图"""
import uuid
import jwt
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Household, Device, DeviceTypeConfig, DeviceUsageHabit
from ..monthly_engine import calc_effective_power, calc_damage_probability

# 品牌品质系数对照表
BRAND_BQF_MAP = {
    # 冰箱
    '海尔冰箱': 1.25, '美的冰箱': 1.15, '容声': 1.10, '西门子冰箱': 1.30,
    '松下冰箱': 1.20, '美菱': 0.95, '新飞': 0.95, 'TCL冰箱': 0.95, '小米冰箱': 0.90, '云米': 0.90,
    # 空调
    '格力': 1.25, '美的空调': 1.15, '海尔空调': 1.15, '大金': 1.35, '三菱': 1.35,
    '奥克斯': 1.00, '小米空调': 0.95, '华凌': 0.95, '科龙': 0.90, '长虹': 0.90,
    # 洗衣机
    '海尔洗衣机': 1.20, '小天鹅': 1.20, '美的洗衣机': 1.10, '西门子洗衣机': 1.35, '博世': 1.35,
    '松下洗衣机': 1.25,
    # 电视机
    '海信': 1.15, 'TCL电视': 1.10, '小米电视': 0.95, '索尼': 1.35, '三星': 1.30, '创维': 0.90, '康佳': 0.90,
    # 热水器
    '海尔热水器': 1.20, '美的热水器': 1.10, 'A.O.史密斯': 1.35, '万家乐': 0.95, '万和': 0.95,
    # 电脑
    '联想': 1.10, '戴尔': 1.10, '惠普': 1.10, '华硕电脑': 1.05, '宏碁': 1.05, '苹果': 1.25, '华为': 1.15,
    # 厨房电器
    '格兰仕': 1.10, '松下微波炉': 1.25, '苏泊尔': 1.10, '九阳': 1.00, '方太': 1.25, '老板': 1.20,
    # 清洁电器
    '戴森': 1.30, '小狗': 1.05, '科沃斯': 1.15, '石头': 1.15, '小米扫地': 0.95,
    # 照明
    '欧普': 1.10, '雷士': 1.10, '飞利浦': 1.15, '小米照明': 1.00,
    # 风扇/暖器
    '美的风扇': 1.10, '格力风扇': 1.10, '艾美特': 1.05, '小米风扇': 1.00,
    # 网络
    'TP-LINK': 1.10, '小米路由': 1.00, '华为路由': 1.15, '华硕路由': 1.20,
}

# 每种电器类型的品牌选项
DEVICE_BRANDS = {
    'FRIDGE_DOUBLE': ['海尔冰箱', '美的冰箱', '容声', '西门子冰箱', '松下冰箱', '美菱', '小米冰箱', '其他'],
    'FRIDGE_FRENCH': ['海尔冰箱', '美的冰箱', '容声', '西门子冰箱', '松下冰箱', '小米冰箱', '其他'],
    'AC_1HP': ['格力', '美的空调', '海尔空调', '大金', '奥克斯', '小米空调', '华凌', '其他'],
    'AC_1.5HP': ['格力', '美的空调', '海尔空调', '大金', '三菱', '奥克斯', '小米空调', '华凌', '其他'],
    'AC_2HP': ['格力', '美的空调', '海尔空调', '大金', '三菱', '奥克斯', '其他'],
    'AC_CENTRAL': ['格力', '美的空调', '大金', '三菱', '其他'],
    'WASHER_TOP': ['海尔洗衣机', '小天鹅', '美的洗衣机', '松下洗衣机', '其他'],
    'WASHER_FRONT': ['海尔洗衣机', '小天鹅', '美的洗衣机', '西门子洗衣机', '博世', '松下洗衣机', '其他'],
    'TV_55': ['海信', 'TCL电视', '小米电视', '索尼', '三星', '创维', '其他'],
    'TV_65': ['海信', 'TCL电视', '小米电视', '索尼', '三星', '创维', '其他'],
    'WH_STORAGE': ['海尔热水器', '美的热水器', 'A.O.史密斯', '万家乐', '万和', '其他'],
    'PC_DESKTOP': ['联想', '戴尔', '惠普', '华硕电脑', '宏碁', '其他'],
    'LAPTOP': ['联想', '戴尔', '惠普', '苹果', '华为', '小米', '其他'],
    'MICROWAVE': ['格兰仕', '美的厨房', '松下微波炉', '其他'],
    'INDUCTION': ['美的厨房', '苏泊尔', '九阳', '其他'],
    'RICE_COOKER': ['美的厨房', '苏泊尔', '松下微波炉', '小米', '其他'],
    'KETTLE': ['美的厨房', '苏泊尔', '小米', '其他'],
    'RANGE_HOOD': ['方太', '老板', '美的厨房', '海尔厨房', '其他'],
    'VACUUM': ['戴森', '小狗', '美的厨房', '小米', '其他'],
    'ROBOT_VACUUM': ['科沃斯', '石头', '小米扫地', '其他'],
    'LED_LIVING': ['欧普', '雷士', '飞利浦', '小米照明', '其他'],
    'LED_BEDROOM': ['欧普', '雷士', '飞利浦', '小米照明', '其他'],
    'FAN': ['美的风扇', '格力风扇', '艾美特', '小米风扇', '其他'],
    'HEATER': ['美的风扇', '格力风扇', '艾美特', '小米风扇', '其他'],
    'ROUTER': ['TP-LINK', '小米路由', '华为路由', '华硕路由', '其他'],
    '_default': ['一线品牌', '普通品牌', '其他'],
}


def _get_user_from_request(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return User.objects.get(id=payload.get('user_id'))
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return None


def _get_household(user):
    try:
        return user.household
    except Household.DoesNotExist:
        return None


@api_view(['GET'])
def get_device_types(request):
    """获取所有设备类型，按大类分组"""
    types = DeviceTypeConfig.objects.filter(is_active=1).order_by('category', 'device_name')
    categories = {}
    for dt in types:
        if dt.category not in categories:
            categories[dt.category] = []
        type_code = dt.device_type_code
        categories[dt.category].append({
            'type_code': type_code,
            'device_name': dt.device_name,
            'default_power': dt.default_power,
            'power_range': dt.power_range,
            'expected_lifespan_years': dt.expected_lifespan_years,
            'typical_daily_hours': float(dt.typical_daily_hours) if dt.typical_daily_hours else None,
        })
    return Response({'status': 'success', 'categories': categories})


@api_view(['GET'])
def get_device_type_detail(request, type_code):
    """获取设备类型详情 + 品牌选项 + 使用习惯选项"""
    try:
        dt = DeviceTypeConfig.objects.get(device_type_code=type_code, is_active=1)
    except DeviceTypeConfig.DoesNotExist:
        return Response({'status': 'error', 'message': '设备类型不存在'}, status=404)

    brands = DEVICE_BRANDS.get(type_code, DEVICE_BRANDS['_default'])
    habits = DeviceUsageHabit.objects.filter(is_active=1)

    return Response({
        'status': 'success',
        'device_type': {
            'type_code': dt.device_type_code,
            'device_name': dt.device_name,
            'category': dt.category,
            'default_power': dt.default_power,
            'power_range': dt.power_range,
            'expected_lifespan_years': dt.expected_lifespan_years,
            'typical_daily_hours': float(dt.typical_daily_hours) if dt.typical_daily_hours else None,
        },
        'brands': [{'name': b, 'bqf': BRAND_BQF_MAP.get(b, 1.0)} for b in brands],
        'habits': [{'id': h.habit_id, 'name': h.habit_name, 'code': h.habit_code} for h in habits],
    })


@api_view(['GET', 'POST'])
def user_devices(request):
    """获取/添加用户设备"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)

    household = _get_household(user)
    if not household:
        return Response({'status': 'error', 'message': '用户未绑定家庭账户'}, status=404)

    if request.method == 'GET':
        devices_list = Device.objects.filter(household=household).select_related(
            'device_type', 'usage_habit'
        ).order_by('-created_at')

        return Response({'status': 'success', 'devices': [{
            'device_id': d.device_id,
            'device_type_code': d.device_type.device_type_code,
            'device_name': d.device_type.device_name,
            'custom_name': d.custom_name or d.device_type.device_name,
            'category': d.device_type.category,
            'rated_power': d.rated_power,
            'effective_power': d.effective_power or d.rated_power,
            'brand_choice': d.brand_choice,
            'bqf': float(d.bqf),
            'purchase_date': str(d.purchase_date) if d.purchase_date else None,
            'usage_years': float(d.usage_years),
            'daily_usage_hours': float(d.daily_usage_hours),
            'usage_habit_name': d.usage_habit.habit_name if d.usage_habit else None,
            'is_active': d.is_active,
            'damage_probability': float(d.damage_probability),
            'damage_date': str(d.damage_date) if d.damage_date else None,
        } for d in devices_list]})

    elif request.method == 'POST':
        type_code = request.data.get('device_type_code')
        if not type_code:
            return Response({'status': 'error', 'message': '请选择设备类型'}, status=400)

        try:
            config = DeviceTypeConfig.objects.get(device_type_code=type_code, is_active=1)
        except DeviceTypeConfig.DoesNotExist:
            return Response({'status': 'error', 'message': '设备类型不存在'}, status=404)

        # 生成设备ID
        device_id = f"DEV_{household.household_id}_{uuid.uuid4().hex[:6]}"

        # 品牌品质系数
        brand = request.data.get('brand_choice', '普通品牌')
        bqf = BRAND_BQF_MAP.get(brand, 1.0)

        # 使用习惯
        habit_id = request.data.get('usage_habit_id')
        habit = None
        if habit_id:
            try:
                habit = DeviceUsageHabit.objects.get(habit_id=habit_id)
            except DeviceUsageHabit.DoesNotExist:
                pass

        rated_power = request.data.get('rated_power', config.default_power)
        daily_hours = float(request.data.get('daily_usage_hours', config.typical_daily_hours or 1))
        purchase_date = request.data.get('purchase_date')
        usage_years = float(request.data.get('usage_years', 0))

        # 计算有效功率
        effective_power = calc_effective_power(
            rated_power, usage_years, config.expected_lifespan_years,
            float(config.aging_power_increase_percent)
        )

        # 计算损坏概率
        damage_prob = calc_damage_probability(
            usage_years, config.expected_lifespan_years,
            float(config.weibull_beta), bqf
        )

        device = Device.objects.create(
            device_id=device_id,
            household=household,
            device_type=config,
            custom_name=request.data.get('custom_name', ''),
            rated_power=rated_power,
            brand_choice=brand,
            bqf=bqf,
            purchase_date=purchase_date,
            usage_years=usage_years,
            daily_usage_hours=daily_hours,
            usage_habit=habit,
            usage_season=request.data.get('usage_season'),
            usage_frequency=request.data.get('usage_frequency', 1),
            effective_power=effective_power,
            damage_probability=round(damage_prob, 4),
        )

        return Response({
            'status': 'success',
            'device_id': device.device_id,
            'effective_power': effective_power,
            'damage_probability': round(damage_prob, 4),
        })


@api_view(['GET', 'PUT', 'DELETE'])
def device_detail(request, device_id):
    """获取/更新/删除设备"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)

    household = _get_household(user)

    try:
        device = Device.objects.get(device_id=device_id)
    except Device.DoesNotExist:
        return Response({'status': 'error', 'message': '设备不存在'}, status=404)

    if household and device.household_id != household.household_id:
        return Response({'status': 'error', 'message': '无权操作此设备'}, status=403)

    if request.method == 'GET':
        return Response({
            'status': 'success',
            'device': {
                'device_id': device.device_id,
                'device_type_code': device.device_type.device_type_code,
                'device_name': device.device_type.device_name,
                'custom_name': device.custom_name,
                'category': device.device_type.category,
                'rated_power': device.rated_power,
                'effective_power': device.effective_power,
                'brand_choice': device.brand_choice,
                'bqf': float(device.bqf),
                'purchase_date': str(device.purchase_date) if device.purchase_date else None,
                'usage_years': float(device.usage_years),
                'daily_usage_hours': float(device.daily_usage_hours),
                'usage_habit_name': device.usage_habit.habit_name if device.usage_habit else None,
                'is_active': device.is_active,
                'damage_probability': float(device.damage_probability),
                'damage_date': str(device.damage_date) if device.damage_date else None,
            }
        })

    elif request.method == 'PUT':
        for field in ['custom_name', 'daily_usage_hours', 'usage_season', 'usage_frequency']:
            if field in request.data:
                setattr(device, field, request.data[field])
        if 'usage_habit_id' in request.data:
            try:
                device.usage_habit = DeviceUsageHabit.objects.get(habit_id=request.data['usage_habit_id'])
            except DeviceUsageHabit.DoesNotExist:
                pass
        device.save()
        return Response({'status': 'success', 'message': '已更新'})

    elif request.method == 'DELETE':
        device.delete()
        return Response({'status': 'success', 'message': '已删除'})


@api_view(['GET'])
def device_history(request, device_id):
    """查询设备月度用电历史"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)

    from ..models import ElectricityRecord
    try:
        device = Device.objects.get(device_id=device_id)
    except Device.DoesNotExist:
        return Response({'status': 'error', 'message': '设备不存在'}, status=404)

    records = ElectricityRecord.objects.filter(
        device=device
    ).order_by('-year_month')[:12]

    return Response({
        'status': 'success',
        'history': [{
            'year_month': r.year_month,
            'total_kwh': float(r.total_kwh),
            'avg_daily_kwh': float(r.avg_daily_kwh) if r.avg_daily_kwh else None,
        } for r in records]
    })
