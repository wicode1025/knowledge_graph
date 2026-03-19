# 改进FCM聚类算法详解

## 一、项目背景

本项目基于论文《基于知识图谱与改进FCM算法的电力用户数据聚类分析方法》，实现了改进的模糊C均值聚类算法，用于对电力用户进行分群。

**数据来源**：英国REFIT数据集（20个家庭、8个月电器级用电数据）

---

## 二、FCM聚类基础

### 2.1 什么是FCM？

FCM（Fuzzy C-Means，模糊C均值）是一种软聚类算法。

| 对比项 | K-means（硬聚类） | FCM（软聚类） |
|--------|-------------------|---------------|
| 归属方式 | 非此即彼 | 概率归属 |
| 输出 | 单一标签 | 隶属度矩阵 |
| 适用场景 | 界限分明的数据 | 界限模糊的数据 |

### 2.2 为什么要用FCM分析用电行为？

用电行为具有"模糊性"：
- 用户可能既节能又浪费（不同时间段）
- 用电模式可能在不同季节变化
- 软分类更能反映真实情况

---

## 三、项目中FCM的实现

### 3.1 算法参数

```python
class ImprovedFCM:
    def __init__(self,
                 n_clusters=4,      # 聚4类用户
                 max_iter=100,     # 最多迭代100次
                 m=2.0,            # 模糊系数
                 epsilon=1e-5,     # 收敛阈值
                 use_density_peak=True):  # 使用密度峰值初始化
```

### 3.2 输入特征

```python
# 原始特征（5维）
feature_cols = [
    'avg_daily_kwh',   # 日均用电量
    'std_daily_kwh',   # 用电波动(标准差)
    'max_daily_kwh',   # 最大日用电
    'min_daily_kwh',   # 最小日用电
    'cv'               # 变异系数 = std/mean
]
```

### 3.3 特征融合

```python
# 如果有TransE嵌入向量，拼接在原始特征后面
if embeddings is not None:
    X = np.hstack([X, embeddings])
# 最终特征维度 = 5 + 嵌入维度(64) = 69维
```

---

## 四、核心改进点详解

### 改进1：密度峰值初始化

#### 4.1.1 为什么需要改进初始化？

传统FCM随机选择初始聚类中心，导致：
- 每次运行结果不同
- 可能陷入局部最优
- 需要多次运行取最优

#### 4.1.2 密度峰值算法原理

参考论文：Rodriguez & Laio, Science 2014

**核心思想**：选择同时具有**高密度**和**高距离**的点作为初始中心

**步骤**：

```
1. 计算距离矩阵
   distances = euclidean_distances(X, X)

2. 计算截断距离 dc
   dc = 距离分布的2%分位值

3. 计算局部密度 rho
   ρi = Σ exp(-(dist/dc)²)
   解释：周围有多少"近邻"

4. 计算到高密度点的距离 delta
   δi = min(到所有更高密度点的距离)
   解释：离开高密度区域的"代价"

5. 计算决策值 gamma
   γ = ρ × δ
   同时满足：高密度 + 远离高密度区域

6. 选择gamma最高的n个点作为初始中心
```

#### 4.1.3 代码实现

```python
def _density_peak_initialization(self, X):
    # 计算距离矩阵
    distances = euclidean_distances(X, X)

    # 步骤1：计算截断距离 dc
    dc_percentile = 2
    dc = np.percentile(distances[distances > 0], dc_percentile)

    # 步骤2：计算局部密度 rho
    rho = np.zeros(n_samples)
    for i in range(n_samples):
        rho[i] = np.sum(np.exp(-(distances[i, :] / dc) ** 2)) - 1

    # 步骤3：计算到高密度点的距离 delta
    delta = np.zeros(n_samples)
    sorted_rho_idx = np.argsort(-rho)  # 按密度降序

    for i, idx in enumerate(sorted_rho_idx):
        if i == 0:
            delta[idx] = np.max(distances[idx, :])
        else:
            higher_density_idx = sorted_rho_idx[:i]
            delta[idx] = np.min(distances[idx, higher_density_idx])

    # 步骤4：计算决策值 gamma
    rho_norm = (rho - rho.min()) / (rho.max() - rho.min() + 1e-10)
    delta_norm = (delta - delta.min()) / (delta.max() - delta.min() + 1e-10)
    gamma = rho_norm * delta_norm

    # 步骤5：选择初始中心
    center_indices = np.argsort(-gamma)[:self.n_clusters]
    return X[center_indices].copy()
```

#### 4.1.4 可视化解释

```
高密度区域
    ●●●●●●●●●●●●  ← 高密度、高距离 = 最佳中心点
    ●●○●●●●●●●○  ← 高密度、低距离
    ○○●●●○○●●●○  ← 低密度
    ○○○●●○○○○○○

    ○ = 普通点
    ● = 高密度点
```

---

### 改进2：自适应权重调整（信息熵）

#### 4.2.1 什么是信息熵？

熵 = 衡量"不确定性"的度量

| 熵低 | 熵高 |
|------|------|
| 确定性强 | 不确定性强 |
| 隶属度差异大 | 隶属度差异小 |
| 典型用户 | 边缘用户 |

#### 4.2.2 为什么要用熵调整？

- 边缘用户（同时属于多个类）噪声大
- 应该降低这些用户的权重
- 让聚类更关注"典型"用户

#### 4.2.3 计算公式

