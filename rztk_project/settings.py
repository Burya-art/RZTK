import environ
from pathlib import Path

# Инициализация environ
env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent
env.read_env(BASE_DIR / '.env')

# Основные настройки
SECRET_KEY = env('SECRET_KEY', default='django-insecure-xxu(cqz#-ie*ng-omy2y)q+tx))$mwidx(b8jlub=bo!(l%qq7')
DEBUG = env.bool('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', 'web', 'rztk.store', 'www.rztk.store'])

# CSRF налаштування
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=['https://rztk.store', 'https://www.rztk.store'])

# Приложения
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Потрібно для allauth
    'rest_framework',
    'drf_yasg',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'shop.apps.ShopConfig',
    'products.apps.ProductsConfig',
    'basket.apps.BasketConfig',
    'orders.apps.OrdersConfig',
    'reviews.apps.ReviewsConfig',
    'account.apps.AccountConfig',
    'nova_poshta.apps.NovaPoshtaConfig',
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
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rztk_project.urls'

# Шаблоны
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# LiqPay налаштування
LIQPAY_PUBLIC_KEY = env('LIQPAY_PUBLIC_KEY', default='sandbox_i14605356113')
LIQPAY_PRIVATE_KEY = env('LIQPAY_PRIVATE_KEY', default='sandbox_DtTeFQZdPcpwHLR9j0QfGuEcrWdowgPMRnO7ZD4I')
LIQPAY_SANDBOX = env.bool('LIQPAY_SANDBOX', default=True)

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

# Django REST Framework налаштування
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# Django Allauth - соціальна аутентифікація
SITE_ID = 2  # ID сайту в Django sites framework (localhost:8000)

# Бекенди для аутентифікації (email + соціальний)
AUTHENTICATION_BACKENDS = [
    'account.backends.EmailBackend',  # Аутентифікація через email
    'django.contrib.auth.backends.ModelBackend',  # Звичайний логін/пароль (резерв)
    'allauth.account.auth_backends.AuthenticationBackend',  # Соціальні мережі
]

# Налаштування allauth 
SOCIALACCOUNT_QUERY_EMAIL = True  # Запитуємо email з соціальних мереж
SOCIALACCOUNT_LOGIN_ON_GET = True  # Автоматично переходимо до Google
SOCIALACCOUNT_AUTO_SIGNUP = True  # Автоматично створюємо акаунт через Google

# Основні налаштування входу
LOGIN_REDIRECT_URL = '/account/profile/'  # Куди перенаправити після успішного входу
LOGIN_URL = '/account/login/'  # Наша сторінка входу  
LOGOUT_REDIRECT_URL = '/'  # Куди перенаправити після виходу

# Відключаємо allauth перевизначення URLs
ACCOUNT_ADAPTER = 'allauth.account.adapter.DefaultAccountAdapter'
ACCOUNT_LOGIN_URL = None  # Не перевизначаємо login URL
ACCOUNT_SIGNUP_URL = None  # Не перевизначаємо signup URL

SOCIALACCOUNT_ADAPTER = 'account.adapters.GoogleSocialAccountAdapter'  # підключає кастомний адаптер

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': env('GOOGLE_OAUTH2_CLIENT_ID', default=''),
            'secret': env('GOOGLE_OAUTH2_CLIENT_SECRET', default=''),
        },
        'SCOPE': [  # запитує дозвіл на профіль, email і фото
            'profile',
            'email',
            'openid',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'VERIFIED_EMAIL': True,
    }
}
