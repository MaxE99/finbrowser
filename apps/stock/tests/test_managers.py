# Django imports
from django.test import TestCase

# Local imports
from apps.tests.test_instances import CreateTestInstances
from apps.stock.models import Stock


class TestStockManager(CreateTestInstances, TestCase):
    def test_filter_by_search_term(self):
        stocks = Stock.objects.filter_by_search_term("Ford")
        self.assertEqual(stocks.count(), 1)
