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

**Варіант A: Інтерактивне підключення SSH**
```bash
# Підключення через SSH (буде запитано пароль)
ssh -p 2222 root@91.108.121.124
# Введіть пароль: U-2#(F(58GcxT1g0Y-rz
```

**Варіант B: Автоматичне підключення з expect (для скриптів)**
```bash
# Використання expect для автоматизації (потрібно встановити expect)
expect -c "
spawn ssh -p 2222 root@91.108.121.124
expect \"password:\"
send \"U-2#(F(58GcxT1g0Y-rz\r\"
expect \"#\"
send \"pwd\r\"
expect \"#\"
send \"exit\r\"
expect eof
"
```

**Варіант C: Копіювання файлів через SCP з expect**
```bash
# Копіювання файлу на сервер
expect -c "
spawn scp -P 2222 /local/path/file.py root@91.108.121.124:/root/rztk/
expect \"password:\"
send \"U-2#(F(58GcxT1g0Y-rz\r\"
expect eof
"
```

**Важливо:** Якщо `expect` не встановлено, встановіть його:
```bash
# На macOS
brew install expect

# На Ubuntu/Debian  
sudo apt-get install expect
```

### 3. Резервне копіювання (критично важливо!)

```bash
# На сервері
cd /root

# Видалення старих резервних копій (залишаємо тільки останні 2)
find /root -name "backup_*.sql" -type f | sort -r | tail -n +3 | xargs rm -f
find /root -name "rztk_backup_*.tar.gz" -type f | sort -r | tail -n +3 | xargs rm -f
find /root -name "media_backup_*.tar.gz" -type f | sort -r | tail -n +3 | xargs rm -f

# Створення резервної копії бази даних
docker exec rztk_db_1 pg_dump -U rztk_user rztk_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Резервна копія проекту
tar -czf rztk_backup_$(date +%Y%m%d_%H%M%S).tar.gz rztk/

# Резервна копія медіа файлів (якщо є)
docker run --rm -v rztk_media_volume:/data -v $(pwd):/backup alpine tar czf /backup/media_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .

# Перевірка створених резервних копій
echo "Створені резервні копії:"
ls -la backup_* rztk_backup_* media_backup_* 2>/dev/null | tail -3
```

### 4. Зупинка сервісів

bash
# Зупинка всіх контейнерів
cd /root/rztk
docker-compose down


### 5. Синхронізація файлів з локального проекту

