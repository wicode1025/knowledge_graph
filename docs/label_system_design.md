# 电力用户行为画像标签体系设计方案

## 一、总体设计思路

### 1.1 设计目标

构建一个**基于FCM模糊聚类的用户画像标签体系**，具备以下特征：
- **工程化**: 代码可维护、易扩展、符合软件工程规范
- **层次化**: 多级标签体系，从宏观到微观
- **可解释性**: 每个标签有明确的业务含义
- **实用性**: 支持知识图谱可视化、用户查询、推荐系统等场景

### 1.2 技术基础

| 技术要素 | 说明 |
|----------|------|
| 聚类算法 | FCM (Fuzzy C-Means) 模糊聚类 |
| 聚类数量 | 4个类别 (根据业务需要可调整) |
| 隶属度阈值 | 0.5 (低于此值视为隶属度低) |
| 边界判定 | max - min < 0.5 视为边界/摆渡用户 |

---

## 二、聚类结果分析

### 2.1 原始FCM聚类分布 (280用户)

```
┌──────────────┬─────────┬────────────────────────────────┐
│ 聚类标签      │ 用户数  │ 特征描述                       │
├──────────────┼─────────┼────────────────────────────────┤
│ 节能型       │  197    │ 用电量低、用电稳定              │
│ 普通型       │   58    │ 用电量中等、无明显特征          │
│ 波动型       │   16    │ 用电波动大、峰谷差异明显        │
│ 高耗能型     │    9    │ 用电量高、持续高负荷            │
└──────────────┴─────────┴────────────────────────────────┘
```

### 2.2 隶属度分布分析

根据隶属度分析，用户可分为三类：

| 用户类别 | 判定条件 | 占比 | 处理方式 |
|----------|----------|------|----------|
| 清晰用户 | max - min >= 0.5 | ~75% | 保留原标签 |
| 边界用户 | max - min < 0.5 | ~15% | 标记为"摆渡型" |
| 低隶属用户 | max < 0.5 | ~10% | 标记为"待定"或排除 |

---

## 三、标签体系架构

### 3.1 四级标签层次

```
Level 1: 宏观分类 (能耗等级)
    │
    ├── 一级标签: 节能型 (低能耗)
    ├── 一级标签: 普通型 (中等能耗)
    ├── 一级标签: 摆渡型 (边界用户)
    ├── 一级标签: 高耗能型 (高能耗)
    │
    ▼
Level 2: 行为特征 (次级分类)
    │
    ├── 节能型 → 稳定节能型 / 间歇节能型
    ├── 普通型 → 稳定普通型 / 波动普通型
    ├── 摆渡型 → 节能摆渡型 / 高耗能摆渡型
    └── 高耗能型 → 持续高耗能型 / 周期高耗能型
    │
    ▼
Level 3: 细分标签
    │
    ├── 根据FCM隶属度细分
    ├── 根据用电模式细分
    └── 根据设备使用情况细分
    │
    ▼
Level 4: 业务标签 (工单相关)
    │
    ├── 投诉记录标签
    ├── 故障历史标签
    └── 服务记录标签
```

### 3.2 标签编码规范

```
格式: [能耗等级]-[行为特征]-[细分标识]-[业务标识]

示例:
- JNF-WD-01-00  (节能型-稳定型-细分01-无工单)
- PTH-JG-02-01  (摆渡型-高耗能摆渡-细分02-有投诉)
```

| 字段 | 编码 | 说明 |
|------|------|------|
| 能耗等级 | JNF/PTH/BDY/GNH | 节能/普通/摆渡/高耗能 |
| 行为特征 | WD/BD/JG/ZQ | 稳定/波动/间歇/周期 |
| 细分标识 | 01-99 | 序号 |
| 业务标识 | 00-99 | 工单标记 |

---

## 四、标签定义详细说明

### 4.1 一级标签 (能耗等级)

