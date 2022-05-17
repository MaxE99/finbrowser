# Django imports
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
# Python imports
from datetime import timedelta, date
# Local imports
from accounts.models import CookieSettings, SocialLink, Website
from home.models import (Article, HighlightedArticle, List, Sector, Source,
                         ListRating, ExternalSource, Notification, NotificationMessage)
from home.forms import (AddListForm, ListPicChangeForm, ListNameChangeForm,
                        AddExternalArticleForm)
from home.logic.pure_logic import paginator_create
from accounts.forms import (EmailAndUsernameChangeForm, PasswordChangingForm,
                            ProfileChangeForm, PrivacySettingsForm,
                            CookieSettingsForm)

User = get_user_model()


@login_required()
def feed(request):
    notifications = Notification.objects.filter(user=request.user)
    unseen_notifications = NotificationMessage.objects.filter(notification__in=notifications, user_has_seen=False).count()
    # cache.set('current_user', request.user)
    if 'createListForm' in request.POST:
        add_list_form = AddListForm(request.POST, request.FILES)
        if add_list_form.is_valid():
            new_list = add_list_form.save(commit=False)
            new_list.creator = request.user
            new_list.save()
            list_id = new_list.list_id
            messages.success(request, 'List has been created!')
            return redirect('home:list-details', list_id=list_id)
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
            messages.success(request, 'Article has been added!')
            return redirect('home:feed')
    user_lists = List.objects.get_created_lists(request.user)
    subscribed_lists = List.objects.get_subscribed_lists(request.user)
    subscribed_sources = Source.objects.get_subscribed_sources(request.user)
    subscribed_articles = Article.objects.get_articles_from_subscribed_sources(
        subscribed_sources)
    subscribed_articles, _ = paginator_create(request, subscribed_articles, 10,
                                              'subscribed_articles')
    highlighted_articles = HighlightedArticle.objects.filter(
        user=request.user).order_by('-article__pub_date')
    highlighted_articles, _ = paginator_create(request, highlighted_articles,
                                               10, 'highlighted_articles')
    add_list_form = AddListForm()
    add_external_articles_form = AddExternalArticleForm()
    highlighted_articles_titles = HighlightedArticle.objects.get_highlighted_articles_title(
        request.user)
    context = {
        'add_list_form': add_list_form,
        'add_external_articles_form': add_external_articles_form,
        'user_lists': user_lists,
        'subscribed_lists': subscribed_lists,
        'subscribed_sources': subscribed_sources,
        'subscribed_articles': subscribed_articles,
        'highlighted_articles': highlighted_articles,
        'highlighted_articles_titles': highlighted_articles_titles,
        'unseen_notifications': unseen_notifications
    }
    return render(request, 'home/feed.html', context)


def lists(request):
    notifications = Notification.objects.filter(user=request.user)
    unseen_notifications = NotificationMessage.objects.filter(notification__in=notifications, user_has_seen=False).count()
    if 'createListForm' in request.POST:
        add_list_form = AddListForm(request.POST, request.FILES)
        if add_list_form.is_valid():
            new_list = add_list_form.save(commit=False)
            new_list.creator = request.user
            new_list.save()
            list_id = new_list.list_id
            messages.success(request, f'List has been created!')
            return redirect('home:list-details', list_id=list_id)
    lists = List.objects.filter(is_public=True).order_by('name')
    add_list_form = AddListForm()
    results_found = len(lists)
    lists, _ = paginator_create(request, lists, 10)
    return render(
        request, 'home/lists.html', {
            'add_list_form': add_list_form,
            'lists': lists,
            'results_found': results_found,
            'unseen_notifications': unseen_notifications
        })


