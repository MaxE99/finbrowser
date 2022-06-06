# Django imports
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormMixin
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.template.defaultfilters import slugify
# Python imports
from datetime import timedelta, date
# Local imports
from accounts.models import SocialLink, Website
from home.models import Article, HighlightedArticle, List, Sector, Source, ListRating, ExternalSource, Notification
from home.forms import AddListForm, ListPicChangeForm, ListNameChangeForm, AddExternalArticleForm
from home.logic.pure_logic import paginator_create
from accounts.forms import EmailAndUsernameChangeForm, PasswordChangingForm, ProfileChangeForm, PrivacySettingsForm
from home.base_logger import logger

User = get_user_model()


# Mixins:

# class NotificationMixin(ContextMixin):
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         if self.request.user.is_authenticated:
#             unseen_notifications, source_notifications, list_notifications = notifications_get(self.request.user)
#         else:
#             unseen_notifications = source_notifications = list_notifications = None
#         context['unseen_notifications'] = unseen_notifications
#         context['source_notifications'] = source_notifications
#         context['list_notifications'] = list_notifications
#         return context


class AddToListInfoMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['highlighted_articles_titles'] = HighlightedArticle.objects.get_highlighted_articles_title(self.request.user)
            context['user_lists'] = List.objects.get_created_lists(self.request.user)
        else:
            context['highlighted_articles_titles'] = None
            context['user_lists'] = None
        return context


class CreateListFormMixin(FormMixin):
    form_class = AddListForm

    def post(self, request, *args, **kwargs):
        form = AddListForm(request.POST, request.FILES)
        multi_form_page = True if 'multi_form_page' in kwargs else False
        if form.is_valid():
            new_list = form.save(commit=False)
            if self.request.user.is_authenticated is False:
                messages.error(self.request, 'Only users can create lists!')
                return "Failed" if multi_form_page else redirect('home:lists')
            elif List.objects.filter(name=new_list.name, creator=self.request.user).exists():
                messages.error(self.request, 'You have already created a list with this name!')
                return "Failed" if multi_form_page else redirect('home:lists')
            else:
                new_list.creator = self.request.user
                new_list.save()
                profile_slug = new_list.creator.profile.slug
                list_slug = new_list.slug
                messages.success(self.request, 'List has been created!')
                return [profile_slug, list_slug] if multi_form_page else redirect('home:list-details', profile_slug=profile_slug, list_slug=list_slug)
        else:
            messages.error(request, "Error: Only PNG and JPG files are currently supported!")
            return "Failed" if multi_form_page else HttpResponseRedirect(self.request.path_info)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_list_form'] = AddListForm()
        return context


class AddArticlesToListsMixin(AddToListInfoMixin, CreateListFormMixin):
    """Both Mixins are almost always used together"""


class AddExternalArticleFormMixin(FormMixin):
    form_class = AddExternalArticleForm

    def post(self, request, *args, **kwargs):
        add_external_articles_form = AddExternalArticleForm(request.POST)
        if add_external_articles_form.is_valid():
            data = add_external_articles_form.cleaned_data
            website_name = data['website_name']
            sector = data['sector']
            title = data['title']
            link = data['link']
            pub_date = data['pub_date']
            external_source = ExternalSource.objects.create(user=request.user, website_name=website_name, sector=sector)
            article = Article.objects.create(title=title, link=link, pub_date=pub_date, external_source=external_source)
            HighlightedArticle.objects.create(user=request.user, article=article)
            messages.success(request, 'Article has been added!')
        else:
            logger.error(f'Add external articles form not valid! - {add_external_articles_form.errors.as_data()}')
            messages.error(self.request, 'Error: External article could not be added!')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_external_articles_form'] = AddExternalArticleForm()
        return context


# Views:

class SectorView(ListView):
    model = Sector
    context_object_name = 'sectors'
    template_name = 'home/sectors.html'
    queryset = Sector.objects.prefetch_related('source_set').all().order_by('name')


class ListsView(ListView, CreateListFormMixin):
    model = List
    context_object_name = 'lists'
    template_name = 'home/lists.html'
    queryset = List.objects.select_related('creator__profile').filter(is_public=True).order_by('name')
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results_found'] = self.queryset.count()
        return context


