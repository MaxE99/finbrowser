# Django Imports
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone

# Python Import
from datetime import timedelta

# Local Imports
from apps.accounts.models import Website
from apps.article.models import Article, HighlightedArticle, TrendingTopicContent
from apps.home.models import Notification, NotificationMessage
from apps.list.models import List
from apps.sector.models import Sector
from apps.source.models import Source, SourceRating, SourceTag
from apps.stock.models import Stock, Portfolio, PortfolioStock, PortfolioKeyword

User = get_user_model()


def create_test_users():
    testuser1 = User.objects.create(username="TestUser1", email="testuser1@mail.com")
    testuser1.set_password("testpw99")
    testuser1.save()
    for i in range(2, 11):
        User.objects.create(username=f"TestUser{i}", email=f"testuser{i}mail.com")
    testuser12 = User.objects.create(username="TestUser12", email="testuser12@mail.com")
    testuser12.set_password("testpw99")
    testuser12.save()


def create_test_sectors():
    for i in range(1, 11):
        Sector.objects.create(name=f"TestSector{i}")


def create_test_website():
    for i in range(1, 11):
        Website.objects.create(name=f"TestWebsite{i}")
    Website.objects.create(name="Twitter")


def create_test_sources():
    source1 = Source.objects.create(
        url="www.testsource1.com/",
        slug="testsource1",
        name="TestSource1",
        paywall="Yes",
        website=get_object_or_404(Website, name="TestWebsite1"),
        sector=get_object_or_404(Sector, name="TestSector1"),
        top_source=True,
        content_type="Analysis",
    )
    source1.subscribers.add(get_object_or_404(User, username="TestUser1"))
    source1.subscribers.add(get_object_or_404(User, username="TestUser2"))
    source1.subscribers.add(get_object_or_404(User, username="TestUser8"))
    source2 = Source.objects.create(
        url="www.testsource2.com/",
        slug="testsource2",
        name="TestSource2",
        paywall="No",
        website=get_object_or_404(Website, name="TestWebsite1"),
        sector=get_object_or_404(Sector, name="TestSector2"),
        top_source=False,
        content_type="News",
    )
    source2.subscribers.add(get_object_or_404(User, username="TestUser1"))
    source3 = Source.objects.create(
        url="www.testsource3.com/",
        slug="testsource3",
        name="TestSource3",
        paywall="Yes",
        website=get_object_or_404(Website, name="TestWebsite2"),
        sector=get_object_or_404(Sector, name="TestSector2"),
        top_source=True,
        content_type="Commentary",
    )
    source3.subscribers.add(get_object_or_404(User, username="TestUser1"))
    Source.objects.create(
        url="www.testsource4.com/",
        slug="testsource4",
        name="TestSource4",
        paywall="No",
        website=get_object_or_404(Website, name="TestWebsite1"),
        sector=get_object_or_404(Sector, name="TestSector2"),
        top_source=False,
        content_type="News",
    )
    Source.objects.create(
        url="www.testsource5.com/",
        slug="testsource5",
        name="TestSource5",
        paywall="Yes",
        website=get_object_or_404(Website, name="TestWebsite2"),
        sector=get_object_or_404(Sector, name="TestSector3"),
        top_source=False,
        content_type="Commentary",
    )
    Source.objects.create(
        url="www.testsource6.com/",
        slug="testsource6",
        name="TestSource6",
        paywall="Yes",
        website=get_object_or_404(Website, name="TestWebsite3"),
        sector=get_object_or_404(Sector, name="TestSector4"),
        top_source=False,
        content_type="Analysis",
    )
    Source.objects.create(
        url="www.testsource7.com/",
        slug="testsource7",
        name="TestSource7",
        paywall="No",
        website=get_object_or_404(Website, name="TestWebsite4"),
        sector=get_object_or_404(Sector, name="TestSector1"),
        top_source=False,
        content_type="Commentary",
    )
    Source.objects.create(
        url="www.testsource8.com/",
        slug="testsource8",
        name="TestSource8",
        paywall="Yes",
        website=get_object_or_404(Website, name="TestWebsite1"),
        sector=get_object_or_404(Sector, name="TestSector1"),
        top_source=False,
        content_type="News",
    )
    Source.objects.create(
        url="www.testsource9.com/",
        slug="testsource9",
        name="TestSource9",
        paywall="Yes",
        website=get_object_or_404(Website, name="TestWebsite4"),
        sector=get_object_or_404(Sector, name="TestSector3"),
        top_source=False,
        content_type="Commentary",
    )
    Source.objects.create(
        url="www.testsource10.com/",
        slug="testsource10",
        name="TestSource10",
        paywall="Yes",
        website=get_object_or_404(Website, name="TestWebsite6"),
        sector=get_object_or_404(Sector, name="TestSector3"),
        top_source=True,
        content_type="Analysis",
    )
    Source.objects.create(
        url="www.testsource11.com/",
        slug="testsource11",
        name="TestSource11",
        paywall="Yes",
        website=get_object_or_404(Website, name="Twitter"),
        sector=get_object_or_404(Sector, name="TestSector3"),
        top_source=True,
        content_type="Analysis",
    )
    Source.objects.create(
        url="www.festsource11.com/",
        slug="festsource11",
        name="festSource11",
        paywall="Yes",
        website=get_object_or_404(Website, name="Twitter"),
        sector=get_object_or_404(Sector, name="TestSector5"),
        top_source=True,
        content_type="Commentary",
    )


