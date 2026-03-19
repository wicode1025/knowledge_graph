"""
基于论文《考虑负荷季节特性的电力用户用电行为画像》的负荷特征提取模块
核心方法：
1. VMD变分模态分解 - 将负荷序列分解为多个本征模态函数(IMF)
2. 模糊熵(FE) - 表征负荷序列的复杂性
3. 多维特征提取 - 统计特征、频域特征、复杂性特征
4. 季节因子计算
5. DTW动态时间规整 - 典型日提取
"""

import numpy as np
import pandas as pd
from scipy import signal
from scipy.stats import skew, kurtosis
from scipy.spatial.distance import euclidean
from collections import Counter
import warnings
warnings.filterwarnings('ignore')


class LoadFeatureExtractor:
    """
    负荷特征提取器
    基于论文方法提取多维特征
    """

    def __init__(self, sampling_rate=96):
        """
        参数:
            sampling_rate: 采样率 (96 = 15分钟采样一天96个点)
        """
        self.sampling_rate = sampling_rate

    def vmd_decomposition(self, data, K=5, alpha=2000, tau=0.0, tol=1e-7, max_iter=500):
        """
        变分模态分解 (VMD)
        将信号分解为K个本征模态函数

        参数:
            data: 输入负荷序列
            K: 模态数量
            alpha: 带宽约束
            tau: 噪声容忍度
            tol: 收敛容差
            max_iter: 最大迭代次数

        返回:
            u: IMF分量数组 (K, n)
            omega: 中心频率数组
        """
        # 简化的VMD实现
        # 实际论文中会使用更完整的变分优化

        n = len(data)
        t = np.arange(n) / self.sampling_rate

        # 使用经验模态分解的简化版本
        imfs = []
        remainder = data.copy()

        for k in range(K):
            # 提取一个IMF
            imf = self._extract_imf(remainder)
            imfs.append(imf)
            remainder = remainder - imf

        if len(imfs) == 0:
            return np.array([data]), np.array([0])

        return np.array(imfs), np.array([0] * len(imfs))

    def _extract_imf(self, signal_data, max_iter=100):
        """提取本征模态函数 (简化版)"""
        h = signal_data.copy()
        for _ in range(max_iter):
            # 计算上下包络
            upper = self._get_envelope(h, 1)
            lower = self._get_envelope(h, -1)

            # 计算均值
            m = (upper + lower) / 2

            # 更新
            h = h - m

            # 检查是否满足IMF条件
            if self._is_imf(h):
                break

        return h

    def _get_envelope(self, signal_data, direction):
        """获取信号包络"""
        from scipy.interpolate import CubicSpline

        n = len(signal_data)
        x = np.arange(n)

        # 找极值点
        if direction > 0:
            peaks, _ = signal.find_peaks(signal_data)
        else:
            peaks, _ = signal.find_peaks(-signal_data)

        if len(peaks) < 2:
            return np.ones(n) * np.mean(signal_data)

        # 插值
        cs = CubicSpline(peaks, signal_data[peaks])
        envelope = cs(x)

        return envelope

    def _is_imf(self, signal_data):
        """检查是否满足IMF条件"""
        zero_crossings = len(np.where(np.diff(np.sign(signal_data)))[0])
        peaks, _ = signal.find_peaks(signal_data)

        # IMF条件：过零点数与极值点数相差不超过1
        return abs(zero_crossings - len(peaks)) <= 1

    def fuzzy_entropy(self, series, m=2, r_ratio=0.2):
        """
        计算模糊熵 (Fuzzy Entropy)
        表征时间序列的复杂性

        参数:
            series: 时间序列
            m: 嵌入维度
            r_ratio: 相似性阈值比例 (通常取0.1-0.3)

        返回:
            FE: 模糊熵值
        """
        N = len(series)

        # 标准化
        std = np.std(series)
        if std < 1e-10:
            return 0

        series = (series - np.mean(series)) / std

        # 相似性阈值
        r = r_ratio * np.std(series)

        def _fuzzy_distance(xi, xj, m, r):
            """模糊距离"""
            max_val = 0
            for k in range(m):
                diff = abs(xi[k] - xj[k])
                fuzzy = np.exp(-diff ** 2 / r ** 2)
                max_val = max(max_val, fuzzy)
            return max_val

        # 计算m维模式
        def phi(m):
            sum_val = 0
            for i in range(N - m):
                for j in range(N - m):
                    if i != j:
                        dist = 0
                        for k in range(m):
                            dist = max(dist, abs(series[i + k] - series[j + k]))
                        sum_val += np.exp(-dist ** 2 / r ** 2)
            return sum_val / ((N - m) * (N - m - 1) + 1e-10)

        try:
            phi_m = phi(m)
            phi_m1 = phi(m + 1)

            if phi_m < 1e-10 or phi_m1 < 1e-10:
                return 0

            FE = np.log(phi_m / phi_m1)
            return max(0, FE)
        except:
            return 0

    def sample_entropy(self, series, m=2, r_ratio=0.2):
        """
        样本熵 (Sample Entropy)
        """
        N = len(series)
        r = r_ratio * np.std(series)

        def _max_dist(xi, xj):
            return max(abs(xi - xj))

        # 构建模板
        templates_m = [series[i:i + m] for i in range(N - m)]
        templates_m1 = [series[i:i + m + 1] for i in range(N - m - 1)]

        # 计算匹配
        count_m = 0
        for template in templates_m:
            for other in templates_m:
                if np.allclose(template, other):
                    count_m += 1

        count_m1 = 0
        for template in templates_m1:
            for other in templates_m1:
                if np.allclose(template, other):
                    count_m1 += 1

        if count_m == 0:
            return 0

        return -np.log(count_m1 / count_m)

    def extract_statistical_features(self, load_series):
        """
        提取统计特征
        基于论文: 均值、方差、标准差、峰值、谷值、峰谷差、偏度、峰度
        """
        features = {
            'mean': np.mean(load_series),
            'variance': np.var(load_series),
            'std': np.std(load_series),
            'max': np.max(load_series),
            'min': np.min(load_series),
            'range': np.max(load_series) - np.min(load_series),
            'skewness': skew(load_series),
            'kurtosis': kurtosis(load_series),
            'cv': np.std(load_series) / (np.mean(load_series) + 1e-10),  # 变异系数
            'load_factor': np.mean(load_series) / (np.max(load_series) + 1e-10),  # 负荷率
            'peak_factor': np.max(load_series) / (np.mean(load_series) + 1e-10),  # 峰值因子
        }
        return features

    def extract_frequency_features(self, load_series):
        """
        提取频域特征
        基于论文: 主频、频谱熵、功率谱重心
        """
        n = len(load_series)

        # FFT
        fft_vals = np.fft.fft(load_series)
        fft_freq = np.fft.fftfreq(n, 1 / self.sampling_rate)

        # 只取正频率
        positive_freq_idx = fft_freq > 0
        positive_freq = fft_freq[positive_freq_idx]
        positive_amp = np.abs(fft_vals[positive_freq_idx])

        # 功率谱
        power_spectrum = positive_amp ** 2
        power_spectrum_norm = power_spectrum / (np.sum(power_spectrum) + 1e-10)

        # 主频
        dominant_freq = positive_freq[np.argmax(positive_amp)]

        # 频谱熵
        spectrum_entropy = -np.sum(power_spectrum_norm * np.log(power_spectrum_norm + 1e-10))

        # 功率谱重心
        spectral_centroid = np.sum(positive_freq * power_spectrum) / (np.sum(power_spectrum) + 1e-10)

        features = {
            'dominant_freq': dominant_freq,
            'spectrum_entropy': spectrum_entropy,
            'spectral_centroid': spectral_centroid,
            'spectral_energy': np.sum(power_spectrum),
        }

        return features

    def extract_complexity_features(self, load_series):
        """
        提取复杂性特征
        基于论文: 模糊熵、样本熵、排列熵
        """
        # 模糊熵
        fe = self.fuzzy_entropy(load_series, m=2, r_ratio=0.2)

        # 样本熵
        se = self.sample_entropy(load_series, m=2, r_ratio=0.2)

        # 排列熵
        pe = self.permutation_entropy(load_series, order=3)

        # VMD分解后的各IMF模糊熵
        imfs, _ = self.vmd_decomposition(load_series, K=3)
        imf_fuzzy_entropies = []
        for imf in imfs:
            imf_fe = self.fuzzy_entropy(imf, m=2, r_ratio=0.2)
            imf_fuzzy_entropies.append(imf_fe)

        features = {
            'fuzzy_entropy': fe,
            'sample_entropy': se,
            'permutation_entropy': pe,
            'vmd_imf_entropy_mean': np.mean(imf_fuzzy_entropies) if imf_fuzzy_entropies else 0,
            'vmd_imf_entropy_std': np.std(imf_fuzzy_entropies) if imf_fuzzy_entropies else 0,
            'num_imf_components': len(imfs),
        }

        return features

    def permutation_entropy(self, series, order=3, delay=1):
        """
        排列熵 (Permutation Entropy)
        衡量时间序列的复杂性
        """
        n = len(series)

        # 构建排列模式
        patterns = []
        for i in range(n - order * delay):
            pattern = []
            for j in range(order):
                pattern.append(series[i + j * delay])
            # 排序得到排列索引
            sorted_idx = np.argsort(pattern)
            patterns.append(tuple(sorted_idx))

        # 统计各模式出现次数
        pattern_counts = Counter(patterns)

        # 计算熵
        total = sum(pattern_counts.values())
        entropy = 0
        for count in pattern_counts.values():
            p = count / total
            if p > 0:
                entropy -= p * np.log(p)

        # 归一化
        max_entropy = np.log(np.math.factorial(order))
        if max_entropy > 0:
            entropy = entropy / max_entropy

        return entropy

    def extract_all_features(self, load_series):
        """
        提取所有特征
        整合统计特征、频域特征、复杂性特征
        """
        stat_features = self.extract_statistical_features(load_series)
        freq_features = self.extract_frequency_features(load_series)
        complexity_features = self.extract_complexity_features(load_series)

        return {**stat_features, **freq_features, **complexity_features}


