# Django Imports
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils.timezone import now
# Python Import
from datetime import timedelta
# Local Imports
from apps.sector.models import Sector
from apps.accounts.models import Website, SocialLink
from apps.list.models import List, ListRating
from apps.source.models import Source, SourceRating
from apps.article.models import Article, HighlightedArticle
from apps.home.models import Notification

User = get_user_model()

def create_test_users():
    testuser1 = User.objects.create(username='TestUser1', email='testuser1@mail.com')
    testuser1.set_password("testpw99")
    testuser1.save()
    for i in range(2, 11):
        User.objects.create(username=f"TestUser{i}", email=f"testuser{i}mail.com")

def create_test_sectors():
    for i in range(1, 11):
        Sector.objects.create(name=f"TestSector{i}", slug=f"testsector{i}")

def create_test_website():
    for i in range(1, 11):
        Website.objects.create(name=f"TestWebsite{i}")

def create_test_lists():
    List.objects.create(name="TestList1", is_public=True, creator=get_object_or_404(User, username="TestUser1"))
    List.objects.create(name="TestList2", is_public=True, creator=get_object_or_404(User, username="TestUser2"))
    List.objects.create(name="TestList3", is_public=True, creator=get_object_or_404(User, username="TestUser1"))
    List.objects.create(name="TestList4", is_public=True, creator=get_object_or_404(User, username="TestUser4"))
    List.objects.create(name="TestList5", is_public=True, creator=get_object_or_404(User, username="TestUser1"))
    List.objects.create(name="TestList6", is_public=True, creator=get_object_or_404(User, username="TestUser6"))
    List.objects.create(name="TestList7", is_public=True, creator=get_object_or_404(User, username="TestUser6"))
    List.objects.create(name="TestList8", is_public=True, creator=get_object_or_404(User, username="TestUser5"))
    List.objects.create(name="TestList9", is_public=True, creator=get_object_or_404(User, username="TestUser3"))
    List.objects.create(name="TestList10", is_public=True, creator=get_object_or_404(User, username="TestUser2"))

def create_test_sources():
    Source.objects.create(url="www.testsource1.com/", slug="testsource1", name="TestSource1", paywall="Yes", website=get_object_or_404(Website, name="TestWebsite1"), sector=get_object_or_404(Sector, name="TestSector1"))
    Source.objects.create(url="www.testsource2.com/", slug="testsource2", name="TestSource2", paywall="No", website=get_object_or_404(Website, name="TestWebsite1"), sector=get_object_or_404(Sector, name="TestSector2"))
    Source.objects.create(url="www.testsource3.com/", slug="testsource3", name="TestSource3", paywall="Yes", website=get_object_or_404(Website, name="TestWebsite2"), sector=get_object_or_404(Sector, name="TestSector2"))
    Source.objects.create(url="www.testsource4.com/", slug="testsource4", name="TestSource4", paywall="No", website=get_object_or_404(Website, name="TestWebsite1"), sector=get_object_or_404(Sector, name="TestSector2"))
    Source.objects.create(url="www.testsource5.com/", slug="testsource5", name="TestSource5", paywall="Yes", website=get_object_or_404(Website, name="TestWebsite2"), sector=get_object_or_404(Sector, name="TestSector3"))
    Source.objects.create(url="www.testsource6.com/", slug="testsource6", name="TestSource6", paywall="Yes", website=get_object_or_404(Website, name="TestWebsite3"), sector=get_object_or_404(Sector, name="TestSector4"))
    Source.objects.create(url="www.testsource7.com/", slug="testsource7", name="TestSource7", paywall="No", website=get_object_or_404(Website, name="TestWebsite4"), sector=get_object_or_404(Sector, name="TestSector1"))
    Source.objects.create(url="www.testsource8.com/", slug="testsource8", name="TestSource8", paywall="Yes", website=get_object_or_404(Website, name="TestWebsite1"), sector=get_object_or_404(Sector, name="TestSector1"))
    Source.objects.create(url="www.testsource9.com/", slug="testsource9", name="TestSource9", paywall="Yes", website=get_object_or_404(Website, name="TestWebsite4"), sector=get_object_or_404(Sector, name="TestSector3"))
    Source.objects.create(url="www.testsource10.com/", slug="testsource10", name="TestSource10", paywall="Yes", website=get_object_or_404(Website, name="TestWebsite6"), sector=get_object_or_404(Sector, name="TestSector3"))

