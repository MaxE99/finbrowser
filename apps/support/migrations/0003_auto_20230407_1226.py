# Generated by Django 3.2.13 on 2023-04-07 12:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0002_auto_20230306_1350'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contact',
            old_name='contact_email',
            new_name='email',
        ),
        migrations.RenameField(
            model_name='contact',
            old_name='explanation',
            new_name='message',
        ),
    ]