```python
# 计算隶属度熵
entropy = -Σ u × log(u)

# 权重调整
weight = 1 - entropy^α
# α = 0.5
# 熵越高 → 权重越低
```

**示例**：
```
用户A隶属度 = [0.9, 0.1] → 熵低 → 权重高（典型）
用户B隶属度 = [0.4, 0.6] → 熵高 → 权重低（边缘）
```

#### 4.2.4 代码实现

```python
def _compute_membership_entropy(self, U):
    """计算隶属度矩阵的熵"""
    U_safe = np.clip(U, 1e-10, 1.0)
    entropy = -np.sum(U_safe * np.log(U_safe), axis=1)

    # 归一化
    max_entropy = -np.log(1.0 / self.n_clusters)
    normalized_entropy = entropy / max_entropy

    return normalized_entropy

def _adaptive_weight_adjustment(self, X, centers, U):
    """自适应权重调整"""
    # 计算熵
    entropy = self._compute_membership_entropy(U)

    # 样本权重：熵越高，权重越低
    alpha = 0.5
    sample_weights = 1 - (entropy ** alpha)

    # 特征权重：基于类内方差
    feature_weights = np.ones(n_features)
    for j in range(n_features):
        cluster_variance = 0
        for k in range(self.n_clusters):
            cluster_points = X[U[:, k] > 0.5]
            if len(cluster_points) > 0:
                variance = np.var(cluster_points[:, j])
                cluster_variance += U[:, k].mean() * variance
        if cluster_variance > 0:
            feature_weights[j] = 1.0 / (1.0 + cluster_variance)

    return feature_weights, sample_weights
```

---

### 改进3：知识图谱嵌入特征融合

#### 4.3.1 为什么要融合嵌入向量？

原始特征只反映"数值"层面的差异：
- 日均用电量
- 用电波动
- 最大/最小值

**但忽略**：
- 用户之间的语义关系
- 设备关联关系
- 行为模式相似性

#### 4.3.2 融合方式

```python
# 原始特征 + TransE嵌入向量
X_fused = np.hstack([X_original, X_embedding])
# 维度：5 + 64 = 69维
```

---

## 五、完整算法流程

### 5.1 主函数

```python
def fcm_clustering_with_kg(n_clusters=4, use_embeddings=True):
    # 1. 读取数据
    profile_df = pd.read_csv('user_profiles 2. .csv')

    #提取特征
    X = profile_df[['avg_daily_kwh', 'std_daily_kwh',
                    'max_daily_kwh', 'min_daily_kwh']].values
    cv = profile_df['std_daily_kwh'] / profile_df['avg_daily_kwh']
    X = np.column_stack([X, cv.values])

    # 3. 读取嵌入向量
    embeddings = pd.read_csv('user_embeddings.csv')
    emb_vectors = embeddings.drop('user_id', axis=1).values

    # 4. 融合特征
    X_fused = np.hstack([X, emb_vectors])

    # 5. 执行改进FCM
    fcm = ImprovedFCM(n_clusters=4, use_density_peak=True)
    fcm.fit(X_fused)

    # 6. 输出结果
    profile_df['cluster'] = fcm.cluster_labels_

    return profile_df, fcm
```

### 5.2 迭代过程

```python
for iteration in range(100):
    # 步骤1：计算到各中心的距离
    distances = euclidean_distances(X, centers)

    # 步骤2：更新隶属度矩阵
    U_new[i,k] = 1 / Σ(distances[i,k]/distances[i,j])^(2/(m-1))

    # 步骤3：计算自适应权重
    feature_weights, sample_weights = adaptive_weight(U_new)

    # 步骤4：应用权重
    U_weighted = U_new * sample_weights

    # 步骤5：检查收敛
    if ||U_new - U_old|| < epsilon:
        break

    # 步骤6：更新聚类中心
    centers[k] = Σ(u[k]^m × x) / Σ(u[k]^m)
```

---

## 六、输出结果

### 6.1 用户标签生成

```python
# 根据平均用电量排序，自动分配标签
cluster_energies = df.groupby('cluster')['avg_daily_kwh'].mean()
sorted_clusters = cluster_energies.sort_values()

label_map = {
    最低: '节能型',
    低: '普通型',
    高: '波动型',
    最高: '高耗能型'
}
```

### 6.2 隶属度输出

```python
# 每个用户对4个类的隶属度
{
    'user_id': 'REFIT_H1',
    'cluster': 0,
    'cluster_label': '节能型',
    'membership': {
        0: 0.85,   # 85%属于节能型
        1: 0.10,
        2: 0.03,
        3: 0.02
    },
    'entropy': 0.23  # 熵越低越典型
}
```

---

## 七、面试常见问题

### Q1: FCM和K-means的区别？
- FCM是软聚类，输出隶属度概率
- FCM支持模糊边界，更适合用电行为分析

### Q2: 密度峰值初始化的优势？
- 自动确定初始中心，避免随机性
- 结果稳定可复现

### Q3: 信息熵调整的作用？
- 降低边缘/噪声用户的影响
- 让聚类更关注典型用户

### Q4: 为什么融合TransE嵌入？
- 补充语义信息，不只是数值特征
- 捕捉用户间的隐含关系

---

## 八、参考文献

1. Rodriguez A, Laio A. Clustering by fast search and find of density peaks[J]. Science, 2014
2. Zadeh L A. Fuzzy sets[J]. Information and control, 1965
3. Bordes A, et al. Translating embeddings for modeling multi-relational data[C]. NIPS, 2013