def create_test_social_links():
    SocialLink.objects.create(profile=get_object_or_404(User, username="TestUser1").profile, url="www.website/testuser1.com", website=get_object_or_404(Website, name="TestWebsite4"))
    SocialLink.objects.create(profile=get_object_or_404(User, username="TestUser2").profile, url="www.website/testuser2.com", website=get_object_or_404(Website, name="TestWebsite1"))
    SocialLink.objects.create(profile=get_object_or_404(User, username="TestUser3").profile, url="www.website/testuser3.com", website=get_object_or_404(Website, name="TestWebsite1"))
    SocialLink.objects.create(profile=get_object_or_404(User, username="TestUser1").profile, url="www.website/testuser4.com", website=get_object_or_404(Website, name="TestWebsite3"))
    SocialLink.objects.create(profile=get_object_or_404(User, username="TestUser2").profile, url="www.website/testuser5.com", website=get_object_or_404(Website, name="TestWebsite4"))
    SocialLink.objects.create(profile=get_object_or_404(User, username="TestUser1").profile, url="www.website/testuser6.com", website=get_object_or_404(Website, name="TestWebsite1"))
    SocialLink.objects.create(profile=get_object_or_404(User, username="TestUser1").profile, url="www.website/testuser7.com", website=get_object_or_404(Website, name="TestWebsite5"))
    SocialLink.objects.create(profile=get_object_or_404(User, username="TestUser2").profile, url="www.website/testuser8.com", website=get_object_or_404(Website, name="TestWebsite2"))
    SocialLink.objects.create(profile=get_object_or_404(User, username="TestUser1").profile, url="www.website/testuser9.com", website=get_object_or_404(Website, name="TestWebsite3"))
    SocialLink.objects.create(profile=get_object_or_404(User, username="TestUser3").profile, url="www.website/testuser10.com", website=get_object_or_404(Website, name="TestWebsite8"))

def create_test_notifications():
    Notification.objects.create(user=get_object_or_404(User, username="TestUser1"), list=get_object_or_404(List, name="TestList1"))
    Notification.objects.create(user=get_object_or_404(User, username="TestUser2"), list=get_object_or_404(List, name="TestList1"))
    Notification.objects.create(user=get_object_or_404(User, username="TestUser2"), list=get_object_or_404(List, name="TestList2"))
    Notification.objects.create(user=get_object_or_404(User, username="TestUser3"), list=get_object_or_404(List, name="TestList2"))
    Notification.objects.create(user=get_object_or_404(User, username="TestUser3"), list=get_object_or_404(List, name="TestList3"))
    Notification.objects.create(user=get_object_or_404(User, username="TestUser1"), list=get_object_or_404(List, name="TestList1"))
    Notification.objects.create(user=get_object_or_404(User, username="TestUser1"), list=get_object_or_404(List, name="TestList3"))
    Notification.objects.create(user=get_object_or_404(User, username="TestUser2"), list=get_object_or_404(List, name="TestList2"))
    Notification.objects.create(user=get_object_or_404(User, username="TestUser1"), list=get_object_or_404(List, name="TestList1"))
    Notification.objects.create(user=get_object_or_404(User, username="TestUser2"), list=get_object_or_404(List, name="TestList1"))

def create_test_list_ratings():
    ListRating.objects.create(user=get_object_or_404(User, username="TestUser1"), list=get_object_or_404(List, name="TestList1"), rating=3)
    ListRating.objects.create(user=get_object_or_404(User, username="TestUser2"), list=get_object_or_404(List, name="TestList1"), rating=4)
    ListRating.objects.create(user=get_object_or_404(User, username="TestUser3"), list=get_object_or_404(List, name="TestList1"), rating=5)
    ListRating.objects.create(user=get_object_or_404(User, username="TestUser4"), list=get_object_or_404(List, name="TestList2"), rating=4)
    ListRating.objects.create(user=get_object_or_404(User, username="TestUser5"), list=get_object_or_404(List, name="TestList2"), rating=4)
    ListRating.objects.create(user=get_object_or_404(User, username="TestUser6"), list=get_object_or_404(List, name="TestList1"), rating=3)
    ListRating.objects.create(user=get_object_or_404(User, username="TestUser7"), list=get_object_or_404(List, name="TestList1"), rating=1)
    ListRating.objects.create(user=get_object_or_404(User, username="TestUser8"), list=get_object_or_404(List, name="TestList3"), rating=5)
    ListRating.objects.create(user=get_object_or_404(User, username="TestUser9"), list=get_object_or_404(List, name="TestList1"), rating=5)
    ListRating.objects.create(user=get_object_or_404(User, username="TestUser1"), list=get_object_or_404(List, name="TestList2"), rating=2)

