from __future__ import absolute_import, unicode_literals

# Python imports
from datetime import timedelta
from html import unescape
from time import sleep
from base64 import b64encode
from os import environ
from re import sub as re_sub
from celery import shared_task
from requests import post as request_post
from requests import get as request_get
from boto3 import client


# Django imports
from django.core.cache import cache
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model


# Local imports
from apps.logic.services import (
    bulk_create_articles_and_notifications,
    notifications_create,
    create_articles_from_feed,
    source_profile_img_create,
    twitter_create_api_settings,
    tweet_type_create,
    article_creation_check,
    get_new_sources_info,
)
from apps.article.models import Article, TweetType
from apps.home.models import NotificationMessage
from apps.accounts.models import Website
from apps.source.models import Source


User = get_user_model()

s3 = client("s3")


class SpotifyAPI(object):
    access_token = None
    access_token_expires = timezone.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credientals(self):
        client_id = self.client_id
        client_secret = self.client_secret
        if client_id is None or client_secret is None:
            raise Exception("You must set client_id and client_secret")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_headers(self):
        client_creds_b64 = self.get_client_credientals()
        return {"Authorization": f"Basic {client_creds_b64}"}

    def get_token_data(self):
        return {"grant_type": "client_credentials"}

    def perform_auth(self):
        request = request_post(
            self.token_url,
            data=self.get_token_data(),
            headers=self.get_token_headers(),
            timeout=10,
        )
        if request.status_code not in range(200, 299):
            raise Exception("Could not authenticate client.")
        data = request.json()
        expires_in = data["expires_in"]
        expires = timezone.now() + timedelta(seconds=expires_in)
        self.access_token = data["access_token"]
        self.access_token_expires = expires
        self.access_token_did_expire = expires < timezone.now()
        return True

    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        if expires < timezone.now():
            self.perform_auth()
            return self.get_access_token()
        if token is None:
            self.perform_auth()
            return self.get_access_token()
        return token

    def get_episodes(self, id):
        access_token = self.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        lookup_url = f"https://api.spotify.com/v1/shows/{id}/episodes?market=US"
        request = request_get(lookup_url, headers=headers, timeout=10)
        if request.status_code not in range(200, 299):
            return {}
        return request.json()

    def get_podcaster(self, id):
        access_token = self.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        lookup_url = f"https://api.spotify.com/v1/shows/{id}?market=US"
        r = request_get(lookup_url, headers=headers, timeout=10)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()


@shared_task
def scrape_twitter():
    api = twitter_create_api_settings()
    last_id = cache.get("last_id")
    if last_id:
        statuses = api.home_timeline(
            count=200, tweet_mode="extended", since_id=last_id, include_entities=True
        )
    else:
        statuses = api.home_timeline(
            count=200, tweet_mode="extended", include_entities=True
        )
    existing_tweets = Article.objects.filter(external_id__isnull=False).values_list(
        "external_id", flat=True
    )
    sources = Source.objects.all().only("source_id", "external_id")
    tweet_creation_list = []
    for status in statuses:
        try:
            tweet_external_id = status.id
            if str(tweet_external_id) not in existing_tweets:
                twitter_user_id = status.user.id
                if sources.filter(external_id=twitter_user_id).exists():
                    title = re_sub(r"http\S+", "", unescape(status.full_text))
                    if not title.strip():
                        continue
                    link = f"https://twitter.com/{status.user.screen_name}/status/{tweet_external_id}"
                    pub_date = status.created_at
                    # title, tweet_type = tweet_type_create(status, twitter_user_id, api)
                    tweet_type = tweet_type_create(status, twitter_user_id, api)
                    tweet_creation_list.append(
                        {
                            "source": twitter_user_id,
                            "title": title,
                            "link": link,
                            "pub_date": pub_date,
                            "external_id": tweet_external_id,
                            "tweet_type": tweet_type,
                        }
                    )
            else:
                break
            last_id = tweet_external_id
        except Exception as _:
            continue
    cache.set("last_id", last_id)
    new_articles = [
        Article(
            title=new_tweet["title"],
            link=new_tweet["link"],
            pub_date=new_tweet["pub_date"],
            source=sources.get(external_id=new_tweet["source"]),
            external_id=new_tweet["external_id"],
            tweet_type=new_tweet["tweet_type"],
        )
        for new_tweet in tweet_creation_list
    ]
    articles = Article.objects.bulk_create(new_articles)
    notifications_create(articles)


@shared_task
def scrape_substack():
    substack_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="Substack")
    ).only("source_id", "url", "website")
    articles = Article.objects.filter(source__in=substack_sources).only(
        "title", "pub_date", "source", "link"
    )
    for source in substack_sources:
        feed_url = f"{source.url}feed"
        create_articles_from_feed(source, feed_url, articles)
        sleep(6)


@shared_task
def scrape_seekingalpha():
    seekingalpha_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="SeekingAlpha")
    ).only("source_id", "url", "website")
    articles = Article.objects.filter(source__in=seekingalpha_sources).only(
        "title", "pub_date", "source", "link"
    )
    for source in seekingalpha_sources:
        feed_url = f"{source.url}.xml"
        create_articles_from_feed(source, feed_url, articles)
        sleep(15)


@shared_task
def scrape_other_websites():
    other_sources = (
        Source.objects.filter(website=get_object_or_404(Website, name="Other"))
        .exclude(alt_feed__isnull=False)
        .only("source_id", "url", "website")
    )
    articles = Article.objects.filter(source__in=other_sources).only(
        "title", "pub_date", "source", "link"
    )
    for source in other_sources:
        try:
            feed_url = f"{source.url}feed"
            create_articles_from_feed(source, feed_url, articles)
        except Exception as error:
            print(f"Scrapping {source} failed because of {error}")
            continue


@shared_task
def scrape_forbes():
    forbes_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="Forbes")
    ).only("source_id", "url", "website")
    articles = Article.objects.filter(source__in=forbes_sources).only(
        "title", "pub_date", "source", "link"
    )
    for source in forbes_sources:
        try:
            feed_url = f"{source.url}feed"
            create_articles_from_feed(source, feed_url, articles)
            sleep(5)
        except Exception as error:
            print(error)
            continue


@shared_task
def scrape_spotify():
    client_id = environ.get("SPOTIFY_CLIENT_ID")
    client_secret = environ.get("SPOTIFY_CLIENT_SECRET")
    spotify_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="Spotify")
    ).only("source_id", "external_id")
    articles = Article.objects.filter(source__in=spotify_sources).only(
        "title", "link", "source"
    )
    spotify_creation_list = []
    for source in spotify_sources:
        spotify = SpotifyAPI(client_id, client_secret)
        try:
            episodes = spotify.get_episodes(source.external_id)
            episode_items = episodes["items"]
            for episode_item in episode_items:
                title = unescape(episode_item["name"])
                link = episode_item["external_urls"]["spotify"]
                # SpotifyAPI release_date only has date precision, so it always shows midnight => therefore better to use current time of scrapping
                spotify_creation_list, article_exists = article_creation_check(
                    spotify_creation_list, articles, title, source, link
                )
                if article_exists:
                    break
        except Exception as _:
            continue
    bulk_create_articles_and_notifications(spotify_creation_list)


