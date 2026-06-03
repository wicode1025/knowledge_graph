"""
Neo4j 数据库连接管理
"""
from neo4j import GraphDatabase
from django.conf import settings


class Neo4jConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.driver = None
        return cls._instance

    def connect(self):
        """建立Neo4j连接"""
        if self.driver is None:
            config = settings.NEO4J_CONFIG
            self.driver = GraphDatabase.driver(
                config['URI'],
                auth=config['AUTH']
            )
        return self.driver

    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.close()
            self.driver = None

    def execute_query(self, query, parameters=None):
        """执行查询"""
        driver = self.connect()
        with driver.session(database=settings.NEO4J_CONFIG.get('DATABASE', 'neo4j')) as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

    def execute_single(self, query, parameters=None):
        """执行单条查询"""
        driver = self.connect()
        with driver.session(database=settings.NEO4J_CONFIG.get('DATABASE', 'neo4j')) as session:
            result = session.run(query, parameters)
            record = result.single()
            return record.data() if record else None


# 全局连接实例
neo4j_conn = Neo4jConnection()


# ==================== 知识图谱操作函数 ====================

def create_seasonal_entities():
    """
    创建季节性实体节点
    基于论文: 考虑负荷季节特性
    """
    queries = [
        # 季节实体
        "MERGE (s:Season {name: 'spring', name_cn: '春季', temperature_range: '10-20', description: '春季气温适宜'})",
        "MERGE (s:Season {name: 'summer', name_cn: '夏季', temperature_range: '25-35', description: '夏季高温炎热，空调负荷高'})",
        "MERGE (s:Season {name: 'autumn', name_cn: '秋季', temperature_range: '15-25', description: '秋季气温适中'})",
        "MERGE (s:Season {name: 'winter', name_cn: '冬季', temperature_range: '0-10', description: '冬季寒冷，取暖负荷高'})",

        # 典型日实体
        "MERGE (t:TypicalDay {name: 'weekday', name_cn: '工作日', description: '正常工作日'})",
        "MERGE (t:TypicalDay {name: 'weekend', name_cn: '周末', description: '周末休息日'})",
        "MERGE (t:TypicalDay {name: 'holiday', name_cn: '节假日', description: '法定节假日'})",

        # 时段实体
        "MERGE (p:TimePeriod {name: 'morning_peak', name_cn: '早峰', hours: '7-9', description: '早高峰'})",
        "MERGE (p:TimePeriod {name: 'midday', name_cn: '午间', hours: '11-13', description: '午间时段'})",
        "MERGE (p:TimePeriod {name: 'evening_peak', name_cn: '晚峰', hours: '18-21', description: '晚高峰'})",
        "MERGE (p:TimePeriod {name: 'night', name_cn: '夜间', hours: '22-6', description: '夜间低谷'})",

        # 气象条件实体
        "MERGE (w:Weather {name: 'hot', name_cn: '高温', temp_range: '>30', impact: 'high'})",
        "MERGE (w:Weather {name: 'mild', name_cn: '适宜', temp_range: '15-25', impact: 'low'})",
        "MERGE (w:Weather {name: 'cold', name_cn: '低温', temp_range: '<10', impact: 'high'})",
    ]

    for query in queries:
        try:
            neo4j_conn.execute_query(query)
        except Exception as e:
            print(f"Error creating seasonal entity: {e}")

    return True


def create_seasonal_relationship(user_id, season, factor):
    """
    创建用户-季节关系
    关系属性包含季节影响因子
    """
    query = """
    MATCH (u:User {user_id: $user_id})
    MATCH (s:Season {name: $season})
    MERGE (u)-[r:AFFECTED_BY_SEASON]->(s)
    SET r.factor = $factor,
        r.impact_level = CASE
            WHEN $factor > 0.3 THEN 'high'
            WHEN $factor > 0.15 THEN 'medium'
            ELSE 'low'
        END
    RETURN u, s, r
    """
    try:
        result = neo4j_conn.execute_query(query, {
            'user_id': user_id,
            'season': season,
            'factor': factor
        })
        return result
    except Exception as e:
        print(f"Error creating seasonal relationship: {e}")
        return None