def create_test_stock():
    Stock.objects.create(ticker="MSFT", short_company_name="Microsoft")
    Stock.objects.create(ticker="AMZN", short_company_name="Amazon")
    Stock.objects.create(ticker="TSLA", short_company_name="Tesla")
    Stock.objects.create(ticker="SNOW", short_company_name="Snowflake")
    Stock.objects.create(ticker="NVDA", short_company_name="Nvidia")
    Stock.objects.create(ticker="INTC", short_company_name="Intel")
    Stock.objects.create(ticker="TSM", short_company_name="Taiwan Semiconductor")
    Stock.objects.create(ticker="META", short_company_name="Meta Platforms")
    Stock.objects.create(ticker="GOOG", short_company_name="Alphabet")
    Stock.objects.create(ticker="F", short_company_name="Ford")
    Stock.objects.create(ticker="TEST", short_company_name="Test Company")


def create_test_notifications():
    Notification.objects.create(
        user=get_object_or_404(User, username="TestUser1"),
        source=get_object_or_404(Source, name="TestSource1"),
    )
    Notification.objects.create(
        user=get_object_or_404(User, username="TestUser2"),
        source=get_object_or_404(Source, name="TestSource1"),
    )
    Notification.objects.create(
        user=get_object_or_404(User, username="TestUser2"),
        source=get_object_or_404(Source, name="TestSource2"),
    )
    Notification.objects.create(
        user=get_object_or_404(User, username="TestUser3"),
        source=get_object_or_404(Source, name="TestSource1"),
    )
    Notification.objects.create(
        user=get_object_or_404(User, username="TestUser3"),
        source=get_object_or_404(Source, name="TestSource3"),
    )
    Notification.objects.create(
        user=get_object_or_404(User, username="TestUser1"),
        source=get_object_or_404(Source, name="TestSource5"),
    )
    Notification.objects.create(
        user=get_object_or_404(User, username="TestUser1"),
        source=get_object_or_404(Source, name="TestSource7"),
    )
    Notification.objects.create(
        user=get_object_or_404(User, username="TestUser2"),
        source=get_object_or_404(Source, name="TestSource4"),
    )
    Notification.objects.create(
        user=get_object_or_404(User, username="TestUser1"),
        source=get_object_or_404(Source, name="TestSource3"),
    )
    Notification.objects.create(
        user=get_object_or_404(User, username="TestUser2"),
        source=get_object_or_404(Source, name="TestSource9"),
    )
    Notification.objects.create(
        user=get_object_or_404(User, username="TestUser1"),
        stock=get_object_or_404(Stock, ticker="TSLA"),
    )
    Notification.objects.create(
        user=get_object_or_404(User, username="TestUser1"),
        keyword="AWS",
    )
    Notification.objects.create(
        user=get_object_or_404(User, username="TestUser1"),
        keyword="Twitch",
    )


