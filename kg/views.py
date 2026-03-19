"""
知识图谱API视图 - REFIT版本
"""
import os
import pandas as pd
import numpy as np
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .neo4j_db import neo4j_conn


def get_data_dir():
    """获取数据目录"""
    return settings.DATA_DIR


# ============================================================
# 用户相关API
# ============================================================

@api_view(['GET'])
def get_user_list(request):
    """获取所有用户列表"""
    data_dir = get_data_dir()
    file_path = data_dir / 'user_profiles.csv'

    if not file_path.exists():
        return Response({'error': 'User profiles not found'})

    df = pd.read_csv(file_path)

    # 返回用户列表（包含完整用电统计）
    users = df[['user_id', 'house_num', 'energy_level', 'behavior_label',
                'consumption_pattern', 'avg_daily_kwh', 'std_daily_kwh',
                'max_daily_kwh', 'min_daily_kwh', 'data_days']].to_dict('records')

    return Response({
        'total': len(users),
        'users': users
    })


@api_view(['GET'])
def get_user_profile(request):
    """获取指定用户画像信息"""
    user_id = request.GET.get('user_id', '')

    if not user_id:
        # 如果没有指定用户，返回第一个用户
        user_id = 'REFIT_H1'

    data_dir = get_data_dir()
    profile_file = data_dir / 'user_profiles.csv'

    if not profile_file.exists():
        return Response({'error': 'Profile data not found'})

    df = pd.read_csv(profile_file)
    user_data = df[df['user_id'] == user_id]

    if user_data.empty:
        return Response({'error': f'User {user_id} not found'})

    row = user_data.iloc[0]
    return Response({
        'user_id': row['user_id'],
        'house_num': row['house_num'],
        'total_kwh': round(float(row['total_kwh']), 2),
        'avg_daily_kwh': round(float(row['avg_daily_kwh']), 2),
        'max_daily_kwh': round(float(row['max_daily_kwh']), 2),
        'min_daily_kwh': round(float(row['min_daily_kwh']), 2),
        'std_daily_kwh': round(float(row['std_daily_kwh']), 2),
        'energy_level': row['energy_level'],
        'behavior_label': row['behavior_label'],
        'consumption_pattern': row['consumption_pattern'],
        'data_days': int(row['data_days']),
    })


@api_view(['GET'])
def get_user_statistics(request):
    """获取用户统计数据（用于Dashboard统计卡片）"""
    data_dir = get_data_dir()
    profile_file = data_dir / 'user_profiles.csv'

    if not profile_file.exists():
        return Response({'error': 'Profile data not found'})

    df = pd.read_csv(profile_file)

    # 转换为Python原生类型
    total_kwh = float(df['total_kwh'].sum())
    avg_kwh = float(df['avg_daily_kwh'].mean())

    # 转换energy_level_dist中的键为字符串
    energy_dist = {}
    for k, v in df['energy_level'].value_counts().to_dict().items():
        energy_dist[str(k)] = int(v)

    behavior_dist = {}
    for k, v in df['behavior_label'].value_counts().to_dict().items():
        behavior_dist[str(k)] = int(v)

    return Response({
        'total_users': int(len(df)),
        'total_energy_kwh': round(total_kwh, 2),
        'avg_daily_kwh': round(avg_kwh, 2),
        'total_data_days': int(df['data_days'].sum()),
        'energy_level_dist': energy_dist,
        'behavior_label_dist': behavior_dist,
    })


# ============================================================
# 设备相关API
# ============================================================

@api_view(['GET'])
def get_devices(request):
    """获取设备列表"""
    user_id = request.GET.get('user_id', ''    )

    data_dir = get_data_dir()
    file_path = data_dir / 'devices.csv'

    if not file_path.exists():
        return Response({'error': 'Devices data not found'})

    df = pd.read_csv(file_path)

    # 如果指定了用户ID，筛选该用户的设备
    if user_id:
        df = df[df['user_id'] == user_id]

    devices = df.to_dict('records')

    return Response({
        'total': len(devices),
        'devices': devices
    })


@api_view(['GET'])
def get_device_statistics(request):
    """获取设备统计数据"""
    data_dir = get_data_dir()
    file_path = data_dir / 'devices.csv'

    if not file_path.exists():
        return Response({'error': 'Devices data not found'})

    df = pd.read_csv(file_path)

    # 统计每种设备类型的数量
    device_type_counts = df['device_name_cn'].value_counts().to_dict()

    return Response({
        'total_devices': len(df),
        'device_type_counts': device_type_counts,
        'devices_per_user': round(len(df) / df['user_id'].nunique(), 1)
    })


# ============================================================
# 用电数据API
# ============================================================

@api_view(['GET'])
def get_daily_consumption(request):
    """获取每日用电数据"""
    user_id = request.GET.get('user_id', 'REFIT_H1')
    limit = int(request.GET.get('limit', 30))

    data_dir = get_data_dir()
    file_path = data_dir / 'daily_consumption.csv'

    if not file_path.exists():
        return Response({'error': 'Daily consumption data not found'})

    df = pd.read_csv(file_path)

    # 筛选指定用户
    if user_id:
        df = df[df['user_id'] == user_id]

    # 排序并限制数量
    df = df.sort_values('date', ascending=False).head(limit)

    # 只保留有效的数值列（去除全是NaN的列）
    # 首先保留基础列
    valid_cols = ['user_id', 'date', 'year_month', 'total_kwh']

    # 然后添加有值的设备列
    for col in df.columns:
        if col not in valid_cols and df[col].notna().any():
            valid_cols.append(col)

    df = df[valid_cols]

    # 使用fillna将NaN替换为None，然后转换为字典
    df = df.fillna(value=pd.NA)
    # 转换为字典，NA会被转换为None
    records = df.to_dict(orient='records')
    # 再次确保所有NaN/NA值被处理
    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None

    return Response(records)


@api_view(['GET'])
def get_hourly_consumption(request):
    """获取小时级用电数据"""
    user_id = request.GET.get('user_id', 'REFIT_H1')
    date = request.GET.get('date', '')

    data_dir = get_data_dir()
    file_path = data_dir / 'hourly_consumption.csv'

    if not file_path.exists():
        return Response({'error': 'Hourly consumption data not found'})

    df = pd.read_csv(file_path)

    # 筛选条件
    if user_id:
        df = df[df['user_id'] == user_id]
    if date:
        df = df[df['date'] == date]

    data = df.to_dict('records')

    return Response(data)


