"""
TransE图嵌入模块 - 基于论文《基于知识图谱与改进FCM算法的电力用户数据聚类分析方法》
实现TransE算法学习用户嵌入向量，用于增强用户画像和聚类
"""

import numpy as np
import pandas as pd
from collections import defaultdict
import random


class TransEEmbedding:
    """
    TransE图嵌入算法实现

    核心思想: h + r ≈ t
    - h: 头实体向量
    - r: 关系向量
    - t: 尾实体向量
    """

    def __init__(self, embedding_dim=64, learning_rate=0.01, margin=1.0,
                 n_epochs=500, batch_size=128, normalizer_l=2):
        """
        参数:
            embedding_dim: 嵌入维度
            learning_rate: 学习率
            margin: 间隔边界
            n_epochs: 训练轮数
            batch_size: 批大小
            normalizer_l: L2范数归一化
        """
        self.embedding_dim = embedding_dim
        self.learning_rate = learning_rate
        self.margin = margin
        self.n_epochs = n_epochs
        self.batch_size = batch_size
        self.normalizer_l = normalizer_l

        self.entity_embeddings = {}
        self.relation_embeddings = {}

    def _initialize_embeddings(self, entities, relations):
        """初始化实体和关系嵌入"""
        scale = 0.1

        for entity in entities:
            # 随机初始化，服从均匀分布
            self.entity_embeddings[entity] = np.random.uniform(
                -scale, scale, self.embedding_dim
            ).astype(np.float32)

        for relation in relations:
            self.relation_embeddings[relation] = np.random.uniform(
                -scale, scale, self.embedding_dim
            ).astype(np.float32)

    def _normalize_embeddings(self):
        """对嵌入向量进行L2归一化"""
        for entity in self.entity_embeddings:
            norm = np.linalg.norm(self.entity_embeddings[entity])
            if norm > 0:
                self.entity_embeddings[entity] /= norm

    def _distance(self, h, r, t):
        """计算三元组的距离 (L1 or L2)"""
        # h + r - t
        diff = h + r - t

        if self.normalizer_l == 1:
            return np.sum(np.abs(diff))
        else:
            return np.sum(diff ** 2)

    def _sample_negative_triplets(self, triplets, entities):
        """
        采样负样本三元组
        策略: 替换头实体或尾实体
        """
        negative_triplets = []

        for triplet in triplets:
            h, r, t = triplet

            # 随机决定替换头实体还是尾实体 (50%概率)
            if random.random() < 0.5:
                # 替换头实体
                h_neg = random.choice(entities)
                negative_triplets.append((h_neg, r, t))
            else:
                # 替换尾实体
                t_neg = random.choice(entities)
                negative_triplets.append((h, r, t_neg))

        return negative_triplets

    def _get_embeddings(self, triplet):
        """获取三元组的嵌入向量"""
        h, r, t = triplet

        # 如果实体不在嵌入表中，返回None
        if h not in self.entity_embeddings:
            return None
        if t not in self.entity_embeddings:
            return None
        if r not in self.relation_embeddings:
            return None

        return (
            self.entity_embeddings[h].copy(),
            self.relation_embeddings[r].copy(),
            self.entity_embeddings[t].copy()
        )

    def fit(self, triplets, entities, relations):
        """
        训练TransE模型

        参数:
            triplets: 三元组列表 [(h, r, t), ...]
            entities: 实体列表
            relations: 关系列表
        """
        print(f"Training TransE with {len(triplets)} triplets...")
        print(f"Entities: {len(entities)}, Relations: {len(relations)}")

        # 初始化嵌入
        self._initialize_embeddings(entities, relations)
        self._normalize_embeddings()

        # 训练
        for epoch in range(self.n_epochs):
            # 打乱三元组顺序
            random.shuffle(triplets)

            total_loss = 0.0
            n_batches = len(triplets) // self.batch_size + 1

            for batch_idx in range(n_batches):
                start = batch_idx * self.batch_size
                end = min(start + self.batch_size, len(triplets))
                batch = triplets[start:end]

                if len(batch) == 0:
                    continue

                # 采样负样本
                negative_batch = self._sample_negative_triplets(batch, entities)

                # 计算损失
                loss = 0.0

                for i, (pos_triplet, neg_triplet) in enumerate(zip(batch, negative_batch)):
                    pos_emb = self._get_embeddings(pos_triplet)
                    neg_emb = self._get_embeddings(neg_triplet)

                    if pos_emb is None or neg_emb is None:
                        continue

                    pos_h, pos_r, pos_t = pos_emb
                    neg_h, neg_r, neg_t = neg_emb

                    # 计算距离
                    pos_dist = self._distance(pos_h, pos_r, pos_t)
                    neg_dist = self._distance(neg_h, neg_r, neg_t)

                    # TransE损失函数 (margin-based ranking loss)
                    loss += max(0, pos_dist - neg_dist + self.margin)

                if loss > 0:
                    total_loss += loss

                    # 梯度更新 (简化版SGD)
                    for i, (pos_triplet, neg_triplet) in enumerate(zip(batch, negative_batch)):
                        pos_emb = self._get_embeddings(pos_triplet)
                        neg_emb = self._get_embeddings(neg_triplet)

                        if pos_emb is None or neg_emb is None:
                            continue

                        pos_h, pos_r, pos_t = pos_emb
                        neg_h, neg_r, neg_t = neg_emb

                        # 计算梯度 (简化)
                        pos_diff = pos_h + pos_r - pos_t
                        neg_diff = neg_h + neg_r - neg_t

                        # 更新实体嵌入
                        for entity in [pos_triplet[0], neg_triplet[0]]:
                            if entity in self.entity_embeddings:
                                self.entity_embeddings[entity] -= self.learning_rate * (pos_diff - neg_diff)

                        for entity in [pos_triplet[2], neg_triplet[2]]:
                            if entity in self.entity_embeddings:
                                self.entity_embeddings[entity] -= self.learning_rate * (-pos_diff + neg_diff)

                        # 更新关系嵌入
                        for relation in [pos_triplet[1], neg_triplet[1]]:
                            if relation in self.relation_embeddings:
                                self.relation_embeddings[relation] -= self.learning_rate * (pos_diff - neg_diff)

            # 归一化
            self._normalize_embeddings()

            if (epoch + 1) % 50 == 0:
                avg_loss = total_loss / len(triplets) if len(triplets) > 0 else 0
                print(f"Epoch {epoch + 1}/{self.n_epochs}, Loss: {avg_loss:.4f}")

        print("Training completed!")

    def get_entity_embedding(self, entity):
        """获取实体的嵌入向量"""
        return self.entity_embeddings.get(entity, None)

    def get_similar_entities(self, entity, top_k=5):
        """找到相似的实体"""
        if entity not in self.entity_embeddings:
            return []

        entity_vec = self.entity_embeddings[entity]
        similarities = []

        for other_entity, other_vec in self.entity_embeddings.items():
            if other_entity != entity:
                # 计算余弦相似度
                dot_product = np.dot(entity_vec, other_vec)
                norm_product = np.linalg.norm(entity_vec) * np.linalg.norm(other_vec)
                similarity = dot_product / (norm_product + 1e-10)
                similarities.append((other_entity, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]


def extract_kg_triplets():
    """
    从知识图谱中提取三元组

    返回:
        triplets: 三元组列表
        entities: 实体列表
        relations: 关系列表
    """
    from django.conf import settings

    data_dir = settings.DATA_DIR

    # 读取数据
    users_df = pd.read_csv(data_dir / 'user_profiles.csv')
    devices_df = pd.read_csv(data_dir / 'devices.csv')

    triplets = []
    entities = set()
    relations = set()

    # 用户 -> 拥有设备 -> 设备
    for _, row in devices_df.iterrows():
        user_id = row['user_id']
        device_id = row['device_id']

        triplets.append((user_id, 'OWNS', device_id))
        entities.add(user_id)
        entities.add(device_id)
        relations.add('OWNS')

    # 用户 -> 能耗等级 -> EnergyLevel
    for _, row in users_df.iterrows():
        user_id = row['user_id']
        energy_level = row['energy_level']

        if pd.notna(energy_level):
            triplets.append((user_id, 'HAS_ENERGY_LEVEL', energy_level))
            entities.add(user_id)
            entities.add(energy_level)
            relations.add('HAS_ENERGY_LEVEL')

    # 用户 -> 行为标签 -> BehaviorLabel
    for _, row in users_df.iterrows():
        user_id = row['user_id']
        behavior_label = row['behavior_label']

        if pd.notna(behavior_label):
            triplets.append((user_id, 'HAS_BEHAVIOR_LABEL', behavior_label))
            entities.add(user_id)
            entities.add(behavior_label)
            relations.add('HAS_BEHAVIOR_LABEL')

    # 用户 -> 用电模式 -> ConsumptionPattern
    for _, row in users_df.iterrows():
        user_id = row['user_id']
        pattern = row['consumption_pattern']

        if pd.notna(pattern):
            triplets.append((user_id, 'FOLLOWS_PATTERN', pattern))
            entities.add(user_id)
            entities.add(pattern)
            relations.add('FOLLOWS_PATTERN')

    # 用户 -> 相似用户 (基于聚类)
    # 从K-means聚类结果中获取相似用户对
    try:
        from kg.clustering import get_cluster_summary
        summary = get_cluster_summary()

        for cluster in summary:
            users_list = cluster.get('users', [])
            for i, user1 in enumerate(users_list):
                for user2 in users_list[i+1:]:
                    # 互为相似用户
                    triplets.append((user1, 'SIMILAR_TO', user2))
                    triplets.append((user2, 'SIMILAR_TO', user1))
                    entities.add(user1)
                    entities.add(user2)
                    relations.add('SIMILAR_TO')
    except Exception as e:
        print(f"Could not add similarity triplets: {e}")

    # 设备 -> 关联设备 (基于共现分析)
    # 这里简化处理，实际可以从设备共现数据中获取

    return triplets, list(entities), list(relations)


def train_and_save_embeddings(embedding_dim=64):
    """
    训练并保存用户嵌入向量
    """
    from django.conf import settings
    import os

    data_dir = settings.DATA_DIR

    # 提取三元组
    triplets, entities, relations = extract_kg_triplets()

    if len(triplets) == 0:
        print("No triplets found!")
        return None

    # 创建并训练TransE模型
    model = TransEEmbedding(
        embedding_dim=embedding_dim,
        learning_rate=0.01,
        margin=1.0,
        n_epochs=300,
        batch_size=32
    )

    model.fit(triplets, entities, relations)

    # 提取用户嵌入向量
    users_df = pd.read_csv(data_dir / 'user_profiles.csv')

    embeddings_list = []
    for _, row in users_df.iterrows():
        user_id = row['user_id']
        embedding = model.get_entity_embedding(user_id)

        if embedding is not None:
            emb_dict = {'user_id': user_id}
            for i, val in enumerate(embedding):
                emb_dict[f'emb_{i}'] = val
            embeddings_list.append(emb_dict)

    # 保存嵌入向量
    if embeddings_list:
        embeddings_df = pd.DataFrame(embeddings_list)
        output_file = data_dir / 'user_embeddings.csv'
        embeddings_df.to_csv(output_file, index=False)
        print(f"Saved embeddings to {output_file}")

    return embeddings_df


def get_user_embedding(user_id, embedding_dim=64):
    """
    获取指定用户的嵌入向量

    参数:
        user_id: 用户ID
        embedding_dim: 嵌入维度

    返回:
        嵌入向量numpy数组
    """
    from django.conf import settings
    import os

    data_dir = settings.DATA_DIR
    embedding_file = data_dir / 'user_embeddings.csv'

    if not embedding_file.exists():
        # 如果文件不存在，先训练
        print("Embeddings file not found. Training...")
        train_and_save_embeddings(embedding_dim)

    if embedding_file.exists():
        df = pd.read_csv(embedding_file)
        user_row = df[df['user_id'] == user_id]

        if not user_row.empty:
            emb_cols = [c for c in df.columns if c.startswith('emb_')]
            return user_row[emb_cols].values[0]

    return None


def get_all_embeddings():
    """
    获取所有用户的嵌入向量

    返回:
        包含所有用户嵌入的DataFrame
    """
    from django.conf import settings
    data_dir = settings.DATA_DIR
    embedding_file = data_dir / 'user_embeddings.csv'

    if not embedding_file.exists():
        return None

    df = pd.read_csv(embedding_file)
    return df


def compute_user_similarity(user_id1, user_id2, embedding_dim=64):
    """
    计算两个用户基于图嵌入的语义相似度

    参数:
        user_id1: 用户1 ID
        user_id2: 用户2 ID
        embedding_dim: 嵌入维度

    返回:
        相似度 (0-1)
    """
    emb1 = get_user_embedding(user_id1, embedding_dim)
    emb2 = get_user_embedding(user_id2, embedding_dim)

    if emb1 is None or emb2 is None:
        return None

    # 余弦相似度
    dot_product = np.dot(emb1, emb2)
    norm_product = np.linalg.norm(emb1) * np.linalg.norm(emb2)

    similarity = dot_product / (norm_product + 1e-10)

    # 归一化到0-1
    return (similarity + 1) / 2


if __name__ == '__main__':
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'power_profile.settings')
    django.setup()

    # 测试TransE嵌入
    print("Training TransE embeddings...")

    triplets, entities, relations = extract_kg_triplets()
    print(f"Total triplets: {len(triplets)}")
    print(f"Unique entities: {len(entities)}")
    print(f"Unique relations: {len(relations)}")

    # 训练
    embeddings_df = train_and_save_embeddings(embedding_dim=32)

    if embeddings_df is not None:
        print(f"\nEmbedding shape: {embeddings_df.shape}")
        print(embeddings_df.head())
