# Generated by Django 4.0.3 on 2022-04-14 06:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0027_rename_score_listrating_rating_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='list',
            name='likes',
        ),
    ]