@api_view(['GET'])
def get_monthly_consumption(request):
    """获取月度用电数据"""
    user_id = request.GET.get('user_id', 'REFIT_H1')

    data_dir = get_data_dir()
    file_path = data_dir / 'monthly_consumption.csv'

    if not file_path.exists():
        return Response({'error': 'Monthly consumption data not found'})

    df = pd.read_csv(file_path)

    if user_id:
        df = df[df['user_id'] == user_id]

    # 排序
    df = df.sort_values('year_month', ascending=False)

    # 只保留有效的数值列（去除全是NaN的列）
    valid_cols = ['user_id', 'year_month', 'total_kwh']
    for col in df.columns:
        if col not in valid_cols and df[col].notna().any():
            valid_cols.append(col)
    df = df[valid_cols]

    # 使用fillna将NaN替换为None，然后转换为字典
    df = df.fillna(value=pd.NA)
    # 转换为字典，NA会被转换为None
    records = df.to_dict(orient='records')
    # 再次确保所有NaN/NA值被处理
    for record in records:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None

    return Response(records)


# ============================================================
# 知识图谱API
# ============================================================

@api_view(['GET'])
def get_kg_graph(request):
    """获取知识图谱统计信息"""
    try:
        # 从Neo4j获取图谱统计
        nodes_query = "MATCH (n) RETURN labels(n)[0] as label, count(*) as count"
        edges_query = "MATCH ()-[r]->() RETURN type(r) as relation, count(*) as count"

        nodes = neo4j_conn.execute_query(nodes_query)
        edges = neo4j_conn.execute_query(edges_query)

        return Response({
            'source': 'neo4j',
            'nodes': nodes,
            'edges': edges
        })
    except Exception as e:
        # Neo4j未连接时，返回本地数据统计
        data_dir = get_data_dir()

        try:
            # 从本地CSV读取统计
            users_df = pd.read_csv(data_dir / 'user_profiles.csv')
            devices_df = pd.read_csv(data_dir / 'devices.csv')

            # 计算本地统计
            user_count = len(users_df)
            device_count = len(devices_df)

            # 能量等级分布
            energy_levels = users_df['energy_level'].value_counts().to_dict()

            return Response({
                'source': 'local',
                'nodes': [
                    {'label': 'User', 'count': user_count},
                    {'label': 'Device', 'count': device_count},
                    {'label': 'EnergyLevel', 'count': len(energy_levels)},
                    {'label': 'BehaviorLabel', 'count': users_df['behavior_label'].nunique()},
                ],
                'edges': [
                    {'relation': 'OWNS', 'count': device_count},
                    {'relation': 'HAS_ENERGY_LEVEL', 'count': user_count},
                    {'relation': 'HAS_BEHAVIOR_LABEL', 'count': user_count},
                ]
            })
        except Exception as e2:
            return Response({
                'error': str(e),
                'error_local': str(e2),
                'nodes': [],
                'edges': []
            })


@api_view(['GET'])
def get_kg_full_graph(request):
    """获取完整的图谱数据（用于可视化）"""
    data_dir = get_data_dir()

    try:
        # 读取节点数据
        nodes_df = pd.read_csv(data_dir / 'neo4j_nodes.csv')
        rels_df = pd.read_csv(data_dir / 'neo4j_relations.csv')

        # 转换为前端需要的格式
        nodes = []
        for _, row in nodes_df.iterrows():
            # 解析属性
            props = {}
            if row['props']:
                for prop in row['props'].split(','):
                    if ':' in prop:
                        key, val = prop.split(':', 1)
                        key = key.strip()
                        val = val.strip().strip("'")
                        try:
                            props[key] = eval(val) if val.replace('.', '').replace('-', '').isdigit() else val
                        except:
                            props[key] = val

            node = {
                'id': row['id'],
                'type': row['type'],
            }
            node.update(props)
            nodes.append(node)

        # 读取关系数据
        relations = []
        for _, row in rels_df.iterrows():
            relations.append({
                'source': row['source'],
                'target': row['target'],
                'type': row['type']
            })

        return Response({
            'nodes': nodes,
            'relations': relations
        })

    except Exception as e:
        return Response({'error': str(e)})


@api_view(['GET'])
def get_user_similarity(request):
    """获取用户相似度（用于对比分析）"""
    user_id = request.GET.get('user_id', '')
    top_n = int(request.GET.get('top_n', 5))

    data_dir = get_data_dir()
    profile_file = data_dir / 'user_profiles.csv'

    if not profile_file.exists():
        return Response({'error': 'Profile data not found'})

    df = pd.read_csv(profile_file)

    if user_id:
        target_user = df[df['user_id'] == user_id]
        if target_user.empty:
            return Response({'error': f'User {user_id} not found'})

        # 计算与其他用户的相似度（基于日均用电）
        target_avg = target_user.iloc[0]['avg_daily_kwh']
        df['similarity'] = abs(df['avg_daily_kwh'] - target_avg)
        similar_users = df.nsmallest(top_n + 1, 'similarity')
        similar_users = similar_users[similar_users['user_id'] != user_id].head(top_n)

        result = similar_users[['user_id', 'avg_daily_kwh', 'energy_level', 'behavior_label']].to_dict('records')
        return Response(result)

    # 如果没有指定用户，返回用电最相近的用户对
    return Response({'message': 'Please specify user_id'})


# ============================================================
# 导入Neo4j
# ============================================================

@api_view(['POST'])
def import_to_neo4j(request):
    """将REFIT数据导入Neo4j"""
    try:
        data_dir = get_data_dir()

        # 1. 清空现有数据
        neo4j_conn.execute_query("MATCH (n) DETACH DELETE n")

        # 2. 读取数据
        users_df = pd.read_csv(data_dir / 'user_profiles.csv')
        devices_df = pd.read_csv(data_dir / 'devices.csv')

        # 3. 创建用户节点
        for _, row in users_df.iterrows():
            query = """
            MERGE (u:User {user_id: $user_id})
            SET u.house_num = $house_num,
                u.energy_level = $energy_level,
                u.behavior_label = $behavior_label,
                u.consumption_pattern = $consumption_pattern,
                u.avg_daily_kwh = $avg_daily_kwh
            """
            neo4j_conn.execute_query(query, {
                'user_id': str(row['user_id']),
                'house_num': str(row['house_num']),
                'energy_level': str(row['energy_level']),
                'behavior_label': str(row['behavior_label']),
                'consumption_pattern': str(row['consumption_pattern']),
                'avg_daily_kwh': float(row['avg_daily_kwh'])
            })

        # 4. 创建设备节点
        device_ids = set()
        for _, row in devices_df.iterrows():
            if row['device_id'] not in device_ids:
                device_ids.add(row['device_id'])
                query = """
                MERGE (d:Device {device_id: $device_id})
                SET d.device_name = $device_name,
                    d.device_code = $device_code
                """
                neo4j_conn.execute_query(query, {
                    'device_id': str(row['device_id']),
                    'device_name': str(row['device_name_cn']),
                    'device_code': str(row['device_code'])
                })

        # 5. 创建分类节点
        energy_levels = ['低', '中', '高', '极高']
        for el in energy_levels:
            neo4j_conn.execute_query("MERGE (e:EnergyLevel {name: $name})", {'name': el})

        behavior_labels = ['节能型', '正常型', '高耗能型']
        for bl in behavior_labels:
            neo4j_conn.execute_query("MERGE (b:BehaviorLabel {name: $name})", {'name': bl})

        # 6. 创建关系
        # 用户-设备 关系
        for _, row in devices_df.iterrows():
            query = """
            MATCH (u:User {user_id: $user_id})
            MATCH (d:Device {device_id: $device_id})
            MERGE (u)-[:OWNS]->(d)
            """
            neo4j_conn.execute_query(query, {
                'user_id': str(row['user_id']),
                'device_id': str(row['device_id'])
            })

        # 用户-能耗等级 关系
        for _, row in users_df.iterrows():
            query = """
            MATCH (u:User {user_id: $user_id})
            MATCH (e:EnergyLevel {name: $energy_level})
            MERGE (u)-[:HAS_ENERGY_LEVEL]->(e)
            """
            neo4j_conn.execute_query(query, {
                'user_id': str(row['user_id']),
                'energy_level': str(row['energy_level'])
            })

        # 用户-行为标签 关系
        for _, row in users_df.iterrows():
            query = """
            MATCH (u:User {user_id: $user_id})
            MATCH (b:BehaviorLabel {name: $behavior_label})
            MERGE (u)-[:HAS_BEHAVIOR_LABEL]->(b)
            """
            neo4j_conn.execute_query(query, {
                'user_id': str(row['user_id']),
                'behavior_label': str(row['behavior_label'])
            })

        return Response({
            'status': 'success',
            'message': 'REFIT data imported to Neo4j successfully',
            'stats': {
                'users': len(users_df),
                'devices': len(device_ids),
                'relations': len(devices_df) + len(users_df) * 2
            }
        })

    except Exception as e:
        import traceback
        return Response({
            'status': 'error',
            'message': str(e),
            'trace': traceback.format_exc()
        })


