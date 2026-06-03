# 本地配置文件模板
# 复制此文件为 settings.local.py 并填入实际值

# MySQL数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'electric_user_profile',
        'USER': 'root',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

NEO4J_CONFIG = {
    'URI': 'bolt://localhost:7687',
    'AUTH': ('neo4j', 'your_neo4j_password'),
    'DATABASE': 'neo4j',
}

SECRET_KEY = 'django-insecure-your-secret-key-here'
