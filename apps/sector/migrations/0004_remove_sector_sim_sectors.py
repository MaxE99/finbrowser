# Generated by Django 3.2.13 on 2023-05-28 11:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sector', '0003_sector_sim_sectors'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sector',
            name='sim_sectors',
        ),
    ]