| 标签名称 | 编码 | 判定条件 | 业务含义 | 用户数 |
|----------|------|----------|----------|--------|
| 节能型 | JNF | max(隶属度) >= 0.5 且 属于节能聚类 | 用电效率高，注重节能 | ~180 |
| 普通型 | PTH | max(隶属度) >= 0.5 且 属于普通聚类 | 用电行为无明显特征 | ~50 |
| 摆渡型 | BDY | max - min < 0.5 | 处于分类边界，难以归类 | ~30 |
| 高耗能型 | GNH | max(隶属度) >= 0.5 且 属于高耗能聚类 | 用电量大，需关注 | ~10 |
| 待定 | DDX | max(隶属度) < 0.5 | 隶属度过低，无法分类 | ~10 |

### 4.2 二级标签 (行为特征)

```
节能型 (JNF) 的细分:
├── JNF-WD: 稳定节能型
│   ├── 特征: 用电波动小，全天分布均匀
│   ├── 判定: 方差 < 阈值
│   └── 建议: 可推广节能习惯
│
└── JNF-BD: 间歇节能型
    ├── 特征: 用电时段集中，有明显低谷期
    ├── 判定: 方差 >= 阈值
    └── 建议: 优化用电时段

普通型 (PTH) 的细分:
├── PTH-WD: 稳定普通型
│   ├── 特征: 用电稳定，无明显峰谷
│   └── 判定: 变异系数 < 0.3
│
└── PTH-BD: 波动普通型
    ├── 特征: 用电有一定波动
    └── 判定: 变异系数 >= 0.3

摆渡型 (BDY) 的细分:
├── BDY-JF: 节能摆渡型
│   ├── 特征: 在节能和普通之间摇摆
│   └── 隶属度: 节能>=0.35 且 普通>=0.35 且 diff<0.5
│
└── BDY-GH: 高耗能摆渡型
    ├── 特征: 在普通和高耗能之间摇摆
    └── 隶属度: 普通>=0.35 且 高耗能>=0.35 且 diff<0.5

高耗能型 (GNH) 的细分:
├── GNH-ZQ: 持续高耗能型
│   ├── 特征: 全天持续高负荷
│   ├── 判定: 白天平均负荷 > 夜间平均负荷 * 1.2
│   └── 建议: 错峰用电指导
│
└── GNH-BD: 周期高耗能型
    ├── 特征: 间歇性高负荷
    └── 判定: 高负荷时段占比 < 50%
```

### 4.3 三级标签 (FCM隶属度细分)

基于FCM隶属度值的细分：

```
标签格式: [一级]-[二级]-[隶属度等级]

示例:
- JNF-WD-H  (节能-稳定-高隶属度 >= 0.8)
- JNF-WD-M  (节能-稳定-中隶属度 0.5-0.8)
- JNF-WD-L  (节能-稳定-低隶属度 0.5-0.6)

隶属度等级:
- H (High): >= 0.8
- M (Middle): 0.5 - 0.8
- L (Low): 0.5 - 0.6 (接近边界)
```

### 4.4 四级标签 (业务标签 - 工单相关)

```
业务标签从工单数据中提取:

┌────────────┬─────────┬────────────────────────────────┐
│ 标签类型    │ 编码    │ 说明                           │
├────────────┼─────────┼────────────────────────────────┤
│ 无工单      │ 00     │ 无任何工单记录                 │
├────────────┼─────────┼────────────────────────────────┤
│ 有投诉      │ 01     │ 存在投诉工单                   │
├────────────┼─────────┼────────────────────────────────┤
│ 有故障      │ 02     │ 存在故障工单                   │
├────────────┼─────────┼────────────────────────────────┤
│ 有维修      │ 03     │ 存在维修工单                   │
├────────────┼─────────┼────────────────────────────────┤
│ 多次工单    │ 04     │ 工单数 >= 3                    │
└────────────┴─────────┴────────────────────────────────┘

组合规则:
- 优先级: 投诉 > 故障 > 维修 > 多次工单 > 无工单
- 例如: 同时有投诉和故障，标记为 01
```

---

## 五、数据结构设计

### 5.1 用户标签表 (user_tags)

