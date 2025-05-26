# 测试专用设置文件
from .settings import *

# 测试数据库设置（使用内存数据库加速测试）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# 禁用调试模式
DEBUG = False

# 简化密码验证（加速测试）
AUTH_PASSWORD_VALIDATORS = []

# 禁用缓存
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# 禁用邮件发送
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# 简化日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    },
}

# 测试时禁用媒体文件处理
MEDIA_ROOT = '/tmp/test_media/'

# 加速测试的中间件设置
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# 测试时使用的秘钥
SECRET_KEY = 'test-secret-key-for-testing-only'

# 允许的主机
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# 测试覆盖率设置
COVERAGE_MODULE_EXCLUDES = [
    'tests$', 'settings$', 'urls$', 'locale$',
    'migrations', 'fixtures', 'admin$', 'django_extensions',
]

# 测试运行器
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# 测试并行设置
TEST_PARALLEL = True