def lists_search(request, timeframe, content_type, minimum_rating, sources):
    notifications = Notification.objects.filter(user=request.user)
    unseen_notifications = NotificationMessage.objects.filter(notification__in=notifications, user_has_seen=False).count()
    if 'createListForm' in request.POST:
        add_list_form = AddListForm(request.POST, request.FILES)
        if add_list_form.is_valid():
            new_list = add_list_form.save(commit=False)
            new_list.creator = request.user
            new_list.save()
            list_id = new_list.list_id
            messages.success(request, f'List has been created!')
            return redirect('home:list-details', list_id=list_id)
    filter_args = {'main_website_source': sources}
    if timeframe != 'All' and timeframe != None:
        filter_args['updated_at__gte'] = date.today() - timedelta(
            days=int(timeframe))
    filter_args = dict(
        (k, v) for k, v in filter_args.items() if v is not None and v != 'All')
    lists = List.objects.filter(**filter_args).filter(
        is_public=True).order_by('name')
    ##########################################################################
    # filter content_type
    if content_type != 'All':
        exclude_list = []
        if content_type == "Articles":
            for list in lists:
                if len(list.articles.all()) <= len(list.sources.all()):
                    exclude_list.append(list)
                    # lists.exclude(list_id=list.list_id)
        else:
            for list in lists:
                if len(list.articles.all()) >= len(list.sources.all()):
                    exclude_list.append(list)
                    # lists.exclude(list_id=list.list_id)
        if len(exclude_list):
            for list in exclude_list:
                lists = lists.exclude(list_id=list.list_id)

    # filter minimum_rating
    exclude_list = []
    if minimum_rating != 'All' and minimum_rating is not None:
        minimum_rating = float(minimum_rating)
        for list in lists:
            if list.get_average_rating != "None":
                if list.get_average_rating < minimum_rating:
                    exclude_list.append(list)
            else:
                exclude_list.append(list)
    if len(exclude_list):
        for list in exclude_list:
            lists = lists.exclude(list_id=list.list_id)
    ##########################################################################
    add_list_form = AddListForm()
    results_found = len(lists)
    lists, _ = paginator_create(request, lists, 10)
    return render(
        request, 'home/lists.html', {
            'add_list_form': add_list_form,
            'lists': lists,
            'results_found': results_found,
            'unseen_notifications': unseen_notifications
        })



def sectors(request):
    notifications = Notification.objects.filter(user=request.user)
    unseen_notifications = NotificationMessage.objects.filter(notification__in=notifications, user_has_seen=False).count()
    sectors = Sector.objects.all().order_by('name')
    return render(request, 'home/sectors.html', {'sectors': sectors, 'unseen_notifications': unseen_notifications})


def articles(request):
    notifications = Notification.objects.filter(user=request.user)
    unseen_notifications = NotificationMessage.objects.filter(notification__in=notifications, user_has_seen=False).count()
    if 'createListForm' in request.POST:
        add_list_form = AddListForm(request.POST, request.FILES)
        if add_list_form.is_valid():
            new_list = add_list_form.save(commit=False)
            new_list.creator = request.user
            new_list.save()
            list_id = new_list.list_id
            messages.success(request, f'List has been created!')
            return redirect('home:list-details', list_id=list_id)
    search_articles = Article.objects.filter(external_source=None).order_by('-pub_date')
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
        'user_lists': user_lists,
        'unseen_notifications': unseen_notifications
    }
    return render(request, 'home/articles.html', context)


def articles_search(request, timeframe, sector, paywall, sources):
    notifications = Notification.objects.filter(user=request.user)
    unseen_notifications = NotificationMessage.objects.filter(notification__in=notifications, user_has_seen=False).count()
    if 'createListForm' in request.POST:
        add_list_form = AddListForm(request.POST, request.FILES)
        if add_list_form.is_valid():
            new_list = add_list_form.save(commit=False)
            new_list.creator = request.user
            new_list.save()
            list_id = new_list.list_id
            messages.success(request, f'List has been created!')
            return redirect('home:list-details', list_id=list_id)
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
        'user_lists': user_lists,
        'unseen_notifications': unseen_notifications
    }
    return render(request, 'home/articles.html', context)    

def list_details(request, list_id):
    notifications = Notification.objects.filter(user=request.user)
    unseen_notifications = NotificationMessage.objects.filter(notification__in=notifications, user_has_seen=False).count()
    list = get_object_or_404(List, list_id=list_id)
    if list.creator == request.user or list.is_public == True:
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
                    new_list = add_list_form.save(commit=False)
                    new_list.creator = request.user
                    new_list.save()
                    list_id = new_list.list_id
                    messages.success(request, f'List has been created!')
                    return redirect('home:list-details', list_id=list_id)
        latest_articles = Article.objects.get_articles_from_list_sources(list)
        latest_articles, _ = paginator_create(request, latest_articles, 10,
                                              'latest_articles')
        change_list_pic_form = ListPicChangeForm()
        change_list_name_form = ListNameChangeForm()
        ammount_of_ratings = ListRating.objects.get_ammount_of_ratings(list_id)
        average_rating = ListRating.objects.get_average_rating(list_id)
        highlighted_articles = List.objects.get_highlighted_articles(list_id)
        highlighted_articles, _ = paginator_create(request,
                                                   highlighted_articles, 10,
                                                   'highlighted_articles')
        add_list_form = AddListForm()
        if request.user.is_authenticated:
            highlighted_articles_titles = HighlightedArticle.objects.get_highlighted_articles_title(
                request.user)
            user_lists = List.objects.get_created_lists(request.user)
            notifications_activated = Notification.objects.filter(
                user=request.user, list=list).exists()
            if request.user in list.subscribers.all():
                subscribed = True
            else:
                subscribed = False
            user_rating = ListRating.objects.get_user_rating(
                request.user, list_id)
        else:
            highlighted_articles_titles = None
            user_lists = None
            subscribed = False  # Refactoren
            user_rating = None
            notifications_activated = None
        context = {
            'add_list_form': add_list_form,
            'ammount_of_ratings': ammount_of_ratings,
            'change_list_name_form': change_list_name_form,
            'change_list_pic_form': change_list_pic_form,
            'list': list,
            'subscribed': subscribed,
            'latest_articles': latest_articles,
            'average_rating': average_rating,
            'user_rating': user_rating,
            'highlighted_articles': highlighted_articles,
            'highlighted_articles_titles': highlighted_articles_titles,
            'user_lists': user_lists,
            'notifications_activated': notifications_activated,
            'unseen_notifications': unseen_notifications
        }
        return render(request, 'home/list_details.html', context)
    else:
        raise Http404("This list does not exist!")