def create_test_articles():
    Article.objects.create(
        title="TestArticle1",
        source=get_object_or_404(Source, name="TestSource1"),
        link="www.testarticle1.com",
        pub_date=(timezone.now() - timedelta(days=2)),
    )
    Article.objects.create(
        title="TestArticle2",
        source=get_object_or_404(Source, name="TestSource1"),
        link="www.testarticle2.com",
        pub_date=(timezone.now() - timedelta(days=1)),
    )
    Article.objects.create(
        title="TestArticle3",
        source=get_object_or_404(Source, name="TestSource2"),
        link="www.testarticle3.com",
        pub_date=(timezone.now() - timedelta(days=3)),
    )
    Article.objects.create(
        title="TestArticle4",
        source=get_object_or_404(Source, name="TestSource2"),
        link="www.testarticle4.com",
        pub_date=(timezone.now() - timedelta(days=4)),
    )
    Article.objects.create(
        title="TestArticle5",
        source=get_object_or_404(Source, name="TestSource3"),
        link="www.testarticle5.com",
        pub_date=(timezone.now() - timedelta(days=5)),
    )
    Article.objects.create(
        title="TestArticle6",
        source=get_object_or_404(Source, name="TestSource1"),
        link="www.testarticle6.com",
        pub_date=(timezone.now() - timedelta(days=6)),
    )
    Article.objects.create(
        title="TestArticle7",
        source=get_object_or_404(Source, name="TestSource1"),
        link="www.testarticle7.com",
        pub_date=(timezone.now() - timedelta(days=6)),
    )
    Article.objects.create(
        title="TestArticle8",
        source=get_object_or_404(Source, name="TestSource3"),
        link="www.testarticle8.com",
        pub_date=(timezone.now() - timedelta(days=4)),
    )
    Article.objects.create(
        title="TestArticle9",
        source=get_object_or_404(Source, name="TestSource2"),
        link="www.testarticle9.com",
        pub_date=(timezone.now() - timedelta(days=8)),
    )
    Article.objects.create(
        title="TestArticle10",
        source=get_object_or_404(Source, name="TestSource1"),
        link="www.testarticle10.com",
        pub_date=(timezone.now() - timedelta(days=3)),
    )
    article11 = Article.objects.create(
        title="TestArticle11",
        source=get_object_or_404(Source, name="TestSource11"),
        link="www.testarticle11.com",
        pub_date=(timezone.now() - timedelta(days=3)),
    )
    TrendingTopicContent.objects.create(article=article11)
    Article.objects.create(
        title="Today we look at $F which is ...",
        source=get_object_or_404(Source, name="TestSource1"),
        link="www.testarticle12.com",
        pub_date=(timezone.now() - timedelta(days=3)),
    )
    Article.objects.create(
        title="Ford is making more automobiles ...",
        source=get_object_or_404(Source, name="TestSource1"),
        link="www.testarticle13.com",
        pub_date=(timezone.now() - timedelta(days=3)),
    )
    Article.objects.create(
        title="Title that holds Test without Article behind it",
        source=get_object_or_404(Source, pk=7),
        link="testarticle14.com",
        pub_date=(timezone.now() - timedelta(days=4)),
    )


def create_test_notification_messages():
    NotificationMessage.objects.create(
        notification=Notification.objects.all()[1],
        article=get_object_or_404(Article, title="TestArticle11"),
        date=timezone.now(),
    )
    NotificationMessage.objects.create(
        notification=Notification.objects.all()[2],
        article=get_object_or_404(Article, title="TestArticle10"),
        date=timezone.now(),
    )
    NotificationMessage.objects.create(
        notification=Notification.objects.all()[3],
        article=get_object_or_404(Article, title="TestArticle9"),
        date=timezone.now(),
    )
    NotificationMessage.objects.create(
        notification=Notification.objects.all()[4],
        article=get_object_or_404(Article, title="TestArticle8"),
        date=timezone.now(),
    )
    NotificationMessage.objects.create(
        notification=Notification.objects.all()[5],
        article=get_object_or_404(Article, title="TestArticle7"),
        date=timezone.now(),
    )
    NotificationMessage.objects.create(
        notification=Notification.objects.all()[6],
        article=get_object_or_404(Article, title="TestArticle6"),
        date=timezone.now(),
    )


