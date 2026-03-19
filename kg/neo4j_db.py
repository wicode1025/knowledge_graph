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