```sql
CREATE TABLE user_tags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(50) NOT NULL,

    -- 一级标签
    energy_level VARCHAR(10),  -- JNF/PTH/BDY/GNH/DDX

    -- 二级标签
    behavior_type VARCHAR(10), -- WD/BD/JG/ZQ

    -- 三级标签
    membership_grade CHAR(1),  -- H/M/L

    -- 业务标签
    business_tag VARCHAR(10), -- 00-04

    -- FCM数据
    cluster_id INT,            -- 聚类ID 0-3
    membership_max FLOAT,     -- 最大隶属度
    membership_min FLOAT,     -- 最小隶属度
    membership_diff FLOAT,    -- max - min

    -- 原始数据
    fcm_membership_json TEXT, -- 完整隶属度JSON

    created_at DATETIME,
    updated_at DATETIME,

    INDEX idx_user_id (user_id),
    INDEX idx_energy_level (energy_level),
    INDEX idx_cluster_id (cluster_id)
);
```

### 5.2 标签统计表 (tag_statistics)

```sql
CREATE TABLE tag_statistics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tag_type VARCHAR(20),     -- energy_level/behavior_type/etc
    tag_value VARCHAR(20),    -- 标签值
    user_count INT,           -- 用户数量
    avg_consumption FLOAT,    -- 平均用电量
    calculated_at DATETIME,

    INDEX idx_tag_type_value (tag_type, tag_value)
);
```

### 5.3 Python数据结构

```python
# 用户标签数据结构
class UserTag:
    def __init__(self):
        self.user_id: str = ""

        # 层级标签
        self.level1: str = ""  # 能耗等级: JNF/PTH/BDY/GNH/DDX
        self.level2: str = ""  # 行为特征: WD/BD/JG/ZQ
        self.level3: str = ""  # 隶属度等级: H/M/L
        self.level4: str = ""  # 业务标签: 00-04

        # FCM原始数据
        self.cluster_id: int = 0
        self.membership_max: float = 0.0
        self.membership_min: float = 0.0
        self.membership_diff: float = 0.0
        self.memberships: Dict[int, float] = {}  # 聚类ID -> 隶属度

        # 组合标签 (显示用)
        self.combined_tag: str = ""  # 如 "JNF-WD-H-00"

    def get_display_name(self) -> str:
        """获取可读标签名"""
        level1_names = {
            'JNF': '节能型', 'PTH': '普通型',
            'BDY': '摆渡型', 'GNH': '高耗能型', 'DDX': '待定'
        }
        return f"{level1_names.get(self.level1, '未知')}"

# 标签统计
class TagStatistics:
    def __init__(self):
        self.total_users: int = 0
        self.clear_users: int = 0      # 清晰分类用户
        self.boundary_users: int = 0   # 边界用户
        self.low_membership_users: int = 0  # 低隶属度用户

        self.level1_distribution: Dict[str, int] = {}  # 一级分布
        self.level2_distribution: Dict[str, int] = {}  # 二级分布
        self.business_tag_distribution: Dict[str, int] = {}  # 业务标签分布
```

---

## 六、算法实现

### 6.1 标签生成流程

```
┌─────────────────┐
│  读取FCM结果     │
│  (280用户)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  计算隶属度差值   │
│  diff = max-min  │
└────────┬────────┘
         │
    ┌────┴────┐
    │ diff >= 0.5? │ ──yes──▶ 清晰用户 → 判定聚类
    └────┬────┘                    │
         │no                       ▼
         ▼                  ┌──────────────┐
┌─────────────────┐        │ 判定聚类ID    │
│  max >= 0.5?    │ ──no──▶ │ (节能/普通/   │
└────────┬────────┘          │  高耗能)      │
         │yes                └──────────────┘
         │                         │
         ▼                         ▼
┌─────────────────┐        ┌──────────────┐
│  边界用户        │        │  生成Level1  │
│  标记为摆渡型    │        │  + Level2    │
└─────────────────┘        └──────────────┘
                                 │
                                 ▼
                        ┌──────────────┐
                        │ 判定用电模式  │
                        │ (稳定/波动)   │
                        └──────────────┘
                                 │
                                 ▼
                        ┌──────────────┐
                        │  生成Level3  │
                        │ (H/M/L)      │
                        └──────────────┘
                                 │
                                 ▼
                        ┌──────────────┐
                        │ 读取工单数据  │
                        │  生成Level4   │
                        └──────────────┘
                                 │
                                 ▼
                        ┌──────────────┐
                        │  组合完整标签 │
                        │  保存到数据库 │
                        └──────────────┘
```

