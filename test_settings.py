from rztk_project.settings import *

# Переключаємо на SQLite для тестів
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Відключаємо міграції для швидкості
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Використовуємо локальний кеш для тестів
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Прискорюємо хешування паролів для тестів
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]