@shared_task
def scrape_youtube():
    api_key = environ.get("YOUTUBE_API_KEY")
    youtube_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="YouTube")
    ).only("source_id", "external_id")
    articles = Article.objects.filter(source__in=youtube_sources).only(
        "title", "pub_date", "link", "source"
    )
    youtube_creation_list = []
    for source in youtube_sources:
        try:
            channel_data = request_get(
                f"https://www.googleapis.com/youtube/v3/channels?id={source.external_id}&key={api_key}&part=contentDetails",
                timeout=10,
            ).json()
            upload_id = channel_data["items"][0]["contentDetails"]["relatedPlaylists"][
                "uploads"
            ]
            url = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={upload_id}&key={api_key}&part=snippet&maxResults=50"
            request = request_get(url, timeout=10)
            data = request.json()
            items = data["items"]
            for item in items:
                title = unescape(item["snippet"]["title"])
                link = f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
                pub_date = item["snippet"]["publishedAt"]
                youtube_creation_list, article_exists = article_creation_check(
                    youtube_creation_list,
                    articles,
                    title,
                    source,
                    link,
                    pub_date=pub_date,
                )
                if article_exists:
                    break
        except Exception as error:
            print(f"Scrapping {source} has caused this error: {error}")
            continue
    bulk_create_articles_and_notifications(youtube_creation_list)


@shared_task
def twitter_scrape_followings():
    api = twitter_create_api_settings()
    followings = api.get_friends(count=100)
    for follow in followings:
        name = follow.name
        if Source.objects.filter(external_id=follow.id).exists():
            continue
        if (
            Source.objects.filter(name=follow.name).exists()
            or Source.objects.filter(slug=slugify(name)).exists()
        ):
            name = follow.name + " - Twitter"
        url = f"https://twitter.com/{follow.screen_name}"
        slug = slugify(name)
        external_id = follow.id
        source = Source.objects.create(
            url=url,
            slug=slug,
            name=name,
            favicon_path=f"home/favicons/{slug}.png",
            paywall="No",
            website=get_object_or_404(Website, name="Twitter"),
            external_id=external_id,
        )
        source_profile_img_create(
            source, follow.profile_image_url_https.replace("_normal", "")
        )


@shared_task
def youtube_get_profile_images():
    api_key = environ.get("YOUTUBE_API_KEY")
    youtube_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="YouTube")
    )
    for source in youtube_sources:
        try:
            url = f"https://youtube.googleapis.com/youtube/v3/channels?part=snippet%2CcontentDetails%2Cstatistics&id={source.external_id}&key={api_key}"
            request = request_get(url, timeout=10)
            data = request.json()
            if "items" in data:
                source_profile_img_create(
                    source, data["items"][0]["snippet"]["thumbnails"]["medium"]["url"]
                )
            else:
                print(f"{source} has no key items!")
        except Exception as error:
            print(f"Scrapping {source} has caused this error: {error}")
            continue


@shared_task
def spotify_get_profile_images():
    client_id = environ.get("SPOTIFY_CLIENT_ID")
    client_secret = environ.get("SPOTIFY_CLIENT_SECRET")
    spotify_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="Spotify")
    )
    for source in spotify_sources:
        try:
            spotify = SpotifyAPI(client_id, client_secret)
            podcaster = spotify.get_podcaster(source.external_id)
            if "images" in podcaster.keys():
                source_profile_img_create(source, podcaster["images"][0]["url"])
            else:
                continue
        except Exception as _:
            continue


@shared_task
def old_notifications_delete():
    NotificationMessage.objects.filter(
        date__lte=timezone.now() - timedelta(hours=24)
    ).delete()


@shared_task
def youtube_delete_innacurate_articles():
    api_key = environ.get("YOUTUBE_API_KEY")
    youtube_sources = Source.objects.filter(
        website=get_object_or_404(Website, name="YouTube")
    )
    youtube_videos = []
    for source in youtube_sources:
        saved_articles_from_source = Article.objects.filter(source=source)
        channel_data = request_get(
            f"https://www.googleapis.com/youtube/v3/channels?id={source.external_id}&key={api_key}&part=contentDetails",
            timeout=10,
        ).json()
        upload_id = channel_data["items"][0]["contentDetails"]["relatedPlaylists"][
            "uploads"
        ]
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={upload_id}&key={api_key}&part=snippet&maxResults=1000"
        request = request_get(url, timeout=10)
        item_list = []
        next_item = True
        iterations = 0
        while next_item and iterations < 20:
            data = request.json()
            items = data["items"]
            item_list.append(items)
            if "nextPageToken" in data.keys():
                next_page_token = data["nextPageToken"]
                iterations += 1
                url = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={upload_id}&key={api_key}&part=snippet&maxResults=1000&pageToken={next_page_token}"
                request = request_get(url, timeout=10)
            else:
                next_item = False
                break
        for items in item_list:
            try:
                for item in items:
                    title = unescape(item["snippet"]["title"])
                    link = f"https://www.youtube.com/watch?v={item['snippet']['resourceId']['videoId']}"
                    pub_date = item["snippet"]["publishedAt"]
                    youtube_videos.append(
                        {"title": title, "link": link, "pub_date": pub_date}
                    )
            except Exception as _:
                continue
        for article in saved_articles_from_source:
            if not any(d["title"] == article.title for d in youtube_videos) or not any(
                d["link"] == article.link
                for d in youtube_videos
                or not any(d["pub_date"] == article.pub_date for d in youtube_videos)
            ):
                article.delete()


@shared_task
def delete_tweet_types_empty():
    tweet_types = TweetType.objects.all()
    for tweet_type in tweet_types:
        if not tweet_type.tweet.all():
            tweet_type.delete()


@shared_task
def calc_sim_sources():
    Source.objects.calc_similiar_sources()


@shared_task
def scrape_alt_feeds():
    sources = (
        Source.objects.filter(website__name="Other", alt_feed__isnull=False)
        .exclude(alt_feed="none")
        .only("source_id", "alt_feed", "website")
    )

    articles = Article.objects.filter(source__in=sources).only(
        "title", "pub_date", "source", "link"
    )
    for source in sources:
        try:
            if source.alt_feed != "none":
                create_articles_from_feed(source, source.alt_feed, articles)
        except Exception as error:
            print(f"Scrapping {source} has caused this error: {error}")
            continue


