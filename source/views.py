# Django import
from django.views.generic.detail import DetailView
# Local import
from home.models import Notification, Source, Article, List, SourceRating
from home.logic.pure_logic import paginator_create
from home.views import AddArticlesToListsMixin


class SourceDetailView(DetailView, AddArticlesToListsMixin):
    model = Source
    context_object_name = 'source'
    template_name = 'source/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        source = self.get_object()
        if self.request.user.is_authenticated:
            subscribed = True if self.request.user in source.subscribers.all() else False
            user_rating = SourceRating.objects.get_user_rating(self.request.user, source)
            notifications_activated = Notification.objects.filter(user=self.request.user, source=source).exists()
        else:
            subscribed = False  
            user_rating = notifications_activated = None
        context['latest_articles'] = paginator_create(self.request, Article.objects.get_content_from_source(source), 10, 'latest_articles')
        context['lists'] = paginator_create(self.request, List.objects.get_lists_with_source(source), 10, 'lists')
        context['subscribed'] = subscribed
        context['user_rating'] = user_rating
        context['notifications_activated'] = notifications_activated
        return context
