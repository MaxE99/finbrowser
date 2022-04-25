# Django imports
from django.shortcuts import redirect, render, get_object_or_404
from django.core.cache import cache
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
# Python imports
from datetime import timedelta, date
# Local imports
from accounts.models import SocialLink, Website
from home.models import (Article, HighlightedArticle, List, Sector, Source,
                         ListRating, ExternalSource, Notification)
from home.forms import (AddListForm, ListPicChangeForm, ListNameChangeForm,
                        AddExternalArticleForm)
from home.logic.pure_logic import paginator_create
from accounts.forms import (EmailAndUsernameChangeForm, PasswordChangingForm,
                            ProfileChangeForm)

User = get_user_model()


@login_required()
def feed(request):
    if 'createListForm' in request.POST:
        add_list_form = AddListForm(request.POST, request.FILES)
        if add_list_form.is_valid():
            add_list_form.save()
            messages.success(request, f'List has been created!')
            return redirect('home:feed')
    elif 'addExternalArticlesForm' in request.POST:
        add_external_articles_form = AddExternalArticleForm(request.POST)
        if add_external_articles_form.is_valid():
            data = add_external_articles_form.cleaned_data
            website_name = data['website_name']
            sector = data['sector']
            title = data['title']
            link = data['link']
            pub_date = data['pub_date']
            external_source = ExternalSource.objects.create(
                user=request.user, website_name=website_name)
            external_source.sector.add(sector)
            article = Article.objects.create(title=title,
                                             link=link,
                                             pub_date=pub_date,
                                             external_source=external_source)
            HighlightedArticle.objects.create(user=request.user,
                                              article=article)
            messages.success(request, f'Article has been added!')
            return redirect('home:feed')
    user_lists = List.objects.get_created_lists(request.user)
    subscribed_lists = List.objects.get_subscribed_lists(request.user)
    subscribed_sources = Source.objects.get_subscribed_sources(request.user)
    subscribed_articles = Article.objects.get_articles_from_subscribed_sources(
        subscribed_sources)
    subscribed_articles, _ = paginator_create(request, subscribed_articles, 10)
    highlighted_articles = HighlightedArticle.objects.filter(
        user=request.user).order_by('-article__pub_date')
    highlighted_articles, _ = paginator_create(request, highlighted_articles,
                                               10)
    add_list_form = AddListForm()
    add_external_articles_form = AddExternalArticleForm()
    highlighted_articles_titles = HighlightedArticle.objects.get_highlighted_articles_title(
        request.user)
    context = {
        'add_external_articles_form': add_external_articles_form,
        'add_list_form': add_list_form,
        'user_lists': user_lists,
        'subscribed_lists': subscribed_lists,
        'subscribed_sources': subscribed_sources,
        'subscribed_articles': subscribed_articles,
        'highlighted_articles': highlighted_articles,
        'highlighted_articles_titles': highlighted_articles_titles
    }
    return render(request, 'home/feed.html', context)


def lists(request):
    cache.set('current_user', request.user)
    if 'createListForm' in request.POST:
        add_list_form = AddListForm(request.POST, request.FILES)
        if add_list_form.is_valid():
            new_list = add_list_form.save()
            list_id = new_list.list_id
            messages.success(request, f'List has been created!')
            return redirect('home:list-details', list_id=list_id)
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
    lists = List.objects.filter(**filter_args).filter(
        is_public=True).order_by('name')
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
    sectors = Sector.objects.all().order_by('name')
    return render(request, 'home/sectors.html', {'sectors': sectors})


