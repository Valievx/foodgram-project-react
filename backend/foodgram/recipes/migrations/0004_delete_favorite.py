# Generated by Django 2.2.19 on 2023-10-14 16:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20231014_1613'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Favorite',
        ),
    ]
