# Django import
from django.shortcuts import render, get_object_or_404
# Local import
from home.models import Source, Article, List, SourceRating
from home.logic.pure_logic import paginator_create
from home.logic.selectors import website_logo_get


def profile(request, domain):
    source = get_object_or_404(Source, domain=domain)
    articles = Article.objects.filter(source=source).order_by('-pub_date')
    articles, _ = paginator_create(request, articles, 5)
    lists = List.objects.filter(sources__source_id=source.source_id)
    website_logo = website_logo_get(source.website)
    if request.user in source.subscribers.all():
        subscribed = True
    else:
        subscribed = False
    user_rating = SourceRating.objects.get_user_rating(request.user, source)
    average_rating = SourceRating.objects.get_average_rating(source)
    context = {
        'articles': articles,
        'lists': lists,
        'source': source,
        'website_logo': website_logo,
        'subscribed': subscribed,
        'user_rating': user_rating,
        'average_rating': average_rating
    }
    return render(request, 'source/profile.html', context)