class SeasonalAnalyzer:
    """
    季节特性分析器
    基于论文方法分析用户的季节特性
    """

    def __init__(self):
        self.seasons = ['spring', 'summer', 'autumn', 'winter']
        self.season_names = {'spring': '春季', 'summer': '夏季', 'autumn': '秋季', 'winter': '冬季'}

    def get_season_from_date(self, date):
        """根据日期判断季节"""
        month = pd.to_datetime(date).month

        if month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        elif month in [9, 10, 11]:
            return 'autumn'
        else:
            return 'winter'

    def calculate_season_factor(self, daily_loads):
        """
        计算季节因子
        论文公式: Sf = (1/n) * Σ(Pi / Pavg)
        """
        daily_loads = np.array(daily_loads)
        avg_load = np.mean(daily_loads)

        if avg_load < 1e-10:
            return 1.0

        factors = daily_loads / avg_load
        season_factor = np.mean(factors)

        return season_factor

    def calculate_season_load_ratio(self, df, date_col='date', load_col='total_kwh'):
        """
        计算各季节用电量占比
        """
        df = df.copy()
        df['season'] = df[date_col].apply(self.get_season_from_date)

        season_loads = df.groupby('season')[load_col].sum()
        total_load = season_loads.sum()

        ratios = {}
        for season in self.seasons:
            if season in season_loads.index:
                ratios[season] = season_loads[season] / (total_load + 1e-10)
            else:
                ratios[season] = 0

        return ratios

    def get_season_adaptation(self, user_loads_df):
        """
        获取用户季节适应性
        识别用户是夏季高负荷型还是冬季高负荷型
        """
        ratios = self.calculate_season_load_ratio(user_loads_df)

        # 识别主要季节
        max_season = max(ratios, key=ratios.get)
        min_season = min(ratios, key=ratios.get)

        adaptation = {
            'dominant_season': max_season,
            'dominant_season_name': self.season_names[max_season],
            'dominant_ratio': ratios[max_season],
            'lowest_season': min_season,
            'seasonality_index': ratios[max_season] - ratios[min_season],  # 季节性指数
            'ratios': {k: round(v, 4) for k, v in ratios.items()},
            'ratios_cn': {self.season_names[k]: round(v, 4) for k, v in ratios.items()},
        }

        # 季节适应性标签
        if ratios['summer'] > 0.35 and ratios['summer'] > ratios['winter'] * 1.2:
            adaptation['label'] = '夏季敏感型'
            adaptation['description'] = '夏季用电量明显高于其他季节，可能与空调使用相关'
        elif ratios['winter'] > 0.35 and ratios['winter'] > ratios['summer'] * 1.2:
            adaptation['label'] = '冬季敏感型'
            adaptation['description'] = '冬季用电量明显高于其他季节，可能与取暖设备相关'
        elif ratios['spring'] > 0.3 and ratios['autumn'] > 0.3:
            adaptation['label'] = '平稳型'
            adaptation['description'] = '季节性变化较小，用电较为平稳'
        else:
            adaptation['label'] = '均衡型'
            adaptation['description'] = '各季节用电量相对均衡'

        return adaptation