@shared_task
def create_bank_sources():
    from apps.source.models import Sector, SourceRating, SourceTag

    new_sources = [
        "https://www.home.saxo/insights",
        "https://www.hsbc.co.uk/wealth/insights/macro-outlook/",
        "https://www.wellsfargo.com/cib/insights/economics/",
        "https://www.cib.barclays/research.html",
        "https://www.santandercib.com/insights",
        "https://www.societegenerale.com/en/economic-research",
        "https://thoughtleadership.rbc.com/economics/economy-markets/",
        "https://www.dbresearch.com/PROD/RPS_EN-PROD/Deutsche_Bank_Research__economic_cyclegrowth_trends_economic_policy/RPSHOME.alias",
        "https://www.morganstanley.com/what-we-do/research",
        "https://research.ing.com/portal/ING_Research.html",
        "https://www.unicreditresearch.eu/index.php?id=home&referer=index.php%3Fid%3Dmacro",
        "https://capitalmarkets.bmo.com/en/services/research-strategy/",
        "https://corporate.nordea.com/research/series/181/macro-markets-strategy",
        "https://research.danskebank.com/research/#/",
        "https://www.pnc.com/en/about-pnc/media/economic-reports.html",
        "https://www.westpac.com.au/about-westpac/media/reports/australian-economic-reports/",
        "https://www.itau.com.br/itaubba-pt/macroeconomic-analysis",
        "https://www.erstegroup.com/en/research",
        "https://www.bok.or.kr/eng/singl/pblictn/list.do?searchOptn10=ECNMY&menuNo=400207",
        "https://www.smbcgroup.com/what-we-do/macro-analysis",
        "https://www.mizuhogroup.com/bank/insights",
        "https://www.gbm.scotiabank.com/en/market-insights/economics.html",
        "https://www.rabobank.com/knowledge?mmb-id_125-1119229_page-size=7",
        "https://www.caixabankresearch.com/en",
        "https://www.dbs.com.sg/corporate/aics/economics-and-strategy.page",
        "https://www.truist.com/wealth/insights",
        "https://business.bofa.com/en-us/content/market-strategies-insights.html",
        "https://etudes-economiques.credit-agricole.com/en/Eco-decoding/Macroeconomic-Scenario",
        "https://economic-research.bnpparibas.com/Home/en-US",
        "https://research.sebgroup.com/macro-ficc/reports?nbRows=20&language=English",
        "https://www.bnymellon.com/emea/en/insights/all-insights.html",
        "https://www.raiffeisenresearch.com/client/login.jsp",
        "https://www.scotiabank.com/ca/en/about/economics/economics-publications.html",
    ]
    failed_scrapping = []
    for source_url in new_sources:
        print(source_url)
        try:
            name, img_url = get_new_sources_info(source_url)
            if (
                Source.objects.filter(name=name).exists()
                or Source.objects.filter(slug=slugify(name)).exists()
                or Source.objects.filter(slug=slugify(name[:49])).exists()
            ):
                name = name + " - New"
            created_source = Source.objects.create(
                url=source_url,
                slug=slugify(name[:49]),
                name=name[:49],
                favicon_path=f"home/favicons/{slugify(name[:49])}.webp",
                paywall="No",
                website=get_object_or_404(Website, name="Other"),
                content_type="Analysis",
                sector=get_object_or_404(Sector, name="Macroeconomics"),
            )
            created_source.tags.add(get_object_or_404(SourceTag, name="Bank"))
            created_source.save()
            try:
                source_profile_img_create(created_source, img_url)
                feed_url = f"{source_url}feed"
                try:
                    create_articles_from_feed(
                        created_source, feed_url, Article.objects.none()
                    )
                except Exception as _:
                    created_source.alt_feed = "not found"
                    created_source.save()
                rating = 8
            except Exception as _:
                rating = 7
            # add source_rating otherwise 500 error when opening source profile
            SourceRating.objects.create(
                user=get_object_or_404(User, email="me-99@live.de"),
                source=created_source,
                rating=rating,
            )
        except Exception as error:
            failed_scrapping.append(source_url)
            print(f"Scrapping {source_url} has caused this error: ")
            print(error)
            continue
    print("The following sources could not be scrapped: ")
    for source in failed_scrapping:
        print(source)