def create_test_source_ratings():
    SourceRating.objects.create(
        user=get_object_or_404(User, username="TestUser1"),
        source=get_object_or_404(Source, name="TestSource1"),
        rating=5,
    )
    SourceRating.objects.create(
        user=get_object_or_404(User, username="TestUser2"),
        source=get_object_or_404(Source, name="TestSource1"),
        rating=4,
    )
    SourceRating.objects.create(
        user=get_object_or_404(User, username="TestUser3"),
        source=get_object_or_404(Source, name="TestSource1"),
        rating=1,
    )
    SourceRating.objects.create(
        user=get_object_or_404(User, username="TestUser4"),
        source=get_object_or_404(Source, name="TestSource2"),
        rating=2,
    )
    SourceRating.objects.create(
        user=get_object_or_404(User, username="TestUser5"),
        source=get_object_or_404(Source, name="TestSource2"),
        rating=3,
    )
    SourceRating.objects.create(
        user=get_object_or_404(User, username="TestUser6"),
        source=get_object_or_404(Source, name="TestSource3"),
        rating=2,
    )
    SourceRating.objects.create(
        user=get_object_or_404(User, username="TestUser7"),
        source=get_object_or_404(Source, name="TestSource2"),
        rating=3,
    )
    SourceRating.objects.create(
        user=get_object_or_404(User, username="TestUser8"),
        source=get_object_or_404(Source, name="TestSource1"),
        rating=1,
    )
    SourceRating.objects.create(
        user=get_object_or_404(User, username="TestUser9"),
        source=get_object_or_404(Source, name="TestSource3"),
        rating=4,
    )
    SourceRating.objects.create(
        user=get_object_or_404(User, username="TestUser1"),
        source=get_object_or_404(Source, name="TestSource4"),
        rating=3,
    )


def create_test_portfolio():
    portfolio1 = Portfolio.objects.create(
        user=get_object_or_404(User, username="TestUser1"), name="Portfolio1"
    )
    portfolio1.blacklisted_sources.add(get_object_or_404(Source, source_id=1))
    Portfolio.objects.create(
        user=get_object_or_404(User, username="TestUser1"), name="Portfolio2"
    )
    Portfolio.objects.create(
        user=get_object_or_404(User, username="TestUser1"), name="Portfolio3"
    )
    Portfolio.objects.create(
        user=get_object_or_404(User, username="TestUser1"), name="Portfolio4"
    )
    Portfolio.objects.create(
        user=get_object_or_404(User, username="TestUser1"), name="Portfolio5"
    )
    Portfolio.objects.create(
        user=get_object_or_404(User, username="TestUser1"), name="Portfolio6"
    )
    Portfolio.objects.create(
        user=get_object_or_404(User, username="TestUser1"), name="Portfolio7"
    )
    Portfolio.objects.create(
        user=get_object_or_404(User, username="TestUser1"), name="Portfolio8"
    )
    Portfolio.objects.create(
        user=get_object_or_404(User, username="TestUser2"), name="Portfolio9"
    )
    Portfolio.objects.create(
        user=get_object_or_404(User, username="TestUser3"), name="Portfolio10"
    )
    Portfolio.objects.create(
        user=get_object_or_404(User, username="TestUser12"), name="Portfolio11"
    )


def create_test_portfolio_stock():
    PortfolioStock.objects.create(
        portfolio=get_object_or_404(Portfolio, name="Portfolio1"),
        stock=get_object_or_404(Stock, ticker="TSLA"),
    )
    PortfolioStock.objects.create(
        portfolio=get_object_or_404(Portfolio, name="Portfolio1"),
        stock=get_object_or_404(Stock, ticker="MSFT"),
    )
    PortfolioStock.objects.create(
        portfolio=get_object_or_404(Portfolio, name="Portfolio1"),
        stock=get_object_or_404(Stock, ticker="GOOG"),
    )
    PortfolioStock.objects.create(
        portfolio=get_object_or_404(Portfolio, name="Portfolio1"),
        stock=get_object_or_404(Stock, ticker="NVDA"),
    )
    PortfolioStock.objects.create(
        portfolio=get_object_or_404(Portfolio, name="Portfolio1"),
        stock=get_object_or_404(Stock, ticker="TSM"),
    )
    PortfolioStock.objects.create(
        portfolio=get_object_or_404(Portfolio, name="Portfolio1"),
        stock=get_object_or_404(Stock, ticker="META"),
    )
    PortfolioStock.objects.create(
        portfolio=get_object_or_404(Portfolio, name="Portfolio1"),
        stock=get_object_or_404(Stock, ticker="SNOW"),
    )
    PortfolioStock.objects.create(
        portfolio=get_object_or_404(Portfolio, name="Portfolio2"),
        stock=get_object_or_404(Stock, ticker="TSLA"),
    )
    PortfolioStock.objects.create(
        portfolio=get_object_or_404(Portfolio, name="Portfolio2"),
        stock=get_object_or_404(Stock, ticker="TSM"),
    )
    PortfolioStock.objects.create(
        portfolio=get_object_or_404(Portfolio, name="Portfolio3"),
        stock=get_object_or_404(Stock, ticker="TSLA"),
    )
    PortfolioStock.objects.create(
        portfolio=get_object_or_404(Portfolio, name="Portfolio11"),
        stock=get_object_or_404(Stock, ticker="TSLA"),
    )


