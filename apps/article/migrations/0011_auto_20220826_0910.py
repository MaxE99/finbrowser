# Generated by Django 3.2.13 on 2022-08-26 09:10

from django.db import migrations
from django.contrib.postgres.search import SearchVector
import django.contrib.postgres.indexes
import django.contrib.postgres.search


def compute_search_vector(apps, schema_editor):
    Article = apps.get_model("article", "Article")
    Article.objects.update(search_vector=SearchVector("title"))

class Migration(migrations.Migration):

    dependencies = [
        ("article", "0010_alter_article_tweet_type"),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(null=True),
        ),
        migrations.AddIndex(
            model_name='article',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_vector'], name='article_art_search__b97288_gin'),
        ),
        migrations.RunSQL(
            sql="""
            CREATE TRIGGER search_vector_trigger
            BEFORE INSERT OR UPDATE OF title, search_vector
            ON article_article
            FOR EACH ROW EXECUTE PROCEDURE
            tsvector_update_trigger(
                search_vector, 'pg_catalog.english', title
            );
            UPDATE article_article SET search_vector = NULL;
            """,
            reverse_sql="""
            DROP TRIGGER IF EXISTS search_vector_trigger
            ON article_article;
            """,
        ),
        migrations.RunPython(
            compute_search_vector, reverse_code=migrations.RunPython.noop
        ),
    ]
