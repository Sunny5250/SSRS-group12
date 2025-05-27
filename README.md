# 📚 图书馆座位预约管理系统

一个基于Django开发的现代化图书馆座位预约管理系统，为学生、教师和管理员提供便捷的自习室预约服务。

## ✨ 功能特性

### 👥 多用户角色支持
- **学生用户**: 浏览自习室、创建预约、管理个人预约记录
- **教师用户**: 享有预约权限，可能具有优先预约权
- **管理员**: 系统管理、预约审核、数据统计

### 🏢 自习室管理
- 自习室信息展示（名称、位置、容量、设备）
- 自习室图片上传
- 实时预约状态查看
- 灵活的时间段配置

### 📅 预约系统
- 直观的预约界面
- 实时冲突检测
- 预约状态管理（待确认、已确认、已取消、已完成）
- 预约历史记录追踪
- 批量预约管理

### 🔧 管理功能
- 预约申请审核
- 用户权限管理
- 系统数据统计
- 搜索和筛选功能

### 📊 数据统计
- 个人预约统计
- 系统整体使用情况
- 预约趋势分析
- 导出功能

### 🛡️ 安全特性
- 用户认证和授权
- 数据验证和安全检查
- 跨站请求伪造(CSRF)保护
- 权限控制

## 🛠️ 技术栈

- **后端框架**: Django 4.2.7
- **API框架**: Django REST Framework 3.14.0
- **数据库**: SQLite (开发) / MySQL (生产)
- **前端**: HTML + CSS + JavaScript (Bootstrap)
- **测试框架**: pytest + pytest-django
- **图像处理**: Pillow
- **跨域支持**: django-cors-headers

## 📋 系统要求

- Python 3.8+
- Django 4.2+
- 现代浏览器支持

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd study_room_system
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 数据库配置

#### 开发环境（SQLite）
```bash
# 创建数据库迁移
python manage.py makemigrations

# 执行迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

#### 生产环境（MySQL）
1. 安装MySQL服务器
2. 创建数据库：
```sql
CREATE DATABASE study_room_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
3. 修改 `settings.py` 中的数据库配置：
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "study_room_db",
        "USER": "your_username",
        "PASSWORD": "your_password",
        "HOST": "localhost",
        "PORT": "3306",
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}
```

### 5. 生成示例数据

```bash
python populate_data.py
```

这将创建：
- 7个时间段（早8点到晚10点）
- 6个不同类型的自习室
- 测试用户账号
- 示例预约记录

### 6. 启动开发服务器

```bash
python manage.py runserver
```

访问 http://127.0.0.1:8000 查看应用

## 🧪 测试

### 运行所有测试
```bash
python run_tests.py
```

### 运行特定测试
```bash
# 单元测试
pytest -m unit

# 集成测试
pytest -m integration

# 性能测试
pytest -m performance

# 指定应用测试
pytest accounts/
pytest rooms/
pytest bookings/
```

### 测试覆盖率
```bash
pytest --cov=. --cov-report=html
```

查看覆盖率报告：打开 `htmlcov/index.html`

## 📁 项目结构

```
study_room_system/
├── accounts/              # 用户管理应用
│   ├── models.py         # 用户模型
│   ├── views.py          # 用户视图
│   └── urls.py           # 用户路由
├── rooms/                # 自习室管理应用
│   ├── models.py         # 自习室和时间段模型
│   ├── views.py          # 自习室视图
│   └── urls.py           # 自习室路由
├── bookings/             # 预约管理应用
│   ├── models.py         # 预约模型
│   ├── views.py          # 预约视图
│   ├── api_views.py      # API视图
│   ├── serializers.py    # API序列化器
│   └── urls.py           # 预约路由
├── test_dashboard/       # 测试仪表板
├── tests/                # 测试文件
├── templates/            # HTML模板
├── static/               # 静态文件
├── media/                # 媒体文件
├── study_room_system/    # 项目配置
│   ├── settings.py       # 项目设置
│   ├── urls.py           # 主路由
│   └── wsgi.py           # WSGI配置
├── manage.py             # Django管理脚本
├── requirements.txt      # 依赖文件
├── populate_data.py      # 示例数据生成
├── run_tests.py          # 测试运行脚本
└── pytest.ini           # pytest配置
```

## 🔑 默认账号

### 测试账号
- **学生账号**: `student1` / `testpass123`
- **学生账号**: `student2` / `testpass123`
- **教师账号**: `teacher1` / `testpass123`

### 管理员账号
通过以下命令创建：
```bash
python manage.py createsuperuser
```

## 🌐 API接口

系统提供RESTful API接口：

### 自习室相关
- `GET /api/rooms/` - 获取自习室列表
- `GET /api/rooms/{id}/` - 获取自习室详情

### 预约相关
- `GET /api/bookings/` - 获取预约列表
- `POST /api/bookings/` - 创建新预约
- `GET /api/bookings/{id}/` - 获取预约详情
- `PUT /api/bookings/{id}/` - 更新预约
- `DELETE /api/bookings/{id}/` - 删除预约

### 时间段相关
- `GET /api/timeslots/` - 获取时间段列表
- `GET /api/available-slots/{room_id}/{date}/` - 获取可用时间段

## 🚀 生产环境部署

### 1. 环境准备
```bash
# 安装生产环境依赖
pip install gunicorn
pip install whitenoise
```

### 2. 配置设置
修改 `settings.py`：
```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'your-ip-address']

# 静态文件配置
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... 其他中间件
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 3. 收集静态文件
```bash
python manage.py collectstatic
```

### 4. 启动生产服务器
```bash
gunicorn study_room_system.wsgi:application --bind 0.0.0.0:8000
```

### 5. 使用Nginx（推荐）
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /path/to/your/project/staticfiles/;
    }

    location /media/ {
        alias /path/to/your/project/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔧 配置说明

### 环境变量
建议使用环境变量管理敏感配置：

```bash
# .env 文件
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=mysql://user:password@localhost/dbname
ALLOWED_HOSTS=your-domain.com,your-ip
```

### 数据库配置
- **开发环境**: SQLite（默认）
- **生产环境**: MySQL（推荐）

### 缓存配置
生产环境建议配置Redis缓存：
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

## 📝 开发指南

### 代码规范
- 遵循PEP 8代码规范
- 使用有意义的变量和函数名
- 添加适当的注释和文档字符串

### 测试规范
- 为新功能编写测试用例
- 保持测试覆盖率在80%以上
- 使用pytest进行测试

### 提交规范
- 使用清晰的提交信息
- 每个提交只包含一个功能或修复
- 提交前运行测试确保代码质量

## 🐛 常见问题

### 1. 数据库连接错误
```bash
# 检查数据库服务是否启动
# 检查数据库配置是否正确
# 确保数据库用户有足够权限
```

### 2. 静态文件无法加载
```bash
# 运行收集静态文件命令
python manage.py collectstatic

# 检查STATIC_URL和STATIC_ROOT配置
```

### 3. 图片上传失败
```bash
# 检查MEDIA_URL和MEDIA_ROOT配置
# 确保media目录有写入权限
```

### 4. 测试失败
```bash
# 检查测试数据库配置
# 确保所有依赖已安装
# 查看具体错误信息
```

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

### 贡献步骤
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 项目Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 邮箱: your-email@example.com

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

**⭐ 如果这个项目对您有帮助，请给我们一个星标！** 