def create_test_list():
    list1 = List.objects.create(
        name="List1", creator=get_object_or_404(User, username="TestUser1")
    )
    list1.sources.add(get_object_or_404(Source, name="TestSource1"))
    list1.sources.add(get_object_or_404(Source, name="TestSource3"))
    list1.sources.add(get_object_or_404(Source, name="TestSource9"))
    list1.articles.add(get_object_or_404(Article, title="TestArticle1"))
    List.objects.create(
        name="List2", creator=get_object_or_404(User, username="TestUser1")
    )
    List.objects.create(
        name="List3", creator=get_object_or_404(User, username="TestUser1")
    )
    List.objects.create(
        name="List4", creator=get_object_or_404(User, username="TestUser1")
    )
    List.objects.create(
        name="List5", creator=get_object_or_404(User, username="TestUser1")
    )
    List.objects.create(
        name="List6", creator=get_object_or_404(User, username="TestUser1")
    )
    List.objects.create(
        name="List7", creator=get_object_or_404(User, username="TestUser1")
    )
    List.objects.create(
        name="List8", creator=get_object_or_404(User, username="TestUser2")
    )
    List.objects.create(
        name="List9", creator=get_object_or_404(User, username="TestUser3")
    )
    List.objects.create(
        name="List10", creator=get_object_or_404(User, username="TestUser2")
    )
    List.objects.create(
        name="List11", creator=get_object_or_404(User, username="TestUser12")
    )


def create_test_highlighted_articles():
    HighlightedArticle.objects.create(
        user=get_object_or_404(User, username="TestUser1"),
        article=get_object_or_404(Article, title="TestArticle1"),
    )
    HighlightedArticle.objects.create(
        user=get_object_or_404(User, username="TestUser2"),
        article=get_object_or_404(Article, title="TestArticle2"),
    )
    HighlightedArticle.objects.create(
        user=get_object_or_404(User, username="TestUser2"),
        article=get_object_or_404(Article, title="TestArticle3"),
    )
    HighlightedArticle.objects.create(
        user=get_object_or_404(User, username="TestUser1"),
        article=get_object_or_404(Article, title="TestArticle4"),
    )
    HighlightedArticle.objects.create(
        user=get_object_or_404(User, username="TestUser3"),
        article=get_object_or_404(Article, title="TestArticle5"),
    )
    HighlightedArticle.objects.create(
        user=get_object_or_404(User, username="TestUser1"),
        article=get_object_or_404(Article, title="TestArticle6"),
    )
    HighlightedArticle.objects.create(
        user=get_object_or_404(User, username="TestUser2"),
        article=get_object_or_404(Article, title="TestArticle1"),
    )
    HighlightedArticle.objects.create(
        user=get_object_or_404(User, username="TestUser1"),
        article=get_object_or_404(Article, title="TestArticle8"),
    )
    HighlightedArticle.objects.create(
        user=get_object_or_404(User, username="TestUser1"),
        article=get_object_or_404(Article, title="TestArticle5"),
    )
    HighlightedArticle.objects.create(
        user=get_object_or_404(User, username="TestUser3"),
        article=get_object_or_404(Article, title="TestArticle1"),
    )


def create_source_tags():
    for i in range(1, 11):
        SourceTag.objects.create(name=f"TestTag{i}")


def create_portfolio_keywords():
    for i in range(1, 11):
        keyword = PortfolioKeyword.objects.create(keyword=f"TestKeyword{i}")
        get_object_or_404(PortfolioStock, pk=i).keywords.add(keyword)
    last_keyword = PortfolioKeyword.objects.create(keyword="Last Keyword")
    get_object_or_404(PortfolioStock, pk=11).keywords.add(last_keyword)


class CreateTestInstances(object):
    @classmethod
    def setUpClass(cls):
        super(CreateTestInstances, cls).setUpClass()
        create_test_users()
        create_test_sectors()
        create_test_website()
        create_test_sources()
        create_test_stock()
        create_test_notifications()
        create_test_articles()
        create_test_notification_messages()
        create_test_source_ratings()
        create_test_portfolio()
        create_test_portfolio_stock()
        create_test_list()
        create_test_highlighted_articles()
        create_source_tags()
        create_portfolio_keywords()
