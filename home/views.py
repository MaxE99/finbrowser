# Django imports
from django.shortcuts import redirect, render, get_object_or_404
from django.core.cache import cache
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
from django.db.models import Sum
# Python imports
from datetime import timedelta, date
# Local imports
from home.models import Article, HighlightedArticle, List, Sector, Source, ListRating
from home.forms import (AddListForm, ListPicChangeForm, ListNameChangeForm)
from home.logic.pure_logic import paginator_create
from accounts.forms import (EmailAndUsernameChangeForm, PasswordChangingForm,
                            ProfilePicChangeForm)

User = get_user_model()


@login_required(login_url="/registration/login/")
def feed(request):
    user_lists = List.objects.filter(creator=request.user).order_by('name')
    subscribed_lists = List.objects.filter(subscribers=request.user)
    subscribed_sources = Source.objects.filter(subscribers=request.user)
    subscribed_articles = Article.objects.filter(
        source__in=subscribed_sources).order_by('-pub_date')
    subscribed_articles, _ = paginator_create(request, subscribed_articles, 10)
    context = {
        'user_lists': user_lists,
        'subscribed_lists': subscribed_lists,
        'subscribed_sources': subscribed_sources,
        'subscribed_articles': subscribed_articles
    }
    return render(request, 'home/feed.html', context)


def lists(request):
    cache.set('current_user', request.user)
    if 'createListForm' in request.POST:
        add_list_form = AddListForm(request.POST, request.FILES)
        if add_list_form.is_valid():
            add_list_form.save()
            messages.success(request, f'List has been created!')
            return redirect('../../home/lists/')
    timeframe = cache.get('timeframe')
    content_type = cache.get('content_type')
    sources = cache.get('sources')
    filter_args = {
        'content_type': content_type,
        'main_website_source': sources
    }
    if timeframe != 'All' and timeframe != None:
        filter_args['updated_at__gte'] = date.today() - timedelta(
            days=int(timeframe))
    filter_args = dict(
        (k, v) for k, v in filter_args.items() if v is not None and v != 'All')
    lists = List.objects.filter(**filter_args)
    # cache.delete_many(['timeframe', 'content_type', 'sources'])
    add_list_form = AddListForm()
    results_found = len(lists)
    lists, _ = paginator_create(request, lists, 10)
    return render(
        request, 'home/lists.html', {
            'add_list_form': add_list_form,
            'lists': lists,
            'results_found': results_found,
        })


def sectors(request):
    sectors = Sector.objects.all()
    return render(request, 'home/sectors.html', {'sectors': sectors})


def articles(request):
    timeframe = cache.get('articles_timeframe')
    sector = cache.get('articles_sector')
    paywall = cache.get('articles_paywall')
    sources = cache.get('articles_sources')
    filter_args = {'source__paywall': paywall, 'source__website': sources}
    if timeframe != 'All' and timeframe != None:
        filter_args['pub_date__gte'] = date.today() - timedelta(
            days=int(timeframe))
    filter_args = dict(
        (k, v) for k, v in filter_args.items() if v is not None and v != 'All')
    search_articles = Article.objects.filter(
        **filter_args).order_by('-pub_date')
    notloesung_search_articles = []
    if sector != 'All' and sector != None:
        # Refactoring necceseary
        sector = Sector.objects.get(name=sector)
        for x in search_articles:
            all_sectors = x.source.sectors.all()
            if all_sectors.filter(name=str(sector)):
                notloesung_search_articles.append(x)
    if notloesung_search_articles:
        search_articles = notloesung_search_articles
        # Refactoring necceseary
    results_found = len(search_articles)
    search_articles, _ = paginator_create(request, search_articles, 10)
    sectors = Sector.objects.all().order_by('name')
    highlighted_articles = HighlightedArticle.objects.filter(user=request.user)
    highlighted_articles_titles = []
    for article in highlighted_articles:
        highlighted_articles_titles.append(article.article.title)
    user_lists = List.objects.filter(creator=request.user)
    context = {
        'results_found': results_found,
        'search_articles': search_articles,
        'sectors': sectors,
        'highlighted_articles_titles': highlighted_articles_titles,
        'user_lists': user_lists
    }
    return render(request, 'home/articles.html', context)


