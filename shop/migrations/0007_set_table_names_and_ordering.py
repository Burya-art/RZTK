
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_optimize_product_indexes'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelTable(
            name='brand',
            table='brands',
        ),
        migrations.AlterModelTable(
            name='category',
            table='categories',
        ),
        migrations.AlterModelTable(
            name='product',
            table='products',
        ),
    ]
