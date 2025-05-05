from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_add_surname_field_to_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='surname',
        ),
    ]
