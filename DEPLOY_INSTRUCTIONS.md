# Інструкція з деплою оновлень проекту RZTK

## Загальна інформація про проект

**Домен:** https://rztk.store  
**VPS:** srv836555.hstgr.cloud  
**IP:** 91.108.121.124  
**SSH порт:** 2222  
**Користувач:** root  
**Пароль:** U-2#(F(58GcxT1g0Y-rz  
**Шлях до проекту на сервері:** /root/rztk  

## Архітектура проекту

### Сервіси
- **Системний Nginx**: SSL термінація, обробка домену (порт 443/80)
- **Django (web)**: Веб-додаток (порт 8000)
- **PostgreSQL**: База даних
- **Redis**: Кешування та сесії (порт 6379)
- **RabbitMQ**: Черга повідомлень (порт 5672)
- **Celery**: Фонові завдання
- **Docker Nginx**: Проксі для статики (порт 8080)

### Важливі файли конфігурації
- `/tmp/nginx_rztk_fixed.conf` - Системний Nginx для домену
- `/root/rztk/docker-compose.yml` - Конфігурація Docker сервісів
- `/root/rztk/rztk_project/settings.py` - Налаштування Django

## Процедура деплою оновлень

### 1. Підготовка локального проекту

```bash
# Перевірка, що всі зміни збережені локально
cd /Users/ihorburchik/Desktop/Python/RZTK/RZTK

# Перевірка стану проекту
git status

# ВАЖЛИВО: НЕ робити git commit та git push!
# Ми деплоїмо без коміту в GitHub
```

### 2. Підключення до сервера

```bash
# Підключення через SSH
ssh -p 2222 root@91.108.121.124
# Пароль: U-2#(F(58GcxT1g0Y-rz
```

### 3. Резервне копіювання (критично важливо!)

```bash
# На сервері
cd /root

# Створення резервної копії бази даних
docker exec rztk_db_1 pg_dump -U rztk_user rztk_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Резервна копія проекту
tar -czf rztk_backup_$(date +%Y%m%d_%H%M%S).tar.gz rztk/

# Резервна копія медіа файлів (якщо є)
docker run --rm -v rztk_media_volume:/data -v $(pwd):/backup alpine tar czf /backup/media_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .
```

### 4. Зупинка сервісів

```bash
# Зупинка всіх контейнерів
cd /root/rztk
docker-compose down
```

### 5. Синхронізація файлів з локального проекту

