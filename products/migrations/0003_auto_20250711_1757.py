from django.contrib.postgres.operations import TrigramExtension
from django.contrib.postgres.search import SearchVector
from django.db import migrations
from django.contrib.postgres.indexes import GinIndex


class Migration(migrations.Migration):
    dependencies = [
        ('products', '0002_initial'),
    ]

    operations = [
        # Увімкнути розширення для trigram пошуку
        TrigramExtension(),

        # Створити GIN індекс для швидкого full-text пошуку
        migrations.RunSQL(
            """
            CREATE INDEX IF NOT EXISTS products_search_idx 
            ON products 
            USING GIN (to_tsvector('russian', name || ' ' || description));
            """,
            reverse_sql="DROP INDEX IF EXISTS products_search_idx;"
        ),
    ]