def create_typical_day_relationship(user_id, typical_day_type, match_score):
    """
    创建用户-典型日关系
    """
    query = """
    MATCH (u:User {user_id: $user_id})
    MATCH (t:TypicalDay {name: $typical_day_type})
    MERGE (u)-[r:BELONGS_TO_DAY]->(t)
    SET r.match_score = $match_score
    RETURN u, t, r
    """
    try:
        result = neo4j_conn.execute_query(query, {
            'user_id': user_id,
            'typical_day_type': typical_day_type,
            'match_score': match_score
        })
        return result
    except Exception as e:
        print(f"Error creating typical day relationship: {e}")
        return None


def create_time_period_relationship(user_id, time_period, load_ratio):
    """
    创建用户-时段关系
    记录用户在各时段的用电比例
    """
    query = """
    MATCH (u:User {user_id: $user_id})
    MATCH (p:TimePeriod {name: $time_period})
    MERGE (u)-[r:USES_AT_PERIOD]->(p)
    SET r.load_ratio = $load_ratio,
        r.period_type = CASE
            WHEN $load_ratio > 0.3 THEN 'high_usage'
            WHEN $load_ratio > 0.15 THEN 'medium_usage'
            ELSE 'low_usage'
        END
    RETURN u, p, r
    """
    try:
        result = neo4j_conn.execute_query(query, {
            'user_id': user_id,
            'time_period': time_period,
            'load_ratio': load_ratio
        })
        return result
    except Exception as e:
        print(f"Error creating time period relationship: {e}")
        return None


def get_user_seasonal_graph(user_id):
    """
    获取用户的季节性知识图谱
    包含季节、典型日、时段等关系
    """
    query = """
    MATCH (u:User {user_id: $user_id})
    OPTIONAL MATCH (u)-[r1:AFFECTED_BY_SEASON]->(s:Season)
    OPTIONAL MATCH (u)-[r2:BELONGS_TO_DAY]->(t:TypicalDay)
    OPTIONAL MATCH (u)-[r3:USES_AT_PERIOD]->(p:TimePeriod)
    RETURN u,
        collect(DISTINCT {season: s.name, season_cn: s.name_cn, factor: r1.factor, impact: r1.impact_level}) as seasons,
        collect(DISTINCT {typical_day: t.name, typical_day_cn: t.name_cn, score: r2.match_score}) as typical_days,
        collect(DISTINCT {period: p.name, period_cn: p.name_cn, ratio: r3.load_ratio, usage: r3.period_type}) as time_periods
    """
    try:
        result = neo4j_conn.execute_single(query, {'user_id': user_id})
        return result
    except Exception as e:
        print(f"Error getting seasonal graph: {e}")
        return None


def create_device_correlation_relationship(device1, device2, correlation):
    """
    创建设备关联关系
    基于论文中的设备联动分析
    """
    query = """
    MATCH (d1:Device {device_id: $device1})
    MATCH (d2:Device {device_id: $device2})
    MERGE (d1)-[r:CORRELATES_WITH]->(d2)
    SET r.correlation = $correlation,
        r.relation_type = CASE
            WHEN $correlation > 0.7 THEN 'strong_positive'
            WHEN $correlation > 0.3 THEN 'moderate_positive'
            WHEN $correlation > -0.3 THEN 'weak'
            WHEN $correlation > -0.7 THEN 'moderate_negative'
            ELSE 'strong_negative'
        END
    RETURN d1, d2, r
    """
    try:
        result = neo4j_conn.execute_query(query, {
            'device1': device1,
            'device2': device2,
            'correlation': correlation
        })
        return result
    except Exception as e:
        print(f"Error creating device correlation: {e}")
        return None


