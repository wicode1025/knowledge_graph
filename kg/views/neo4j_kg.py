"""知识图谱视图 V3 - 分层架构 + 丰富详情"""
import jwt, json
from datetime import date
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Household, Device, ElectricityRecord, Bill, SystemMonth, HousingInfo, IncomeInfo, FamilyMember


def _get_user_from_request(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return User.objects.get(id=payload.get('user_id'))
    except Exception:
        return None


class DEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal): return float(o)
        if isinstance(o, date): return str(o)
        return super().default(o)


@api_view(['GET'])
def get_user_kg(request):
    user = _get_user_from_request(request)
    if not user:
        return Response({'status': 'error', 'message': '未登录'}, status=401)
    try: household = user.household
    except Household.DoesNotExist:
        return Response({'status': 'error', 'message': '未绑定'}, status=404)

    hid = household.household_id

    # 能耗计算
    records = ElectricityRecord.objects.filter(household=household).order_by('year_month')
    total_kwh = sum(float(r.total_kwh) for r in records)
    months = records.values('year_month').distinct().count() or 1
    avg_kwh = round(total_kwh / months, 1)
    if avg_kwh < 100: el_lv, el_color = '节能型', '#67c23a'
    elif avg_kwh < 250: el_lv, el_color = '普通型', '#5470c6'
    elif avg_kwh < 500: el_lv, el_color = '摆渡型', '#e6a23c'
    else: el_lv, el_color = '高耗能型', '#e74c3c'

    # 月度趋势数据
    monthly_trend = []
    ym_totals = {}
    for r in records:
        ym_totals[r.year_month] = ym_totals.get(r.year_month, 0) + float(r.total_kwh)
    for ym in sorted(ym_totals.keys())[-12:]:
        monthly_trend.append({'month': ym, 'kwh': round(ym_totals[ym], 1)})

    # 设备数据
    devices = Device.objects.filter(household=household).select_related('device_type', 'usage_habit')
    device_count = devices.count()
    active_count = devices.filter(is_active=1).count()
    damaged_count = device_count - active_count

    # 设备类别分布
    cat_dist = {}
    device_colors = {
        '空气调节': '#a8d8ea', '厨房电器': '#fce4b8', '清洁卫生': '#f8cecc',
        '影音娱乐': '#d5c4e1', '办公数码': '#b5d8c3', '照明': '#f9f3c1',
    }
    for d in devices:
        cat = d.device_type.category
        cat_dist[cat] = cat_dist.get(cat, 0) + 1
    device_pie = [{'name': k, 'value': v, 'color': device_colors.get(k, '#ccc')} for k, v in cat_dist.items()]

    # 高危设备
    high_risk = [d for d in devices if float(d.damage_probability) > 0.5]

    # 账单
    all_bills = Bill.objects.filter(household=household).order_by('-bill_month')
    bills = all_bills[:6]
    paid_count = all_bills.filter(status=2).count()
    total_bills = all_bills.count()

    # 缴费趋势
    bill_trend = []
    for b in all_bills.order_by('bill_month')[:12]:
        bill_trend.append({
            'month': b.bill_month, 'amount': float(b.total_amount),
            'paid': b.status == 2,
        })

    # 住房
    housing = HousingInfo.objects.filter(household=household).first()
    income = IncomeInfo.objects.filter(household=household).order_by('-year').first()
    family = FamilyMember.objects.filter(household=household).order_by('member_seq')

    # ====== 构建节点 ======
    nodes, links = [], []

    # L0: 用户中心节点
    user_info = {
        'gender': ol(household.gender, 'gender'),
        'birth': str(household.birth_year) if household.birth_year else '--',
        'education': ol(household.education_level, 'education'),
        'marital': ol(household.marital_status, 'marital'),
        'occupation': ol(household.occupation, 'occupation'),
        'urban': ol(household.is_urban, 'urban'),
        'schedule': ol(household.daily_schedule, 'schedule'),
        'health': ol(household.self_health, 'health'),
        'political': ol(household.political_status, 'political'),
        'religion': ol(household.religion, 'religion'),
        'phone': household.phone or '--',
        'work_unit': household.work_unit or '--',
        'address': household.address_detail or '--',
    }
    nodes.append({
        'id': hid, 'name': household.real_name, 'category': 'user',
        'symbolSize': 70, 'group': 'center',
        'itemStyle': {'color': '#3b82f6'},
        'detail': {
            'type': 'user', 'name': household.real_name,
            'info': user_info,
            'energy': {'level': el_lv, 'avg_kwh': avg_kwh, 'color': el_color},
            'trend': monthly_trend,
            'housing': {
                'type': ol(housing.housing_type, 'housing_type') if housing else '--',
                'area': float(housing.housing_area) if housing and housing.housing_area else None,
                'bedroom': housing.bedroom_count if housing else 0,
                'living': housing.living_room_count if housing else 0,
                'kitchen': housing.kitchen_count if housing else 0,
                'bathroom': housing.bathroom_count if housing else 0,
                'floor': housing.floor_level if housing else None,
                'total_floors': housing.total_floors if housing else None,
                'elevator': housing.has_elevator if housing else 0,
                'heating': ol(housing.heating_type, 'heating') if housing else '--',
                'orientation': ol(housing.orientation, 'orientation') if housing else '--',
                'building_age': housing.building_age if housing else None,
            } if housing else None,
            'income': {
                'personal': float(income.personal_income) if income and income.personal_income else None,
                'household': float(income.household_income) if income and income.household_income else None,
                'source': ol(income.income_source, 'income_source') if income else '--',
                'self_rating': income.self_evaluated_wealth if income else None,
            } if income else None,
            'members': [{'name': m.name, 'relation': {2:'配偶',3:'子女',4:'父母',5:'岳父母/公婆',6:'兄弟姐妹',7:'其他'}.get(m.relation,''), 'cohabit': m.is_cohabit} for m in family],
            'stats': {'devices': device_count, 'active': active_count, 'damaged': damaged_count, 'bills': total_bills, 'paid': paid_count},
        },
    })

    # L1: 设备管理大类
    cd_id = f'{hid}_devices'
    nodes.append({
        'id': cd_id, 'name': f'设备管理 ({device_count}台)', 'category': 'category',
        'symbolSize': 56, 'group': 'category',
        'itemStyle': {'color': '#ebf0f5', 'borderColor': '#c8d6e5', 'borderWidth': 2, 'borderRadius': 8},
        'detail': {
            'type': 'category', 'subtype': 'devices', 'name': '设备管理',
            'total': device_count, 'active': active_count, 'damaged': damaged_count,
            'pie_data': device_pie,
            'high_risk': [{'name': d.custom_name or d.device_type.device_name, 'prob': float(d.damage_probability)} for d in high_risk],
        },
    })
    links.append({'source': hid, 'target': cd_id, 'value': ''})

    for d in devices:
        did = d.device_id
        cat = d.device_type.category
        pwr = d.effective_power or d.rated_power
        # 设备月度用电
        dev_records = ElectricityRecord.objects.filter(device=d).order_by('-year_month')[:6]
        dev_kwh = [{'month': r.year_month, 'kwh': float(r.total_kwh)} for r in reversed(dev_records)]
        nodes.append({
            'id': did, 'name': (d.custom_name or d.device_type.device_name),
            'category': 'device', 'symbolSize': min(24 + pwr / 50, 44), 'group': cd_id, 'hidden': True,
            'itemStyle': {'color': device_colors.get(cat, '#ccc')},
            'detail': {
                'type': 'device', 'name': d.custom_name or d.device_type.device_name,
                'category': cat, 'power': pwr, 'rated_power': d.rated_power,
                'usage_years': float(d.usage_years), 'hours': float(d.daily_usage_hours),
                'damage_prob': float(d.damage_probability), 'is_active': d.is_active,
                'brand': d.brand_choice, 'lifespan': d.device_type.expected_lifespan_years,
                'habit': d.usage_habit.habit_name if d.usage_habit else '',
                'monthly_kwh': dev_kwh,
                'damage_pred': calc_damage_pred(d),
            },
        })
        links.append({'source': cd_id, 'target': did, 'value': ''})

    # L1: 用电特征大类
    ce_id = f'{hid}_energy'
    nodes.append({
        'id': ce_id, 'name': '用电特征', 'category': 'category',
        'symbolSize': 56, 'group': 'category',
        'itemStyle': {'color': '#ebf0f5', 'borderColor': '#c8d6e5', 'borderWidth': 2, 'borderRadius': 8},
        'detail': {
            'type': 'category', 'subtype': 'energy', 'name': '用电特征',
            'level': el_lv, 'avg_kwh': avg_kwh, 'total_kwh': round(total_kwh, 1),
            'months': months, 'level_color': el_color,
            'trend': monthly_trend,
            'max_month': max(ym_totals.values()) if ym_totals else 0,
            'min_month': min(ym_totals.values()) if ym_totals else 0,
            'std_kwh': round(calc_std(list(ym_totals.values())), 1) if ym_totals else 0,
        },
    })
    links.append({'source': hid, 'target': ce_id, 'value': ''})

    el_node_id = f'{hid}_el'
    nodes.append({
        'id': el_node_id, 'name': f'能耗: {el_lv}', 'category': 'sub',
        'symbolSize': 26, 'group': ce_id, 'hidden': True,
        'itemStyle': {'color': el_color},
        'detail': {'type': 'tag', 'name': '能耗等级', 'value': el_lv, 'avg_kwh': avg_kwh},
    })
    links.append({'source': ce_id, 'target': el_node_id, 'value': ''})

    kwh_node_id = f'{hid}_kwh'
    nodes.append({
        'id': kwh_node_id, 'name': f'月均 {avg_kwh} kWh', 'category': 'sub',
        'symbolSize': 26, 'group': ce_id, 'hidden': True,
        'itemStyle': {'color': '#91c7ae'},
        'detail': {'type': 'kwh', 'name': '月均用电', 'avg_kwh': avg_kwh, 'total_kwh': round(total_kwh, 1), 'months': months, 'trend': monthly_trend, 'max': max(ym_totals.values()) if ym_totals else 0, 'min': min(ym_totals.values()) if ym_totals else 0},
    })
    links.append({'source': ce_id, 'target': kwh_node_id, 'value': ''})

    if monthly_trend:
        last = monthly_trend[-1]
        last_id = f'{hid}_last_kwh'
        nodes.append({
            'id': last_id, 'name': f'上月 {last["kwh"]:.1f} kWh', 'category': 'sub',
            'symbolSize': 26, 'group': ce_id, 'hidden': True,
            'itemStyle': {'color': '#d5c4e1'},
            'detail': {'type': 'kwh', 'name': '上月用电', 'value': last['kwh'], 'month': last['month']},
        })
        links.append({'source': ce_id, 'target': last_id, 'value': ''})

    # L1: 账单记录大类
    cb_id = f'{hid}_bills'
    nodes.append({
        'id': cb_id, 'name': f'账单记录 ({total_bills}条)', 'category': 'category',
        'symbolSize': 56, 'group': 'category',
        'itemStyle': {'color': '#ebf0f5', 'borderColor': '#c8d6e5', 'borderWidth': 2, 'borderRadius': 8},
        'detail': {
            'type': 'category', 'subtype': 'bills', 'name': '账单记录',
            'total': total_bills, 'paid': paid_count, 'unpaid': total_bills - paid_count,
            'total_cost': round(sum(float(b.total_amount) for b in all_bills), 2),
            'repair_cost': round(sum(float(b.repair_cost or 0) for b in all_bills), 2),
            'pay_rate': round(paid_count / total_bills * 100, 1) if total_bills > 0 else 0,
            'credit': '良好' if not all_bills.filter(warning_flag=1).exists() else '较差',
            'trend': bill_trend,
        },
    })
    links.append({'source': hid, 'target': cb_id, 'value': ''})

    for b in bills:
        bid = f'bill_{b.bill_id[-8:]}'
        paid = b.status == 2
        nodes.append({
            'id': bid, 'name': f'{b.bill_month} ¥{float(b.total_amount):.0f}',
            'category': 'sub', 'symbolSize': 24, 'group': cb_id, 'hidden': True,
            'itemStyle': {'color': '#d4edda' if paid else '#fff3cd'},
            'detail': {
                'type': 'bill', 'month': b.bill_month,
                'kwh': float(b.total_kwh), 'elec_cost': float(b.electricity_cost),
                'repair_cost': float(b.repair_cost or 0), 'total': float(b.total_amount),
                'unit_price': float(b.unit_price), 'status': '已缴' if paid else '未缴',
                'paid_date': str(b.paid_date) if b.paid_date else None,
                'due_date': str(b.due_date) if b.due_date else None,
                'warning': b.warning_flag == 1,
            },
        })
        links.append({'source': cb_id, 'target': bid, 'value': ''})

    # L1: 家庭信息大类
    cf_id = f'{hid}_family'
    nodes.append({
        'id': cf_id, 'name': '家庭信息', 'category': 'category',
        'symbolSize': 56, 'group': 'category',
        'itemStyle': {'color': '#ebf0f5', 'borderColor': '#c8d6e5', 'borderWidth': 2, 'borderRadius': 8},
        'detail': {
            'type': 'category', 'subtype': 'family', 'name': '家庭信息',
            'members': [{'name': m.name, 'relation': {2:'配偶',3:'子女',4:'父母',5:'岳父母/公婆',6:'兄弟姐妹',7:'其他'}.get(m.relation,''), 'cohabit': m.is_cohabit} for m in family],
        },
    })
    links.append({'source': hid, 'target': cf_id, 'value': ''})

    if housing:
        h_id = f'{hid}_house'
        nodes.append({
            'id': h_id, 'name': f'住房: {ol(housing.housing_type,"housing_type") or "--"}',
            'category': 'sub', 'symbolSize': 26, 'group': cf_id, 'hidden': True,
            'itemStyle': {'color': '#f9f3c1'},
            'detail': {
                'type': 'housing',
                'housing_type': ol(housing.housing_type, 'housing_type'),
                'area': float(housing.housing_area) if housing.housing_area else None,
                'bedroom': housing.bedroom_count, 'living': housing.living_room_count,
                'kitchen': housing.kitchen_count, 'bathroom': housing.bathroom_count,
                'floor': housing.floor_level, 'total_floors': housing.total_floors,
                'elevator': housing.has_elevator, 'heating': ol(housing.heating_type, 'heating'),
                'orientation': ol(housing.orientation, 'orientation'),
                'building_age': housing.building_age,
            },
        })
        links.append({'source': cf_id, 'target': h_id, 'value': ''})

    if income:
        inc_id = f'{hid}_income'
        inc_name = f'年收入 ¥{float(income.personal_income):.0f}' if income.personal_income else '收入未填'
        nodes.append({
            'id': inc_id, 'name': inc_name, 'category': 'sub',
            'symbolSize': 26, 'group': cf_id, 'hidden': True,
            'itemStyle': {'color': '#d5c4e1'},
            'detail': {
                'type': 'income',
                'personal': float(income.personal_income) if income.personal_income else None,
                'household': float(income.household_income) if income.household_income else None,
                'source': ol(income.income_source, 'income_source') if income else '--',
                'self_rating': income.self_evaluated_wealth if income else None,
            },
        })
        links.append({'source': cf_id, 'target': inc_id, 'value': ''})

    # L1: 画像标签大类
    ct_id = f'{hid}_tags'
    nodes.append({
        'id': ct_id, 'name': '画像标签', 'category': 'category',
        'symbolSize': 56, 'group': 'category',
        'itemStyle': {'color': '#ebf0f5', 'borderColor': '#c8d6e5', 'borderWidth': 2, 'borderRadius': 8},
        'detail': {
            'type': 'category', 'subtype': 'tags', 'name': '画像标签',
            'tags': [{'name': '能耗等级', 'value': el_lv}, {'name': '缴费信用', 'value': '良好' if not all_bills.filter(warning_flag=1).exists() else '较差'}, {'name': '设备数', 'value': f'{device_count}台'}],
            'radar': {
                'indicator': [{'name':'用电量','max':500},{'name':'设备数','max':15},{'name':'收入','max':300000},{'name':'面积','max':200},{'name':'缴费率','max':100},{'name':'活跃度','max':10}],
                'user_values': [avg_kwh, device_count, float(income.personal_income or 0), float(housing.housing_area or 0) if housing else 0, round(paid_count/total_bills*100,1) if total_bills>0 else 0, device_count],
                'avg_values': [180, 7, 100000, 100, 60, 6],
            },
        },
    })
    links.append({'source': hid, 'target': ct_id, 'value': ''})

    te_id = f'{hid}_tag_el'
    nodes.append({
        'id': te_id, 'name': f'标签: {el_lv}', 'category': 'sub',
        'symbolSize': 22, 'group': ct_id, 'hidden': True,
        'itemStyle': {'color': '#e8daef'},
        'detail': {'type': 'tag', 'name': '能耗等级', 'value': el_lv, 'avg_kwh': avg_kwh, 'range': '100-250 kWh'},
    })
    links.append({'source': ct_id, 'target': te_id, 'value': ''})

    return Response({
        'status': 'success',
        'nodes': nodes, 'links': links,
        'summary': {'energy_level': el_lv, 'avg_monthly_kwh': avg_kwh, 'device_count': device_count, 'bill_count': total_bills, 'paid_count': paid_count},
    })