### 6.2 核心代码实现

```python
# kg/tag_generator.py

from typing import Dict, List, Tuple
import json

class LabelGenerator:
    """用户标签生成器"""

    # 隶属度阈值
    MEMBERSHIP_THRESHOLD = 0.5
    BOUNDARY_THRESHOLD = 0.5

    # 聚类标签映射
    CLUSTER_LABELS = {
        0: 'JNF',  # 节能型
        1: 'PTH',  # 普通型
        2: 'GNH',  # 高耗能型
        3: 'WD'    # 稳定型 (需要根据实际聚类结果调整)
    }

    def generate_user_label(self, user_id: str, memberships: Dict[int, float],
                          consumption_stats: dict, work_orders: List[dict]) -> UserTag:
        """生成用户完整标签"""
        tag = UserTag()
        tag.user_id = user_id
        tag.memberships = memberships

        # Step 1: 判定用户类别
        max_cluster = max(memberships, key=memberships.get)
        max_membership = memberships[max_cluster]
        min_membership = min(memberships.values())
        diff = max_membership - min_membership

        tag.cluster_id = max_cluster
        tag.membership_max = max_membership
        tag.membership_min = min_membership
        tag.membership_diff = diff

        # 判定逻辑
        if max_membership < self.MEMBERSHIP_THRESHOLD:
            # 低隶属度用户
            tag.level1 = 'DDX'  # 待定
        elif diff < self.BOUNDARY_THRESHOLD:
            # 边界用户
            tag.level1 = 'BDY'  # 摆渡型
        else:
            # 清晰用户
            tag.level1 = self.CLUSTER_LABELS.get(max_cluster, 'PTH')

        # Step 2: 判定行为特征 (Level 2)
        tag.level2 = self._determine_behavior_type(consumption_stats)

        # Step 3: 判定隶属度等级 (Level 3)
        tag.level3 = self._determine_membership_grade(max_membership)

        # Step 4: 判定业务标签 (Level 4)
        tag.level4 = self._determine_business_tag(work_orders)

        # 组合标签
        tag.combined_tag = f"{tag.level1}-{tag.level2}-{tag.level3}-{tag.level4}"

        return tag

    def _determine_behavior_type(self, stats: dict) -> str:
        """根据用电统计判定行为特征"""
        cv = stats.get('coefficient_of_variation', 0)  # 变异系数

        if cv < 0.3:
            return 'WD'  # 稳定型
        else:
            return 'BD'  # 波动型

    def _determine_membership_grade(self, max_membership: float) -> str:
        """判定隶属度等级"""
        if max_membership >= 0.8:
            return 'H'   # 高
        elif max_membership >= 0.65:
            return 'M'   # 中
        else:
            return 'L'   # 低

    def _determine_business_tag(self, work_orders: List[dict]) -> str:
        """根据工单数据判定业务标签"""
        if not work_orders:
            return '00'  # 无工单

        # 统计工单类型
        has_complaint = any(o.get('type') == 'complaint' for o in work_orders)
        has_fault = any(o.get('type') == 'fault' for o in work_orders)
        has_repair = any(o.get('type') == 'repair' for o in work_orders)

        if has_complaint:
            return '01'  # 有投诉
        elif has_fault:
            return '02'  # 有故障
        elif has_repair:
            return '03'  # 有维修
        elif len(work_orders) >= 3:
            return '04'  # 多次工单
        else:
            return '00'
```

### 6.3 批量生成脚本

```python
# scripts/generate_all_labels.py

def main():
    generator = LabelGenerator()

    # 读取FCM结果
    fcm_data = load_fcm_results()

    # 读取用电统计数据
    consumption_stats = load_consumption_stats()

    # 读取工单数据
    work_orders = load_work_orders()

    # 批量生成标签
    for user_id in fcm_data.keys():
        memberships = fcm_data[user_id]
        stats = consumption_stats.get(user_id, {})
        orders = work_orders.get(user_id, [])

        tag = generator.generate_user_label(user_id, memberships, stats, orders)
        save_to_database(tag)

    print("标签生成完成!")

if __name__ == '__main__':
    main()
```

---

## 七、知识图谱集成

### 7.1 图谱节点更新

根据新标签体系，知识图谱节点更新如下：