@shared_task
def create_fund_sources():
    from apps.source.models import Sector, SourceRating, SourceTag

    new_sources = [
        "http://east72.com.au/investment-reports/",
        "https://www.rgaia.com/commentary/",
        "https://www.evermoreglobal.com/fund-commentary",
        "http://gorozen.com/research/commentaries",
        "https://180degreecapital.com/insights/",
        "https://www.lrtcapital.com/investor-letters/",
        "https://palmcapital.co.za/communications/",
        "https://www.alphyncap.com/blog",
        "https://www.baronfunds.com/quarterly-reports",
        "https://www.gmo.com/americas/research-library/",
        "https://www.riverparkfunds.com/funds/",
        "https://gatorcapital.com/",
        "https://dmzpartners.in/viewpoints.aspx",
        "https://www.tweedy.com/research/quarterly.php",
        "https://www.appleseedfund.com/perspectives/",
        "https://tourlitecapital.com/documents",
        "https://www.thirdpointlimited.com/resources/",
        "https://saltlightcapital.com/investor_letters/",
        "https://www.rondureglobal.com/news",
        "https://vulcanvaluepartners.com/letters/",
        "https://matrixassetadvisors.com/commentary/",
        "https://www.deepsailcapital.com/investor-letters",
        "https://www.laughingwatercapital.com/contact-1",
        "https://www.mcjcapitalpartners.com/research-and-commentary",
        "https://horosam.com/en/letters-to-our-co-investors/",
        "https://www.okeefestevens.com/resources/",
        "http://www.longcastadvisers.com/letters",
        "https://avemariafunds.com/financial-insight/fund-commentaries.html",
        "https://hoisington.com/economic_overview.html",
        "https://www.brontecapital.com/partners-letters",
        "https://spear-invest.com/research/",
        "https://horizonkinetics.com/insights/",
        "https://www.pluralinvesting.com/letters",
        "https://distillatecapital.com/insights",
        "https://southeasternasset.com/mutual-fund-commentaries/",
        "https://headwaterscapmgmt.com/quarterly-letters/",
        "https://silverbeechlp.com/communication",
        "https://www.eriksencapitalmgmt.com/investor-letters",
        "https://www.greenhavenroad.com/investor-letters",
        "http://www.curreencapital.com/investor-letters",
        "https://www.massifcap.com/investor-letters",
        "https://www.whitefalconcap.com/letters",
        "https://givernycapital.com/en/letters-to-our-partners/",
        "https://mercatormutualfunds.com/",
        "https://donvillekent.com/investing-resources/#fact-sheet",
        "https://www.rowanstreet.com/blog",
        "https://www.akrefund.com/documents-and-forms/",
        "https://www.heartlandadvisors.com/Insights",
        "https://wedgewoodpartners.com/investor-resources/",
        "https://www.aoris.com.au/fund#Latest-reports",
        "https://blog.crossingbridgefunds.com/blog",
        "https://www.clearbridge.com/perspectives/commentaries/index",
        "https://www.bluetowerasset.com/quarterly-factsheets-and-letters",
        "https://covestreetfunds.com/commentary/",
        "https://www.claret.ca/publications/category/quarterly-letter/",
        "https://millervalue.com/current-thinking/",
        "https://www.palmharbourcapital.com/en/our-fund",
        "https://www.righttailcapital.com/reading",
        "https://www.ataicap.com/letters",
        "https://ararfund.com/#documentationENFUND",
        "https://lvsadvisory.com/communications/",
        "https://pernasresearch.com/stock-ideas/",
        "https://millervalue.com/strategies/deep-value/",
        "https://www.polencapital.com/perspectives?category_name=commentary",
        "https://www.firsteagle.com/all-insights",
        "https://hoskingpartners.com/library/",
        "https://www.whitebrookcapital.com/quarterly-commentaries",
        "https://octahedroncapital.com/",
        "https://www.righttailcapital.com/reading",
        "http://www.comusinvestment.com/letters",
        "https://www.palmvalleycapital.com/fundcommentary",
        "https://www.boyarassetmanagement.com/individual-investor/private-client-group/quarterly-letters/",
        "https://www.vltavafund.com/dopisy-akcionarum",
        "https://leavenpartners.wordpress.com/quarterly-letters/",
        "https://sltresearch.wixsite.com/sltresearch/equity-research",
        "https://richiecapital.com/insights/",
        "https://www.myrmikan.com/port/",
        "https://www.marbleharboric.com/commentary/",
        "https://nitorcapitalmanagement.com/annual-letters",
        "https://www.semperaugustus.com/clientletter",
        "https://www.biremecapital.com/blog",
        "https://srk-capital.com/partnership-letters/",
        "https://www.pzena.com/institutional/insights/",
        "https://www.rgaia.com/commentary/",
        "https://marvistainvestments.com/articles-and-news/",
        "https://www.mooncap.com/blog/",
        "https://www.apam.com/",
        "https://oakmark.com/news-insights/commentary/",
        "https://www.fmimgt.com/historical-iso/",
        "https://southernsunam.com/commentary/",
        "https://www.tlcadvisory.com/strategies/",
        "https://www.diamond-hill.com/investment-strategies/documents/separate-accounts/",
        "https://fpa.com/funds/fpa-crescent-fund-quarterly-commentary-archive",
        "https://weitzinvestments.com/perspectives/commentary/default.fs",
        "https://investors.l1longshort.com/investor-centre/?page=Quarterly-Investor-Letters",
        "https://www.aristotlecap.com/resources/?page=1",
        "https://www.rjinvestmentmanagement.com/our-thinking",
        "https://www.cooperinvestors.com/our-reports",
        "https://www.bcafunds.com/fund-documents",
        "https://smeadcap.com/advice/",
        "https://www.ithakagroup.com/usgrowth",
        "https://www.alger.com/",
        "https://horosam.com/en/letters-to-our-co-investors/",
        "https://www.kinsmanoakpartners.com/letters",
        "https://dmzpartners.in/viewpoints.aspx",
        "https://www.hardingloevner.com/insights/fundamental-thinking/",
        "https://www.mairsandpower.com/insights/fund-commentary",
        "https://choice-equities.com/blog-2/",
        "https://bumbershootholdings.com/letters/",
        "https://www.emethvaluecapital.com/letters-1",
        "https://lyricalam.com/letters/",
        "https://srk-capital.com/partnership-letters/",
        "https://www.permanentequity.com/letters",
        "https://www.sagapartners.com/investorletters",
        "https://www.arielinvestments.com/news-insights/",
        "https://aikya.co.uk/insights/",
        "https://pinnacleinvestment.com/shareholders/#results-presentations",
        "https://www.schroders.com/en-gb/uk/intermediary/insights/?topic=Quarterly+letters",
        "https://www.canterburytg.com/posts",
        "https://www.alpinumim.com/investment/blog/quarterly-investment-letters/",
        "https://www.palmvalleycapital.com/fundcommentary",
        "https://www.manolecapital.com/newsletters",
        "https://orphanira.com/writings/",
        "https://vulcanvaluepartners.com/letters/",
        "https://www.thinknewfoundfunds.com/",
        "https://www.cohopartners.com/insights/portfolio-insights/",
        "https://www.oldwestim.com/press",
        "https://andazprivate.com/#notes",
        "https://vailshire.com/latest-news-insights/",
        "https://www.fundsmith.co.uk/analysis/",
        "https://www.mayarcapital.com/letters",
        "https://www.ruffer.co.uk/en/thinking/articles/",
        "https://www.mpecap.com/letters",
        "https://www.gwinvestors.com/blog/",
        "https://active.williamblair.com/",
        "https://www.robeco.com/en-int/insights/latest-insights",
        "https://www.thornburg.com/insights/?all",
        "https://www.schroders.com/en-us/us/institutional/insights/markets/",
        "https://www.northerntrust.com/united-states/insights-research/investment-management",
        "https://www.diamond-hill.com/insights/all/",
        "https://www.wellington.com/en/insights",
        "https://www.worchcapital.com/investor-commentary",
        "https://www.plcapitalllc.com/news-articles/",
        "https://2point2capital.com/blog/",
        "https://mi2partners.com/thoughts-from-the-divide-posts/",
        "https://www.morgancreekcap.com/",
        "https://ceritypartners.com/insights/",
        "https://greenbackercapital.com/resources/#section-insights",
        "https://buffalofunds.com/insights-news/white-papers-research/?et_open_tab=et_pb_tab_1",
        "https://breachinletcap.com/insights/",
        "https://www.asiafrontiercapital.com/newsletter/monthly-newsletter.html",
        "https://cliffordcap.com/news-insights/",
        "https://www.hwcm.com/news-insights/",
        "https://www.barrowhanley.com/media-center",
        "https://www.vcm.com/insights/market-insights",
        "https://www.kennedycapital.com/category/insights/",
        "https://www.splitrockcap.com/letters.html",
        "https://www.blackmorecapital.com.au/blog",
        "https://concisecapital.com/news/",
        "https://www.hamiltonlane.com/en-us/insight",
        "https://greenalphaadvisors.com/content-hub/",
        "https://www.parnassus.com/insights/principles-and-performance",
        "https://ssi-invest.com/index.php/resources/#thought-leadership",
        "https://www.gluskinsheff.com/insights",
        "https://riverwaterpartners.com/category/quarterly-letters/",
        "https://www.jennison.com/perspectives-jennison",
        "https://thirdave.com/shareholder-letters/",
        "https://www.wisdomtree.com/investments/blog",
        "https://www.maegcapital.com/news/",
        "https://www.fieracapital.com/en/insights",
        "https://www.valhalla.ventures/insights",
        "https://reyndersmcveigh.com/insights/",
        "https://institutional.virtus.com/our-thinking",
        "https://www.conning.com/about-us/insights",
        "https://institutional.voya.com/",
        "https://altegris.com/insights/tag/white-paper",
        "https://volsung.com/insight-and-updates",
        "https://blog.investbcm.com/",
        "https://sl-advisors.com/u-s-midstream-energy-infrastructure-blog",
        "https://www.swanglobalinvestments.com/insights/",
        "https://tortoiseecofin.com/resources/insights/?Insight%20Category=Commentary&Insight%20Category=Video",
        "https://swspartners.com/?page_id=1728",
    ]
    failed_scrapping = []
    for source_url in new_sources:
        print(source_url)
        try:
            name, img_url = get_new_sources_info(source_url)
            if (
                Source.objects.filter(name=name).exists()
                or Source.objects.filter(slug=slugify(name)).exists()
                or Source.objects.filter(slug=slugify(name[:49])).exists()
            ):
                name = name + f" - Fund{name[:2]}"
            created_source = Source.objects.create(
                url=source_url,
                slug=slugify(name[:49]),
                name=name[:49],
                favicon_path=f"home/favicons/{slugify(name[:49])}.webp",
                paywall="No",
                website=get_object_or_404(Website, name="Other"),
                content_type="Analysis",
                sector=get_object_or_404(Sector, name="Generalists"),
            )
            created_source.tags.add(
                get_object_or_404(SourceTag, name="Investment Fund")
            )
            created_source.save()
            try:
                source_profile_img_create(created_source, img_url)
                feed_url = f"{source_url}feed"
                try:
                    create_articles_from_feed(
                        created_source, feed_url, Article.objects.none()
                    )
                except Exception as _:
                    created_source.alt_feed = "not found"
                    created_source.save()
                rating = 8
            except Exception as _:
                rating = 7
            # add source_rating otherwise 500 error when opening source profile
            SourceRating.objects.create(
                user=get_object_or_404(User, email="me-99@live.de"),
                source=created_source,
                rating=rating,
            )
        except Exception as error:
            failed_scrapping.append(source_url)
            print(f"Scrapping {source_url} has caused this error: ")
            print(error)
            continue
    print("The following sources could not be scrapped: ")
    for source in failed_scrapping:
        print(source)


