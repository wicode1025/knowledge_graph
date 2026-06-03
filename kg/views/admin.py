"""管理员视图"""
import jwt
from datetime import date
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Household, Device, Bill, RepairOrder, SystemMonth, Announcement, ElectricityRecord, HousingInfo, IncomeInfo, FamilyMember, Notice


def _get_admin_user(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(id=payload.get('user_id'))
        if not user.is_staff:
            return None
        return user
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return None


@api_view(['GET'])
def admin_dashboard(request):
    """管理员仪表盘"""
    user = _get_admin_user(request)
    if not user:
        return Response({'status': 'error', 'message': '无权限'}, status=403)

    sm = SystemMonth.get_current()
    total_users = Household.objects.count()
    total_devices = Device.objects.count()
    active_devices = Device.objects.filter(is_active=1).count()
    damaged_devices = Device.objects.filter(is_active=0).count()
    pending_repairs = RepairOrder.objects.filter(status=1).count()
    current_bills = Bill.objects.filter(bill_month=sm.year_month)
    bills_paid = current_bills.filter(status=2).count()
    bills_total = current_bills.count()

    return Response({
        'status': 'success',
        'stats': {
            'system_month': sm.year_month,
            'total_users': total_users,
            'total_devices': total_devices,
            'active_devices': active_devices,
            'damaged_devices': damaged_devices,
            'pending_repairs': pending_repairs,
            'bills_collected': f'{bills_paid}/{bills_total}',
            'unit_price': float(sm.unit_price),
            'total_months_elapsed': sm.total_months_elapsed,
        }
    })


@api_view(['GET'])
def admin_user_list(request):
    """管理员查看用户列表"""
    user = _get_admin_user(request)
    if not user:
        return Response({'status': 'error', 'message': '无权限'}, status=403)

    households = Household.objects.select_related('user').all().order_by('household_id')
    return Response({
        'status': 'success',
        'users': [{
            'household_id': h.household_id,
            'username': h.user.username,
            'real_name': h.real_name,
            'phone': h.phone,
            'education_level': h.education_level,
            'occupation': h.occupation,
            'device_count': Device.objects.filter(household=h).count(),
            'created_at': str(h.created_at),
        } for h in households]
    })


@api_view(['GET'])
def admin_repair_orders(request):
    """管理员查看所有维修工单"""
    user = _get_admin_user(request)
    if not user:
        return Response({'status': 'error', 'message': '无权限'}, status=403)

    status_filter = request.query_params.get('status')
    orders = RepairOrder.objects.select_related(
        'household', 'device', 'device__device_type'
    ).order_by('-created_at')

    if status_filter:
        orders = orders.filter(status=int(status_filter))

    status_map = {1: '待审核', 2: '已派单', 3: '维修中', 4: '已完成(待缴费)', 5: '已完成(已缴费)', 6: '已取消'}
    return Response({
        'status': 'success',
        'orders': [{
            'order_id': o.order_id,
            'household_id': o.household.household_id,
            'household_name': o.household.real_name,
            'device_name': o.device.custom_name or o.device.device_type.device_name,
            'fault_description': o.fault_description[:100],
            'status': o.status,
            'status_text': status_map.get(o.status, '未知'),
            'repair_cost': float(o.repair_cost) if o.repair_cost else None,
            'technician_name': o.technician_name,
            'created_at': str(o.created_at),
        } for o in orders]
    })


@api_view(['POST'])
def assign_repair(request, order_id):
    """管理员派单"""
    user = _get_admin_user(request)
    if not user:
        return Response({'status': 'error', 'message': '无权限'}, status=403)

    try:
        o = RepairOrder.objects.get(order_id=order_id)
    except RepairOrder.DoesNotExist:
        return Response({'status': 'error', 'message': '报修单不存在'}, status=404)

    technician = request.data.get('technician_name', '维修师傅')
    o.technician_name = technician
    o.status = 2  # 已派单
    o.save()

    return Response({'status': 'success', 'message': f'已派单给{technician}'})


@api_view(['POST'])
def complete_repair(request, order_id):
    """管理员完成维修"""
    user = _get_admin_user(request)
    if not user:
        return Response({'status': 'error', 'message': '无权限'}, status=403)

    try:
        o = RepairOrder.objects.get(order_id=order_id)
    except RepairOrder.DoesNotExist:
        return Response({'status': 'error', 'message': '报修单不存在'}, status=404)

    cost = request.data.get('repair_cost', 0)
    result = request.data.get('repair_result', '已修复')

    o.repair_cost = cost
    o.repair_result = result
    o.completed_date = date.today()
    o.status = 4  # 已完成(待缴费)
    o.save()

    return Response({
        'status': 'success',
        'message': f'维修完成，费用¥{cost}将计入下月账单'
    })

@api_view(['GET', 'POST'])
def announcements(request):
    """管理公告"""
    if request.method == 'GET':
        user = _get_admin_user(request)
        anns = Announcement.objects.all().order_by('-created_at')
        return Response({'status': 'success', 'announcements': [{
            'id': a.id, 'title': a.title, 'content': a.content,
            'is_pinned': a.is_pinned, 'is_active': a.is_active,
            'created_at': str(a.created_at),
        } for a in anns]})

    if request.method == 'POST':
        user = _get_admin_user(request)
        if not user:
            return Response({'status': 'error', 'message': '无权限'}, status=403)
        a = Announcement.objects.create(
            title=request.data.get('title', ''),
            content=request.data.get('content', ''),
            is_pinned=request.data.get('is_pinned', 0),
            created_by=user,
        )
        return Response({'status': 'success', 'id': a.id})


@api_view(['PUT', 'DELETE'])
def announcement_detail(request, ann_id):
    user = _get_admin_user(request)
    if not user:
        return Response({'status': 'error', 'message': '无权限'}, status=403)
    try:
        a = Announcement.objects.get(id=ann_id)
    except Announcement.DoesNotExist:
        return Response({'status': 'error', 'message': '不存在'}, status=404)
    if request.method == 'PUT':
        if 'title' in request.data: a.title = request.data['title']
        if 'content' in request.data: a.content = request.data['content']
        if 'is_pinned' in request.data: a.is_pinned = request.data['is_pinned']
        if 'is_active' in request.data: a.is_active = request.data['is_active']
        a.save()
        return Response({'status': 'success'})
    if request.method == 'DELETE':
        a.delete()
        return Response({'status': 'success'})

@api_view(['GET'])
def admin_messages(request):
    """管理员查看所有留言"""
    user = _get_admin_user(request)
    if not user:
        return Response({'status': 'error', 'message': '无权限'}, status=403)
    from ..models import Message
    msgs = Message.objects.select_related('household').order_by('-created_at')[:50]
    return Response({'status': 'success', 'messages': [{
        'id': m.id, 'household_id': m.household.household_id,
        'household_name': m.household.real_name,
        'content': m.content, 'is_read': m.is_read,
        'reply': m.reply, 'replied_at': str(m.replied_at) if m.replied_at else None,
        'created_at': str(m.created_at),
    } for m in msgs]})


@api_view(['POST'])
def reply_message(request, msg_id):
    """管理员回复留言"""
    user = _get_admin_user(request)
    if not user:
        return Response({'status': 'error', 'message': '无权限'}, status=403)
    from ..models import Message
    from datetime import datetime
    try:
        m = Message.objects.get(id=msg_id)
    except Message.DoesNotExist:
        return Response({'status': 'error', 'message': '不存在'}, status=404)
    m.reply = request.data.get('reply', '')
    m.replied_by = user
    m.replied_at = datetime.now()
    m.is_read = 1
    m.save()
    return Response({'status': 'success'})

@api_view(['DELETE'])
def delete_message(request, msg_id):
    """管理员删除留言"""
    user = _get_admin_user(request)
    if not user:
        return Response({'status': 'error', 'message': '无权限'}, status=403)
    from ..models import Message
    try:
        m = Message.objects.get(id=msg_id)
        m.delete()
        return Response({'status': 'success'})
    except Message.DoesNotExist:
        return Response({'status': 'error', 'message': '不存在'}, status=404)

@api_view(['GET'])
def admin_user_detail(request, household_id):
    """管理员查看用户完整详情"""
    user = _get_admin_user(request)
    if not user:
        return Response({'status': 'error', 'message': '无权限'}, status=403)
    try:
        h = Household.objects.get(household_id=household_id)
    except Household.DoesNotExist:
        return Response({'status': 'error', 'message': '不存在'}, status=404)

    devices = Device.objects.filter(household=h).select_related('device_type','usage_habit')
    bills_qs = Bill.objects.filter(household=h)
    bills = bills_qs.order_by('-bill_month')[:12]
    records = ElectricityRecord.objects.filter(household=h)
    housing = HousingInfo.objects.filter(household=h).first()
    income = IncomeInfo.objects.filter(household=h).order_by('-year').first()
    family = FamilyMember.objects.filter(household=h).order_by('member_seq')
    notices = Notice.objects.filter(household=h).order_by('-created_at')[:5]
    repair_orders = RepairOrder.objects.filter(household=h).order_by('-created_at')[:5]

    # 能耗
    total_kwh = sum(float(r.total_kwh) for r in records)
    months = records.values('year_month').distinct().count() or 1
    avg_kwh = round(total_kwh / months, 1)

    return Response({'status':'success','user':{
        'household_id':h.household_id,'real_name':h.real_name,'username':h.user.username,
        'gender':h.gender,'birth_year':h.birth_year,'birth_month':h.birth_month,
        'education':h.education_level,'marital':h.marital_status,'occupation':h.occupation,
        'phone':h.phone,'address':h.address_detail,'is_urban':h.is_urban,
        'schedule':h.daily_schedule,'health':h.self_health,
        'created_at':str(h.created_at),
        'housing':{'type':housing.housing_type,'area':float(housing.housing_area) if housing and housing.housing_area else None,'bedroom':housing.bedroom_count if housing else 0,'living':housing.living_room_count if housing else 0,'floor':housing.floor_level if housing else None,'total_floors':housing.total_floors if housing else None,'elevator':housing.has_elevator if housing else 0,'heating':housing.heating_type if housing else None,'orientation':housing.orientation if housing else None} if housing else None,
        'income':{'personal':float(income.personal_income) if income and income.personal_income else None,'household':float(income.household_income) if income and income.household_income else None,'source':income.income_source if income else None} if income else None,
        'avg_kwh':avg_kwh,'total_kwh':round(total_kwh,1),'device_count':devices.count(),'damaged':devices.filter(is_active=0).count(),
        'bills':bills_qs.count(),'paid_bills':bills_qs.filter(status=2).count(),
        'devices':[{'id':d.device_id,'name':d.custom_name or d.device_type.device_name,'type':d.device_type.category,'power':d.effective_power or d.rated_power,'years':float(d.usage_years),'damage_prob':float(d.damage_probability),'is_active':d.is_active,'brand':d.brand_choice,'habit':d.usage_habit.habit_name if d.usage_habit else ''} for d in devices],
        'recent_bills':[{'month':b.bill_month,'kwh':float(b.total_kwh),'amount':float(b.total_amount),'status':'已缴' if b.status==2 else '未缴'} for b in bills[:6]],
        'family':[{'name':m.name,'relation':m.relation} for m in family],
    }})

@api_view(['POST'])
def admin_create_user(request):
    """管理员创建新用户"""
    user = _get_admin_user(request)
    if not user:
        return Response({'status': 'error', 'message': '无权限'}, status=403)
    uname = request.data.get('username','').strip()
    pwd = request.data.get('password','pass123456')
    if not uname:
        return Response({'status': 'error', 'message': '用户名不能为空'}, status=400)
    if User.objects.filter(username=uname).exists():
        return Response({'status': 'error', 'message': '用户名已存在'}, status=400)
    u = User.objects.create_user(username=uname, password=pwd)
    idx = Household.objects.count() + 1
    h = Household.objects.create(household_id=f'H{idx:04d}', user=u, real_name=request.data.get('real_name', uname))
    return Response({'status': 'success', 'household_id': h.household_id})


@api_view(['PUT'])
def admin_edit_user(request, household_id):
    """管理员编辑用户"""
    user = _get_admin_user(request)
    if not user:
        return Response({'status': 'error', 'message': '无权限'}, status=403)
    try:
        h = Household.objects.get(household_id=household_id)
    except Household.DoesNotExist:
        return Response({'status': 'error', 'message': '不存在'}, status=404)
    fields = ['real_name','gender','birth_year','birth_month','education_level','marital_status',
              'political_status','religion','occupation','work_unit','phone','address_detail',
              'is_urban','daily_schedule','self_health']
    for f in fields:
        if f in request.data: setattr(h, f, request.data[f])
    h.save()
    return Response({'status': 'success'})


@api_view(['DELETE'])
def admin_delete_user(request, household_id):
    """管理员删除用户"""
    user = _get_admin_user(request)
    if not user:
        return Response({'status': 'error', 'message': '无权限'}, status=403)
    try:
        h = Household.objects.get(household_id=household_id)
    except Household.DoesNotExist:
        return Response({'status': 'error', 'message': '不存在'}, status=404)
    h.user.delete()
    return Response({'status': 'success'})