def sector_details(request, slug):
    notifications = Notification.objects.filter(user=request.user)
    unseen_notifications = NotificationMessage.objects.filter(notification__in=notifications, user_has_seen=False).count()
    if 'createListForm' in request.POST:
        add_list_form = AddListForm(request.POST, request.FILES)
        if add_list_form.is_valid():
            new_list = add_list_form.save(commit=False)
            new_list.creator = request.user
            new_list.save()
            list_id = new_list.list_id
            messages.success(request, f'List has been created!')
            return redirect('home:list-details', list_id=list_id)
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
        'articles_from_top_sources': articles_from_top_sources,
        'articles_from_sector': articles_from_sector,
        'sector': sector,
        'highlighted_articles_titles': highlighted_articles_titles,
        'user_lists': user_lists,
        'unseen_notifications': unseen_notifications
    }
    return render(request, 'home/sector_details.html', context)


@login_required()
def settings(request):
    notifications = Notification.objects.filter(user=request.user)
    unseen_notifications = NotificationMessage.objects.filter(notification__in=notifications, user_has_seen=False).count()
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
        elif 'changePrivacySettingsForm' in request.POST:
            privacy_settings_form = PrivacySettingsForm(
                request.POST, instance=request.user.profile.privacysettings)
            if privacy_settings_form.is_valid():
                form = privacy_settings_form.save(commit=False)
                form.profile = request.user.profile
                form.save()
                return redirect('home:settings')
    profile_change_form = ProfileChangeForm(bio=request.user.profile.bio)
    email_and_name_change_form = EmailAndUsernameChangeForm(
        username=request.user.username, email=request.user.email)
    change_password_form = PasswordChangingForm(request.user)
    websites = Website.objects.all()
    social_links = SocialLink.objects.filter(profile=request.user.profile)
    privacy_settings_form = PrivacySettingsForm(
        instance=request.user.profile.privacysettings)
    context = {
        'change_password_form': change_password_form,
        'email_and_name_change_form': email_and_name_change_form,
        'profile_change_form': profile_change_form,
        'social_links': social_links,
        'websites': websites,
        'privacy_settings_form': privacy_settings_form,
        'unseen_notifications': unseen_notifications
    }
    return render(request, 'home/settings.html', context)


def main(request):
    cookie_settings_form = CookieSettingsForm()
    notifications_subscribtions = Notification.objects.filter(user=request.user)
    notifications = NotificationMessage.objects.filter(notification__in=notifications_subscribtions, user_has_seen=False)
    unseen_notifications = notifications.count()
    context = {'cookie_settings_form': cookie_settings_form, 'unseen_notifications': unseen_notifications, 'notifications': notifications}
    return render(request, 'home/main.html', context)


def search_results(request, search_term):
    notifications = Notification.objects.filter(user=request.user)
    unseen_notifications = NotificationMessage.objects.filter(notification__in=notifications, user_has_seen=False).count()
    if 'createListForm' in request.POST:
        add_list_form = AddListForm(request.POST, request.FILES)
        if add_list_form.is_valid():
            new_list = add_list_form.save(commit=False)
            new_list.creator = request.user
            new_list.save()
            list_id = new_list.list_id
            messages.success(request, f'List has been created!')
            return redirect('home:list-details', list_id=list_id)
    filtered_lists = List.objects.filter_lists(search_term)
    filtered_lists, _ = paginator_create(request, filtered_lists, 10,
                                         'filtered_lists')
    filtered_sources = Source.objects.filter_sources(search_term)
    filtered_articles = Article.objects.filter_articles(search_term)
    filtered_articles, _ = paginator_create(request, filtered_articles, 10,
                                            'filtered_articles')
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
        'user_lists': user_lists, 
        'unseen_notifications': unseen_notifications
    }
    return render(request, 'home/search_results.html', context)