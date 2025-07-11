
#!/bin/bash

# Скрипт для деплою проекту RZTK
echo "Починаємо деплой проекту RZTK..."

# Оновлюємо код з git
echo "Оновлюємо код..."
git pull origin feature/first-feature

# Зупиняємо контейнери
echo "Зупиняємо контейнери..."
docker-compose down

# Збираємо нові образи
echo "Збираємо нові образи..."
docker-compose build --no-cache

# Запускаємо контейнери
echo "Запускаємо контейнери..."
docker-compose up -d

# Виконуємо міграції
echo "Виконуємо міграції..."
docker-compose exec -T web python manage.py migrate

# Збираємо статичні файли
echo "Збираємо статичні файли..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Перевіряємо статус
echo "Перевіряємо статус контейнерів..."
docker-compose ps

echo "Деплой завершено!"