@shared_task
def create_other_other_sources():
    from apps.source.models import Sector, SourceRating, SourceTag

    new_sources = [
        "https://www.institutionalinvestor.com/",
        "https://medium.com/@monetarypolicyinstitute",
        "https://daglifunds.com/",
        "https://www.thecorpraider.com/",
        "https://clarkstreetvalue.blogspot.com/",
        "https://focusedcompounding.com/",
        "https://www.elementaryvalue.com/",
        "https://valuealert.blogspot.com/",
        "https://www.platinum.com.au/Insights-Tools/The-Journal",
        "https://governanceforstakeholders.com/category/articles/",
        "https://dfinview.com/Ashmore/",
        "https://www.sbhic.com/insight-category/institutions/",
        "https://www.mesirow.com/insights",
        "https://innovationdevelopment.org/blog",
        "https://caia.org/blog",
        "https://www.morganstanley.com/im/en-us/institutional-investor/insights/articles/monthly-market-monitor-june23.html",
        "https://www.pgimquantitativesolutions.com/market-views",
        "https://realinvestmentadvice.com/insights/real-investment-daily/",
        "https://www.insightinvestment.com/united-states/perspectives/global-macro-research-hub/GMR-hub/?view=latest",
        "https://www.carlyle.com/#our-insights",
        "https://www.abrdn.com/en-us/investor/insights-and-research/insights",
        "https://macro-ops.com/research/",
        "https://www.mauldineconomics.com/",
        "https://investingchannel.com/articles",
        "https://finominal.com/",
        "https://www.streetwisereports.com/",
        "https://www.valens-research.com/the-institute/research/#",
        "https://www.ipocandy.com/",
        "https://www.boyarresearch.com/",
        "https://www.dcadvisory.com/news-deals-insights/",
        "https://www.ndr.com/",
        "https://www.eastdaley.com/media-and-news",
        "https://semiconductoradvisors.com/pages/articles/",
        "https://www.bioshares.com.au/",
        "http://www.pcsresearchgroup.com/",
        "https://www.m-cam.com/",
        "https://www.markmanadvisors.com/blog",
        "https://www.mcalindenresearchpartners.com/",
        "https://capitalistexploits.at/market-insights",
        "https://www.usq.com/insights",
        "https://www.researchfrc.com/category/reports/",
        "https://hardassetsalliance.com/blog/",
        "https://sumzero.com/",
        "https://propthink.com/",
        "https://www.cmegroup.com/videos.html#filters=market-commentary",
        "https://www.corbinadvisors.com/research/",
        "https://www.mhinvest.com/public/literature/quarterly-report/?cc=O",
        "https://www.dbroot.com/resources/?newsCategorySlug=market-commentary",
        "https://www.livianco.com/resources",
        "https://appomattox.com/news-insights/",
        "https://seabridge.com/commentary/",
        "https://www.sitkapacific.com/memos-articles-letters/",
        "https://kayne.com/insights/",
        "https://arsinvestmentpartners.com/outlook-insights/",
        "https://info.telemus.com/blog/tag/monthly-quarterly-commentary",
        "https://www.usfunds.com/resource-listing/?resource-type=investor-alert",
        "https://www.ftinstitutional.com/",
        "https://www.avivainvestors.com/en-de/views/aiq-investment-thinking/economic-research/",
        "https://www.alliancebernstein.com/corporate/en/insights-landing.html",
        "https://www.nb.com/en/global/home",
        "https://www.janushenderson.com/en-us/advisor/insights/",
        "https://europe.pimco.com/en-eu/insights/economic-and-market-commentary",
        "https://www.guggenheiminvestments.com/perspectives/sector-views",
        "https://www.newyorklifeinvestments.com/insights",
        "https://www.gweiss.com/insights",
        "https://russellinvestments.com/us/insights",
        "https://www.mellon.com/insights.html",
        "https://www.amundi.com/usinvestors/Insights/Research-Insights",
        "https://www.eatonvance.com/advisory-blog.php?since=2023-03-23&until=2023-06-23",
        "https://www.matthewsasia.com/insights/",
        "https://www.loomissayles.com/",
        "https://kraneshares.com/",
        "https://contrarianedge.com/",
        "https://www.serenityalts.com/blog",
        "https://www.crystalfunds.com/insights",
        "https://www.kingstreet.com/Insights",
        "https://www.fitchratings.com/",
        "https://www.abnamro.com/en/research",
        "https://research.sebgroup.com/macro-ficc",
        "https://www.researchonline.se/macro/start",
        "https://www.nbc.ca/about-us/news-media/financial-news/financial-analysis.html",
        "https://www.qnb.com/sites/qnb/qnbqatar/page/en/enresearch.html",
        "https://www2.deloitte.com/us/en/pages/outlooks/industry-outlooks.html",
        "https://www.regions.com/wealth-management/asset-management/leadership",
        "https://www.mckinsey.com/mgi/our-research/all-research",
        "https://www.yolegroup.com/articles/?fwp_post_categories=technology-insights",
        "https://valueinvestorsclub.com/",
        "https://globalvaluehunter.com/investment-ideas/",
        "https://www.thebeartrapsreport.com/blog/",
        "https://www.brownstoneresearch.com/bleeding-edge/",
        "https://www.visualcapitalist.com/",
        "https://lplresearch.com/",
        "https://insight.factset.com/",
        "https://www.newyorkfed.org/research",
        "https://www.econostream-media.com/",
        "https://www.macrodesiac.com/",
        "https://realinvestmentadvice.com/insights/real-investment-daily/",
        "https://fwintersberger.substack.com/",
        "https://morningporridge.com/blog/",
        "https://www.nsenergybusiness.com/",
        "https://www.globalcapital.com/",
        "https://scottgrannis.blogspot.com/",
        "https://macro-ops.com/research/",
        "https://www.epi.org/blog/",
        "https://www.dlacalle.com/en/",
        "https://www.spectramarkets.com/am-fx-archive/",
        "https://www.bankofengland.co.uk/news/publications",
        "https://www.capitaleconomics.com/capital-views",
        "https://hedgopia.com/",
        "https://bondvigilantes.com/",
        "https://inflationguy.blog/",
        "https://www.hedgefundtelemetry.com/",
        "https://www.man.com/maninstitute",
        "https://www.oxfordeconomics.com/resource-hub/",
        "https://www.christophe-barraud.com/blog/",
        "https://blog.faisalkhan.com/",
        "https://about.bnef.com/blog/?tactic-page=443258",
        "https://www.semiconductors.org/",
    ]
    failed_scrapping = []
    for source_url in new_sources:
        print(source_url)
        try:
            name, img_url = get_new_sources_info(source_url)
            if (
                Source.objects.filter(name=name).exists()
                or Source.objects.filter(slug=slugify(name)).exists()
                or Source.objects.filter(slug=slugify(name[:49])).exists()
            ):
                name = name + f" - Other {name[:2]}"
            created_source = Source.objects.create(
                url=source_url,
                slug=slugify(name[:49]),
                name=name[:49],
                favicon_path=f"home/favicons/{slugify(name[:49])}.webp",
                paywall="No",
                website=get_object_or_404(Website, name="Other"),
                content_type="Analysis",
                sector=get_object_or_404(Sector, name="Generalists"),
            )
            try:
                source_profile_img_create(created_source, img_url)
                feed_url = f"{source_url}feed"
                try:
                    create_articles_from_feed(
                        created_source, feed_url, Article.objects.none()
                    )
                except Exception as _:
                    created_source.alt_feed = "not found"
                    created_source.save()
                rating = 8
            except Exception as _:
                rating = 7
            # add source_rating otherwise 500 error when opening source profile
            SourceRating.objects.create(
                user=get_object_or_404(User, email="me-99@live.de"),
                source=created_source,
                rating=rating,
            )
        except Exception as error:
            failed_scrapping.append(source_url)
            print(f"Scrapping {source_url} has caused this error: ")
            print(error)
            continue
    print("The following sources could not be scrapped: ")
    for source in failed_scrapping:
        print(source)


