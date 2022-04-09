# Django import
from django.shortcuts import render, get_object_or_404
# Local import
from home.models import Source, Article, List, Sector
from home.logic.pure_logic import paginator_create
from home.logic.selectors import website_logo_get


def profile(request, domain):
    source = get_object_or_404(Source, domain=domain)
    articles = Article.objects.filter(source=source)
    articles, _ = paginator_create(request, articles, 5)
    lists = List.objects.filter(sources__source_id=source.source_id)
    sectors = Sector.objects.filter(sources=source)
    website_logo = website_logo_get(source.website)
    if request.user in source.subscribers.all():
        subscribed = True
    else:
        subscribed = False
    context = {
        'articles': articles,
        'lists': lists,
        'sectors': sectors,
        'source': source,
        'website_logo': website_logo,
        'subscribed': subscribed
    }
    return render(request, 'source/profile.html', context)
