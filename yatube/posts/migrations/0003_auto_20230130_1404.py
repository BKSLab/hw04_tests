# Generated by Django 2.2.9 on 2023-01-30 10:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0002_auto_20230129_1251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(unique=True),
        ),
    ]