class TypicalDayExtractor:
    """
    典型日提取器
    基于论文: 使用DTW距离的K-means++聚类提取典型日
    """

    def __init__(self):
        pass

    def dtw_distance(self, series1, series2):
        """
        计算动态时间规整(DTW)距离
        用于衡量两个时间序列的相似性
        """
        n, m = len(series1), len(series2)

        # 构建成本矩阵
        dtw_matrix = np.full((n + 1, m + 1), np.inf)
        dtw_matrix[0, 0] = 0

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                cost = abs(series1[i - 1] - series2[j - 1])
                dtw_matrix[i, j] = cost + min(
                    dtw_matrix[i - 1, j],      # 插入
                    dtw_matrix[i, j - 1],     # 删除
                    dtw_matrix[i - 1, j - 1]  # 匹配
                )

        return dtw_matrix[n, m]

    def normalize_series(self, series):
        """标准化序列"""
        std = np.std(series)
        if std < 1e-10:
            return np.zeros_like(series)
        return (series - np.mean(series)) / std

    def kmeans_plusplus_init(self, data, k):
        """K-means++初始化"""
        centroids = [data[0]]
        for _ in range(1, k):
            distances = np.array([min([np.linalg.norm(x - c) for c in centroids]) for x in data])
            probabilities = distances / distances.sum()
            idx = np.random.choice(len(data), p=probabilities)
            centroids.append(data[idx])
        return np.array(centroids)

    def kmeans_with_dtw(self, daily_loads, k=3, max_iter=50):
        """
        使用DTW距离的K-means聚类
        提取典型日
        """
        # 标准化
        normalized_loads = [self.normalize_series(load) for load in daily_loads]

        # K-means++初始化
        centroids = self.kmeans_plusplus_init(normalized_loads, k)

        labels = np.zeros(len(daily_loads))

        for iteration in range(max_iter):
            # 分配到最近的中心
            new_labels = []
            for load in normalized_loads:
                distances = [self.dtw_distance(load, c) for c in centroids]
                new_labels.append(np.argmin(distances))

            new_labels = np.array(new_labels)

            # 检查收敛
            if np.array_equal(labels, new_labels):
                break

            labels = new_labels

            # 更新中心
            for i in range(k):
                cluster_loads = [normalized_loads[j] for j in range(len(normalized_loads)) if labels[j] == i]
                if cluster_loads:
                    centroids[i] = np.mean(cluster_loads, axis=0)

        # 计算各簇的代表日（距离中心最近的日）
        typical_days = []
        for i in range(k):
            cluster_loads = [normalized_loads[j] for j in range(len(normalized_loads)) if labels[j] == i]
            if cluster_loads:
                centroid = centroids[i]
                distances = [self.dtw_distance(load, centroid) for load in cluster_loads]
                # 找到距离中心最近的原始负荷序列
                original_idx = [j for j in range(len(normalized_loads)) if labels[j] == i][np.argmin(distances)]
                typical_days.append({
                    'cluster': i,
                    'typical_index': original_idx,
                    'typical_load': daily_loads[original_idx],
                    'count': len(cluster_loads),
                    'avg_load': np.mean([daily_loads[j] for j in range(len(daily_loads)) if labels[j] == i])
                })

        return labels, typical_days, centroids

    def extract_typical_days(self, user_loads_df, n_clusters=3):
        """
        提取用户的典型用电日

        参数:
            user_loads_df: 用户日负荷DataFrame，需要有date和total_kwh列
            n_clusters: 聚类数量

        返回:
            典型日信息
        """
        # 获取每日负荷曲线（如果有每15分钟数据）
        # 这里简化处理，使用日用电量
        daily_loads = user_loads_df['total_kwh'].values

        if len(daily_loads) < n_clusters:
            return None

        labels, typical_days, centroids = self.kmeans_with_dtw(daily_loads, k=n_clusters)

        # 按平均负荷排序典型日
        typical_days = sorted(typical_days, key=lambda x: x['avg_load'])

        result = {
            'typical_days': typical_days,
            'labels': labels.tolist(),
            'n_clusters': n_clusters,
        }

        return result


