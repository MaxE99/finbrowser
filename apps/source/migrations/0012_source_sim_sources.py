# Generated by Django 3.2.13 on 2023-03-07 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('source', '0011_remove_source_sim_sources'),
    ]

    operations = [
        migrations.AddField(
            model_name='source',
            name='sim_sources',
            field=models.ManyToManyField(blank=True, related_name='_source_source_sim_sources_+', to='source.Source'),
        ),
    ]
