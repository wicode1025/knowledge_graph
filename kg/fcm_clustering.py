"""
改进FCM聚类算法 - 基于论文《基于知识图谱与改进FCM算法的电力用户数据聚类分析方法》
核心改进：
1. 密度峰值优化初始聚类中心选择
2. 自适应隶属度权重调整（引入信息熵）
3. 知识图谱嵌入特征融合
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import euclidean_distances
import warnings
warnings.filterwarnings('ignore')


class ImprovedFCM:
    """
    改进的模糊C均值聚类算法
    融合知识图谱嵌入特征，支持密度峰值初始化
    """

    def __init__(self, n_clusters=4, max_iter=100, m=2.0, epsilon=1e-5,
                 embedding_dim=0, use_density_peak=True):
        """
        参数:
            n_clusters: 聚类数目
            max_iter: 最大迭代次数
            m: 模糊系数 (通常取2.0)
            epsilon: 收敛阈值
            embedding_dim: 知识图谱嵌入维度
            use_density_peak: 是否使用密度峰值初始化
        """
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.m = m
        self.epsilon = epsilon
        self.embedding_dim = embedding_dim
        self.use_density_peak = use_density_peak

        self.centers = None  # 聚类中心
        self.U = None  # 隶属度矩阵
        self.cluster_labels_ = None  # 最终标签
        self.membership_entropy_ = None  # 隶属度熵

    def _density_peak_initialization(self, X):
        """
        密度峰值算法选择初始聚类中心
        参考论文: Rodriguez & Laio, Science 2014
        """
        n_samples = X.shape[0]

        # 计算距离矩阵
        distances = euclidean_distances(X, X)

        # 计算局部密度
        # 使用截断距离 (dc为距离阈值，取距离分布的2%)
        dc_percentile = 2
        dc = np.percentile(distances[distances > 0], dc_percentile)

        # 计算每个点的局部密度
        rho = np.zeros(n_samples)
        for i in range(n_samples):
            rho[i] = np.sum(np.exp(-(distances[i, :] / dc) ** 2)) - 1

        # 计算到高密度点的最小距离
        delta = np.zeros(n_samples)
        sorted_rho_idx = np.argsort(-rho)  # 按密度降序排列

        for i, idx in enumerate(sorted_rho_idx):
            if i == 0:
                # 最高密度点，距离设为最大距离
                delta[idx] = np.max(distances[idx, :])
            else:
                # 到所有高密度点的最小距离
                higher_density_idx = sorted_rho_idx[:i]
                delta[idx] = np.min(distances[idx, higher_density_idx])

        # 计算决策函数 gamma = rho * delta
        # 归一化
        rho_norm = (rho - rho.min()) / (rho.max() - rho.min() + 1e-10)
        delta_norm = (delta - delta.min()) / (delta.max() - delta.min() + 1e-10)
        gamma = rho_norm * delta_norm

        # 选择gamma最高的n_clusters个点作为初始中心
        center_indices = np.argsort(-gamma)[:self.n_clusters]

        # 返回初始中心
        return X[center_indices].copy()

    def _compute_membership_entropy(self, U):
        """
        计算隶属度矩阵的熵
        用于自适应权重调整
        """
        n_samples = U.shape[0]

        # 避免log(0)
        U_safe = np.clip(U, 1e-10, 1.0)

        # 计算每个样本的熵
        entropy = -np.sum(U_safe * np.log(U_safe), axis=1)

        # 归一化到[0, 1]
        max_entropy = -np.log(1.0 / self.n_clusters)  # 最大熵
        normalized_entropy = entropy / max_entropy

        return normalized_entropy

    def _adaptive_weight_adjustment(self, X, centers, U):
        """
        自适应权重调整
        根据隶属度熵调整每个特征维度的重要性
        """
        n_samples, n_features = X.shape

        # 计算隶属度熵
        entropy = self._compute_membership_entropy(U)

        # 熵越高（不确定性越大），权重越低
        # 权重 = 1 - entropy^alpha
        alpha = 0.5  # 调整系数

        # 计算每个特征的基础权重（基于类间方差）
        feature_weights = np.ones(n_features)

        # 根据熵调整权重
        for j in range(n_features):
            # 计算类内散度
            cluster_variance = 0
            for k in range(self.n_clusters):
                cluster_points = X[U[:, k] > 0.5]
                if len(cluster_points) > 0:
                    variance = np.var(cluster_points[:, j])
                    cluster_variance += U[:, k].mean() * variance

            # 方差大的特征权重低
            if cluster_variance > 0:
                feature_weights[j] = 1.0 / (1.0 + cluster_variance)

        # 应用熵调整
        sample_weights = 1 - (entropy ** alpha)
        sample_weights = sample_weights / sample_weights.sum() * n_samples

        return feature_weights, sample_weights

    def fit(self, X, embeddings=None):
        """
        训练模型

        参数:
            X: 原始特征矩阵 (n_samples, n_features)
            embeddings: 知识图谱嵌入向量 (n_samples, embedding_dim)
        """
        # 特征融合：如果有嵌入向量，拼接在原始特征后面
        if embeddings is not None and len(embeddings) == X.shape[0]:
            X = np.hstack([X, embeddings])
            self.embedding_dim = embeddings.shape[1]

        n_samples, n_features = X.shape

        # 标准化
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # 初始化聚类中心
        if self.use_density_peak:
            self.centers = self._density_peak_initialization(X_scaled)
        else:
            # 随机选择初始中心
            idx = np.random.choice(n_samples, self.n_clusters, replace=False)
            self.centers = X_scaled[idx].copy()

        # 初始化隶属度矩阵
        self.U = np.zeros((n_samples, self.n_clusters))

        # 迭代更新
        for iteration in range(self.max_iter):
            # 计算距离矩阵
            distances = euclidean_distances(X_scaled, self.centers)

            # 避免除零
            distances = np.maximum(distances, 1e-10)

            # 更新隶属度矩阵
            U_new = np.zeros((n_samples, self.n_clusters))

            for i in range(n_samples):
                for k in range(self.n_clusters):
                    # FCM隶属度计算公式
                    sum_term = 0
                    for j in range(self.n_clusters):
                        sum_term += (distances[i, k] / distances[i, j]) ** (2 / (self.m - 1))

                    U_new[i, k] = 1.0 / sum_term if sum_term > 0 else 0

            # 自适应权重调整
            feature_weights, sample_weights = self._adaptive_weight_adjustment(
                X_scaled, self.centers, U_new
            )

            # 应用样本权重
            U_new = U_new * sample_weights[:, np.newaxis]
            U_new = U_new / U_new.sum(axis=1, keepdims=True)

            # 检查收敛
            if np.max(np.abs(U_new - self.U)) < self.epsilon:
                self.U = U_new
                break

            self.U = U_new

            # 更新聚类中心
            for k in range(self.n_clusters):
                um = self.U[:, k] ** self.m
                self.centers[k] = np.sum(X_scaled * um[:, np.newaxis], axis=0) / np.sum(um)

        # 计算最终标签（基于最大隶属度）
        self.cluster_labels_ = np.argmax(self.U, axis=1)

        # 计算隶属度熵
        self.membership_entropy_ = self._compute_membership_entropy(self.U)

        return self

    def predict(self, X, embeddings=None):
        """
        预测样本的隶属度

        参数:
            X: 原始特征矩阵
            embeddings: 知识图谱嵌入向量

        返回:
            隶属度矩阵
        """
        if embeddings is not None and len(embeddings) == X.shape[0]:
            X = np.hstack([X, embeddings])

        X_scaled = self.scaler.transform(X)
        n_samples = X_scaled.shape[0]

        # 计算到中心的距离
        distances = euclidean_distances(X_scaled, self.centers)
        distances = np.maximum(distances, 1e-10)

        # 计算隶属度
        U_pred = np.zeros((n_samples, self.n_clusters))
        for i in range(n_samples):
            for k in range(self.n_clusters):
                sum_term = 0
                for j in range(self.n_clusters):
                    sum_term += (distances[i, k] / distances[i, j]) ** (2 / (self.m - 1))
                U_pred[i, k] = 1.0 / sum_term if sum_term > 0 else 0

        return U_pred

    def get_cluster_centers(self):
        """获取聚类中心"""
        return self.centers

    def get_membership_matrix(self):
        """获取隶属度矩阵"""
        return self.U

    def get_membership_entropy(self):
        """获取隶属度熵"""
        return self.membership_entropy_

    def get_fuzzy_labels(self, threshold=0.5):
        """
        获取模糊标签
        如果样本对某个簇的隶属度超过阈值，则分配该标签
        可能返回一个样本多个标签
        """
        labels = []
        for i in range(len(self.U)):
            sample_labels = np.where(self.U[i] >= threshold)[0].tolist()
            if not sample_labels:
                # 如果没有超过阈值的，取最大隶属度的
                sample_labels = [np.argmax(self.U[i])]
            labels.append(sample_labels)
        return labels


def fcm_clustering_with_kg(n_clusters=4, use_embeddings=True):
    """
    基于知识图谱的FCM聚类主函数

    参数:
        n_clusters: 聚类数目
        use_embeddings: 是否使用知识图谱嵌入

    返回:
        聚类结果DataFrame
    """
    from django.conf import settings

    data_dir = settings.DATA_DIR

    # 读取用户画像数据
    profile_df = pd.read_csv(data_dir / 'user_profiles.csv')

    # 提取原始特征
    feature_cols = ['avg_daily_kwh', 'std_daily_kwh', 'max_daily_kwh', 'min_daily_kwh']
    X = profile_df[feature_cols].values

    # 计算变异系数
    cv = profile_df['std_daily_kwh'] / (profile_df['avg_daily_kwh'] + 1e-10)
    X = np.column_stack([X, cv.values])

    # 尝试读取嵌入向量
    embeddings = None
    if use_embeddings:
        try:
            embedding_file = data_dir / 'user_embeddings.csv'
            if embedding_file.exists():
                emb_df = pd.read_csv(embedding_file)
                embeddings = emb_df.drop('user_id', axis=1).values
                print(f"Loaded embeddings: {embeddings.shape}")
        except Exception as e:
            print(f"Could not load embeddings: {e}")

    # 执行改进FCM聚类
    fcm = ImprovedFCM(
        n_clusters=n_clusters,
        max_iter=100,
        m=2.0,
        use_density_peak=True
    )
    fcm.fit(X, embeddings)

    # 添加结果到DataFrame
    profile_df['fcm_cluster'] = fcm.cluster_labels_
    profile_df['membership_entropy'] = fcm.membership_entropy_

    # 添加各簇的隶属度
    for i in range(n_clusters):
        profile_df[f'membership_cluster_{i}'] = fcm.U[:, i]

    # 根据特征自动标记簇标签
    cluster_energies = profile_df.groupby('fcm_cluster')['avg_daily_kwh'].mean()
    sorted_clusters = cluster_energies.sort_values()

    label_map = {}
    label_names = ['节能型', '普通型', '波动型', '高耗能型']

    for idx, cluster_id in enumerate(sorted_clusters.index):
        if idx < len(label_names):
            label_map[cluster_id] = label_names[idx]
        else:
            label_map[cluster_id] = f'类型{idx}'

    profile_df['fcm_cluster_label'] = profile_df['fcm_cluster'].map(label_map)

    return profile_df, fcm


def get_fcm_cluster_summary():
    """获取FCM聚类摘要"""
    from django.conf import settings

    data_dir = settings.DATA_DIR

    # 检查是否有缓存的聚类结果
    result_file = data_dir / 'fcm_cluster_results.csv'

    try:
        if result_file.exists():
            df = pd.read_csv(result_file)
        else:
            df, _ = fcm_clustering_with_kg()
            df.to_csv(result_file, index=False)
    except Exception as e:
        print(f"Error in clustering: {e}")
        return []

    # 生成摘要
    summary = []
    for cluster_id in df['fcm_cluster'].unique():
        cluster_data = df[df['fcm_cluster'] == cluster_id]

        # 计算平均隶属度
        membership_cols = [c for c in df.columns if c.startswith('membership_cluster_')]
        avg_membership = cluster_data[membership_cols].mean().max()

        summary.append({
            'cluster_id': int(cluster_id),
            'cluster_label': cluster_data['fcm_cluster_label'].iloc[0],
            'user_count': len(cluster_data),
            'avg_energy': round(cluster_data['avg_daily_kwh'].mean(), 2),
            'avg_std': round(cluster_data['std_daily_kwh'].mean(), 2),
            'avg_membership': round(avg_membership, 3),
            'avg_entropy': round(cluster_data['membership_entropy'].mean(), 3),
            'users': cluster_data['user_id'].tolist()
        })

    return summary


def get_user_fcm_membership(user_id):
    """获取用户的FCM隶属度"""
    from django.conf import settings

    data_dir = settings.DATA_DIR
    result_file = data_dir / 'fcm_cluster_results.csv'

    if not result_file.exists():
        return None

    df = pd.read_csv(result_file)
    user_data = df[df['user_id'] == user_id]

    if user_data.empty:
        return None

    row = user_data.iloc[0]
    membership = {}

    for i in range(4):
        col = f'membership_cluster_{i}'
        if col in row:
            membership[int(i)] = round(float(row[col]), 4)

    return {
        'user_id': user_id,
        'cluster': int(row['fcm_cluster']),
        'cluster_label': row['fcm_cluster_label'],
        'membership': membership,
        'entropy': round(float(row['membership_entropy']), 4)
    }


if __name__ == '__main__':
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'power_profile.settings')
    django.setup()

    # 测试FCM聚类
    print("Running FCM clustering...")
    df, fcm = fcm_clustering_with_kg(n_clusters=4)

    print("\nCluster Summary:")
    summary = get_fcm_cluster_summary()
    for s in summary:
        print(f"Cluster {s['cluster_id']}: {s['cluster_label']} - {s['user_count']} users, "
              f"avg: {s['avg_energy']} kWh, entropy: {s['avg_entropy']}")
