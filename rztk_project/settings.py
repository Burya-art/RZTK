import environ
from pathlib import Path

# Инициализация environ
env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent
env.read_env(BASE_DIR / '.env')

# Основные настройки
SECRET_KEY = env('SECRET_KEY', default='django-insecure-xxu(cqz#-ie*ng-omy2y)q+tx))$mwidx(b8jlub=bo!(l%qq7')
DEBUG = env.bool('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', 'web'])

# Приложения
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shop.apps.ShopConfig',
    'products.apps.ProductsConfig',
    'basket.apps.BasketConfig',
    'orders.apps.OrdersConfig',
    'reviews.apps.ReviewsConfig',
    'django_redis',
    'django_celery_results',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rztk_project.urls'

# Шаблоны
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'rztk_project.context_processors.categories_and_brands',
            ],
        },
    },
]

WSGI_APPLICATION = 'rztk_project.wsgi.application'

# База данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='rztk_db'),
        'USER': env('DB_USER', default='rztk_user'),
        'PASSWORD': env('DB_PASSWORD', default='12345'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

# Старая база данных
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'rztk_db',
#         'USER': 'rztk_user',
#         'PASSWORD': '12345',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# Валидация паролей
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Интернационализация
LANGUAGE_CODE = 'uk'  # українська мова
TIME_ZONE = 'Europe/Kyiv'  # часова зона України
USE_I18N = True
USE_TZ = True

# Статические и медиа файлы
STATIC_URL = '/static/'
STATIC_ROOT = '/app/staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static/']
MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media'

# Автоинкремент
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Перенаправления
LOGIN_REDIRECT_URL = 'account:profile'
LOGOUT_REDIRECT_URL = 'products:product_list'
LOGIN_URL = 'account:login'

# Настройки Redis
REDIS_HOST = env('REDIS_HOST', default='127.0.0.1')
REDIS_PORT = env('REDIS_PORT', default='6379')
REDIS_DB = env('REDIS_DB', default='1')
REDIS_PASSWORD = env('REDIS_PASSWORD', default=None)

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}' if REDIS_PASSWORD else f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 3600,
    }
}

# Настройки RabbitMQ
RABBITMQ_HOST = env('RABBITMQ_HOST', default='localhost')
RABBITMQ_PORT = env('RABBITMQ_PORT', default='5672')
RABBITMQ_USER = env('RABBITMQ_USER', default='rztk_user')
RABBITMQ_PASSWORD = env('RABBITMQ_PASSWORD', default='12345')

# API Новая Почта
NOVA_POSHTA_API_KEY = env('NOVA_POSHTA_API_KEY', default='')

# Логирование
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Celery настройки
CELERY_BROKER_URL = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
