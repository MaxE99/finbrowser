# Django import
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
# Local import
from home.models import Source, Article, List, SourceRating
from home.logic.pure_logic import paginator_create
from home.logic.selectors import website_logo_get


def profile(request, domain):
    source = get_object_or_404(Source, domain=domain)
    articles = Article.objects.filter(source=source)
    articles, _ = paginator_create(request, articles, 5)
    lists = List.objects.filter(sources__source_id=source.source_id)
    website_logo = website_logo_get(source.website)
    if request.user in source.subscribers.all():
        subscribed = True
    else:
        subscribed = False
    if SourceRating.objects.filter(user=request.user, source=source).exists():
        source_rating = get_object_or_404(SourceRating,
                                          user=request.user,
                                          source=source)
        user_rating = source_rating.rating
    else:
        user_rating = False
    source_ratings = SourceRating.objects.filter(source=source)
    sum_ratings = SourceRating.objects.filter(source=source).aggregate(
        Sum('rating'))
    sum_ratings = sum_ratings.get("rating__sum", 0)
    average_rating = sum_ratings / len(source_ratings)
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
