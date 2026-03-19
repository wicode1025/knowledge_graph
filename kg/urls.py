"""
知识图谱应用URL配置 - REFIT版本
"""
from django.urls import path
from . import views

urlpatterns = [
    # 用户相关
    path('users/', views.get_user_list, name='user_list'),
    path('profile/', views.get_user_profile, name='user_profile'),
    path('statistics/', views.get_user_statistics, name='user_statistics'),
    path('comparison/', views.get_comparison, name='comparison'),
    path('similarity/', views.get_user_similarity, name='similarity'),

    # 设备相关
    path('devices/', views.get_devices, name='devices'),
    path('device-stats/', views.get_device_statistics, name='device_statistics'),

    # 用电数据
    path('consumption/daily/', views.get_daily_consumption, name='daily_consumption'),
    path('consumption/hourly/', views.get_hourly_consumption, name='hourly_consumption'),
    path('consumption/monthly/', views.get_monthly_consumption, name='monthly_consumption'),

    # 知识图谱
    path('graph/', views.get_kg_graph, name='kg_graph'),
    path('graph/full/', views.get_kg_full_graph, name='kg_full_graph'),

    # 用户分群
    path('clusters/', views.get_user_clusters, name='user_clusters'),
    path('clusters/users/', views.get_cluster_users, name='cluster_users'),
    path('clusters/similar/', views.get_user_similar_users, name='similar_users'),
    path('clusters/export/', views.export_clusters_to_neo4j, name='export_clusters'),

    # 导入Neo4j
    path('import/', views.import_to_neo4j, name='import_neo4j'),

    # 知识图谱增强型用户画像
    path('profile/graph/', views.get_user_profile_graph, name='profile_graph'),
    path('profile/network/', views.get_user_network, name='profile_network'),
    path('profile/pattern/', views.get_user_pattern, name='profile_pattern'),
    path('profile/similar/', views.get_profile_similar_users, name='profile_similar'),
    path('profile/saving-tips/', views.get_saving_tips, name='saving_tips'),
    path('profile/device-correlation/', views.get_device_correlation, name='device_correlation'),

    # 新增：基于改进FCM和TransE嵌入的用户画像
    path('fcm-clusters/', views.get_fcm_clusters, name='fcm_clusters'),
    path('fcm-membership/', views.get_user_fcm_membership, name='fcm_membership'),
    path('embedding/', views.get_user_embedding, name='user_embedding'),
    path('embeddings/all/', views.get_all_embeddings, name='all_embeddings'),
    path('profile/enhanced/', views.get_enhanced_profile, name='enhanced_profile'),
    path('profile/embedding-similarity/', views.get_kg_embedding_similarity, name='embedding_similarity'),
    path('profile/weather-impact/', views.get_weather_impact, name='weather_impact'),
    path('embeddings/train/', views.train_embeddings, name='train_embeddings'),

    # 基于论文的季节性特征API
    path('profile/seasonal/', views.get_user_seasonal_features, name='seasonal_features'),
    path('profile/season-adaptation/', views.get_user_season_adaptation, name='season_adaptation'),
    path('profile/typical-days/', views.get_user_typical_days, name='typical_days'),
    path('profile/complexity/', views.get_user_complexity_features, name='complexity_features'),
]
