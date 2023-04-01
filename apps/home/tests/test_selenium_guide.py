# Django imports
from django.test import LiveServerTestCase

# Python imports
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

# Local import
from apps.tests.test_selenium_base_functions import login


class GuideTest(LiveServerTestCase):
    pass
