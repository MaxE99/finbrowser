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
# Local imports
from accounts.models import SocialLink, Website
from home.models import Article, HighlightedArticle, List, Sector, Source, ListRating, ExternalSource, Notification, NotificationMessage
from home.forms import AddListForm, ListPicChangeForm, ListNameChangeForm, AddExternalArticleForm
from home.logic.pure_logic import paginator_create, lists_filter, articles_filter
from accounts.forms import EmailAndUsernameChangeForm, PasswordChangingForm, ProfileChangeForm, PrivacySettingsForm
from home.base_logger import logger

User = get_user_model()

try:
    TWITTER = get_object_or_404(Website, name="Twitter")
except:
    logger.error("Twitter not found! Problem with database")
    TWITTER = None

# Mixins:

class AddToListInfoMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['highlighted_content_titles'] = HighlightedArticle.objects.get_highlighted_articles_title(self.request.user)
            context['user_lists'] = List.objects.get_created_lists(self.request.user)
        else:
            context['highlighted_content_titles'] = None
            context['user_lists'] = None
        return context


class NotificationMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            notifications_subscribtions = Notification.objects.filter(user=self.request.user)
            unseen_notifications = NotificationMessage.objects.filter(notification__in=notifications_subscribtions, user_has_seen=False).count()
            source_notifications_subscribtions = Notification.objects.filter(user=self.request.user, source__isnull=False)
            source_notifications = NotificationMessage.objects.filter(notification__in=source_notifications_subscribtions).select_related('article', 'article__source', 'article__source__website').order_by('-date')  
            list_notifications_subscribtions = Notification.objects.filter(user=self.request.user, list__isnull=False)
            list_notifications = NotificationMessage.objects.filter(notification__in=list_notifications_subscribtions).select_related('article', 'article__source', 'article__source__website').order_by('-date')
        else:
            unseen_notifications = source_notifications = list_notifications = None
        context['unseen_notifications'] = unseen_notifications
        context['source_notifications'] = source_notifications
        context['list_notifications'] = list_notifications
        return context


class CreateListFormMixin(FormMixin):
    form_class = AddListForm

    def post(self, request, *args, **kwargs):
        form = AddListForm(request.POST, request.FILES)
        multi_form_page = True if 'multi_form_page' in kwargs else False
        if form.is_valid():
            new_list = form.save(commit=False)
            if self.request.user.is_authenticated is False:
                messages.error(self.request, 'Only registered users can create lists!')
                return "Failed" if multi_form_page else redirect('home:lists')
            elif List.objects.filter(name=new_list.name, creator=self.request.user).exists() or List.objects.filter(slug=slugify(new_list.name), creator=self.request.user).exists():
                messages.error(self.request, 'You have already created a list with that name!')
                return "Failed" if multi_form_page else redirect('home:lists')
            else:
                new_list.creator = self.request.user
                new_list.save()
                profile_slug = new_list.creator.profile.slug
                list_slug = new_list.slug
                messages.success(self.request, 'List has been created!')
                return [profile_slug, list_slug] if multi_form_page else redirect('home:list-details', profile_slug=profile_slug, list_slug=list_slug)
        else:
            messages.error(request, "Currently only PNG and JPG files are supported!")
            return "Failed" if multi_form_page else HttpResponseRedirect(self.request.path_info)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_list_form'] = AddListForm()
        return context


class BaseMixin(AddToListInfoMixin, CreateListFormMixin, NotificationMixin):
    """All 3 Mixins are required for notifications to work on every site"""


class AddExternalArticleFormMixin(FormMixin):
    form_class = AddExternalArticleForm

    def post(self, request, *args, **kwargs):
        add_external_articles_form = AddExternalArticleForm(request.POST)
        if add_external_articles_form.is_valid():
            data = add_external_articles_form.cleaned_data
            website_name = data['website_name']
            title = data['title']
            link = data['link']
            pub_date = data['pub_date']
            external_source = ExternalSource.objects.create(user=request.user, website_name=website_name)
            article = Article.objects.create(title=title, link=link, pub_date=pub_date, external_source=external_source)
            HighlightedArticle.objects.create(user=request.user, article=article)
            messages.success(request, 'Article has been added!')
        else:
            logger.error(f'Add external articles form not valid! - {add_external_articles_form.errors.as_data()}')
            messages.error(self.request, 'Error: Article could not be added!')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_external_articles_form'] = AddExternalArticleForm()
        return context