@shared_task
def add_online_publication_tag():
    from apps.source.models import SourceTag

    for source in Source.objects.filter(
        website__name="Other", content_type="News", sector__name="Generalists"
    ):
        source.tags.add(get_object_or_404(SourceTag, name="Online Publication"))
        source.save()


# =================================================================================
# Tasks that need to be used from time to time
# =================================================================================


# @shared_task
# def stocks_create_all_companies_json():
#     api_key = environ.get("FMP_API_KEY")
#     url = f"https://financialmodelingprep.com/api/v3/stock/list?apikey={api_key}"
#     response = request_get(url, stream=True, timeout=10)
#     if response.status_code == 200:
#         with open("data_next.json", "w") as f:
#             for chunk in response.iter_content(chunk_size=1024):
#                 try:
#                     chunk_str = chunk.decode("utf-8", errors="ignore")
#                     f.write(chunk_str)
#                 except UnicodeDecodeError as err:
#                     print("UnicodeDecodeError:", err)


# @shared_task
# def stocks_create_models_from_json():
#     with open("all_companies_01042023.json", "r") as f:
#         company_data = json.load(f)
#     for item in company_data:
#         symbol = item["symbol"]
#         if (
#             item["type"] == "stock"
#             and all(char not in symbol for char in ("."))
#             and len(symbol) < 7
#         ):
#             if "-" in symbol:
#                 symbol = symbol.replace("-", ".")
#             full_name = item["name"]
#             short_name = full_name
#             for word in full_fillerwords:
#                 short_name = short_name.replace(word, "")
#             for word in short_fillerwords:
#                 short_name = short_name.replace(word, "")
#             stock_instance = Stock.objects.filter(ticker=symbol).first()
#             try:
#                 if stock_instance:
#                     stock_instance.full_company_name = full_name[:100]
#                     stock_instance.short_company_name = short_name[:100]
#                     stock_instance.save()
#                 elif Stock.objects.filter(full_company_name=full_name[:100]).exists():
#                     continue
#                 else:
#                     Stock.objects.create(
#                         ticker=symbol,
#                         full_company_name=full_name[:100],
#                         short_company_name=short_name[:100],
#                     )
#             except Exception as e:
#                 continue


# @shared_task
# def find_english_words():
#     # Load the words from the text file
#     with open("words.txt", "r") as f:
#         words = set(line.strip() for line in f)

#     # Create an empty list to store the matching words
#     english_words = []

#     # Loop through all instances of the Stock model
#     for stock in Stock.objects.all():
#         # Check if the ticker is in the words set
#         if stock.ticker.lower() in words:
#             english_words.append(stock.ticker.lower())
#         # Check if the short_company_name is in the words set
#         if stock.short_company_name.lower() in words:
#             english_words.append(stock.short_company_name.lower())

#     # Write the English words to a new Python file
#     with open("english_words.py", "w") as f:
#         f.write("english_words = {}\n".format(english_words))


# @shared_task
# def delete_article_duplicates():
#     sources = Source.objects.exclude(website__name="Twitter")
#     for source in sources:
#         ids_of_duplicate_articles = []
#         try:
#             articles_from_source = Article.objects.filter(source=source).order_by(
#                 "pub_date"
#             )
#             for article in articles_from_source:
#                 title_duplicates = articles_from_source.filter(title=article.title)
#                 duplicates = title_duplicates.count()
#                 while duplicates > 1:
#                     if (
#                         title_duplicates[duplicates - 1].article_id
#                         not in ids_of_duplicate_articles
#                     ):
#                         ids_of_duplicate_articles.append(
#                             title_duplicates[duplicates - 1].article_id
#                         )
#                     duplicates -= 1
#                 link_duplicates = articles_from_source.filter(link=article.link)
#                 duplicates = link_duplicates.count()
#                 while duplicates > 1:
#                     if (
#                         link_duplicates[duplicates - 1].article_id
#                         not in ids_of_duplicate_articles
#                     ):
#                         ids_of_duplicate_articles.append(
#                             link_duplicates[duplicates - 1].article_id
#                         )
#                     duplicates -= 1
#         except Exception as error:
#             print(error)
#         Article.objects.filter(article_id__in=ids_of_duplicate_articles).delete()


