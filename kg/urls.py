"""知识图谱应用 URL 路由 - V2.0"""
from django.urls import path
from .views import auth, system, household

# 延迟导入避免模块不存在时崩溃
try:
    from .views import devices, electricity, billing, repair
    from .views import admin as admin_views
    from .views import neo4j_kg, clustering as cluster_views
    _has_full_views = True
except ImportError:
    _has_full_views = False

urlpatterns = [
    # ==================== 认证 ====================
    path('auth/login/', auth.auth_login, name='auth_login'),
    path('auth/register/', auth.auth_register, name='auth_register'),
    path('auth/logout/', auth.auth_logout, name='auth_logout'),
    path('auth/verify/', auth.auth_verify, name='auth_verify'),

    # ==================== 系统月份 ====================
    path('system/month/', system.get_system_month, name='system_month'),
    path('system/month/advance/', system.advance_system_month, name='advance_month'),

    # ==================== 用户信息 ====================
    path('household/mine/', household.get_my_household, name='my_household'),
    path('household/mine/update/', household.update_my_household, name='update_household'),
    path('household/housing/update/', household.update_housing_info, name='update_housing'),
    path('household/income/update/', household.update_income_info, name='update_income'),
    path('household/members/', household.family_members, name='family_members'),
    path('household/members/<int:member_id>/', household.family_member_detail, name='family_member_detail'),
    path('options/', household.get_options, name='options'),
    path('announcements/', household.get_announcements, name='announcements'),
    path('messages/', household.messages, name='messages'),
    path('messages/<int:msg_id>/withdraw/', household.withdraw_message, name='withdraw_message'),
]

# 追加需要延迟导入的路由
if _has_full_views:
    urlpatterns += [
        # ==================== 设备管理 ====================
        path('device-types/', devices.get_device_types, name='device_types'),
        path('device-types/<str:type_code>/', devices.get_device_type_detail, name='device_type_detail'),
        path('devices/', devices.user_devices, name='user_devices'),
        path('devices/<str:device_id>/', devices.device_detail, name='device_detail'),
        path('devices/<str:device_id>/history/', devices.device_history, name='device_history'),

        # ==================== 用电记录 ====================
        path('consumption/monthly/', electricity.get_monthly_consumption, name='monthly_consumption'),
        path('consumption/summary/', electricity.get_consumption_summary, name='consumption_summary'),
        path('consumption/trends/', electricity.get_consumption_trends, name='consumption_trends'),

        # ==================== 缴费管理 ====================
        path('bills/', billing.get_my_bills, name='my_bills'),
        path('bills/current/', billing.get_current_bill, name='current_bill'),
        path('bills/<str:bill_id>/', billing.get_bill_detail, name='bill_detail'),
        path('bills/<str:bill_id>/pay/', billing.pay_bill, name='pay_bill'),
        path('notices/', billing.get_notices, name='notices'),

        # ==================== 维修报单 ====================
        path('repairs/', repair.repair_orders, name='repair_orders'),
        path('repairs/<str:order_id>/', repair.repair_order_detail, name='repair_order_detail'),
        path('repairs/<str:order_id>/rate/', repair.rate_repair, name='rate_repair'),

        # ==================== 知识图谱 ====================
        path('graph/full/', neo4j_kg.get_kg_full_graph, name='kg_full_graph'),
        path('graph/user/', neo4j_kg.get_user_kg, name='user_kg'),
        path('graph/sync/', neo4j_kg.sync_to_neo4j, name='sync_neo4j'),

        # ==================== 聚类/画像 ====================
        path('clusters/', cluster_views.get_clusters, name='clusters'),
        path('profile/enhanced/', cluster_views.get_enhanced_profile, name='enhanced_profile'),

        # ==================== 管理员 ====================
        path('admin/stats/', admin_views.admin_dashboard, name='admin_dashboard'),
        path('admin/users/', admin_views.admin_user_list, name='admin_users'),
        path('admin/users/create/', admin_views.admin_create_user, name='admin_create_user'),
        path('admin/users/<str:household_id>/edit/', admin_views.admin_edit_user, name='admin_edit_user'),
        path('admin/users/<str:household_id>/delete/', admin_views.admin_delete_user, name='admin_delete_user'),
        path('admin/users/<str:household_id>/', admin_views.admin_user_detail, name='admin_user_detail'),
        path('admin/repair-orders/', admin_views.admin_repair_orders, name='admin_repairs'),
        path('admin/repair-orders/<str:order_id>/assign/', admin_views.assign_repair, name='assign_repair'),
        path('admin/repair-orders/<str:order_id>/complete/', admin_views.complete_repair, name='complete_repair'),
        path('admin/announcements/', admin_views.announcements, name='admin_announcements'),
        path('admin/announcements/<int:ann_id>/', admin_views.announcement_detail, name='admin_announcement_detail'),
        path('admin/messages/', admin_views.admin_messages, name='admin_messages'),
        path('admin/messages/<int:msg_id>/reply/', admin_views.reply_message, name='reply_message'),
        path('admin/messages/<int:msg_id>/delete/', admin_views.delete_message, name='delete_message'),
    ]