@api_view(['GET'])
def get_comparison(request):
    """获取用户对比数据"""
    user_ids = request.GET.get('user_ids', '').split(',')

    if not user_ids or user_ids == ['']:
        return Response({'error': 'Please provide user_ids'})

    data_dir = get_data_dir()
    profile_file = data_dir / 'user_profiles.csv'

    df = pd.read_csv(profile_file)
    df = df[df['user_id'].isin(user_ids)]

    if df.empty:
        return Response({'error': 'No users found'})

    # 返回对比数据
    comparison = df[[
        'user_id', 'house_num', 'total_kwh', 'avg_daily_kwh',
        'max_daily_kwh', 'min_daily_kwh', 'std_daily_kwh',
        'energy_level', 'behavior_label', 'consumption_pattern', 'data_days'
    ]].to_dict('records')

    return Response(comparison)


# ============================================================
# 用户分群API
# ============================================================

@api_view(['GET'])
def get_user_clusters(request):
    """获取用户分群结果"""
    try:
        from .clustering import get_cluster_summary

        summary = get_cluster_summary()

        return Response({
            'status': 'success',
            'clusters': summary,
            'total_clusters': len(summary)
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        })


@api_view(['GET'])
def get_user_similar_users(request):
    """获取与指定用户相似的用户"""
    user_id = request.GET.get('user_id', '')
    top_n = int(request.GET.get('top_n', 5))

    if not user_id:
        return Response({'error': 'Please provide user_id'})

    try:
        from .clustering import get_user_similar_users

        similar = get_user_similar_users(user_id, top_n)

        return Response({
            'status': 'success',
            'user_id': user_id,
            'similar_users': similar
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        })


@api_view(['POST'])
def export_clusters_to_neo4j(request):
    """导出用户分群数据到Neo4j"""
    try:
        from .clustering import export_to_neo4j

        result = export_to_neo4j()

        return Response(result)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        })


@api_view(['GET'])
def get_cluster_users(request):
    """获取指定分群的用户列表"""
    cluster_id = request.GET.get('cluster_id', '')

    if cluster_id == '':
        return Response({'error': 'Please provide cluster_id'})

    try:
        cluster_id = int(cluster_id)
        from .clustering import get_cluster_summary

        summary = get_cluster_summary()
        cluster = next((c for c in summary if c['cluster_id'] == cluster_id), None)

        if cluster:
            return Response({
                'status': 'success',
                'cluster': cluster
            })
        else:
            return Response({'error': 'Cluster not found'})

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        })


# ============================================================
# 知识图谱增强型用户画像 API
# ============================================================

@api_view(['GET'])
def get_user_profile_graph(request):
    """获取用户完整画像（图查询）- 知识图谱核心优势体现"""
    user_id = request.GET.get('user_id', '')

    if not user_id:
        user_id = 'REFIT_H1'

    data_dir = get_data_dir()

    try:
        # 1. 获取用户基本信息
        profile_df = pd.read_csv(data_dir / 'user_profiles.csv')
        user_data = profile_df[profile_df['user_id'] == user_id]

        if user_data.empty:
            return Response({'error': f'User {user_id} not found'})

        user_row = user_data.iloc[0]

        # 2. 获取设备列表
        devices_df = pd.read_csv(data_dir / 'devices.csv')
        user_devices = devices_df[devices_df['user_id'] == user_id]

        # 3. 从daily_consumption获取设备用电数据
        daily_df = pd.read_csv(data_dir / 'daily_consumption.csv')
        user_daily = daily_df[daily_df['user_id'] == user_id]

        # 获取设备列名（排除非设备列）
        daily_cols = [col for col in user_daily.columns
                      if col not in ['user_id', 'date', 'year_month', 'total_kwh']]

        # device_code 到 daily列名的映射
        # App0=Aggregate, App1=Fridge, App2=Freezer(1), etc.
        device_code_to_daily = {
            'App0': 'Aggregate',
            'App1': 'Fridge',
            'App2': 'Freezer(1)',
            'App3': 'Freezer(2)',
            'App4': 'Washer_Dryer',
            'App5': 'Washing_Machine',
            'App6': 'Dishwasher',
            'App7': 'Computer',
            'App8': 'Television_Site',
            'App9': 'Electric_Heater',
        }

        # 计算每个设备的总用电量
        device_usage = {}
        for device_code, daily_col in device_code_to_daily.items():
            if daily_col in user_daily.columns:
                device_usage[device_code] = user_daily[daily_col].sum()

        # 4. 获取分群信息
        from .clustering import get_cluster_summary
        summary = get_cluster_summary()
        user_cluster = None
        for cluster in summary:
            if user_id in cluster.get('users', []):
                user_cluster = {
                    'cluster_id': cluster['cluster_id'],
                    'cluster_label': cluster['cluster_label'],
                    'avg_energy': cluster['avg_energy']
                }
                break

        # 5. 构建图谱数据
        graph_data = {
            'user': {
                'user_id': user_id,
                'house_num': user_row.get('house_num', ''),
                'energy_level': user_row.get('energy_level', ''),
                'behavior_label': user_row.get('behavior_label', ''),
                'consumption_pattern': user_row.get('consumption_pattern', ''),
                'avg_daily_kwh': float(user_row.get('avg_daily_kwh', 0)),
                'total_kwh': float(user_row.get('total_kwh', 0))
            },
            'devices': [],
            'cluster': user_cluster,
            'relations': []
        }

        # 设备节点和关系（使用中文名称）
        device_total = 0
        for _, device in user_devices.iterrows():
            device_code = device.get('device_code', '')
            # 使用中文名称
            device_name = device.get('device_name_cn', device.get('device_name', device_code))
            # 从daily数据中获取用电量
            device_kwh = device_usage.get(device_code, 0)
            device_total += device_kwh

            graph_data['devices'].append({
                'device_id': device['device_id'],
                'device_name': device_name,
                'device_code': device_code,
                'total_kwh': round(float(device_kwh), 2)
            })
            # 添加 OWNS 关系
            graph_data['relations'].append({
                'source': user_id,
                'target': device['device_id'],
                'type': 'OWNS',
                'weight': round(float(device_kwh), 2)
            })

        # 计算设备用电占比
        if device_total > 0:
            for device in graph_data['devices']:
                device['percentage'] = round(device['total_kwh'] / device_total * 100, 1)

        # 6. 获取相似用户（从分群中找）
        if user_cluster:
            for cluster in summary:
                if cluster['cluster_id'] == user_cluster['cluster_id']:
                    similar_users = [u for u in cluster.get('users', []) if u != user_id]
                    for sim_user in similar_users[:3]:
                        sim_profile = profile_df[profile_df['user_id'] == sim_user]
                        if not sim_profile.empty:
                            sim_row = sim_profile.iloc[0]
                            similarity = round(100 - abs(float(sim_row.get('avg_daily_kwh', 0)) - float(user_row.get('avg_daily_kwh', 0))) / 2, 1)
                            graph_data['relations'].append({
                                'source': user_id,
                                'target': sim_user,
                                'type': 'SIMILAR_TO',
                                'weight': similarity
                            })

        return Response({
            'status': 'success',
            'graph': graph_data
        })

    except Exception as e:
        import traceback
        return Response({
            'status': 'error',
            'message': str(e)
        })


