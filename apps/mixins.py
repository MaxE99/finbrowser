# Django imports
from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormMixin
from django.http import HttpResponseRedirect
from django.template.defaultfilters import slugify
# Local imports
from apps.list.forms import AddListForm
from apps.article.forms import AddExternalArticleForm
from apps.article.models import Article, HighlightedArticle
from apps.list.models import List
from apps.home.models import Notification, NotificationMessage
from apps.source.models import ExternalSource
from apps.base_logger import logger


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
                return "Failed" if multi_form_page else redirect('list:lists')
            elif List.objects.filter(name=new_list.name, creator=self.request.user).exists() or List.objects.filter(slug=slugify(new_list.name), creator=self.request.user).exists():
                messages.error(self.request, 'You have already created a list with that name!')
                return "Failed" if multi_form_page else redirect('list:lists')
            else:
                new_list.creator = self.request.user
                new_list.save()
                profile_slug = new_list.creator.profile.slug
                list_slug = new_list.slug
                messages.success(self.request, 'List has been created!')
                return [profile_slug, list_slug] if multi_form_page else redirect('list:lists-details', profile_slug=profile_slug, list_slug=list_slug)
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