def extract_user_seasonal_features(user_id, data_dir):
    """
    提取用户的季节性特征（整合所有方法）

    参数:
        user_id: 用户ID
        data_dir: 数据目录路径

    返回:
        用户季节性特征字典
    """
    from django.conf import settings

    if data_dir is None:
        from pathlib import Path
        data_dir = Path(settings.DATA_DIR)

    # 读取用电数据
    consumption_file = data_dir / 'daily_consumption.csv'

    if not consumption_file.exists():
        return None

    df = pd.read_csv(consumption_file)
    user_df = df[df['user_id'] == user_id].copy()

    if user_df.empty:
        return None

    # 特征提取器
    extractor = LoadFeatureExtractor()
    seasonal_analyzer = SeasonalAnalyzer()
    typical_extractor = TypicalDayExtractor()

    # 1. 统计特征
    load_series = user_df['total_kwh'].values
    stat_features = extractor.extract_statistical_features(load_series)

    # 2. 频域特征
    freq_features = extractor.extract_frequency_features(load_series)

    # 3. 复杂性特征
    complexity_features = extractor.extract_complexity_features(load_series)

    # 4. 季节适应性分析
    season_adaptation = seasonal_analyzer.get_season_adaptation(user_df)

    # 5. 典型日提取
    typical_days = typical_extractor.extract_typical_days(user_df, n_clusters=3)

    # 整合所有特征
    result = {
        'user_id': user_id,
        'statistical_features': {k: round(v, 4) for k, v in stat_features.items()},
        'frequency_features': {k: round(v, 4) for k, v in freq_features.items()},
        'complexity_features': {k: round(v, 4) for k, v in complexity_features.items()},
        'season_adaptation': season_adaptation,
        'typical_days': typical_days,
    }

    return result


if __name__ == '__main__':
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'power_profile.settings')
    django.setup()

    from django.conf import settings
    data_dir = settings.DATA_DIR

    # 测试特征提取
    print("Testing feature extraction...")

    extractor = LoadFeatureExtractor()

    # 生成测试负荷序列
    test_load = np.random.rand(96) * 2 + 1

    features = extractor.extract_all_features(test_load)
    print("Statistical features:", list(features.keys())[:8])
    print("Frequency features:", list(features.keys())[8:12])
    print("Complexity features:", list(features.keys())[12:])