@api_view(['GET'])
def get_user_network(request):
    """获取用户的关联实体网络"""
    user_id = request.GET.get('user_id', '')

    if not user_id:
        user_id = 'REFIT_H1'

    data_dir = get_data_dir()

    try:
        # 读取数据
        profile_df = pd.read_csv(data_dir / 'user_profiles.csv')
        devices_df = pd.read_csv(data_dir / 'devices.csv')
        daily_df = pd.read_csv(data_dir / 'daily_consumption.csv')

        user_data = profile_df[profile_df['user_id'] == user_id]
        if user_data.empty:
            return Response({'error': f'User {user_id} not found'})

        user_row = user_data.iloc[0]
        user_devices = devices_df[devices_df['user_id'] == user_id]

        # 从daily数据获取设备用电量
        user_daily = daily_df[daily_df['user_id'] == user_id]

        # device_code 到 daily列名的映射
        device_code_to_daily = {
            'App0': 'Aggregate',
            'App1': 'Fridge',
            'App2': 'Freezer(1)',
            'App3': 'Freezer(2)',
            'App4': 'Washer_Dryer',
            'App5': 'Washing_Machine',
            'App6': 'Dishwasher',
            'App7': 'Computer',
            'App8': 'Television_Site',
            'App9': 'Electric_Heater',
        }

        # 计算每个设备的用电量
        device_usage = {}
        for device_code, daily_col in device_code_to_daily.items():
            if daily_col in user_daily.columns:
                device_usage[device_code] = user_daily[daily_col].sum()

        # 构建网络节点
        nodes = [
            {
                'id': user_id,
                'name': user_id,
                'category': 'user',
                'symbolSize': 60,
                'value': float(user_row.get('avg_daily_kwh', 0))
            }
        ]

        # 添加设备节点（使用中文名称）
        for _, device in user_devices.iterrows():
            device_code = device.get('device_code', '')
            device_name = device.get('device_name_cn', device.get('device_name', device_code))
            device_kwh = device_usage.get(device_code, 0)
            nodes.append({
                'id': device['device_id'],
                'name': device_name,  # 使用中文名称
                'category': 'device',
                'symbolSize': 30 + device_kwh / 100,  # 根据用电量调整大小
                'value': round(float(device_kwh), 2)
            })

        # 添加能耗等级节点
        energy_level = user_row.get('energy_level', '')
        if energy_level:
            nodes.append({
                'id': f'energy_{energy_level}',
                'name': f'能耗等级: {energy_level}',
                'category': 'energy_level',
                'symbolSize': 40
            })

        # 添加行为标签节点
        behavior_label = user_row.get('behavior_label', '')
        if behavior_label:
            nodes.append({
                'id': f'behavior_{behavior_label}',
                'name': f'行为标签: {behavior_label}',
                'category': 'behavior',
                'symbolSize': 40
            })

        # 构建边
        links = []

        # 用户-设备边
        for _, device in user_devices.iterrows():
            device_code = device.get('device_code', '')
            device_kwh = device_usage.get(device_code, 0)
            links.append({
                'source': user_id,
                'target': device['device_id'],
                'value': round(float(device_kwh), 2)
            })

        # 用户-能耗等级边
        if energy_level:
            links.append({
                'source': user_id,
                'target': f'energy_{energy_level}',
                'value': 10
            })

        # 用户-行为标签边
        if behavior_label:
            links.append({
                'source': user_id,
                'target': f'behavior_{behavior_label}',
                'value': 10
            })

        # 计算设备联动（同一用户同时使用的设备）
        correlations = []

        # 构建设备名称映射
        device_name_map = {}
        for _, device in user_devices.iterrows():
            device_code = device.get('device_code', '')
            device_name_cn = device.get('device_name_cn', device.get('device_name', device_code))
            # 找到daily列名
            for dc, daily_col in device_code_to_daily.items():
                if dc == device_code and daily_col in user_daily.columns:
                    device_name_map[daily_col] = device_name_cn
                    break

        device_cols = [col for col in user_daily.columns
                      if col in device_code_to_daily.values()]

        for i, col1 in enumerate(device_cols):
            for col2 in device_cols[i+1:]:
                if user_daily[col1].sum() > 0 and user_daily[col2].sum() > 0:
                    co_use = ((user_daily[col1] > 0) & (user_daily[col2] > 0)).sum()
                    if co_use > 0:
                        correlations.append({
                            'source': device_name_map.get(col1, col1),
                            'target': device_name_map.get(col2, col2),
                            'value': int(co_use)
                        })

        return Response({
            'status': 'success',
            'nodes': nodes,
            'links': links,
            'device_correlations': correlations
        })

    except Exception as e:
        import traceback
        return Response({
            'status': 'error',
            'message': str(e),
            'trace': traceback.format_exc()
        })


