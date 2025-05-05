from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='surname',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
