# Django import
from django.shortcuts import render
# Local import
from home.models import Source, Article, List
from home.logic.pure_logic import paginator_create


def profile(request, domain):
    source = Source.objects.get(domain=domain)
    articles = Article.objects.filter(source=source)
    articles, page = paginator_create(request, articles, 5)
    lists = List.objects.filter(sources__source_id=source.source_id)
    context = {
        'articles': articles,
        'lists': lists,
        'page': page,
        'source': source
    }
    return render(request, 'source/profile.html', context)