```
当前用户节点:
├── 数据分支 (Data)
│   ├── 设备节点 (冰箱/空调/...)
│   └── 用电统计 (日均/总用电)
│
└── 标签分支 (Label)
    ├── 一级标签: 节能型/普通型/摆渡型/高耗能型
    │   ├── 行为特征: 稳定型/波动型
    │   └── 隶属度等级: H/M/L
    │
    ├── 二级标签: 行为标签
    │   ├── 稳定节能型
    │   ├── 波动普通型
    │   └── ... (按新体系)
    │
    └── 三级标签: 业务标签
        ├── 有投诉/有故障/有维修
        └── 无工单记录
```

### 7.2 图谱API更新

```python
# 更新获取用户画像API
@api_view(['GET'])
def get_user_profile(request):
    user_id = request.GET.get('user_id')

    # 获取用户标签 (新体系)
    user_tag = get_user_tag(user_id)  # 返回新的四级标签

    # 获取相似用户 (基于新标签体系)
    similar_users = find_similar_users(user_id, threshold=0.7)

    return Response({
        'user_id': user_id,
        'tag': {
            'level1': user_tag.level1,      # 能耗等级
            'level2': user_tag.level2,      # 行为特征
            'level3': user_tag.level3,      # 隶属度等级
            'level4': user_tag.level4,      # 业务标签
            'combined': user_tag.combined_tag,
            'display_name': user_tag.get_display_name()
        },
        'membership': {
            'max': user_tag.membership_max,
            'diff': user_tag.membership_diff,
            'cluster': user_tag.cluster_id
        },
        'similar_users': similar_users
    })
```

---

## 八、实施计划

### Phase 1: 数据准备 (优先级高)

- [ ] 导出FCM聚类结果 (280用户隶属度)
- [ ] 导出用户用电统计数据
- [ ] 导出工单数据
- [ ] 创建user_tags数据库表

### Phase 2: 标签生成 (优先级高)

- [ ] 实现LabelGenerator类
- [ ] 批量生成所有用户标签
- [ ] 验证标签分布合理性
- [ ] 人工抽查关键用户标签

### Phase 3: API更新 (优先级中)

- [ ] 更新profile API返回新标签
- [ ] 更新similarity计算逻辑
- [ ] 新增标签统计API

### Phase 4: 前端集成 (优先级中)

- [ ] 更新知识图谱显示逻辑
- [ ] 标签筛选功能
- [ ] 标签统计展示

### Phase 5: 验证优化 (优先级低)

- [ ] 标签准确性验证
- [ ] 知识图谱交互测试
- [ ] 性能优化

---

## 九、标签体系优势

| 优势 | 说明 |
|------|------|
| **层次化** | 四级标签，层层递进，从宏观到微观 |
| **可解释** | 每个标签都有明确的业务含义和判定依据 |
| **工程化** | 清晰的编码规范，易于维护和扩展 |
| **灵活** | 支持阈值调整，适应不同业务需求 |
| **实用** | 直接支持知识图谱、用户筛选、推荐系统 |

---

## 十、附录

### 10.1 标签名称对照表

| 编码 | 中文名 | 英文名 |
|------|--------|--------|
| JNF | 节能型 | Energy Saving |
| PTH | 普通型 | Normal |
| BDY | 摆渡型 | Boundary |
| GNH | 高耗能型 | High Consumption |
| DDX | 待定 | Undetermined |
| WD | 稳定型 | Stable |
| BD | 波动型 | Volatile |
| H | 高 | High |
| M | 中 | Medium |
| L | 低 | Low |

### 10.2 阈值配置

```python
# 可以在settings中配置
LABEL_CONFIG = {
    'MEMBERSHIP_THRESHOLD': 0.5,      # 隶属度阈值
    'BOUNDARY_DIFF_THRESHOLD': 0.5,   # 边界判定阈值
    'CV_STABLE_THRESHOLD': 0.3,       # 变异系数阈值
    'MEMBERSHIP_GRADE_H': 0.8,        # 高隶属度
    'MEMBERSHIP_GRADE_M': 0.65,       # 中隶属度
    'WORK_ORDER_THRESHOLD': 3,        # 多次工单阈值
}
```