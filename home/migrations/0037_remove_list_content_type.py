# Generated by Django 4.0.3 on 2022-04-26 13:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0036_externalsource_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='list',
            name='content_type',
        ),
    ]
