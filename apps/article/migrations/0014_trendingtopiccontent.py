# Generated by Django 3.2.13 on 2023-03-06 06:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0013_highlightedarticle_unique_highlighted'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrendingTopicContent',
            fields=[
                ('ttopic_id', models.AutoField(primary_key=True, serialize=False)),
                ('article', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='article.article')),
            ],
        ),
    ]
