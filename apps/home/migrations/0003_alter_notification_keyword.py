# Generated by Django 3.2.13 on 2022-08-04 07:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_notification_keyword'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='keyword',
            field=models.CharField(max_length=30, null=True, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(30)]),
        ),
    ]