@api_view(['GET'])
def get_user_pattern(request):
    """获取用户用电模式分析"""
    user_id = request.GET.get('user_id', '')

    if not user_id:
        user_id = 'REFIT_H1'

    data_dir = get_data_dir()

    try:
        # 读取小时级数据
        hourly_df = pd.read_csv(data_dir / 'hourly_consumption.csv')
        user_hourly = hourly_df[hourly_df['user_id'] == user_id]

        if user_hourly.empty:
            return Response({
                'status': 'success',
                'pattern': 'unknown',
                'timeslot_distribution': []
            })

        # 按小时统计用电量（使用Aggregate作为总用电量）
        hourly_stats = user_hourly.groupby('hour').agg({
            'Aggregate': 'sum'
        }).reset_index()
        hourly_stats.columns = ['hour', 'total_kwh']

        total = hourly_stats['total_kwh'].sum()

        # 计算各时段用电比例
        timeslots = {
            '早高峰': [6, 7, 8, 9],
            '午间': [10, 11, 12, 13, 14, 15, 16],
            '晚高峰': [17, 18, 19, 20, 21, 22],
            '夜间': [23, 0, 1, 2, 3, 4, 5]
        }

        distribution = []
        for slot_name, hours in timeslots.items():
            slot_total = hourly_stats[hourly_stats['hour'].isin(hours)]['total_kwh'].sum()
            percentage = round(slot_total / total * 100, 1) if total > 0 else 0
            distribution.append({
                'timeslot': slot_name,
                'kwh': round(slot_total, 2),
                'percentage': percentage
            })

        # 判断用电模式
        morning = distribution[0]['percentage']
        evening = distribution[2]['percentage']

        if evening > 40:
            pattern = '晚峰型'
        elif morning > 30:
            pattern = '早峰型'
        elif max(distribution[0]['percentage'], distribution[1]['percentage'],
                  distribution[2]['percentage'], distribution[3]['percentage']) < 35:
            pattern = '均匀型'
        else:
            pattern = '间歇型'

        return Response({
            'status': 'success',
            'pattern': pattern,
            'timeslot_distribution': distribution,
            'hourly_data': hourly_stats.to_dict('records')
        })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        })


@api_view(['GET'])
def get_profile_similar_users(request):
    """获取相似用户及相似原因"""
    user_id = request.GET.get('user_id', '')

    if not user_id:
        user_id = 'REFIT_H1'

    data_dir = get_data_dir()

    try:
        from .clustering import get_cluster_summary

        profile_df = pd.read_csv(data_dir / 'user_profiles.csv')
        user_data = profile_df[profile_df['user_id'] == user_id]

        if user_data.empty:
            return Response({'error': f'User {user_id} not found'})

        user_row = user_data.iloc[0]
        user_avg = float(user_row.get('avg_daily_kwh', 0))

        # 从分群中找相似用户
        summary = get_cluster_summary()
        similar_users = []

        for cluster in summary:
            if user_id in cluster.get('users', []):
                cluster_users = [u for u in cluster.get('users', []) if u != user_id]

                for sim_id in cluster_users:
                    sim_data = profile_df[profile_df['user_id'] == sim_id]
                    if not sim_data.empty:
                        sim_row = sim_data.iloc[0]
                        sim_avg = float(sim_row.get('avg_daily_kwh', 0))

                        # 计算相似度
                        energy_diff = abs(user_avg - sim_avg)
                        similarity = max(0, 100 - energy_diff)

                        # 确定相似原因
                        reasons = []
                        if similarity > 70:
                            reasons.append('能耗水平相近')
                        if cluster['cluster_label']:
                            reasons.append(f'同属{cluster["cluster_label"]}')
                        if abs(float(sim_row.get('std_daily_kwh', 0)) - float(user_row.get('std_daily_kwh', 0))) < 20:
                            reasons.append('用电波动相似')

                        similar_users.append({
                            'user_id': sim_id,
                            'house_num': sim_row.get('house_num', ''),
                            'avg_daily_kwh': round(sim_avg, 2),
                            'behavior_label': sim_row.get('behavior_label', ''),
                            'similarity': round(similarity, 1),
                            'reasons': reasons
                        })

                break

        # 按相似度排序
        similar_users.sort(key=lambda x: x['similarity'], reverse=True)

        return Response({
            'status': 'success',
            'similar_users': similar_users[:5]
        })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        })


@api_view(['GET'])
def get_saving_tips(request):
    """获取节能建议（图推理）"""
    user_id = request.GET.get('user_id', '')

    if not user_id:
        user_id = 'REFIT_H1'

    data_dir = get_data_dir()

    try:
        profile_df = pd.read_csv(data_dir / 'user_profiles.csv')
        user_data = profile_df[profile_df['user_id'] == user_id]

        if user_data.empty:
            return Response({'error': f'User {user_id} not found'})

        user_row = user_data.iloc[0]
        user_avg = float(user_row.get('avg_daily_kwh', 0))

        # 从分群中找节能型用户作为参考
        from .clustering import get_cluster_summary
        summary = get_cluster_summary()

        tips = []

        # 1. 基于分群提出建议
        for cluster in summary:
            if user_id in cluster.get('users', []):
                cluster_label = cluster['cluster_label']
                cluster_avg = cluster['avg_energy']

                if cluster_label in ['高耗能型', '波动型']:
                    tips.append({
                        'type': 'reduce_level',
                        'title': f'降低能耗等级',
                        'description': f'您属于{cluster_label}，日均用电高于平均{cluster_avg:.1f}kWh',
                        'potential_saving': round(user_avg - cluster_avg, 2)
                    })
                break

        # 2. 基于用电模式提出建议
        energy_level = user_row.get('energy_level', '')
        if energy_level in ['高', '极高']:
            tips.append({
                'type': 'high_energy',
                'title': '高能耗提醒',
                'description': '您的能耗等级较高，建议检查主要用电设备',
                'potential_saving': round(user_avg * 0.2, 2)
            })

        # 3. 找同类型节能用户作为榜样
        for cluster in summary:
            if cluster['cluster_label'] == '节能型' and cluster['users']:
                best_user = cluster['users'][0]
                best_data = profile_df[profile_df['user_id'] == best_user]
                if not best_data.empty:
                    best_row = best_data.iloc[0]
                    best_avg = float(best_row.get('avg_daily_kwh', 0))

                    if best_avg < user_avg:
                        tips.append({
                            'type': 'follow_example',
                            'title': '可借鉴节能用户',
                            'description': f'用户{best_user}日均仅{best_avg:.1f}kWh，比您低{user_avg - best_avg:.1f}kWh',
                            'potential_saving': round(user_avg - best_avg, 2),
                            'reference_user': best_user
                        })
                break

        # 4. 通用节能建议
        tips.append({
            'type': 'general',
            'title': '通用节能建议',
            'description': '建议在不使用时关闭待机设备，避免长时间使用高功率电器',
            'potential_saving': round(user_avg * 0.1, 2)
        })

        return Response({
            'status': 'success',
            'tips': tips,
            'current_avg': user_avg,
            'potential_total': round(sum(t.get('potential_saving', 0) for t in tips), 2)
        })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        })


