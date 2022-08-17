# Django imports
from django.db import models
from django.urls import reverse
# Model imports
from apps.stock.managers import StockManager

class Stock(models.Model):
    stock_id = models.AutoField(primary_key=True)
    ticker = models.CharField(max_length=10, unique=True)
    full_company_name = models.CharField(max_length=100)
    short_company_name = models.CharField(max_length=100)

    objects = StockManager()

    def get_absolute_url(self):
        return reverse('stock:stock-details', kwargs={'slug': self.ticker})

    def __str__(self):
        return f'{self.ticker} - {self.full_company_name} - {self.short_company_name}'