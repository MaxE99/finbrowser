# Generated by Django 3.2.13 on 2022-05-17 10:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0042_auto_20220517_0851'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationmessage',
            name='article',
            field=models.ForeignKey(default=55, on_delete=django.db.models.deletion.CASCADE, to='home.article'),
        ),
    ]
