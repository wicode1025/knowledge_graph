"""
用户分群模块 - 基于知识图谱的智能用户分群
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from django.conf import settings
import os


def get_data_dir():
    """获取数据目录"""
    return settings.DATA_DIR


def extract_user_features():
    """从用电数据中提取用户特征"""
    data_dir = get_data_dir()

    # 读取数据
    daily_df = pd.read_csv(data_dir / 'daily_consumption.csv')
    profiles_df = pd.read_csv(data_dir / 'user_profiles.csv')

    features_list = []

    for user_id in profiles_df['user_id'].unique():
        user_data = daily_df[daily_df['user_id'] == user_id]

        if len(user_data) == 0:
            continue

        # 基础特征
        profile = profiles_df[profiles_df['user_id'] == user_id].iloc[0]

        # 计算各时段用电比例
        # 这里简化处理，实际应该用小时数据
        total_energy = user_data['total_kwh'].sum()

        # 特征构建
        features = {
            'user_id': user_id,
            'house_num': profile.get('house_num', ''),
            # 能耗特征
            'avg_daily_kwh': profile.get('avg_daily_kwh', 0),
            'max_daily_kwh': profile.get('max_daily_kwh', 0),
            'min_daily_kwh': profile.get('min_daily_kwh', 0),
            'std_daily_kwh': profile.get('std_daily_kwh', 0),
            'total_kwh': profile.get('total_kwh', 0),
            # 数据天数
            'data_days': profile.get('data_days', 0),
        }

        # 设备数量（从daily数据中推断）
        device_cols = [col for col in user_data.columns
                     if col not in ['user_id', 'date', 'year_month', 'total_kwh']]
        active_devices = sum(1 for col in device_cols if user_data[col].sum() > 0)
        features['device_count'] = active_devices

        # 计算变异系数（用电稳定性）
        if features['avg_daily_kwh'] > 0:
            features['cv'] = features['std_daily_kwh'] / features['avg_daily_kwh']
        else:
            features['cv'] = 0

        features_list.append(features)

    return pd.DataFrame(features_list)


def perform_clustering(n_clusters=4):
    """执行K-means聚类"""
    # 提取特征
    features_df = extract_user_features()

    # 选择用于聚类的特征
    feature_cols = ['avg_daily_kwh', 'std_daily_kwh', 'cv', 'device_count']

    X = features_df[feature_cols].values

    # 标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # K-means聚类
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)

    # 添加聚类标签
    features_df['cluster'] = clusters

    # 分析每个聚类的特征
    cluster_analysis = []
    for i in range(n_clusters):
        cluster_data = features_df[features_df['cluster'] == i]
        cluster_analysis.append({
            'cluster_id': i,
            'user_count': len(cluster_data),
            'avg_energy': cluster_data['avg_daily_kwh'].mean(),
            'avg_std': cluster_data['std_daily_kwh'].mean(),
            'avg_cv': cluster_data['cv'].mean(),
            'avg_devices': cluster_data['device_count'].mean(),
        })

    return features_df, cluster_analysis, kmeans, scaler


def assign_cluster_labels(features_df, cluster_analysis):
    """根据聚类特征自动分配标签"""
    # 按日均能耗排序
    sorted_clusters = sorted(cluster_analysis, key=lambda x: x['avg_energy'])

    # 分配标签 - 按能耗从低到高分配对应标签
    labels_map = {}
    label_names = ['节能型', '普通型', '波动型', '高耗能型']

    for idx, cluster in enumerate(sorted_clusters):
        cluster_id = cluster['cluster_id']
        # 按排名分配标签：最低能耗=节能型，最高能耗=高耗能型
        labels_map[cluster_id] = label_names[idx]

    features_df['cluster_label'] = features_df['cluster'].map(labels_map)

    return features_df


def build_cluster_kg_data():
    """构建聚类相关的知识图谱数据"""
    features_df, cluster_analysis, kmeans, scaler = perform_clustering(n_clusters=4)
    features_df = assign_cluster_labels(features_df, cluster_analysis)

    # 构建节点数据
    nodes = []
    relations = []

    # 添加聚类中心节点
    for cluster in cluster_analysis:
        nodes.append({
            'type': 'Cluster',
            'id': f"CLUSTER_{cluster['cluster_id']}",
            'props': f"user_count:{cluster['user_count']},avg_energy:{cluster['avg_energy']:.1f}"
        })

    # 添加用户节点和关系
    for _, row in features_df.iterrows():
        # 用户节点
        nodes.append({
            'type': 'User',
            'id': row['user_id'],
            'props': f"cluster:{row['cluster']},cluster_label:'{row['cluster_label']}',avg_daily_kwh:{row['avg_daily_kwh']:.1f}"
        })

        # 用户-聚类关系
        relations.append({
            'source': row['user_id'],
            'target': f"CLUSTER_{row['cluster']}",
            'type': 'BELONGS_TO',
            'props': ''
        })

    # 添加相似用户关系
    for _, row in features_df.iterrows():
        # 找到同一聚类的其他用户
        same_cluster = features_df[
            (features_df['cluster'] == row['cluster']) &
            (features_df['user_id'] != row['user_id'])
        ]

        # 选取最相似的2个用户
        if len(same_cluster) > 0:
            same_cluster = same_cluster.copy()
            same_cluster['diff'] = abs(same_cluster['avg_daily_kwh'] - row['avg_daily_kwh'])
            similar = same_cluster.nsmallest(2, 'diff')

            for _, sim_user in similar.iterrows():
                relations.append({
                    'source': row['user_id'],
                    'target': sim_user['user_id'],
                    'type': 'SIMILAR_TO',
                    'props': f"cluster:{row['cluster']}"
                })

    return features_df, cluster_analysis, nodes, relations


def get_cluster_summary():
    """获取分群摘要"""
    features_df, cluster_analysis, kmeans, scaler = perform_clustering(n_clusters=4)
    features_df = assign_cluster_labels(features_df, cluster_analysis)

    summary = []
    for cluster in cluster_analysis:
        cluster_id = cluster['cluster_id']
        label = features_df[features_df['cluster'] == cluster_id]['cluster_label'].iloc[0]

        # 该聚类的用户列表
        users = features_df[features_df['cluster'] == cluster_id]['user_id'].tolist()

        summary.append({
            'cluster_id': int(cluster_id),
            'cluster_label': label,
            'user_count': cluster['user_count'],
            'avg_energy': round(cluster['avg_energy'], 2),
            'avg_std': round(cluster['avg_std'], 2),
            'avg_cv': round(cluster['avg_cv'], 2),
            'users': users
        })

    return summary


def get_user_similar_users(user_id, top_n=5):
    """获取与指定用户相似的用户"""
    features_df, cluster_analysis, _, _ = perform_clustering(n_clusters=4)
    features_df = assign_cluster_labels(features_df, cluster_analysis)

    # 找到目标用户
    target = features_df[features_df['user_id'] == user_id]
    if target.empty:
        return []

    target = target.iloc[0]
    target_cluster = target['cluster']

    # 找到同一聚类的其他用户
    same_cluster = features_df[
        (features_df['cluster'] == target_cluster) &
        (features_df['user_id'] != user_id)
    ]

    # 计算相似度并排序
    same_cluster = same_cluster.copy()
    same_cluster['similarity'] = (
        abs(same_cluster['avg_daily_kwh'] - target['avg_daily_kwh']) +
        abs(same_cluster['cv'] - target['cv']) * 10
    )

    similar_users = same_cluster.nsmallest(top_n, 'similarity')

    result = []
    for _, row in similar_users.iterrows():
        result.append({
            'user_id': row['user_id'],
            'house_num': row['house_num'],
            'avg_daily_kwh': round(float(row['avg_daily_kwh']), 2),
            'cluster': int(row['cluster']),
            'cluster_label': row['cluster_label'],
            'similarity_score': round(100 - float(row['similarity']), 1)
        })

    return result


def export_to_neo4j():
    """导出聚类数据到Neo4j"""
    from kg.neo4j_db import neo4j_conn

    features_df, cluster_analysis, nodes, relations = build_cluster_kg_data()

    try:
        # 清空现有数据
        neo4j_conn.execute_query("MATCH (n) DETACH DELETE n")

        # 创建聚类节点
        for cluster in cluster_analysis:
            neo4j_conn.execute_query("""
                MERGE (c:Cluster {cluster_id: $id})
                SET c.user_count = $count, c.avg_energy = $energy
            """, {
                'id': int(cluster['cluster_id']),
                'count': cluster['user_count'],
                'energy': cluster['avg_energy']
            })

        # 创建用户节点和关系
        for _, row in features_df.iterrows():
            # 创建用户节点
            neo4j_conn.execute_query("""
                MERGE (u:User {user_id: $id})
                SET u.cluster = $cluster, u.cluster_label = $label,
                    u.avg_daily_kwh = $energy
            """, {
                'id': row['user_id'],
                'cluster': int(row['cluster']),
                'label': row['cluster_label'],
                'energy': float(row['avg_daily_kwh'])
            })

            # 创建归属关系
            neo4j_conn.execute_query("""
                MATCH (u:User {user_id: $uid})
                MATCH (c:Cluster {cluster_id: $cid})
                MERGE (u)-[:BELONGS_TO]->(c)
            """, {
                'uid': row['user_id'],
                'cid': int(row['cluster'])
            })

        # 创建相似用户关系
        for _, row in features_df.iterrows():
            target_cluster = row['cluster']
            same_cluster = features_df[
                (features_df['cluster'] == target_cluster) &
                (features_df['user_id'] != row['user_id'])
            ]

            if len(same_cluster) > 0:
                same_cluster = same_cluster.copy()
                same_cluster['diff'] = abs(same_cluster['avg_daily_kwh'] - row['avg_daily_kwh'])
                similar = same_cluster.nsmallest(2, 'diff')

                for _, sim_user in similar.iterrows():
                    neo4j_conn.execute_query("""
                        MATCH (u1:User {user_id: $id1})
                        MATCH (u2:User {user_id: $id2})
                        MERGE (u1)-[:SIMILAR_TO]->(u2)
                    """, {
                        'id1': row['user_id'],
                        'id2': sim_user['user_id']
                    })

        return {'status': 'success', 'clusters': len(cluster_analysis)}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}


if __name__ == '__main__':
    # 测试
    import django
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'power_profile.settings')
    django.setup()

    summary = get_cluster_summary()
    for s in summary:
        print(f"Cluster {s['cluster_id']}: {s['cluster_label']} - {s['user_count']} users, avg: {s['avg_energy']} kWh")