class ArticleView(ListView, AddArticlesToListsMixin):
    model = Article
    context_object_name = 'search_articles'
    template_name = 'home/articles.html'
    paginate_by = 10

    def get_queryset(self):
        return Article.objects.filter(external_source=None).exclude(source__website=get_object_or_404(Website, name="Twitter")).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        twitter_sources = Source.objects.filter(website=get_object_or_404(Website, name="Twitter"))
        context['results_found'] = self.object_list.count()
        context['sectors'] = Sector.objects.all().order_by('name')
        context['tweets'] = paginator_create(self.request, Article.objects.filter(source__in=twitter_sources).order_by('-pub_date'), 9, 'tweets')
        context['external_articles'] = paginator_create(self.request, Article.objects.filter(external_source=True).order_by('-pub_date'), 9, 'external_articles')
        return context


class MainView(TemplateView):
    template_name = 'home/main.html'


class SectorDetailView(DetailView, AddArticlesToListsMixin):
    model = Sector
    context_object_name = 'sector'
    template_name = 'home/sector_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sector = self.get_object()
        sources = sector.source_set.all().filter(top_source=True)
        context['articles_from_sector'] = paginator_create(self.request, Article.objects.get_articles_from_sector(sector).order_by('-pub_date'), 10, 'articles_from_sector')
        context['articles_from_top_sources'] = paginator_create(self.request, Article.objects.select_related('source', 'source__sector').filter(source__in=sources).order_by('-pub_date'), 10, 'articles_from_top_sources')
        return context


class FeedView(TemplateView, LoginRequiredMixin, AddArticlesToListsMixin, AddExternalArticleFormMixin):
    template_name = 'home/feed.html'

    def post(self, request, *args, **kwargs):
        if 'createListForm' in request.POST:
            post_res = CreateListFormMixin.post(self, request, multi_form_page=True)
            if post_res == 'Failed':
                return redirect('home:feed')
            else:
                profile_slug, list_slug = post_res
                return redirect('home:list-details', profile_slug=profile_slug, list_slug=list_slug)
        elif 'addExternalArticlesForm' in request.POST:
            AddExternalArticleFormMixin.post(self, request)
            return redirect('home:feed')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subscribed_sources = Source.objects.get_subscribed_sources(self.request.user)
        context['user_lists'] = List.objects.get_created_lists(self.request.user)
        context['subscribed_lists'] = List.objects.get_subscribed_lists(self.request.user)
        context['subscribed_sources'] = subscribed_sources
        context['subscribed_articles'] = paginator_create(self.request, Article.objects.get_articles_from_subscribed_sources(subscribed_sources), 10, 'subscribed_articles')
        context['highlighted_articles'] = paginator_create(self.request, HighlightedArticle.objects.select_related('article', 'article__source', 'article__external_source', 'article__source__sector').filter(user=self.request.user).order_by('-article__pub_date'), 10, 'highlighted_articles')
        return context


class SearchResultView(TemplateView, AddArticlesToListsMixin):
    template_name = 'home/search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_term = kwargs['search_term']
        context['filtered_lists'] = paginator_create(self.request, List.objects.filter_lists(search_term), 10, 'filtered_lists')
        context['filtered_sources'] = Source.objects.filter_sources(search_term)
        context['filtered_articles'] = paginator_create(self.request, Article.objects.filter_articles(search_term), 10, 'filtered_articles')
        return context


class ListSearchView(ListView, AddArticlesToListsMixin):
    model = List
    context_object_name = 'lists'
    template_name = 'home/lists.html'
    paginate_by = 10

    def get_queryset(self):
        timeframe = self.kwargs['timeframe']
        content_type = self.kwargs['content_type']
        minimum_rating = self.kwargs['minimum_rating']
        sources = self.kwargs['sources']
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
        return lists

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results_found'] = len(self.get_queryset())
        return context


class ArticleSearchView(ListView, AddArticlesToListsMixin):
    model = Article
    context_object_name = 'search_articles'
    template_name = 'home/articles.html'
    paginate_by = 10

    def get_queryset(self):
        timeframe = self.kwargs['timeframe']
        sector = self.kwargs['sector']
        paywall = self.kwargs['paywall']
        sources = self.kwargs['sources']
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
        return search_articles

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results_found'] = len(self.get_queryset())
        context['sectors'] = Sector.objects.all().order_by('name')
        return context


