# Django imports
from django.db import models
from django.db.models import Sum


class SourceManager(models.Manager):
    def calc_similiar_sources(self):
        sources = list(self.all().prefetch_related("tags"))
        for source in sources:
            sim_dict = {}
            for sim_source in sources:
                if source == sim_source:
                    continue
                score = 0
                if sim_source.sector == source.sector:
                    score += 5
                if sim_source.content_type == source.content_type:
                    score += 3
                if source.top_source and sim_source.top_source == source.top_source:
                    score += 3
                if sim_source.website == source.website:
                    score += 2
                if sim_source.paywall == source.paywall:
                    score += 2
                if source.ammount_of_ratings > 5:
                    if abs(source.average_rating - sim_source.average_rating) < 0.5:
                        score += 1
                    if (
                        abs(source.ammount_of_ratings - sim_source.ammount_of_ratings)
                        < source.ammount_of_ratings / 10
                    ):
                        score += 1
                for tag in sim_source.tags.all():
                    if tag in source.tags.all():
                        score += 3
                sim_dict[sim_source.source_id] = score
            similiar_sources = {
                k: v
                for k, v in sorted(
                    sim_dict.items(), key=lambda item: item[1], reverse=True
                )[0:10]
            }
            calc_sources = []
            for k, v in similiar_sources.items():
                calc_sources.append(k)
            self.filter(pk=source.source_id).first().sim_sources.set(calc_sources)

    def filter_subscribed_sources_by_content_type(self, user):
        subscribed_sources = self.filter_by_subscription(user)
        analysis_sources = subscribed_sources.filter(content_type="Analysis")
        commentary_sources = subscribed_sources.filter(content_type="Commentary")
        news_sources = subscribed_sources.filter(content_type="News")
        return {
            "analysis": analysis_sources,
            "commentary": commentary_sources,
            "news": news_sources,
        }

    def filter_by_sector(self, sector):
        analysis_sources = self.filter(content_type="Analysis", sector=sector)
        commentary_sources = self.filter(content_type="Commentary", sector=sector)
        news_sources = self.filter(content_type="News", sector=sector)
        return {
            "analysis_sources": analysis_sources,
            "commentary_sources": commentary_sources,
            "news_sources": news_sources,
        }

    def filter_by_subscription(self, user):
        return self.filter(subscribers=user).only(
            "favicon_path", "slug", "name", "average_rating", "source_id"
        )

    def filter_by_search_term(self, search_term):
        return self.filter(name__istartswith=search_term)

    def filter_by_list_and_search_term_exclusive(self, search_term, selected_list):
        return self.filter(name__istartswith=search_term).exclude(
            source_id__in=selected_list.sources.all()
        )

    def filter_by_subscription_and_search_term_exclusive(self, search_term, user):
        return self.filter(name__istartswith=search_term).exclude(subscribers=user)

    def get_random_top_sources(self):
        return self.filter(top_source=True).order_by("?")[0:21]


class SourceRatingManager(models.Manager):
    def get_user_rating(self, user, source):
        return (
            self.get(user=user, source=source).rating
            if self.filter(user=user, source=source).exists()
            else False
        )

    def get_average_rating(self, source):
        list_ratings = self.filter(source=source)
        sum_ratings = self.filter(source=source).aggregate(Sum("rating"))
        sum_ratings = sum_ratings.get("rating__sum", None)
        return round(sum_ratings / list_ratings.count(), 1) if sum_ratings else None

    def get_ammount_of_ratings(self, source):
        return self.filter(source=source).count()

    def save_rating(self, user, source, rating):
        if self.filter(user=user, source=source).exists():
            self.filter(user=user, source=source).update(rating=rating)
        else:
            self.create(user=user, source=source, rating=rating)

    def get_user_ratings_dict(self, user):
        ratings = self.filter(user=user).select_related("source")
        result_dict = {}
        # Loop through each SourceRating object and add it to the dictionary
        for rating in ratings:
            result_dict[rating.source.pk] = rating.rating
        return result_dict