def initialize_kg_schema():
    """
    初始化知识图谱模式
    创建所有必要的实体和关系类型
    """
    # 创建季节实体
    create_seasonal_entities()

    # 创建索引
    indexes = [
        "CREATE INDEX IF NOT EXISTS FOR (u:User) ON (u.user_id)",
        "CREATE INDEX IF NOT EXISTS FOR (d:Device) ON (d.device_id)",
        "CREATE INDEX IF NOT EXISTS FOR (s:Season) ON (s.name)",
        "CREATE INDEX IF NOT EXISTS FOR (t:TypicalDay) ON (t.name)",
    ]

    for idx_query in indexes:
        try:
            neo4j_conn.execute_query(idx_query)
        except Exception as e:
            print(f"Error creating index: {e}")

    return True


# ==================== FCM标签导出函数 ====================

def export_fcm_labels_to_neo4j():
    """
    导出FCM标签到Neo4j
    创建新的四级标签体系节点和关系

    优化项（基于学术审视报告）：
    1. 保留完整隶属度向量
    2. 边界用户显式标记
    3. 隶属度熵
    4. 创建用户-标签关系
    """
    import pymysql
    import json

    # 数据库配置
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '20031025wly',
        'charset': 'utf8mb4',
        'database': 'electric_user_profile'
    }

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 获取所有FCM标签
    cursor.execute("SELECT * FROM user_fcm_tags")
    tags = cursor.fetchall()

    cursor.close()
    conn.close()

    if not tags:
        print("没有FCM标签数据")
        return {'status': 'error', 'message': 'No FCM tags found'}

    # 1. 创建一级标签节点 (能耗等级)
    level1_tags = ['JNF', 'PTH', 'BDY', 'GNH', 'DDX']
    level1_display = {
        'JNF': '节能型', 'PTH': '普通型', 'BDY': '摆渡型',
        'GNH': '高耗能型', 'DDX': '待定'
    }

    for tag in level1_tags:
        query = """
        MERGE (l1:FCMTagLevel1 {code: $code})
        SET l1.name = $name,
            l1.category = 'energy_level'
        """
        neo4j_conn.execute_query(query, {
            'code': tag,
            'name': level1_display.get(tag, tag)
        })

    # 2. 创建二级标签节点 (行为特征)
    level2_tags = ['WD', 'BD', 'JG', 'ZQ']
    level2_display = {
        'WD': '稳定型', 'BD': '波动型',
        'JG': '间歇型', 'ZQ': '周期型'
    }

    for tag in level2_tags:
        query = """
        MERGE (l2:FCMTagLevel2 {code: $code})
        SET l2.name = $name,
            l2.category = 'behavior'
        """
        neo4j_conn.execute_query(query, {
            'code': tag,
            'name': level2_display.get(tag, tag)
        })

    # 3. 创建三级标签节点 (能耗模式特征)
    level3_tags = ['ZG', 'YE', 'QY']
    level3_display = {'ZG': '昼间均衡型', 'YE': '夜间波动型', 'QY': '全天候混合型'}

    for tag in level3_tags:
        query = """
        MERGE (l3:FCMTagLevel3 {code: $code})
        SET l3.name = $name,
            l3.category = 'energy_pattern'
        """
        neo4j_conn.execute_query(query, {
            'code': tag,
            'name': level3_display.get(tag, tag)
        })

    # 4. 创建四级标签节点 (服务价值)
    level4_tags = ['GJX', 'ZJZ', 'DJZ', 'FXY']
    level4_display = {
        'GJX': '高价值用户',
        'ZJZ': '中价值用户',
        'DJZ': '低价值用户',
        'FXY': '风险用户'
    }

    for tag in level4_tags:
        query = """
        MERGE (l4:FCMTagLevel4 {code: $code})
        SET l4.name = $name,
            l4.category = 'business'
        """
        neo4j_conn.execute_query(query, {
            'code': tag,
            'name': level4_display.get(tag, tag)
        })

    # 5. 更新用户节点，添加完整FCM标签属性
    # 并创建用户-标签关系
    exported_count = 0
    for row in tags:
        user_id = str(row['user_id'])
        level1 = str(row['level1'])
        level2 = str(row['level2'])
        level3 = str(row['level3'])
        level4 = str(row['level4'])

        # 解析完整隶属度向量
        membership_vector = {}
        if row['membership_json']:
            try:
                membership_vector = json.loads(row['membership_json'])
            except:
                membership_vector = {}

        # 计算边界标记：max - min < 0.5 为边界用户
        membership_diff = float(row['membership_diff']) if row['membership_diff'] else 0
        boundary_flag = membership_diff < 0.5

        # 熵值
        entropy = float(row['entropy']) if row['entropy'] else 0

        # 更新用户节点属性（增强版）
        update_query = """
        MATCH (u:User {user_id: $user_id})
        SET u.fcm_level1 = $level1,
            u.fcm_level2 = $level2,
            u.fcm_level3 = $level3,
            u.fcm_level4 = $level4,
            u.fcm_combined = $combined,
            u.fcm_cluster = $cluster_id,
            u.fcm_membership_max = $membership_max,
            u.fcm_membership_min = $membership_min,
            u.fcm_membership_diff = $membership_diff,
            u.fcm_boundary_flag = $boundary_flag,
            u.fcm_entropy = $entropy,
            u.fcm_membership_vector = $membership_vector
        """
        try:
            neo4j_conn.execute_query(update_query, {
                'user_id': user_id,
                'level1': level1,
                'level2': level2,
                'level3': level3,
                'level4': level4,
                'combined': str(row['combined_tag']),
                'cluster_id': int(row['cluster_id']),
                'membership_max': float(row['membership_max']),
                'membership_min': float(row['membership_min']) if row['membership_min'] else 0,
                'membership_diff': membership_diff,
                'boundary_flag': boundary_flag,
                'entropy': entropy,
                'membership_vector': json.dumps(membership_vector)
            })

            # 创建用户-标签关系（替代属性连接）
            # 关系1: 用户 -> 能耗等级
            if level1 != 'DDX':  # DDX不建立稳定关系
                rel_query1 = f"""
                MATCH (u:User {{user_id: $user_id}})
                MATCH (l1:FCMTagLevel1 {{code: $level1}})
                MERGE (u)-[r:HAS_LEVEL1]->(l1)
                SET r.membership = $membership_max,
                    r.is_primary = true,
                    r.is_boundary = $boundary_flag
                """
                neo4j_conn.execute_query(rel_query1, {
                    'user_id': user_id,
                    'level1': level1,
                    'membership_max': float(row['membership_max']),
                    'boundary_flag': boundary_flag
                })

            # 关系2: 用户 -> 行为特征
            rel_query2 = f"""
            MATCH (u:User {{user_id: $user_id}})
            MATCH (l2:FCMTagLevel2 {{code: $level2}})
            MERGE (u)-[r:HAS_LEVEL2]->(l2)
            SET r.membership = $membership_max
            """
            neo4j_conn.execute_query(rel_query2, {
                'user_id': user_id,
                'level2': level2,
                'membership_max': float(row['membership_max'])
            })

            # 关系3: 用户 -> 能耗模式特征
            rel_query3 = f"""
            MATCH (u:User {{user_id: $user_id}})
            MATCH (l3:FCMTagLevel3 {{code: $level3}})
            MERGE (u)-[r:HAS_LEVEL3]->(l3)
            SET r.membership = $membership_max
            """
            neo4j_conn.execute_query(rel_query3, {
                'user_id': user_id,
                'level3': level3,
                'membership_max': float(row['membership_max'])
            })

            # 关系4: 用户 -> 服务价值
            rel_query4 = f"""
            MATCH (u:User {{user_id: $user_id}})
            MATCH (l4:FCMTagLevel4 {{code: $level4}})
            MERGE (u)-[r:HAS_LEVEL4]->(l4)
            SET r.membership = $membership_max
            """
            neo4j_conn.execute_query(rel_query4, {
                'user_id': user_id,
                'level4': level4,
                'membership_max': float(row['membership_max'])
            })

            exported_count += 1

        except Exception as e:
            print(f"Error updating user {user_id}: {e}")

    print(f"FCM标签已导出到Neo4j: {exported_count} 用户")
    print(f"  - 完整隶属度向量: 已保存")
    print(f"  - 边界用户标记: 已设置")
    print(f"  - 用户-标签关系: 已创建")

    return {
        'status': 'success',
        'users': exported_count
    }