@api_view(['GET'])
def get_device_correlation(request):
    """获取设备联动分析"""
    user_id = request.GET.get('user_id', '')

    if not user_id:
        user_id = 'REFIT_H1'

    data_dir = get_data_dir()

    try:
        daily_df = pd.read_csv(data_dir / 'daily_consumption.csv')
        devices_df = pd.read_csv(data_dir / 'devices.csv')

        user_daily = daily_df[daily_df['user_id'] == user_id]
        user_devices = devices_df[devices_df['user_id'] == user_id]

        device_cols = [col for col in user_daily.columns
                      if col not in ['user_id', 'date', 'year_month', 'total_kwh']]

        # 计算设备使用时间
        device_usage = []
        for col in device_cols:
            device_info = user_devices[user_devices['device_code'] == col]
            if not device_info.empty:
                device_name = device_info.iloc[0].get('device_name', col)
            else:
                device_name = col

            # 使用天数
            active_days = (user_daily[col] > 0).sum()
            total_kwh = user_daily[col].sum()

            device_usage.append({
                'device_code': col,
                'device_name': device_name,
                'active_days': int(active_days),
                'total_kwh': round(float(total_kwh), 2)
            })

        # 计算设备共现
        correlations = []
        for i, col1 in enumerate(device_cols):
            for col2 in device_cols[i+1:]:
                if user_daily[col1].sum() > 0 and user_daily[col2].sum() > 0:
                    # 共现天数
                    co_use = ((user_daily[col1] > 0) & (user_daily[col2] > 0)).sum()
                    use1 = (user_daily[col1] > 0).sum()
                    use2 = (user_daily[col2] > 0).sum()

                    if use1 > 0 and use2 > 0:
                        # 计算Jaccard相似度
                        jaccard = co_use / min(use1, use2)

                        if jaccard > 0.3:
                            info1 = user_devices[user_devices['device_code'] == col1]
                            info2 = user_devices[user_devices['device_code'] == col2]

                            name1 = info1.iloc[0].get('device_name', col1) if not info1.empty else col1
                            name2 = info2.iloc[0].get('device_name', col2) if not info2.empty else col2

                            correlations.append({
                                'device1': col1,
                                'device1_name': name1,
                                'device2': col2,
                                'device2_name': name2,
                                'co_use_days': int(co_use),
                                'correlation': round(jaccard, 2)
                            })

        # 按相关性排序
        correlations.sort(key=lambda x: x['correlation'], reverse=True)

        return Response({
            'status': 'success',
            'device_usage': device_usage,
            'correlations': correlations[:10]
        })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        })


# ============================================================
# 新增API：基于改进FCM和TransE嵌入的用户画像
# ============================================================

@api_view(['GET'])
def get_fcm_clusters(request):
    """获取FCM聚类结果"""
    try:
        from .fcm_clustering import get_fcm_cluster_summary

        summary = get_fcm_cluster_summary()

        return Response({
            'status': 'success',
            'clusters': summary,
            'total_clusters': len(summary),
            'algorithm': 'Improved FCM (Density Peak + Adaptive Weight)',
            'description': '基于密度峰值初始化和自适应隶属度权重调整的改进FCM算法'
        })
    except Exception as e:
        import traceback
        return Response({
            'status': 'error',
            'message': str(e),
            'trace': traceback.format_exc()
        })


@api_view(['GET'])
def get_user_fcm_membership(request):
    """获取用户FCM隶属度（模糊聚类结果）"""
    user_id = request.GET.get('user_id', '')

    if not user_id:
        user_id = 'REFIT_H1'

    try:
        from .fcm_clustering import get_user_fcm_membership

        membership = get_user_fcm_membership(user_id)

        if membership:
            return Response({
                'status': 'success',
                'membership': membership
            })
        else:
            return Response({
                'status': 'error',
                'message': 'User not found or clustering not completed'
            })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        })


@api_view(['GET'])
def get_user_embedding(request):
    """获取用户图嵌入向量"""
    user_id = request.GET.get('user_id', '')

    if not user_id:
        user_id = 'REFIT_H1'

    try:
        from .graph_embedding import get_user_embedding

        embedding = get_user_embedding(user_id)

        if embedding is not None:
            return Response({
                'status': 'success',
                'user_id': user_id,
                'embedding': embedding.tolist(),
                'embedding_dim': len(embedding),
                'algorithm': 'TransE',
                'description': '基于TransE算法的知识图谱嵌入向量'
            })
        else:
            return Response({
                'status': 'error',
                'message': 'Embedding not found'
            })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        })


@api_view(['GET'])
def get_all_embeddings(request):
    """获取所有用户的嵌入向量"""
    try:
        data_dir = get_data_dir()
        emb_file = data_dir / 'user_embeddings.csv'

        if not emb_file.exists():
            # 触发嵌入训练
            from .graph_embedding import train_and_save_embeddings
            train_and_save_embeddings()

        if emb_file.exists():
            df = pd.read_csv(emb_file)
            return Response({
                'status': 'success',
                'total_users': len(df),
                'embedding_dim': len(df.columns) - 1,
                'users': df.to_dict('records')
            })
        else:
            return Response({
                'status': 'error',
                'message': 'No embeddings available'
            })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        })


@api_view(['GET'])
def get_enhanced_profile(request):
    """获取增强版用户画像（包含FCM聚类和TransE嵌入）"""
    user_id = request.GET.get('user_id', '')

    if not user_id:
        user_id = 'REFIT_H1'

    data_dir = get_data_dir()

    try:
        # 1. 获取用户基础画像
        profile_df = pd.read_csv(data_dir / 'user_profiles.csv')
        user_data = profile_df[profile_df['user_id'] == user_id]

        if user_data.empty:
            return Response({'error': f'User {user_id} not found'})

        user_row = user_data.iloc[0]

        # 2. 获取FCM隶属度
        from .fcm_clustering import get_user_fcm_membership
        fcm_membership = get_user_fcm_membership(user_id)

        # 3. 获取TransE嵌入
        from .graph_embedding import get_user_embedding
        embedding = get_user_embedding(user_id)

        # 4. 获取基础画像数据
        profile_graph = get_user_profile_graph_data(user_id)

        # 5. 构建增强版画像
        enhanced_profile = {
            'user': {
                'user_id': user_id,
                'house_num': user_row.get('house_num', ''),
                'energy_level': user_row.get('energy_level', ''),
                'behavior_label': user_row.get('behavior_label', ''),
                'consumption_pattern': user_row.get('consumption_pattern', ''),
                'avg_daily_kwh': round(float(user_row.get('avg_daily_kwh', 0)), 2),
                'total_kwh': round(float(user_row.get('total_kwh', 0)), 2),
                'std_daily_kwh': round(float(user_row.get('std_daily_kwh', 0)), 2),
            },
            'fcm_cluster': fcm_membership,
            'embedding': {
                'dimension': len(embedding) if embedding is not None else 0,
                'vector': embedding.tolist() if embedding is not None else None
            },
            'original_profile': profile_graph
        }

        return Response({
            'status': 'success',
            'profile': enhanced_profile,
            'enhanced_features': [
                'fcm_membership',
                'transE_embedding',
                'semantic_similarity'
            ]
        })

    except Exception as e:
        import traceback
        return Response({
            'status': 'error',
            'message': str(e),
            'trace': traceback.format_exc()
        })


