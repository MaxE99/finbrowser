# Django imports
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

class Sector(models.Model):
    sector_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Sector, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('sector:sector-details', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name