**Варіант A: Копіювання через SCP з expect (з локального комп'ютера)**

```bash
# Django налаштування
expect -c "
spawn scp -P 2222 /Users/ihorburchik/Desktop/Python/RZTK/RZTK/rztk_project/settings.py root@91.108.121.124:/root/rztk/rztk_project/settings.py
expect \"password:\"
send \"U-2#(F(58GcxT1g0Y-rz\r\"
expect eof
"

# .env файл (важливо для змінних оточення)
expect -c "
spawn scp -P 2222 /Users/ihorburchik/Desktop/Python/RZTK/RZTK/.env root@91.108.121.124:/root/rztk/.env
expect \"password:\"
send \"U-2#(F(58GcxT1g0Y-rz\r\"
expect eof
"

# Docker композиція
expect -c "
spawn scp -P 2222 /Users/ihorburchik/Desktop/Python/RZTK/RZTK/docker-compose.yml root@91.108.121.124:/root/rztk/docker-compose.yml
expect \"password:\"
send \"U-2#(F(58GcxT1g0Y-rz\r\"
expect eof
"

# Копіювання додатків проекту (приклад для одного додатку)
expect -c "
spawn scp -P 2222 -r /Users/ihorburchik/Desktop/Python/RZTK/RZTK/account/ root@91.108.121.124:/root/rztk/
expect \"password:\"
send \"U-2#(F(58GcxT1g0Y-rz\r\"
expect eof
"

# Міграції (якщо є нові)
expect -c "
spawn scp -P 2222 /Users/ihorburchik/Desktop/Python/RZTK/RZTK/orders/migrations/0003_payment.py root@91.108.121.124:/root/rztk/orders/migrations/0003_payment.py
expect \"password:\"
send \"U-2#(F(58GcxT1g0Y-rz\r\"
expect eof
"

# Requirements (якщо додавались нові пакети)
expect -c "
spawn scp -P 2222 /Users/ihorburchik/Desktop/Python/RZTK/RZTK/requirements.txt root@91.108.121.124:/root/rztk/requirements.txt
expect \"password:\"
send \"U-2#(F(58GcxT1g0Y-rz\r\"
expect eof
"
```


**Варіант B: Синхронізація всього проекту одною командою**

```bash
# ОБЕРЕЖНО! Це перезапише ВСІ файли проекту
rsync -avz -e "ssh -p 2222" --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' /Users/ihorburchik/Desktop/Python/RZTK/RZTK/ root@91.108.121.124:/root/rztk/
```

### 6. Перевірка залежностей та міграцій

**Підключіться до сервера через expect або вручну:**

```bash
# Виконання команд на сервері через expect
expect -c "
spawn ssh -p 2222 root@91.108.121.124
expect \"password:\"
send \"U-2#(F(58GcxT1g0Y-rz\r\"
expect \"#\"
send \"cd /root/rztk\r\"
expect \"#\"
send \"docker-compose run --rm web python manage.py showmigrations\r\"
expect \"#\"
send \"exit\r\"
expect eof
"

# Якщо змінювався requirements.txt - перебудова образу
expect -c "
spawn ssh -p 2222 root@91.108.121.124
expect \"password:\"
send \"U-2#(F(58GcxT1g0Y-rz\r\"
expect \"#\"
send \"cd /root/rztk && docker-compose build --no-cache web\r\"
expect \"#\"
send \"exit\r\"
expect eof
"

# Застосування міграцій
expect -c "
spawn ssh -p 2222 root@91.108.121.124
expect \"password:\"
send \"U-2#(F(58GcxT1g0Y-rz\r\"
expect \"#\"
send \"cd /root/rztk && docker-compose run --rm web python manage.py migrate\r\"
expect \"#\"
send \"exit\r\"
expect eof
"
```

### 7. Запуск оновленого проекту

```bash
# Запуск всіх сервісів через expect
expect -c "
spawn ssh -p 2222 root@91.108.121.124
expect \"password:\"
send \"U-2#(F(58GcxT1g0Y-rz\r\"
expect \"#\"
send \"cd /root/rztk\r\"
expect \"#\"
send \"docker-compose down\r\"
expect \"#\"
send \"docker-compose up -d\r\"
expect \"#\"
send \"docker ps\r\"
expect \"#\"
send \"exit\r\"
expect eof
"

# Перевірка логів та статусу
expect -c "
spawn ssh -p 2222 root@91.108.121.124
expect \"password:\"
send \"U-2#(F(58GcxT1g0Y-rz\r\"
expect \"#\"
send \"cd /root/rztk && docker logs rztk_web_1 --tail 10\r\"
expect \"#\"
send \"curl -I http://localhost:8000\r\"
expect \"#\"
send \"exit\r\"
expect eof
"
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
5. **Використовувати expect** для автоматизації команд з паролем
6. **Перевіряти .env файл** - API ключі не повинні склеюватися з коментарями

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

### Швидкий відкат через expect

```bash
# Швидкий відкат на сервері
expect -c "
spawn ssh -p 2222 root@91.108.121.124
expect \"password:\"
send \"U-2#(F(58GcxT1g0Y-rz\r\"
expect \"#\"
send \"cd /root/rztk && docker-compose down\r\"
expect \"#\"
send \"cd /root && tar -xzf rztk_backup_YYYYMMDD_HHMMSS.tar.gz\r\"
expect \"#\"
send \"cd /root/rztk && docker-compose up -d db\r\"
expect \"#\"
send \"sleep 10\r\"
expect \"#\"
send \"docker exec -i rztk_db_1 psql -U rztk_user -d rztk_db < /root/backup_YYYYMMDD_HHMMSS.sql\r\"
expect \"#\"
send \"docker-compose up -d\r\"
expect \"#\"
send \"exit\r\"
expect eof
"
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

## Типові проблеми та рішення

### Google OAuth помилки

**Проблема:** `redirect_uri_mismatch`
**Рішення:** Перевірити в Google Cloud Console authorized redirect URIs:
```
https://rztk.store/accounts/google/login/callback/
http://rztk.store/accounts/google/login/callback/
```

**Проблема:** `invalid_client`
**Рішення:** Перевірити що client_id та client_secret правильно встановлені в .env файлі

### База даних помилки

**Проблема:** `column does not exist`
**Рішення:** 
1. Перевірити чи застосовані всі міграції
2. При потребі додати колонку вручну через Django shell
3. Перекопіювати міграції з локального проекту

### API Нової Пошти

**Проблема:** 401 Unauthorized
**Рішення:** Перевірити що API ключ не склеєний з коментарями в .env файлі

---

**Останнє оновлення інструкції:** 12 липня 2025  
**Версія Django:** 5.2.1  
**Версія Python:** 3.11.13  
**Версія expect:** встановлювати через brew/apt