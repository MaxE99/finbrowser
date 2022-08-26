# Django import
from django.views.generic.detail import DetailView
# Local import
from apps.logic.pure_logic import paginator_create, stocks_get_experts
from apps.home.views import TWITTER, BaseMixin
from apps.stock.models import Stock
from apps.article.models import Article
from django.db.models import Q


class StockDetailView(DetailView, BaseMixin):
    model = Stock
    context_object_name = 'stock'
    template_name = 'stock/stock_details.html'

    def get_object(self):
        slug = self.kwargs['slug']
        return Stock.objects.get(ticker=slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stock = self.get_object()
        filtered_content = Article.objects.filter(Q(search_vector=stock.ticker) | Q(search_vector=stock.short_company_name)).select_related('source', 'source__sector', 'tweet_type', 'source__website').order_by('-pub_date')
        filtered_tweets = filtered_content.filter(source__website=TWITTER).select_related('source', 'source__sector', 'tweet_type', 'source__website').order_by('-pub_date')
        context['expert_sources'] = stocks_get_experts(filtered_content)
        context['filtered_tweets'] = paginator_create(self.request, filtered_tweets, 10, 'filtered_tweets')
        context['filtered_articles'] = paginator_create(self.request, filtered_content.exclude(source__website=TWITTER), 20, 'filtered_articles')
        return context
