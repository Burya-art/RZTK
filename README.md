# RZTK - Django E-commerce Platform

🛍️ Інтернет-магазин електроніки розроблений на Django для продажу смартфонів та аксесуарів.

**Сайт:** https://rztk.store

## 🚀 Основні функції

- **Каталог товарів** з PostgreSQL full-text пошуком
- **Автентифікація** через email + Google OAuth
- **Кошик покупок** та обробка замовлень
- **Система відгуків** на товари
- **Інтеграція з Новою Поштою** для доставки
- **Адмін-панель** для управління

## 🛠️ Технології

- **Backend:** Django 5.2.1, DRF 3.15.2, Python 3.11
- **Database:** PostgreSQL 16 (з тригрм пошуком)
- **Cache:** Redis 7
- **Queue:** Celery 5.4.0 + RabbitMQ 3
- **Deploy:** Docker + Docker Compose
- **Testing:** pytest

## 📋 Швидкий старт

### Локальна розробка
# Запуск через Docker
docker-compose up -d

# Міграції
docker-compose run --rm web python manage.py migrate

# Створення суперкористувача
docker-compose run --rm web python manage.py createsuperuser

# Сайт доступний на: http://localhost:8000


### Тестування
# Всі тести
docker-compose run --rm test

# Конкретний додаток
docker-compose run --rm test pytest products/tests/ -v


## 🏗️ Архітектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Django Web    │    │   PostgreSQL    │    │     Redis       │
│    (Port 8000)  │────│   (Port 5432)   │    │   (Port 6379)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Celery      │    │    RabbitMQ     │    │     Nginx       │
│  (Background)   │────│   (Port 5672)   │    │   (Port 8080)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Структура проекту

```
RZTK/
├── account/          # Автентифікація + профілі
├── basket/           # Кошик покупок
├── orders/           # Замовлення + платежі
├── products/         # Каталог товарів
├── reviews/          # Відгуки
├── nova_poshta/      # API Нової Пошти
├── shop/             # Загальні шаблони
├── rztk_project/     # Налаштування Django
├── docker-compose.yml
└── requirements.txt
```

### API Endpoints
- `/api/` - Products API
- `/api/account/` - User API
- `/api/docs/` - Swagger документація
- `/admin/` - Django Admin

## 🚀 Деплой

1. **Резервне копіювання**
2. **Синхронізація файлів**
3. **Перебудова Docker образів**
4. **Застосування міграцій**
5. **Запуск сервісів**

Детальні інструкції як деплоїти: `DEPLOY_INSTRUCTIONS.md`

## 📧 Контакти

- **Автор:** Ihor Burchik
- **Email:** burchik35@gmail.com
- **Сайт:** https://rztk.store