def create_test_articles():
    Article.objects.create(title="TestArticle1", source=get_object_or_404(Source, name="TestSource1"), link="www.testarticle1.com", pub_date=(now() - timedelta(days=2)).strftime("%Y-%m-%d"))
    Article.objects.create(title="TestArticle2", source=get_object_or_404(Source, name="TestSource1"), link="www.testarticle2.com", pub_date=(now() - timedelta(days=1)).strftime("%Y-%m-%d"))
    Article.objects.create(title="TestArticle3", source=get_object_or_404(Source, name="TestSource2"), link="www.testarticle3.com", pub_date=(now() - timedelta(days=3)).strftime("%Y-%m-%d"))
    Article.objects.create(title="TestArticle4", source=get_object_or_404(Source, name="TestSource2"), link="www.testarticle4.com", pub_date=(now() - timedelta(days=4)).strftime("%Y-%m-%d"))
    Article.objects.create(title="TestArticle5", source=get_object_or_404(Source, name="TestSource3"), link="www.testarticle5.com", pub_date=(now() - timedelta(days=5)).strftime("%Y-%m-%d"))
    Article.objects.create(title="TestArticle6", source=get_object_or_404(Source, name="TestSource1"), link="www.testarticle6.com", pub_date=(now() - timedelta(days=6)).strftime("%Y-%m-%d"))
    Article.objects.create(title="TestArticle7", source=get_object_or_404(Source, name="TestSource1"), link="www.testarticle7.com", pub_date=(now() - timedelta(days=6)).strftime("%Y-%m-%d"))
    Article.objects.create(title="TestArticle8", source=get_object_or_404(Source, name="TestSource3"), link="www.testarticle8.com", pub_date=(now() - timedelta(days=4)).strftime("%Y-%m-%d"))
    Article.objects.create(title="TestArticle9", source=get_object_or_404(Source, name="TestSource2"), link="www.testarticle9.com", pub_date=(now() - timedelta(days=8)).strftime("%Y-%m-%d"))
    Article.objects.create(title="TestArticle10", source=get_object_or_404(Source, name="TestSource1"), link="www.testarticle10.com", pub_date=(now() - timedelta(days=3)).strftime("%Y-%m-%d"))

def create_test_highlighted_articles():
    HighlightedArticle.objects.create(user=get_object_or_404(User, username="TestUser1"), article=get_object_or_404(Article, title="TestArticle1"))
    HighlightedArticle.objects.create(user=get_object_or_404(User, username="TestUser2"), article=get_object_or_404(Article, title="TestArticle2"))
    HighlightedArticle.objects.create(user=get_object_or_404(User, username="TestUser2"), article=get_object_or_404(Article, title="TestArticle3"))
    HighlightedArticle.objects.create(user=get_object_or_404(User, username="TestUser1"), article=get_object_or_404(Article, title="TestArticle4"))
    HighlightedArticle.objects.create(user=get_object_or_404(User, username="TestUser3"), article=get_object_or_404(Article, title="TestArticle5"))
    HighlightedArticle.objects.create(user=get_object_or_404(User, username="TestUser1"), article=get_object_or_404(Article, title="TestArticle6"))
    HighlightedArticle.objects.create(user=get_object_or_404(User, username="TestUser2"), article=get_object_or_404(Article, title="TestArticle1"))
    HighlightedArticle.objects.create(user=get_object_or_404(User, username="TestUser1"), article=get_object_or_404(Article, title="TestArticle8"))
    HighlightedArticle.objects.create(user=get_object_or_404(User, username="TestUser1"), article=get_object_or_404(Article, title="TestArticle5"))
    HighlightedArticle.objects.create(user=get_object_or_404(User, username="TestUser3"), article=get_object_or_404(Article, title="TestArticle1"))

def create_test_source_ratings():
    SourceRating.objects.create(user=get_object_or_404(User, username="TestUser1"), source=get_object_or_404(Source, name="TestSource1"), rating=5)
    SourceRating.objects.create(user=get_object_or_404(User, username="TestUser2"), source=get_object_or_404(Source, name="TestSource1"), rating=4)
    SourceRating.objects.create(user=get_object_or_404(User, username="TestUser3"), source=get_object_or_404(Source, name="TestSource1"), rating=1)
    SourceRating.objects.create(user=get_object_or_404(User, username="TestUser4"), source=get_object_or_404(Source, name="TestSource2"), rating=2)
    SourceRating.objects.create(user=get_object_or_404(User, username="TestUser5"), source=get_object_or_404(Source, name="TestSource2"), rating=3)
    SourceRating.objects.create(user=get_object_or_404(User, username="TestUser6"), source=get_object_or_404(Source, name="TestSource3"), rating=2)
    SourceRating.objects.create(user=get_object_or_404(User, username="TestUser7"), source=get_object_or_404(Source, name="TestSource2"), rating=3)
    SourceRating.objects.create(user=get_object_or_404(User, username="TestUser8"), source=get_object_or_404(Source, name="TestSource1"), rating=1)
    SourceRating.objects.create(user=get_object_or_404(User, username="TestUser9"), source=get_object_or_404(Source, name="TestSource3"), rating=4)
    SourceRating.objects.create(user=get_object_or_404(User, username="TestUser1"), source=get_object_or_404(Source, name="TestSource4"), rating=3)