def articles(request):
    timeframe = cache.get('articles_timeframe')
    sector = cache.get('articles_sector')
    paywall = cache.get('articles_paywall')
    sources = cache.get('articles_sources')
    if 'createListForm' in request.POST:
        add_list_form = AddListForm(request.POST, request.FILES)
        if add_list_form.is_valid():
            add_list_form.save()
            messages.success(request, f'List has been created!')
            return redirect('home:articles')
    filter_args = {'source__paywall': paywall, 'source__website': sources}
    if timeframe != 'All' and timeframe != None:
        filter_args['pub_date__gte'] = date.today() - timedelta(
            days=int(timeframe))
    filter_args = dict(
        (k, v) for k, v in filter_args.items() if v is not None and v != 'All')
    search_articles = Article.objects.filter(external_source=None).filter(
        **filter_args).order_by('-pub_date')
    notloesung_search_articles = []
    if sector != 'All' and sector != None:
        # Refactoring necceseary
        sector = Sector.objects.get(name=sector)
        for x in search_articles:
            all_sectors = x.source.sector.all()
            if all_sectors.filter(name=str(sector)):
                notloesung_search_articles.append(x)
    if notloesung_search_articles:
        search_articles = notloesung_search_articles
        # Refactoring necceseary
    results_found = len(search_articles)
    search_articles, _ = paginator_create(request, search_articles, 10)
    sectors = Sector.objects.all().order_by('name')
    if request.user.is_authenticated:
        highlighted_articles_titles = HighlightedArticle.objects.get_highlighted_articles_title(
            request.user)
        user_lists = List.objects.get_created_lists(request.user)
    else:
        highlighted_articles_titles = None
        user_lists = None
    add_list_form = AddListForm()
    context = {
        'add_list_form': add_list_form,
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
            return redirect('home:list-details', list_id=list_id)
        elif 'createListForm' in request.POST:
            add_list_form = AddListForm(request.POST, request.FILES)
            if add_list_form.is_valid():
                add_list_form.save()
                messages.success(request, f'List has been created!')
                return redirect('home:feed')
    if list.content_type == 'Sources':
        articles = Article.objects.get_articles_from_list_sources(list)
        articles, _ = paginator_create(request, articles, 10)
    else:
        articles = None
    change_list_pic_form = ListPicChangeForm()
    change_list_name_form = ListNameChangeForm()
    ammount_of_ratings = ListRating.objects.get_ammount_of_ratings(list_id)
    average_rating = ListRating.objects.get_average_rating(list_id)
    highlighted_articles = List.objects.get_highlighted_articles(list_id)
    add_list_form = AddListForm()
    notifications_activated = Notification.objects.filter(user=request.user,
                                                          list=list).exists()
    if request.user.is_authenticated:
        highlighted_articles_titles = HighlightedArticle.objects.get_highlighted_articles_title(
            request.user)
        user_lists = List.objects.get_created_lists(request.user)
        if request.user in list.subscribers.all():
            subscribed = True
        else:
            subscribed = False
        user_rating = ListRating.objects.get_user_rating(request.user, list_id)
    else:
        highlighted_articles_titles = None
        user_lists = None
        subscribed = False  # Refactoren
        user_rating = None
    context = {
        'add_list_form': add_list_form,
        'ammount_of_ratings': ammount_of_ratings,
        'change_list_name_form': change_list_name_form,
        'change_list_pic_form': change_list_pic_form,
        'list': list,
        'subscribed': subscribed,
        'articles': articles,
        'average_rating': average_rating,
        'user_rating': user_rating,
        'highlighted_articles': highlighted_articles,
        'highlighted_articles_titles': highlighted_articles_titles,
        'user_lists': user_lists,
        'notifications_activated': notifications_activated,
    }
    return render(request, 'home/list_details.html', context)


def sector_details(request, slug):
    sector = get_object_or_404(Sector, slug=slug)
    articles_from_sector = Article.objects.get_articles_from_sector(sector)
    articles_from_sector, _ = paginator_create(request, articles_from_sector,
                                               10)
    sources = sector.sectors.all().filter(top_source=True)
    articles_from_top_sources = Article.objects.filter(
        source__in=sources).order_by('-pub_date')
    articles_from_top_sources, _ = paginator_create(request,
                                                    articles_from_top_sources,
                                                    10)
    context = {
        'articles_from_top_sources': articles_from_top_sources,
        'articles_from_sector': articles_from_sector,
        'sector': sector
    }
    return render(request, 'home/sector_details.html', context)


@login_required()
def settings(request):
    if request.method == "POST":
        if 'changeProfileForm' in request.POST:
            email_and_name_change_form = EmailAndUsernameChangeForm(
                request.POST,
                username=request.user.username,
                email=request.user.email,
                instance=request.user)
            profile_change_form = ProfileChangeForm(
                request.POST,
                request.FILES,
                bio=request.user.profile.bio,
                instance=request.user.profile)
            if profile_change_form.is_valid():
                profile_change_form.save()
                if email_and_name_change_form.is_valid():
                    request.user.save()
                    request.user.profile.save()
                    return redirect('../../settings/')
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
                return redirect('home:settings')
    profile_change_form = ProfileChangeForm(bio=request.user.profile.bio)
    email_and_name_change_form = EmailAndUsernameChangeForm(
        username=request.user.username, email=request.user.email)
    change_password_form = PasswordChangingForm(request.user)
    websites = Website.objects.all()
    social_links = SocialLink.objects.filter(profile=request.user.profile)
    context = {
        'change_password_form': change_password_form,
        'email_and_name_change_form': email_and_name_change_form,
        'profile_change_form': profile_change_form,
        'social_links': social_links,
        'websites': websites
    }
    return render(request, 'home/settings.html', context)


def main(request):
    return render(request, 'home/main.html')


def search_results(request, search_term):
    if 'createListForm' in request.POST:
        add_list_form = AddListForm(request.POST, request.FILES)
        if add_list_form.is_valid():
            add_list_form.save()
            messages.success(request, f'List has been created!')
            return redirect('home:feed')
    filtered_lists = List.objects.filter_lists(search_term)
    filtered_lists, _ = paginator_create(request, filtered_lists, 10)
    filtered_sources = Source.objects.filter_sources(search_term)
    filtered_articles = Article.objects.filter_articles(search_term)
    filtered_articles, _ = paginator_create(request, filtered_articles, 10)
    add_list_form = AddListForm()
    if request.user.is_authenticated:
        highlighted_articles_titles = HighlightedArticle.objects.get_highlighted_articles_title(
            request.user)
        user_lists = List.objects.get_created_lists(request.user)
    else:
        highlighted_articles_titles = None
        user_lists = None
    context = {
        'add_list_form': add_list_form,
        'filtered_articles': filtered_articles,
        'filtered_lists': filtered_lists,
        'filtered_sources': filtered_sources,
        'search_term': search_term,
        'highlighted_articles_titles': highlighted_articles_titles,
        'user_lists': user_lists
    }
    return render(request, 'home/search_results.html', context)