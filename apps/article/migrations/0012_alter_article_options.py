# Generated by Django 3.2.13 on 2022-09-02 07:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0011_auto_20220826_0910'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='article',
            options={'ordering': ('-pub_date',)},
        ),
    ]