# Views:

class SectorView(ListView, BaseMixin):
    model = Sector
    context_object_name = 'sectors'
    template_name = 'home/sectors.html'
    queryset = Sector.objects.prefetch_related('source_set').all().order_by('name')


class ListsView(ListView, BaseMixin):
    model = List
    context_object_name = 'lists'
    template_name = 'home/lists.html'
    queryset = List.objects.select_related('creator__profile').prefetch_related('articles', 'sources').filter(is_public=True).order_by('name')
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results_found'] = self.queryset.count()
        return context


class ArticleView(ListView, BaseMixin):
    model = Article
    template_name = 'home/articles.html'
    paginate_by = 10

    def get_queryset(self):
        return Article.objects.get_content_excluding_website(TWITTER)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tweets_qs = Article.objects.get_content_from_website(TWITTER)
        context['articles'] = paginator_create(self.request, self.get_queryset(), 10, 'articles')
        context['sectors'] = Sector.objects.all().order_by('name')
        context['tweets'] = paginator_create(self.request, tweets_qs, 20, 'tweets')
        context['results_found'] = self.object_list.count() + tweets_qs.count()
        return context


class ArticleSearchView(ListView, BaseMixin):
    model = Article
    template_name = 'home/articles.html'
    paginate_by = 10

    def get_queryset(self):
        sector = get_object_or_404(Sector, name=self.kwargs['sector']).sector_id if self.kwargs['sector'] != "All" else "All"
        source = get_object_or_404(Website, name=self.kwargs['source']).id if self.kwargs['source'] != "All" else "All"
        return articles_filter(self.kwargs['timeframe'], sector, self.kwargs['paywall'], source, Article.objects.select_related('source').filter(external_source=None))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        articles_qs = self.get_queryset().select_related('source', 'source__website', 'source__sector').filter(external_source=None).exclude(source__website=TWITTER).order_by('-pub_date')
        tweets_qs = self.get_queryset().select_related('source').filter(source__website=TWITTER).order_by('-pub_date')
        context['sectors'] = Sector.objects.all().order_by('name')
        context['articles'] = paginator_create(self.request, articles_qs, 10, 'articles')
        context['tweets'] = paginator_create(self.request, tweets_qs, 20, 'tweets')
        context['results_found'] = articles_qs.count() + tweets_qs.count()
        return context



class MainView(TemplateView, BaseMixin):
    template_name = 'home/main.html'


class NotificationView(TemplateView, BaseMixin):
    template_name = 'home/notifications.html'


class SectorDetailView(DetailView, BaseMixin):
    model = Sector
    context_object_name = 'sector'
    template_name = 'home/sector_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sector = self.get_object()
        context['articles_from_sector'] = paginator_create(self.request, Article.objects.get_content_from_sector_excluding_website(sector, TWITTER), 10, 'articles_from_sector')
        context['tweets_from_sector'] = paginator_create(self.request, Article.objects.get_content_from_sector_and_website(sector, TWITTER), 20, 'tweets_from_sector')
        return context


class FeedView(TemplateView, LoginRequiredMixin, BaseMixin, AddExternalArticleFormMixin):
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
        else:
            logger.error(f"Feed view problems with POST request! - {request.POST}")
            return HttpResponseRedirect(self.request.path_info)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subscribed_sources = Source.objects.get_subscribed_sources(self.request.user)
        context['subscribed_lists'] = List.objects.get_subscribed_lists(self.request.user)
        context['subscribed_sources'] = subscribed_sources
        context['subscribed_content'] = paginator_create(self.request, Article.objects.get_subscribed_content_excluding_website(subscribed_sources, TWITTER), 10, 'subscribed_content')
        context['highlighted_content'] = paginator_create(self.request, HighlightedArticle.objects.get_highlighted_articles_from_user_excluding_website(self.request.user, TWITTER), 10, 'highlighted_content')
        context['highlighted_tweets'] = paginator_create(self.request, HighlightedArticle.objects.get_highlighted_articles_from_user_and_website(self.request.user, TWITTER), 10, 'highlighted_tweets')
        context['newest_tweets'] = paginator_create(self.request, Article.objects.get_subscribed_content_from_website(subscribed_sources, TWITTER), 10, 'newest_tweets')
        return context


