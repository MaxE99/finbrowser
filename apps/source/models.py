# Django imports
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.contrib.auth import get_user_model

# Local imports
from django.core.validators import MaxValueValidator, MinValueValidator
from apps.source.managers import SourceManager, SourceRatingManager
from apps.accounts.models import Website
from apps.sector.models import Sector

User = get_user_model()


class SourceTag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ("name",)


class Source(models.Model):
    PAYWALL_CHOICES = [("Yes", "Yes"), ("Semi", "Semi"), ("No", "No")]
    CONTENT_TYPE_CHOICES = [
        ("Analysis", "Analysis"),
        ("Commentary", "Commentary"),
        ("News", "News"),
    ]
    source_id = models.AutoField(primary_key=True)
    url = models.URLField(unique=True)
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100, blank=True, unique=True)
    subscribers = models.ManyToManyField(
        User, related_name="subscriber_source", blank=True
    )
    favicon_path = models.CharField(max_length=500, blank=True)
    paywall = models.CharField(max_length=10, choices=PAYWALL_CHOICES, default="None")
    website = models.ForeignKey(
        Website, blank=True, null=True, on_delete=models.SET_NULL
    )
    sim_sources = models.ManyToManyField(
        "self", symmetrical=False, related_name="similiar_to", blank=True
    )
    top_source = models.BooleanField(default=False)
    sector = models.ForeignKey(Sector, null=True, on_delete=models.SET_NULL)
    external_id = models.CharField(unique=True, null=True, blank=True, max_length=100)
    average_rating = models.FloatField(blank=True, null=True)
    ammount_of_ratings = models.IntegerField(default=0, null=True)
    content_type = models.CharField(
        max_length=15, choices=CONTENT_TYPE_CHOICES, default="Commentary"
    )
    tags = models.ManyToManyField(SourceTag, related_name="source_tags", blank=True)
    alt_feed = models.CharField(null=True, blank=True, max_length=200)

    class Meta:
        ordering = ("name",)

    objects = SourceManager()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Source, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("source:source_profile", kwargs={"slug": self.slug})

    def __str__(self):
        return self.slug


class SourceRating(models.Model):
    source_rating_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1),
        ],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "source"], name="unique_rating")
        ]

    objects = SourceRatingManager()

    def save(self, *args, **kwargs):
        super(SourceRating, self).save(*args, **kwargs)
        Source.objects.filter(source_id=self.source.source_id).update(
            average_rating=round(
                SourceRating.objects.get_average_rating(self.source.source_id), 1
            ),
            ammount_of_ratings=SourceRating.objects.get_ammount_of_ratings(
                self.source.source_id
            ),
        )

    def __str__(self):
        return f"{self.user} - {self.source} - {self.rating}"