# @shared_task
# def forbes_scrape_accounts():
#     new_forbes_sources = []
#     failed_scrapping = []
#     for source_url in new_forbes_sources:
#         try:
#             print(source_url)
#             name, img_url = get_forbes_info(source_url)
#             if (
#                 Source.objects.filter(name=name).exists()
#                 or Source.objects.filter(slug=slugify(name)).exists()
#             ):
#                 name = name + " - Forbes"
#             source = Source.objects.create(
#                 url=source_url,
#                 slug=slugify(name),
#                 name=name,
#                 favicon_path=f"home/favicons/{slugify(name)}.png",
#                 paywall="Semi",
#                 website=get_object_or_404(Website, name="Forbes"),
#                 content_type="News",
#             )
#             source_profile_img_create(source, img_url)
#             # add source_rating otherwise 500 error when opening source profile
#             SourceRating.objects.create(
#                 user=get_object_or_404(User, email="me-99@live.de"),
#                 source=source,
#                 rating=7,
#             )
#             sleep(5)
#         except Exception as error:
#             failed_scrapping.append(source_url)
#             print(f"Scrapping {source_url} has caused this error: ")
#             print(error)
#             continue
#     print("The following sources could not be scrapped: ")
#     for source in failed_scrapping:
#         print(source)


# @shared_task
# def seeking_alpha_scrape_accounts():
#     new_sources = [
#         # {
#         #     "url": "https://seekingalpha.com/author/best-anchor-stocks",
#         #     "name": "Best Anchor Stocks",
#         #     "profile_pic": "https://static.seekingalpha.com/images/users_profile/055/205/028/extra_large_pic.png",
#         #     "rating": 8,
#         #     "sector": "Tech",
#         #     "tags": [],
#         # },
#     ]

#     failed_scrapping = []
#     for source in new_sources:
#         try:
#             print(source)
#             name_of_new_source = source["name"]
#             created_source = Source.objects.create(
#                 url=source["url"],
#                 slug=slugify(name_of_new_source),
#                 name=name_of_new_source,
#                 favicon_path=f"home/favicons/{slugify(name_of_new_source)}.png",
#                 paywall="Yes",
#                 website=get_object_or_404(Website, name="SeekingAlpha"),
#                 content_type="Analysis",
#                 sector=get_object_or_404(Sector, name=source["sector"]),
#             )
#             if len(source["tags"]):
#                 for tag in source["tags"]:
#                     created_source.tags.add(get_object_or_404(SourceTag, name=tag))
#             source_profile_img_create(created_source, source["profile_pic"])
#             # add source_rating otherwise 500 error when opening source profile
#             SourceRating.objects.create(
#                 user=get_object_or_404(User, email="me-99@live.de"),
#                 source=created_source,
#                 rating=source["rating"],
#             )
#             sleep(5)
#         except Exception as error:
#             failed_scrapping.append(name_of_new_source)
#             print(f"Scrapping {name_of_new_source} has caused this error: ")
#             print(error)
#             continue
#     print("The following sources could not be scrapped: ")
#     for source in failed_scrapping:
#         print(source)


# @shared_task
# def find_other_sources_without_feed_first_run():
#     for source in Source.objects.filter(website__name="Other"):
#         try:
#             print("------------------------------------------------")
#             print(source)
#             if not Article.objects.filter(source=source).exists():
#                 rss_feed = find_rss_feed(source.url)
#                 print(rss_feed)
#                 if rss_feed:
#                     source.alt_feed = rss_feed
#                 else:
#                     source.alt_feed = "none"
#                 source.save()
#         except Exception as error:
#             print(f"Error: {error} has occured while scrapping {source}")


# @shared_task
# def scrape_new_mixed_sources():
#     from apps.source.models import Sector, SourceRating

#     new_sources = []
#     failed_scrapping = []
#     for source_url in new_sources:
#         print(source_url)
#         try:
#             name, img_url = get_new_sources_info(source_url)
#             if (
#                 Source.objects.filter(name=name).exists()
#                 or Source.objects.filter(slug=slugify(name)).exists()
#                 or Source.objects.filter(slug=slugify(name[:49])).exists()
#             ):
#                 name = name + " - New"
#             created_source = Source.objects.create(
#                 url=source_url,
#                 slug=slugify(name[:49]),
#                 name=name[:49],
#                 favicon_path=f"home/favicons/{slugify(name[:49])}.webp",
#                 paywall="Yes",
#                 website=get_object_or_404(Website, name="Not Selected"),
#                 content_type="News",
#                 sector=get_object_or_404(Sector, name="Generalists"),
#             )
#             try:
#                 source_profile_img_create(created_source, img_url)
#                 feed_url = f"{source_url}feed"
#                 create_articles_from_feed(
#                     created_source, feed_url, Article.objects.none()
#                 )
#                 rating = 8
#             except Exception as _:
#                 rating = 7
#             # add source_rating otherwise 500 error when opening source profile
#             SourceRating.objects.create(
#                 user=get_object_or_404(User, email="me-99@live.de"),
#                 source=created_source,
#                 rating=rating,
#             )
#         except Exception as error:
#             failed_scrapping.append(source_url)
#             print(f"Scrapping {source_url} has caused this error: ")
#             print(error)
#             continue
#     print("The following sources could not be scrapped: ")
#     for source in failed_scrapping:
#         print(source)


# @shared_task
# def recalc_average_rating():
#     from apps.source.models import SourceRating

#     for source in Source.objects.all():
#         agg_ratings = 0
#         ammount_of_ratings = 0
#         for rating in SourceRating.objects.filter(source=source):
#             agg_ratings += rating.rating
#             ammount_of_ratings += 1
#         source.ammount_of_ratings = ammount_of_ratings
#         source.average_rating = agg_ratings / ammount_of_ratings
#         source.save()


# @shared_task
# def rate_sources():
#     import random
#     from apps.source.models import SourceRating

#     rater_number = random.randint(1, 30)
#     rater = get_object_or_404(User, username=f"InvitedSourceRater{rater_number}")
#     if SourceRating.objects.filter(user=rater).count() < 200:
#         for source in Source.objects.all():
#             if SourceRating.objects.filter(source=source, user=rater).exists():
#                 continue
#             if random.random() < min(0.2, source.ammount_of_ratings * 0.0075):
#                 rating_bonus = 0
#                 rating_random = random.random()
#                 if rating_random > 0.9:
#                     rating_bonus = 2
#                 elif rating_random > 0.75:
#                     rating_bonus = 1
#                 elif rating_random < 0.1:
#                     rating_bonus = -2
#                 elif rating_random < 0.25:
#                     rating_bonus = -1
#                 rating = min(10, round(source.average_rating) + rating_bonus)
#                 SourceRating.objects.create(source=source, user=rater, rating=rating)


# @shared_task
# def create_youtube_sources():
#     from apps.source.models import SourceRating, Sector, SourceTag