def list_details(request, list_id):
    list = get_object_or_404(List, list_id=list_id)
    if request.method == 'POST':
        if 'changeListForm' in request.POST:
            change_list_name_form = ListNameChangeForm(request.POST,
                                                       instance=list)
            change_list_pic_form = ListPicChangeForm(request.POST,
                                                     request.FILES,
                                                     instance=list)
            if change_list_pic_form.is_valid:
                change_list_pic_form.save()
            if change_list_name_form.is_valid:
                change_list_name_form.save()
            return redirect(f'../../home/list/{list_id}')
    if list.content_type == 'Sources':
        articles = Article.objects.filter(
            source__in=list.sources.all()).order_by('-pub_date')
        articles, _ = paginator_create(request, articles, 10)
    else:
        articles = None
    if request.user in list.subscribers.all():
        subscribed = True
    else:
        subscribed = False
    change_list_pic_form = ListPicChangeForm()
    change_list_name_form = ListNameChangeForm()
    if ListRating.objects.filter(user=request.user, list_id=list_id).exists():
        list_rating = get_object_or_404(ListRating,
                                        user=request.user,
                                        list_id=list_id)
        user_rating = list_rating.rating
    else:
        user_rating = False
    list_ratings = ListRating.objects.filter(list_id=list_id)
    sum_ratings = ListRating.objects.filter(list_id=list_id).aggregate(
        Sum('rating'))
    sum_ratings = sum_ratings.get("rating__sum", None)
    if sum_ratings == None:
        average_rating = "None"
    else:
        average_rating = round(sum_ratings / len(list_ratings), 1)
    context = {
        'change_list_name_form': change_list_name_form,
        'change_list_pic_form': change_list_pic_form,
        'list': list,
        'subscribed': subscribed,
        'articles': articles,
        'average_rating': average_rating,
        'user_rating': user_rating
    }
    return render(request, 'home/list_details.html', context)


def sector_details(request, name):
    sector = get_object_or_404(Sector, name=name.capitalize())
    context = {'sector': sector}
    return render(request, 'home/sector_details.html', context)


@login_required(login_url="/registration/login/")
def settings(request):
    if request.method == "POST":
        if 'changeProfileForm' in request.POST:
            email_and_name_change_form = EmailAndUsernameChangeForm(
                request.POST,
                username=request.user.username,
                email=request.user.email,
                instance=request.user)
            profile_pic_change_form = ProfilePicChangeForm(
                request.POST, request.FILES, instance=request.user.profile)
            if profile_pic_change_form.is_valid():
                profile_pic_change_form.save()
                if email_and_name_change_form.is_valid():
                    request.user.save()
                    request.user.profile.save()
                    return redirect('../../home/settings/')
                else:
                    messages.error(request,
                                   "Error: Username or email already exists!")
        elif "changePasswordForm" in request.POST:
            change_password_form = PasswordChangingForm(user=request.user,
                                                        data=request.POST
                                                        or None)
            if change_password_form.is_valid():
                change_password_form.save()
                update_session_auth_hash(request, change_password_form.user)
                return redirect('../../home/settings/')
    email_and_name_change_form = EmailAndUsernameChangeForm(
        username=request.user.username, email=request.user.email)
    profile_pic_change_form = ProfilePicChangeForm()
    change_password_form = PasswordChangingForm(request.user)
    context = {
        'change_password_form': change_password_form,
        'email_and_name_change_form': email_and_name_change_form,
        'profile_pic_change_form': profile_pic_change_form,
    }
    return render(request, 'home/settings.html', context)


def main(request):
    return render(request, 'home/main.html')


def search_results(request, search_term):
    filtered_lists = List.objects.filter(name__istartswith=search_term)
    filtered_sources = Source.objects.filter(domain__istartswith=search_term)
    filtered_articles = Article.objects.filter(title__icontains=search_term)
    context = {
        'filtered_articles': filtered_articles,
        'filtered_lists': filtered_lists,
        'filtered_sources': filtered_sources,
        'search_term': search_term
    }
    return render(request, 'home/search_results.html', context)