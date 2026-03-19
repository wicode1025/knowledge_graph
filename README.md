# 电力用户画像系统

## 项目简介

基于知识图谱的电力用户画像系统，使用 Django + Neo4j + Vue 开发。

## 技术栈

- **后端**: Django 6 + Django REST Framework
- **数据库**: SQLite (业务数据) + Neo4j (知识图谱)
- **前端**: Vue 3 + ECharts + Vue Router
- **数据预处理**: Pandas

## 项目结构

```
knowledege_graph/
├── data/                    # 原始数据 (11个CSV文件)
├── processed_data/          # 预处理后的数据
├── frontend/                # Vue前端项目
│   └── src/
│       ├── api/             # API调用
│       ├── router/          # 路由配置
│       └── views/           # 页面组件
├── kg/                      # Django知识图谱应用
│   ├── models.py           # 数据模型
│   ├── views.py            # API视图
│   ├── urls.py             # URL路由
│   └── neo4j_db.py         # Neo4j连接
├── power_profile/          # Django项目配置
├── manage.py
└── data_preprocessing.py   # 数据预处理脚本
```

## 启动步骤

### 1. 启动后端
```bash
cd D:\Doc\Python\knowledege_graph
python manage.py runserver
```
后端地址: http://localhost:8000

### 2. 启动前端
```bash
cd D:\Doc\Python\knowledege_graph\frontend
npm run dev
```
前端地址: http://localhost:5173

### 3. 启动Neo4j (如已安装)
```bash
neo4j console
```
Neo4j Browser: http://localhost:7474

## API接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/kg/profile/` | GET | 用户画像 |
| `/api/kg/consumption/` | GET | 每日用电 |
| `/api/kg/weather/` | GET | 天气数据 |
| `/api/kg/devices/` | GET | 设备列表 |
| `/api/kg/graph/` | GET | 知识图谱数据 |
| `/api/kg/import/` | POST | 导入Neo4j |

## 功能页面

1. **首页** - 仪表盘，显示用户信息和用电趋势图
2. **用户画像** - 详细用户信息，月度用气量统计
3. **设备** - 设备列表，各设备用电占比饼图
4. **知识图谱** - Neo4j图谱数据，导入功能

## Neo4j数据

导入后包含:
- 1个家庭用户节点
- 4个设备节点 (干衣机、洗碗机、暖通空调、热水器)
- 30个天气节点
- 4个拥有关系