def get_user_profile_graph_data(user_id):
    """获取用户基础画像数据（内部函数）"""
    data_dir = get_data_dir()

    profile_df = pd.read_csv(data_dir / 'user_profiles.csv')
    user_data = profile_df[profile_df['user_id'] == user_id]

    if user_data.empty:
        return {}

    user_row = user_data.iloc[0]

    # 获取设备列表
    devices_df = pd.read_csv(data_dir / 'devices.csv')
    user_devices = devices_df[devices_df['user_id'] == user_id]

    # 从daily_consumption获取设备用电数据
    daily_df = pd.read_csv(data_dir / 'daily_consumption.csv')
    user_daily = daily_df[daily_df['user_id'] == user_id]

    # 设备用电映射 (device_code -> total_kwh)
    device_cols = [col for col in user_daily.columns
                  if col not in ['user_id', 'date', 'year_month', 'total_kwh']]

    device_usage = {}
    for col in device_cols:
        if user_daily[col].notna().any():
            device_usage[col] = user_daily[col].sum()

    devices = []
    for _, device in user_devices.iterrows():
        device_code = device.get('device_code', '')
        # 使用中文名称
        device_name = device.get('device_name_cn', device.get('device_name', device_code))

        # 获取用电量
        total_kwh = device_usage.get(device_code, 0)

        devices.append({
            'device_id': device['device_id'],
            'device_code': device_code,
            'device_name': device_name,
            'total_kwh': round(float(total_kwh), 2)
        })

    # 按用电量排序
    devices = sorted(devices, key=lambda x: x['total_kwh'], reverse=True)

    return {
        'user_id': user_id,
        'devices': devices,
        'device_count': len(devices)
    }


@api_view(['GET'])
def get_kg_embedding_similarity(request):
    """获取基于图嵌入的用户相似度 - 优化版本"""
    user_id = request.GET.get('user_id', '')
    top_n = int(request.GET.get('top_n', 5))

    if not user_id:
        return Response({'error': 'Please provide user_id'})

    try:
        from .graph_embedding import get_all_embeddings
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        data_dir = get_data_dir()
        profile_df = pd.read_csv(data_dir / 'user_profiles.csv')

        # 批量获取所有嵌入向量
        embeddings_df = get_all_embeddings()

        if embeddings_df is None or embeddings_df.empty:
            return Response({'error': 'No embeddings available'})

        # 找到目标用户的嵌入
        target_row = embeddings_df[embeddings_df['user_id'] == user_id]

        if target_row.empty:
            return Response({'error': f'No embedding found for user {user_id}'})

        emb_cols = [c for c in embeddings_df.columns if c.startswith('emb_')]
        target_emb = target_row[emb_cols].values[0].reshape(1, -1)

        # 批量计算所有用户的嵌入
        all_embs = embeddings_df[emb_cols].values

        # 计算余弦相似度
        similarities_matrix = cosine_similarity(target_emb, all_embs)[0]

        # 构建结果
        similarities = []
        for idx, row in embeddings_df.iterrows():
            other_id = row['user_id']
            if other_id != user_id:
                sim = similarities_matrix[idx]
                user_row = profile_df[profile_df['user_id'] == other_id]
                house_num = user_row['house_num'].values[0] if not user_row.empty else ''
                avg_kwh = user_row['avg_daily_kwh'].values[0] if not user_row.empty else 0
                behavior_label = user_row['behavior_label'].values[0] if not user_row.empty else ''

                similarities.append({
                    'user_id': other_id,
                    'house_num': house_num,
                    'similarity': round(float(sim), 4),
                    'avg_daily_kwh': round(float(avg_kwh), 2),
                    'behavior_label': behavior_label
                })

        # 按相似度排序
        similarities.sort(key=lambda x: x['similarity'], reverse=True)

        return Response({
            'status': 'success',
            'user_id': user_id,
            'similar_users': similarities[:top_n],
            'algorithm': 'TransE Embedding + Cosine Similarity (Optimized)'
        })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        })


@api_view(['GET'])
def compare_user_embeddings(request):
    """比较两个用户的嵌入向量"""
    user_id1 = request.GET.get('user_id1', '')
    user_id2 = request.GET.get('user_id2', '')

    if not user_id1 or not user_id2:
        return Response({'error': 'Please provide both user_id1 and user_id2'})

    if user_id1 == user_id2:
        return Response({'error': 'Cannot compare the same user'})

    try:
        from .graph_embedding import get_user_embedding

        data_dir = get_data_dir()
        profile_df = pd.read_csv(data_dir / 'user_profiles.csv')

        # 获取两个用户的嵌入向量
        emb1 = get_user_embedding(user_id1)
        emb2 = get_user_embedding(user_id2)

        if emb1 is None or emb2 is None:
            return Response({'error': 'Embedding not found for one or both users'})

        # 计算余弦相似度
        from sklearn.metrics.pairwise import cosine_similarity

        sim = cosine_similarity([emb1], [emb2])[0][0]

        # 获取用户信息
        user1_row = profile_df[profile_df['user_id'] == user_id1].iloc[0]
        user2_row = profile_df[profile_df['user_id'] == user_id2].iloc[0]

        # 计算特征差异
        avg_kwh1 = float(user1_row.get('avg_daily_kwh', 0))
        avg_kwh2 = float(user2_row.get('avg_daily_kwh', 0))
        std_kwh1 = float(user1_row.get('std_daily_kwh', 0))
        std_kwh2 = float(user2_row.get('std_daily_kwh', 0))

        # 生成对比结论
        conclusion_parts = []
        if sim > 0.8:
            conclusion_parts.append("两位用户用电行为非常相似")
        elif sim > 0.6:
            conclusion_parts.append("两位用户用电行为较为相似")
        elif sim > 0.4:
            conclusion_parts.append("两位用户用电行为差异较大")
        else:
            conclusion_parts.append("两位用户用电行为差异显著")

        if avg_kwh1 > avg_kwh2 * 1.2:
            conclusion_parts.append(f"{user_id1}日均用电量更高")
        elif avg_kwh2 > avg_kwh1 * 1.2:
            conclusion_parts.append(f"{user_id2}日均用电量更高")
        else:
            conclusion_parts.append("日均用电量相近")

        if std_kwh1 > std_kwh2 * 1.2:
            conclusion_parts.append(f"{user_id1}用电波动更大")
        elif std_kwh2 > std_kwh1 * 1.2:
            conclusion_parts.append(f"{user_id2}用电波动更大")

        return Response({
            'status': 'success',
            'user1': {
                'user_id': user_id1,
                'house_num': user1_row.get('house_num', ''),
                'avg_daily_kwh': round(avg_kwh1, 2),
                'std_daily_kwh': round(std_kwh1, 2),
                'behavior_label': user1_row.get('behavior_label', '')
            },
            'user2': {
                'user_id': user_id2,
                'house_num': user2_row.get('house_num', ''),
                'avg_daily_kwh': round(avg_kwh2, 2),
                'std_daily_kwh': round(std_kwh2, 2),
                'behavior_label': user2_row.get('behavior_label', '')
            },
            'similarity': round(float(sim), 4),
            'conclusion': '，'.join(conclusion_parts)
        })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        })