**Варіант A: Копіювання через SCP (з локального комп'ютера)**

```bash
# Django налаштування
scp -P 2222 /Users/ihorburchik/Desktop/Python/RZTK/RZTK/rztk_project/settings.py root@91.108.121.124:/root/rztk/rztk_project/settings.py

# Docker композиція
scp -P 2222 /Users/ihorburchik/Desktop/Python/RZTK/RZTK/docker-compose.yml root@91.108.121.124:/root/rztk/docker-compose.yml

# Nginx конфігурація (якщо змінювалась)
scp -P 2222 /Users/ihorburchik/Desktop/Python/RZTK/RZTK/nginx/nginx.conf root@91.108.121.124:/root/rztk/nginx/nginx.conf

# Копіювання всіх Python файлів проекту
scp -P 2222 -r /Users/ihorburchik/Desktop/Python/RZTK/RZTK/products/ root@91.108.121.124:/root/rztk/
scp -P 2222 -r /Users/ihorburchik/Desktop/Python/RZTK/RZTK/basket/ root@91.108.121.124:/root/rztk/
scp -P 2222 -r /Users/ihorburchik/Desktop/Python/RZTK/RZTK/orders/ root@91.108.121.124:/root/rztk/
scp -P 2222 -r /Users/ihorburchik/Desktop/Python/RZTK/RZTK/reviews/ root@91.108.121.124:/root/rztk/
scp -P 2222 -r /Users/ihorburchik/Desktop/Python/RZTK/RZTK/account/ root@91.108.121.124:/root/rztk/
scp -P 2222 -r /Users/ihorburchik/Desktop/Python/RZTK/RZTK/shop/ root@91.108.121.124:/root/rztk/
scp -P 2222 -r /Users/ihorburchik/Desktop/Python/RZTK/RZTK/nova_poshta/ root@91.108.121.124:/root/rztk/

# Статичні файли (якщо змінювались)
scp -P 2222 -r /Users/ihorburchik/Desktop/Python/RZTK/RZTK/static/ root@91.108.121.124:/root/rztk/

# Requirements (якщо додавались нові пакети)
scp -P 2222 /Users/ihorburchik/Desktop/Python/RZTK/RZTK/requirements.txt root@91.108.121.124:/root/rztk/requirements.txt

# Dockerfile (якщо змінювався)
scp -P 2222 /Users/ihorburchik/Desktop/Python/RZTK/RZTK/Dockerfile root@91.108.121.124:/root/rztk/Dockerfile
```

**Варіант B: Синхронізація всього проекту одною командою**

```bash
# ОБЕРЕЖНО! Це перезапише ВСІ файли проекту
rsync -avz -e "ssh -p 2222" --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' /Users/ihorburchik/Desktop/Python/RZTK/RZTK/ root@91.108.121.124:/root/rztk/
```

### 6. Перевірка залежностей та міграцій

```bash
# На сервері
cd /root/rztk

# Якщо змінювався requirements.txt - перебудова образу
docker-compose build --no-cache web

# Перевірка міграцій (не запускаємо автоматично!)
docker-compose run --rm web python manage.py showmigrations

# Якщо є нові міграції - створення та застосування
docker-compose run --rm web python manage.py makemigrations
docker-compose run --rm web python manage.py migrate
```

### 7. Запуск оновленого проекту

```bash
# Запуск всіх сервісів
docker-compose up -d

# Перевірка статусу контейнерів
docker ps

# Перевірка логів web контейнера
docker logs rztk_web_1 --tail 20

# Збір статичних файлів (якщо потрібно)
docker-compose exec web python manage.py collectstatic --noinput
```

### 8. Перевірка роботи сайту

```bash
# Тест підключення до Django
curl -I http://localhost:8000

# Перевірка Redis
docker exec rztk_redis_1 redis-cli ping

# Перевірка PostgreSQL
docker exec rztk_db_1 pg_isready -U rztk_user

# Перевірка RabbitMQ
docker exec rztk_rabbitmq_1 rabbitmqctl status
```

### 9. Фінальна перевірка

- Відкрити https://rztk.store в браузері
- Перевірити головну сторінку
- Перевірити сторінку товару
- Перевірити авторизацію/реєстрацію
- Перевірити адмін панель: https://rztk.store/admin/

## Критичні моменти та застереження

### 🚨 ВАЖЛИВО

1. **ЗАВЖДИ** робити резервне копіювання перед деплоєм
2. **НЕ** робити git commit/push - деплоїмо файли напряму
3. **Перевіряти** міграції перед їх застосуванням
4. **Тестувати** сайт після кожного кроку

### Змінні середовища в docker-compose.yml

```yaml
environment:
  - DB_HOST=db
  - DB_NAME=rztk_db
  - DB_USER=rztk_user
  - DB_PASSWORD=12345
  - DB_PORT=5432
  - RABBITMQ_HOST=rabbitmq
  - RABBITMQ_USER=rztk_user
  - RABBITMQ_PASSWORD=12345
  - REDIS_HOST=redis
  - REDIS_PORT=6379
  - REDIS_DB=1
  - ALLOWED_HOSTS=localhost,127.0.0.1,web,rztk.store,www.rztk.store
  - CSRF_TRUSTED_ORIGINS=https://rztk.store,https://www.rztk.store
```

### Структура портів

- **80/443**: Системний Nginx (домен)
- **8000**: Django (внутрішній доступ)
- **8080**: Docker Nginx (статика)
- **5432**: PostgreSQL (внутрішній)
- **6379**: Redis (внутрішній)
- **5672**: RabbitMQ (внутрішній)
- **15672**: RabbitMQ Management UI

## Відкат у разі проблем

### Швидкий відкат

```bash
# Зупинка поточних контейнерів
docker-compose down

# Відновлення з резервної копії
cd /root
tar -xzf rztk_backup_YYYYMMDD_HHMMSS.tar.gz

# Відновлення бази даних
docker-compose up -d db
sleep 10
docker exec -i rztk_db_1 psql -U rztk_user -d rztk_db < backup_YYYYMMDD_HHMMSS.sql

# Запуск всіх сервісів
cd rztk
docker-compose up -d
```

## Автоматизація через deploy.sh

Створити скрипт для автоматизації:

```bash
#!/bin/bash
# deploy.sh - скрипт автоматичного деплою

# Функція для відображення помилок
error_exit() {
    echo "ПОМИЛКА: $1" >&2
    exit 1
}

# Резервне копіювання
echo "Створення резервної копії..."
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
docker exec rztk_db_1 pg_dump -U rztk_user rztk_db > backup_${BACKUP_DATE}.sql || error_exit "Не вдалось створити бекап БД"

# Зупинка сервісів
echo "Зупинка сервісів..."
docker-compose down || error_exit "Не вдалось зупинити контейнери"

# Оновлення коду (тут має бути логіка копіювання файлів)
echo "Оновлення коду..."

# Запуск сервісів
echo "Запуск оновлених сервісів..."
docker-compose up -d || error_exit "Не вдалось запустити контейнери"

echo "Деплой завершено успішно!"
```

## Моніторинг після деплою

```bash
# Перегляд логів у реальному часі
docker-compose logs -f web

# Перевірка використання ресурсів
docker stats

# Перевірка дискового простору
df -h

# Перевірка пам'яті
free -h
```

## Контакти та допомога

У разі проблем:
1. Перевірити логи: `docker-compose logs`
2. Перевірити статус контейнерів: `docker ps -a`
3. При критичних помилках - відкат з резервної копії
4. Звернутись до цієї інструкції для детального керівництва

---

**Останнє оновлення інструкції:** $(date)  
**Версія Django:** 5.2.1  
**Версія Python:** 3.11.13