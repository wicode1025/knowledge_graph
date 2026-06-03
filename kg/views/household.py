"""用户信息管理视图"""
import jwt
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Household, FamilyMember, HousingInfo, IncomeInfo, OptionDict, Message


def _get_user_from_request(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return User.objects.get(id=payload.get('user_id'))
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return None


@api_view(['GET'])
def get_my_household(request):
    """获取当前用户完整个人信息"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)

    try:
        household = user.household
    except Household.DoesNotExist:
        return Response({'status': 'error', 'message': '用户未绑定家庭账户'}, status=404)

    # 家庭成员
    members = FamilyMember.objects.filter(household=household).order_by('member_seq')
    # 住房信息
    housing = HousingInfo.objects.filter(household=household).first()
    # 收入信息
    income = IncomeInfo.objects.filter(household=household).order_by('-year').first()

    return Response({
        'status': 'success',
        'household': {
            'household_id': household.household_id,
            'real_name': household.real_name,
            'gender': household.gender,
            'birth_year': household.birth_year,
            'birth_month': household.birth_month,
            'id_number': household.id_number,
            'ethnicity': household.ethnicity,
            'education_level': household.education_level,
            'marital_status': household.marital_status,
            'political_status': household.political_status,
            'religion': household.religion,
            'occupation': household.occupation,
            'work_unit': household.work_unit,
            'province_code': household.province_code,
            'city_code': household.city_code,
            'district_code': household.district_code,
            'is_urban': household.is_urban,
            'address_detail': household.address_detail,
            'phone': household.phone,
            'wechat': household.wechat,
            'has_car': household.has_car,
            'has_pet': household.has_pet,
            'daily_schedule': household.daily_schedule,
            'self_health': household.self_health,
        },
        'members': [{
            'member_seq': m.member_seq,
            'relation': m.relation,
            'name': m.name,
            'gender': m.gender,
            'birth_year': m.birth_year,
            'occupation': m.occupation,
            'is_cohabit': m.is_cohabit,
        } for m in members],
        'housing': {
            'housing_type': housing.housing_type,
            'housing_area': float(housing.housing_area) if housing and housing.housing_area else None,
            'room_count': housing.room_count,
            'bedroom_count': housing.bedroom_count,
            'living_room_count': housing.living_room_count,
            'kitchen_count': housing.kitchen_count,
            'bathroom_count': housing.bathroom_count,
            'floor_level': housing.floor_level,
            'total_floors': housing.total_floors,
            'has_elevator': housing.has_elevator,
            'heating_type': housing.heating_type,
            'building_age': housing.building_age,
            'orientation': housing.orientation,
        } if housing else None,
        'income': {
            'year': income.year,
            'personal_income': float(income.personal_income) if income and income.personal_income else None,
            'household_income': float(income.household_income) if income and income.household_income else None,
            'income_source': income.income_source if income else None,
            'self_evaluated_wealth': income.self_evaluated_wealth if income else None,
        } if income else None,
    })


@api_view(['PUT'])
def update_my_household(request):
    """更新个人信息"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)

    try:
        household = user.household
    except Household.DoesNotExist:
        return Response({'status': 'error', 'message': '用户未绑定家庭账户'}, status=404)

    editable_fields = [
        'real_name', 'gender', 'birth_year', 'birth_month', 'id_number',
        'ethnicity', 'education_level', 'marital_status', 'political_status',
        'religion', 'occupation', 'work_unit', 'province_code', 'city_code',
        'district_code', 'is_urban', 'address_detail', 'phone', 'wechat',
        'has_car', 'has_pet', 'daily_schedule', 'self_health',
    ]
    for field in editable_fields:
        if field in request.data:
            setattr(household, field, request.data[field])
    household.save()

    return Response({'status': 'success', 'message': '个人信息已更新'})


@api_view(['PUT'])
def update_housing_info(request):
    """更新住房信息"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)

    try:
        household = user.household
    except Household.DoesNotExist:
        return Response({'status': 'error', 'message': '用户未绑定'}, status=404)

    housing, _ = HousingInfo.objects.get_or_create(household=household)

    editable_fields = [
        'housing_type', 'housing_area', 'room_count', 'bedroom_count',
        'living_room_count', 'kitchen_count', 'bathroom_count',
        'floor_level', 'total_floors', 'has_elevator', 'heating_type',
        'building_age', 'orientation',
    ]
    for field in editable_fields:
        if field in request.data:
            setattr(housing, field, request.data[field])
    housing.save()

    return Response({'status': 'success', 'message': '住房信息已更新'})


@api_view(['PUT'])
def update_income_info(request):
    """更新收入信息"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)

    try:
        household = user.household
    except Household.DoesNotExist:
        return Response({'status': 'error', 'message': '用户未绑定'}, status=404)

    editable_fields = ['year', 'personal_income', 'household_income', 'income_source', 'self_evaluated_wealth']
    filter_kwargs = {'household': household, 'year': request.data.get('year', 2026)}
    income, _ = IncomeInfo.objects.get_or_create(**filter_kwargs)

    for field in editable_fields:
        if field in request.data:
            setattr(income, field, request.data[field])
    income.save()

    return Response({'status': 'success', 'message': '收入信息已更新'})


@api_view(['GET', 'POST'])
def family_members(request):
    """获取/添加家庭成员"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)

    try:
        household = user.household
    except Household.DoesNotExist:
        return Response({'status': 'error', 'message': '用户未绑定'}, status=404)

    if request.method == 'GET':
        members = FamilyMember.objects.filter(household=household).order_by('member_seq')
        return Response({'status': 'success', 'members': [{
            'id': m.id,
            'member_seq': m.member_seq,
            'relation': m.relation,
            'name': m.name,
            'gender': m.gender,
            'birth_year': m.birth_year,
            'occupation': m.occupation,
            'is_cohabit': m.is_cohabit,
        } for m in members]})

    elif request.method == 'POST':
        max_seq = FamilyMember.objects.filter(household=household).count()
        member = FamilyMember.objects.create(
            household=household,
            member_seq=max_seq + 1,
            relation=request.data.get('relation', 5),
            name=request.data.get('name', ''),
            gender=request.data.get('gender'),
            birth_year=request.data.get('birth_year'),
            occupation=request.data.get('occupation'),
            is_cohabit=request.data.get('is_cohabit', 1),
        )
        return Response({'status': 'success', 'member_id': member.id})


@api_view(['PUT', 'DELETE'])
def family_member_detail(request, member_id):
    """更新/删除家庭成员"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)

    try:
        member = FamilyMember.objects.get(id=member_id, household=user.household)
    except FamilyMember.DoesNotExist:
        return Response({'status': 'error', 'message': '家庭成员不存在'}, status=404)

    if request.method == 'PUT':
        for field in ['relation', 'name', 'gender', 'birth_year', 'occupation', 'is_cohabit']:
            if field in request.data:
                setattr(member, field, request.data[field])
        member.save()
        return Response({'status': 'success', 'message': '已更新'})

    elif request.method == 'DELETE':
        member.delete()
        return Response({'status': 'success', 'message': '已删除'})


@api_view(['GET'])
def get_options(request):
    """获取所有下拉选项"""
    categories = [
        'gender', 'ethnicity', 'education', 'marital', 'political',
        'religion', 'occupation', 'schedule', 'health', 'housing_type',
        'heating', 'orientation', 'income_source', 'urban',
    ]
    result = {}
    for cat in categories:
        options = OptionDict.get_options(cat)
        if options:
            result[cat] = options
    return Response({'status': 'success', 'options': result})


@api_view(['GET'])
def get_announcements(request):
    """获取系统公告（用户端）"""
    from ..models import Announcement
    anns = Announcement.objects.filter(is_active=1).order_by('-is_pinned', '-created_at')[:5]
    return Response({'status': 'success', 'announcements': [{
        'id': a.id, 'title': a.title, 'content': a.content,
        'is_pinned': a.is_pinned, 'created_at': str(a.created_at),
    } for a in anns]})

@api_view(['GET', 'POST'])
def messages(request):
    """用户留言"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)
    try:
        household = user.household
    except Household.DoesNotExist:
        return Response({'status': 'error', 'message': '未绑定'}, status=404)

    if request.method == 'GET':
        msgs = Message.objects.filter(household=household).order_by('-created_at')[:20]
        return Response({'status': 'success', 'messages': [{
            'id': m.id, 'content': m.content, 'is_read': m.is_read,
            'reply': m.reply, 'replied_at': str(m.replied_at) if m.replied_at else None,
            'created_at': str(m.created_at),
        } for m in msgs]})

    if request.method == 'POST':
        content = request.data.get('content', '').strip()
        if not content:
            return Response({'status': 'error', 'message': '内容不能为空'}, status=400)
        m = Message.objects.create(household=household, content=content)
        return Response({'status': 'success', 'id': m.id})


@api_view(['DELETE'])
def withdraw_message(request, msg_id):
    """用户撤回留言"""
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)
    try:
        household = user.household
    except Household.DoesNotExist:
        return Response({'status': 'error', 'message': '未绑定'}, status=404)
    try:
        m = Message.objects.get(id=msg_id, household=household)
    except Message.DoesNotExist:
        return Response({'status': 'error', 'message': '留言不存在或无权操作'}, status=404)
    # 只能撤回管理员未回复的留言
    if m.reply:
        return Response({'status': 'error', 'message': '管理员已回复，无法撤回'}, status=400)
    m.delete()
    return Response({'status': 'success', 'message': '已撤回'})