class SearchResultView(TemplateView, BaseMixin):
    template_name = 'home/search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_term = kwargs['search_term']
        context['filtered_lists'] = paginator_create(self.request, List.objects.filter_lists(search_term), 10, 'filtered_lists')
        context['filtered_sources'] = Source.objects.filter_sources(search_term)
        context['filtered_articles'] = paginator_create(self.request, Article.objects.filter_articles(search_term), 10, 'filtered_articles')
        return context


class ListSearchView(ListView, BaseMixin):
    model = List
    context_object_name = 'lists'
    template_name = 'home/lists.html'
    paginate_by = 10

    def get_queryset(self):
        return lists_filter(self.kwargs['timeframe'], self.kwargs['content_type'], self.kwargs['minimum_rating'], self.kwargs['primary_source'], List.objects.filter(is_public=True).order_by('name'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results_found'] = self.get_queryset().count()
        return context


class ListDetailView(TemplateView, BaseMixin):
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
                    messages.error(request, "Error: Currently only PNG and JPG files are supported!")
                    return HttpResponseRedirect(self.request.path_info)
                if new_list_slug == list_slug:
                    messages.success(request, 'List settings have been saved!')
                elif change_list_name_form.is_valid() and new_list_slug != list_slug and List.objects.filter(creator=request.user, slug=new_list_slug).exists() == False:
                        change_list_name_form.save()
                        messages.success(request, 'List settings have been saved!')
                else:
                    messages.error(request, "Error: You've already created a list with that name!")
                    return HttpResponseRedirect(self.request.path_info)
                if new_list_slug != list_slug:
                    return redirect('home:list-details', profile_slug=profile_slug , list_slug=new_list_slug)
                else:
                    return HttpResponseRedirect(self.request.path_info)
            else:
                logger.error(f'User tried to change list name of list created by another user! - {self.request.user}')
        else:
            return HttpResponseRedirect(self.request.path_info)

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
        context['latest_articles'] = paginator_create(self.request, Article.objects.get_articles_from_list_sources_excluding_website(list, TWITTER), 10, 'latest_articles') 
        context['highlighted_articles'] = paginator_create(self.request, List.objects.get_highlighted_content_from_list_excluding_website(list_id, TWITTER), 10, 'highlighted_articles')
        context['notifications_activated'] = notifications_activated
        context['subscribed'] = subscribed
        context['user_rating'] = user_rating
        context['highlighted_tweets'] = paginator_create(self.request, List.objects.get_highlighted_content_from_list_and_website(list_id, TWITTER), 20, 'highlighted_tweets')
        context['newest_tweets'] = paginator_create(self.request, Article.objects.get_articles_from_list_sources_and_website(list, TWITTER), 20, 'newest_tweets')
        if self.request.user == list.creator:
            context['change_list_pic_form'] = ListPicChangeForm()
            context['change_list_name_form'] = ListNameChangeForm()
        return context


class SettingsView(LoginRequiredMixin, TemplateView, BaseMixin):
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
                    messages.success(request, 'Username and Email have been updated!')
                else:
                    messages.error(request, "Error: Username or email already exists!")
            else:
                messages.error(request, "Error: Currently only PNG and JPG files are supported!")
        elif "changePasswordForm" in request.POST:
            change_password_form = PasswordChangingForm(user=request.user, data=request.POST or None)
            if change_password_form.is_valid():
                change_password_form.save()
                update_session_auth_hash(request, change_password_form.user)
                messages.success(request, 'Password has been changed!')
            else:
                messages.error(request, 'New password is invalid!')
        elif 'changePrivacySettingsForm' in request.POST:
            privacy_settings_form = PrivacySettingsForm(request.POST, instance=request.user.profile.privacysettings)
            if privacy_settings_form.is_valid():
                form = privacy_settings_form.save(commit=False)
                form.profile = request.user.profile
                form.save()
                messages.success(request, 'Privacy settings have been updated!')
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

