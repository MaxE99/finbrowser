# Generated by Django 3.2.13 on 2022-06-01 21:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0005_auto_20220601_2021'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sourcesuggestion',
            name='suggestion_date',
        ),
    ]