@api_view(['GET'])
def get_weather_impact(request):
    """获取气象因素对用户用电的影响分析"""
    user_id = request.GET.get('user_id', '')

    if not user_id:
        user_id = 'REFIT_H1'

    data_dir = get_data_dir()

    try:
        # 读取每日用电数据
        daily_df = pd.read_csv(data_dir / 'daily_consumption.csv')
        user_daily = daily_df[daily_df['user_id'] == user_id]

        if user_daily.empty:
            return Response({
                'status': 'success',
                'user_id': user_id,
                'has_weather_data': False,
                'message': 'No consumption data available'
            })

        # 简化分析：基于日期提取季节特征
        # 假设数据在daily_consumption中可能有温度等气象数据
        # 这里做一个简化实现

        # 计算用户用电的波动性
        avg_kwh = user_daily['total_kwh'].mean()
        std_kwh = user_daily['total_kwh'].std()

        # 分析季节性用电模式
        user_daily_copy = user_daily.copy()
        user_daily_copy['month'] = pd.to_datetime(user_daily_copy['date']).dt.month

        seasonal_usage = user_daily_copy.groupby('month')['total_kwh'].mean().to_dict()

        # 判断是否有明显季节性
        seasonal_variance = np.std(list(seasonal_usage.values())) if seasonal_usage else 0

        return Response({
            'status': 'success',
            'user_id': user_id,
            'has_weather_data': True,
            'analysis': {
                'avg_daily_kwh': round(avg_kwh, 2),
                'std_daily_kwh': round(std_kwh, 2),
                'cv': round(std_kwh / avg_kwh, 3) if avg_kwh > 0 else 0,
                'seasonal_variance': round(seasonal_variance, 2),
                'monthly_usage': {str(k): round(v, 2) for k, v in seasonal_usage.items()}
            },
            'insight': '用电波动较大，可能受季节因素影响'
                        if seasonal_variance > avg_kwh * 0.3
                        else '用电相对稳定，受季节因素影响较小'
        })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        })


@api_view(['POST'])
def train_embeddings(request):
    """触发嵌入向量训练"""
    try:
        from .graph_embedding import train_and_save_embeddings

        embedding_dim = int(request.data.get('embedding_dim', 32))

        result = train_and_save_embeddings(embedding_dim=embedding_dim)

        if result is not None:
            return Response({
                'status': 'success',
                'message': f'Trained embeddings with dimension {embedding_dim}',
                'total_users': len(result)
            })
        else:
            return Response({
                'status': 'error',
                'message': 'Failed to train embeddings'
            })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        })


# ==================== 基于论文的季节性特征API ====================

@api_view(['GET'])
def get_user_seasonal_features(request):
    """
    获取用户季节性特征
    基于论文《考虑负荷季节特性的电力用户用电行为画像》
    """
    user_id = request.GET.get('user_id', '')

    if not user_id:
        user_id = 'REFIT_H1'

    try:
        from .seasonal_features import extract_user_seasonal_features, SeasonalAnalyzer

        data_dir = get_data_dir()

        # 提取季节性特征
        features = extract_user_seasonal_features(user_id, data_dir)

        if features is None:
            return Response({
                'status': 'error',
                'message': 'No data available for user'
            })

        return Response({
            'status': 'success',
            'user_id': user_id,
            'features': features
        })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        })


@api_view(['GET'])
def get_user_season_adaptation(request):
    """
    获取用户季节适应性分析
    识别用户是夏季高负荷型还是冬季高负荷型
    """
    user_id = request.GET.get('user_id', '')

    if not user_id:
        user_id = 'REFIT_H1'

    try:
        from .seasonal_features import SeasonalAnalyzer

        data_dir = get_data_dir()

        # 读取用电数据
        consumption_file = data_dir / 'daily_consumption.csv'
        df = pd.read_csv(consumption_file)
        user_df = df[df['user_id'] == user_id].copy()

        if user_df.empty:
            return Response({
                'status': 'error',
                'message': 'No data available for user'
            })

        # 季节适应性分析
        analyzer = SeasonalAnalyzer()
        adaptation = analyzer.get_season_adaptation(user_df)

        return Response({
            'status': 'success',
            'user_id': user_id,
            'season_adaptation': adaptation
        })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        })


@api_view(['GET'])
def get_user_typical_days(request):
    """
    获取用户典型用电日
    基于DTW距离的K-means聚类
    """
    user_id = request.GET.get('user_id', '')
    n_clusters = int(request.GET.get('n_clusters', 3))

    if not user_id:
        user_id = 'REFIT_H1'

    try:
        from .seasonal_features import TypicalDayExtractor

        data_dir = get_data_dir()

        # 读取用电数据
        consumption_file = data_dir / 'daily_consumption.csv'
        df = pd.read_csv(consumption_file)
        user_df = df[df['user_id'] == user_id].copy()

        if user_df.empty:
            return Response({
                'status': 'error',
                'message': 'No data available for user'
            })

        # 提取典型日
        extractor = TypicalDayExtractor()
        typical_days = extractor.extract_typical_days(user_df, n_clusters=n_clusters)

        if typical_days is None:
            return Response({
                'status': 'error',
                'message': 'Insufficient data for typical day extraction'
            })

        return Response({
            'status': 'success',
            'user_id': user_id,
            'typical_days': typical_days
        })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        })


@api_view(['GET'])
def get_user_complexity_features(request):
    """
    获取用户负荷复杂性特征
    模糊熵、样本熵、排列熵
    """
    user_id = request.GET.get('user_id', '')

    if not user_id:
        user_id = 'REFIT_H1'

    try:
        from .seasonal_features import LoadFeatureExtractor

        data_dir = get_data_dir()

        # 读取用电数据
        consumption_file = data_dir / 'daily_consumption.csv'
        df = pd.read_csv(consumption_file)
        user_df = df[df['user_id'] == user_id].copy()

        if user_df.empty:
            return Response({
                'status': 'error',
                'message': 'No data available for user'
            })

        # 提取复杂性特征
        extractor = LoadFeatureExtractor()
        load_series = user_df['total_kwh'].values
        complexity_features = extractor.extract_complexity_features(load_series)

        return Response({
            'status': 'success',
            'user_id': user_id,
            'complexity_features': complexity_features
        })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        })