class ListDetailView(TemplateView, AddArticlesToListsMixin):
    model = List
    context_object_name = 'list'
    template_name = 'home/list_details.html'

    def post(self, request, *args, **kwargs):
        if 'createListForm' in request.POST:
            post_res = CreateListFormMixin.post(self, request, multi_form_page=True)
            if post_res == 'Failed':
                return redirect('home:feed')
            else:
                profile_slug, list_slug = post_res
                return redirect('home:list-details', profile_slug=profile_slug, list_slug=list_slug)
        elif 'changeListForm' in request.POST:
            profile_slug = self.request.path_info.rsplit('/', 2)[-2]
            list_slug = self.request.path_info.rsplit('/', 1)[-1]
            list = get_object_or_404(List, slug=list_slug)
            if self.request.user == list.creator:
                new_list_slug = slugify(request.POST.get('name'))
                change_list_name_form = ListNameChangeForm(request.POST, instance=list)
                change_list_pic_form = ListPicChangeForm(request.POST, request.FILES, instance=list)
                if change_list_pic_form.is_valid():
                    change_list_pic_form.save()
                else:
                    messages.error(request, "Error: Only PNG and JPG files are currently supported!")
                    return HttpResponseRedirect(self.request.path_info)
                if change_list_name_form.is_valid() and List.objects.filter(creator=request.user, slug=new_list_slug).exists() == False:
                    change_list_name_form.save()
                else:
                    messages.error(request, "Error: You can't use this name!")
                    return HttpResponseRedirect(self.request.path_info)
                if new_list_slug != list_slug:
                    return redirect('home:list-details', profile_slug=profile_slug , list_slug=new_list_slug)
                else:
                    return HttpResponseRedirect(self.request.path_info)
            else:
                logger.error(f'User tried to change list name of list created by another user! - {self.request.user}')
                messages.error(self.request, 'Error: Lists of other users can not be altered!')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        list = get_object_or_404(List, slug=self.kwargs['list_slug'])
        list_id = list.list_id
        if self.request.user.is_authenticated:
            notifications_activated = Notification.objects.filter(user=self.request.user, list=list).exists()
            subscribed = True if self.request.user in list.subscribers.all() else False
            user_rating = ListRating.objects.get_user_rating(self.request.user, list_id)
        else:
            notifications_activated = user_rating = None
            subscribed = False  
        context['list'] = list
        context['latest_articles'] = paginator_create(self.request, Article.objects.get_articles_from_list_sources(list), 10, 'latest_articles') 
        context['highlighted_articles'] = paginator_create(self.request, List.objects.get_highlighted_articles(list.list_id), 10, 'highlighted_articles')
        context['ammount_of_ratings'] = ListRating.objects.get_ammount_of_ratings(list_id)
        context['average_rating'] = ListRating.objects.get_average_rating(list_id)
        context['notifications_activated'] = notifications_activated
        context['subscribed'] = subscribed
        context['user_rating'] = user_rating
        if self.request.user == list.creator:
            context['change_list_pic_form'] = ListPicChangeForm()
            context['change_list_name_form'] = ListNameChangeForm()
        return context


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'home/settings.html'

    def post(self, request, *args, **kwargs):
        if 'changeProfileForm' in request.POST:
            email_and_name_change_form = EmailAndUsernameChangeForm(request.POST, username=request.user.username, email=request.user.email, instance=request.user)
            profile_change_form = ProfileChangeForm(request.POST, request.FILES, bio=request.user.profile.bio, instance=request.user.profile)
            if profile_change_form.is_valid():
                profile_change_form.save()
                if email_and_name_change_form.is_valid():
                    request.user.save()
                    request.user.profile.save()
                else:
                    messages.error(request, "Error: Username or email already exists!")
            else:
                messages.error(request, "Error: Only PNG and JPG files are currently supported!")
        elif "changePasswordForm" in request.POST:
            change_password_form = PasswordChangingForm(user=request.user, data=request.POST or None)
            if change_password_form.is_valid():
                change_password_form.save()
                update_session_auth_hash(request, change_password_form.user)
        elif 'changePrivacySettingsForm' in request.POST:
            privacy_settings_form = PrivacySettingsForm(request.POST, instance=request.user.profile.privacysettings)
            if privacy_settings_form.is_valid():
                form = privacy_settings_form.save(commit=False)
                form.profile = request.user.profile
                form.save()
        return HttpResponseRedirect(self.request.path_info)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['websites'] = Website.objects.all()
        context['social_links'] = SocialLink.objects.select_related('website').filter(profile=self.request.user.profile)
        context['notifications'] = Notification.objects.select_related('source', 'list', 'list__creator__profile').filter(user=self.request.user)
        context['profile_change_form'] = ProfileChangeForm(bio=self.request.user.profile.bio)
        context['email_and_name_change_form'] = EmailAndUsernameChangeForm(username=self.request.user.username, email=self.request.user.email)
        context['change_password_form'] = PasswordChangingForm(self.request.user)
        context['privacy_settings_form'] = PrivacySettingsForm(instance=self.request.user.profile.privacysettings)
        return context