#     new_sources = [
#         {
#             "url": "https://www.youtube.com/@entreprenuership_opportunities",
#             "name": "EO",
#             "rating": 9,
#             "sector": "Venture Capital",
#             "tags": ["Great Storyteller"],
#             "external_id": "UCUFLZTlEPJNr04bQeCKr0PQ",
#         }
#     ]

#     failed_scrapping = []
#     for source in new_sources:
#         try:
#             print(source)
#             name = source["name"]
#             created_source = Source.objects.create(
#                 url=source["url"],
#                 slug=slugify(name),
#                 name=name,
#                 favicon_path=f"home/favicons/{slugify(name)}.webp",
#                 paywall="No",
#                 website=get_object_or_404(Website, name="YouTube"),
#                 content_type="Analysis",
#                 sector=get_object_or_404(Sector, name=source["sector"]),
#             )
#             if len(source["tags"]):
#                 for tag in source["tags"]:
#                     created_source.tags.add(get_object_or_404(SourceTag, name=tag))
#             # add source_rating otherwise 500 error when opening source profile
#             SourceRating.objects.create(
#                 user=get_object_or_404(User, email="me-99@live.de"),
#                 source=created_source,
#                 rating=source["rating"],
#             )
#         except Exception as error:
#             failed_scrapping.append(name)
#             print(f"Scrapping {name} has caused this error: ")
#             print(error)
#             continue
#     print("The following sources could not be scrapped: ")
#     for source in failed_scrapping:
#         print(source)


# @shared_task
# def substack_scrape_accounts():
#     from apps.source.models import SourceRating, Sector

#     new_substack_sources = []
#     scraping_failed = []
#     for source_url in new_substack_sources:
#         try:
#             print(source_url)
#             name, img_url = get_substack_info(source_url)
#             if (
#                 Source.objects.filter(name=name).exists()
#                 or Source.objects.filter(slug=slugify(name)).exists()
#             ):
#                 name = name + " - Substack"
#             source = Source.objects.create(
#                 url=source_url,
#                 slug=slugify(name),
#                 name=name,
#                 favicon_path=f"home/favicons/{slugify(name)}.png",
#                 paywall="No",
#                 website=get_object_or_404(Website, name="Substack"),
#                 content_type="Analysis",
#                 sector=get_object_or_404(Sector, name="Generalists"),
#             )
#             source_profile_img_create(source, img_url)
#             # add source_rating otherwise 500 error when opening source profile
#             SourceRating.objects.create(
#                 user=get_object_or_404(User, email="me-99@live.de"),
#                 source=source,
#                 rating=7,
#             )
#             sleep(5)
#         except Exception as error:
#             scraping_failed.append(source_url)
#             print(f"Scrapping {source_url} has caused this error: ")
#             print(error)
#             continue
#     print("Scrapping has failed for these sources: ")
#     for source in scraping_failed:
#         print(source)


# @shared_task
# def fix_broken_short_company_names():
#     from apps.scrapper.filler_words import new_fillerwords
#     from apps.stock.models import Stock

#     for stock in Stock.objects.all():
#         short_name = stock.short_company_name
#         for word in new_fillerwords:
#             short_name = short_name.replace(word, "")
#         if short_name.endswith(" and"):
#             short_name = short_name.replace(" and", "")
#         if short_name.endswith("orporated"):
#             short_name = short_name.replace("orporated", "")
#         if short_name != stock.short_company_name:
#             stock.short_company_name = short_name
#             stock.save()


# @shared_task
# def create_spotify_sources():
#     from apps.source.models import Sector, SourceRating

#     client_id = environ.get("SPOTIFY_CLIENT_ID")
#     client_secret = environ.get("SPOTIFY_CLIENT_SECRET")
#     spotify_sources = []
#     failed_sources = []
#     for source_url in spotify_sources:
#         if not Source.objects.filter(url=source_url).exists():
#             try:
#                 external_id = source_url.split("https://open.spotify.com/show/")[1]
#                 spotify = SpotifyAPI(client_id, client_secret)
#                 podcaster = spotify.get_podcaster(external_id)
#                 name = podcaster["name"][:49]
#                 if Source.objects.filter(name=name).exists():
#                     name = podcaster["name"][:40] + "- Spotify"
#                 slug = slugify(name)[:49]
#                 source = Source.objects.create(
#                     url=source_url,
#                     slug=slug,
#                     name=name,
#                     favicon_path=f"home/favicons/{slug}.webp",
#                     paywall="No",
#                     website=get_object_or_404(Website, name="Spotify"),
#                     content_type="Analysis",
#                     sector=get_object_or_404(Sector, name="Generalists"),
#                     external_id=external_id,
#                 )
#                 if "images" in podcaster.keys():
#                     source_profile_img_create(source, podcaster["images"][0]["url"])
#                 # add source_rating otherwise 500 error when opening source profile
#                 SourceRating.objects.create(
#                     user=get_object_or_404(User, email="me-99@live.de"),
#                     source=source,
#                     rating=7,
#                 )
#             except Exception as error:
#                 failed_sources.append(source_url)
#                 print(f"Scrapping {source_url} failed due to {error}")
#                 continue
#         sleep(3)
#     print("Scrapping failed for these sources")
#     for source in failed_sources:
#         print(source)


# @shared_task
# def create_news_sources():
#     from apps.source.models import Sector, SourceRating

#     new_sources = []
#     failed_scrapping = []
#     for source_url in new_sources:
#         print(source_url)
#         try:
#             name, img_url = get_new_sources_info(source_url)
#             if (
#                 Source.objects.filter(name=name).exists()
#                 or Source.objects.filter(slug=slugify(name)).exists()
#                 or Source.objects.filter(slug=slugify(name[:49])).exists()
#             ):
#                 name = name + " - New"
#             created_source = Source.objects.create(
#                 url=source_url,
#                 slug=slugify(name[:49]),
#                 name=name[:49],
#                 favicon_path=f"home/favicons/{slugify(name[:49])}.webp",
#                 paywall="No",
#                 website=get_object_or_404(Website, name="Other"),
#                 content_type="News",
#                 sector=get_object_or_404(Sector, name="Generalists"),
#             )
#             try:
#                 source_profile_img_create(created_source, img_url)
#                 feed_url = f"{source_url}feed"
#                 try:
#                     create_articles_from_feed(
#                         created_source, feed_url, Article.objects.none()
#                     )
#                 except Exception as _:
#                     created_source.alt_feed = "not found"
#                     created_source.save()
#                 rating = 8
#             except Exception as _:
#                 rating = 7
#             # add source_rating otherwise 500 error when opening source profile
#             SourceRating.objects.create(
#                 user=get_object_or_404(User, email="me-99@live.de"),
#                 source=created_source,
#                 rating=rating,
#             )
#         except Exception as error:
#             failed_scrapping.append(source_url)
#             print(f"Scrapping {source_url} has caused this error: ")
#             print(error)
#             continue
#     print("The following sources could not be scrapped: ")
#     for source in failed_scrapping:
#         print(source)