def ol(val, cat):
    if val is None or val == '': return None
    from ..models import OptionDict
    for o in OptionDict.get_options(cat):
        if o['item_key'] == str(val): return o['item_value']
    return str(val)


def calc_std(vals):
    if len(vals) < 2: return 0
    avg = sum(vals) / len(vals)
    return (sum((v - avg) ** 2 for v in vals) / len(vals)) ** 0.5


def calc_damage_pred(device):
    """未来12个月损坏概率预测"""
    result = []
    yrs = float(device.usage_years)
    lifespan = device.device_type.expected_lifespan_years
    beta = float(device.device_type.weibull_beta)
    bqf = float(device.bqf)
    import math
    for i in range(13):
        t = yrs + i / 12.0
        eta = lifespan * 1.2 * bqf
        prob = 1 - math.exp(-((t / eta) ** beta))
        result.append({'month': i, 'prob': round(prob, 4)})
    return result


@api_view(['GET'])
def get_kg_full_graph(request):
    user = _get_user_from_request(request)
    if not user or not user.is_staff:
        return Response({'status': 'error', 'message': '无权限'}, status=403)
    from ..models import Bill, IncomeInfo, HousingInfo
    households = Household.objects.exclude(user__is_staff=True)
    devices_qs = Device.objects.select_related('device_type', 'household').exclude(household__user__is_staff=True)
    all_bills = Bill.objects.all()
    recs_qs = ElectricityRecord.objects.all()

    el_colors = {'节能型':'#67c23a','普通型':'#5470c6','摆渡型':'#e6a23c','高耗能型':'#e74c3c'}
    dev_colors = {'空气调节':'#a8d8ea','厨房电器':'#fce4b8','清洁卫生':'#f8cecc','影音娱乐':'#d5c4e1','办公数码':'#b5d8c3','照明':'#f9f3c1'}

    nodes, links = [], []
    energy_dist = {'节能型':0,'普通型':0,'摆渡型':0,'高耗能型':0}
    cat_dist, high_risk = {}, []
    warning_users = 0; total_paid = 0; total_unpaid = 0

    for h in households:
        recs = recs_qs.filter(household=h)
        total_kwh = sum(float(r.total_kwh) for r in recs)
        months = recs.values('year_month').distinct().count() or 1
        avg_kwh = round(total_kwh / months, 1)
        if avg_kwh<100: el='节能型'
        elif avg_kwh<250: el='普通型'
        elif avg_kwh<500: el='摆渡型'
        else: el='高耗能型'
        energy_dist[el] += 1

        hd = devices_qs.filter(household=h); dc = hd.count(); ac = hd.filter(is_active=1).count()
        hb = all_bills.filter(household=h); bc = hb.count(); paid = hb.filter(status=2).count()
        if hb.filter(warning_flag=1).exists(): warning_users += 1
        total_paid += paid; total_unpaid += (bc - paid)

        sz = min(max(40, avg_kwh/5), 70)
        inc = IncomeInfo.objects.filter(household=h).order_by('-year').first()
        hse = HousingInfo.objects.filter(household=h).first()

        nodes.append({'id':h.household_id,'name':h.real_name,'category':'user','symbolSize':sz,'group':'user','itemStyle':{'color':el_colors[el]},'detail':{'type':'user','name':h.real_name,'energy_level':el,'avg_kwh':avg_kwh,'device_count':dc,'active':ac,'damaged':dc-ac,'bills':bc,'paid':paid,'warning':hb.filter(warning_flag=1).exists(),'income':float(inc.personal_income) if inc and inc.personal_income else None,'area':float(hse.housing_area) if hse and hse.housing_area else None,'household_id':h.household_id}})

        for d in hd:
            cat = d.device_type.category; cat_dist[cat]=cat_dist.get(cat,0)+1
            pwr = d.effective_power or d.rated_power; dp = float(d.damage_probability)
            if dp>0.5: high_risk.append({'name':d.custom_name or d.device_type.device_name,'prob':dp,'user':h.real_name})
            nodes.append({'id':d.device_id,'name':d.custom_name or d.device_type.device_name,'category':'device','symbolSize':20,'group':h.household_id,'itemStyle':{'color':dev_colors.get(cat,'#ccc'),'borderColor':'#ff4d4f' if not d.is_active else '#fff','borderWidth':2 if not d.is_active else 1},'detail':{'type':'device','name':d.custom_name or d.device_type.device_name,'category':cat,'power':pwr,'usage_years':float(d.usage_years),'damage_prob':dp,'is_active':d.is_active,'household_name':h.real_name}})
            links.append({'source':h.household_id,'target':d.device_id,'value':''})

    return Response({'status':'success','nodes':nodes,'links':links,'stats':{'total_users':households.count(),'total_devices':devices_qs.count(),'total_bills':all_bills.count(),'paid_bills':total_paid,'unpaid_bills':total_unpaid,'warning_users':warning_users,'energy_dist':energy_dist,'device_cat_dist':{k:v for k,v in sorted(cat_dist.items(),key=lambda x:-x[1])},'high_risk':sorted(high_risk,key=lambda x:-x['prob'])[:5]}})


@api_view(['POST'])
def sync_to_neo4j(request):
    user = _get_user_from_request(request)
    if not user or not user.is_staff:
        return Response({'status': 'error', 'message': '仅管理员'}, status=403)
    try:
        from ..neo4j_sync import sync_all
        return Response({'status': 'success', **sync_all()})
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)
