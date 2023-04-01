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


class SettingsTest(LiveServerTestCase):
    def test_change_username(self):
        driver = login("http://127.0.0.1:8000/profile/settings")
        WebDriverWait(driver, 3).until(
            expected_conditions.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "#id_username",
                )
            )
        )
        driver.find_element(By.CSS_SELECTOR, "#id_username").clear()
        driver.find_element(By.CSS_SELECTOR, "#id_username").send_keys("Ebirdmax99Test")
        driver.find_element(By.CSS_SELECTOR, ".editSection .saveButton").click()
        assert "Ebirdmax99Test" == driver.find_element(
            By.CSS_SELECTOR, "#id_username"
        ).get_attribute("value")
        WebDriverWait(driver, 3).until(
            expected_conditions.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "#id_username",
                )
            )
        )
        driver.find_element(By.CSS_SELECTOR, "#id_username").clear()
        driver.find_element(By.CSS_SELECTOR, "#id_username").send_keys("Ebirdmax99")
        driver.find_element(By.CSS_SELECTOR, ".editSection .saveButton").click()
        assert "Ebirdmax99" == driver.find_element(
            By.CSS_SELECTOR, "#id_username"
        ).get_attribute("value")

    def test_change_email(self):
        driver = login("http://127.0.0.1:8000/profile/settings")
        WebDriverWait(driver, 3).until(
            expected_conditions.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "#id_email",
                )
            )
        )
        driver.find_element(By.CSS_SELECTOR, "#id_email").clear()
        driver.find_element(By.CSS_SELECTOR, "#id_email").send_keys("me-99@livetest.de")
        driver.find_element(By.CSS_SELECTOR, ".editSection .saveButton").click()
        assert "me-99@livetest.de" == driver.find_element(
            By.CSS_SELECTOR, "#id_email"
        ).get_attribute("value")
        WebDriverWait(driver, 3).until(
            expected_conditions.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "#id_email",
                )
            )
        )
        driver.find_element(By.CSS_SELECTOR, "#id_email").clear()
        driver.find_element(By.CSS_SELECTOR, "#id_email").send_keys("me-99@live.de")
        driver.find_element(By.CSS_SELECTOR, ".editSection .saveButton").click()
        assert "me-99@live.de" == driver.find_element(
            By.CSS_SELECTOR, "#id_email"
        ).get_attribute("value")

    def test_change_timezone(self):
        driver = login("http://127.0.0.1:8000/profile/settings")
        WebDriverWait(driver, 3).until(
            expected_conditions.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "#id_timezone",
                )
            )
        ).click()
        assert (
            driver.find_element(
                By.CSS_SELECTOR, "#id_timezone option:checked"
            ).get_attribute("innerText")
            == "Europe/Berlin"
        )
        driver.find_element(By.CSS_SELECTOR, 'option[value="Europe/Athens"]').click()
        assert (
            driver.find_element(
                By.CSS_SELECTOR, "#id_timezone option:checked"
            ).get_attribute("innerText")
            == "Europe/Athens"
        )
        driver.find_element(By.CSS_SELECTOR, ".editSection .saveButton").click()
        WebDriverWait(driver, 3).until(
            expected_conditions.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "#id_timezone",
                )
            )
        ).click()
        assert (
            driver.find_element(
                By.CSS_SELECTOR, "#id_timezone option:checked"
            ).get_attribute("innerText")
            == "Europe/Athens"
        )
        driver.find_element(By.CSS_SELECTOR, 'option[value="Europe/Berlin"]').click()
        driver.find_element(By.CSS_SELECTOR, ".editSection .saveButton").click()
        assert (
            driver.find_element(
                By.CSS_SELECTOR, "#id_timezone option:checked"
            ).get_attribute("innerText")
            == "Europe/Berlin"
        )

    def test_change_password(self):
        driver = login("http://127.0.0.1:8000/profile/settings")
        WebDriverWait(driver, 3).until(
            expected_conditions.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    ".pageWrapper .tabsContainer button",
                )
            )
        )
        driver.find_elements(
            By.CSS_SELECTOR,
            ".pageWrapper .tabsContainer button",
        )[1].click()
        driver.find_element(By.CSS_SELECTOR, "#id_old_password").send_keys("testpw99")
        driver.find_element(By.CSS_SELECTOR, "#id_new_password1").send_keys(
            "testpw1999"
        )
        driver.find_element(By.CSS_SELECTOR, "#id_new_password2").send_keys(
            "testpw1999"
        )
        driver.find_element(
            By.CSS_SELECTOR, ".changePasswordForm .passwordChangeSubmit"
        ).click()
        driver.find_element(By.CSS_SELECTOR, ".headerContainer .userProfile").click()
        driver.find_element(
            By.CSS_SELECTOR, ".headerContainer .profileMenu form button"
        ).click()
        driver = webdriver.Chrome()
        driver.get("http://127.0.0.1:8000/registration/login/")
        driver.set_window_size(1920, 1080)
        driver.find_element(By.CSS_SELECTOR, "#id_login").send_keys("me-99@live.de")
        driver.find_element(By.CSS_SELECTOR, "#id_password").send_keys("testpw1999")
        driver.find_element(By.CSS_SELECTOR, "#id_remember").click()
        driver.find_element(By.CSS_SELECTOR, ".primaryAction").click()
        driver.get("http://127.0.0.1:8000/profile/settings")
        WebDriverWait(driver, 3).until(
            expected_conditions.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    ".pageWrapper .tabsContainer button",
                )
            )
        )
        driver.find_elements(By.CSS_SELECTOR, ".pageWrapper .tabsContainer button")[
            1
        ].click()
        driver.find_element(By.CSS_SELECTOR, "#id_old_password").send_keys("testpw1999")
        driver.find_element(By.CSS_SELECTOR, "#id_new_password1").send_keys("testpw99")
        driver.find_element(By.CSS_SELECTOR, "#id_new_password2").send_keys("testpw99")
        driver.find_element(
            By.CSS_SELECTOR, ".changePasswordForm .passwordChangeSubmit"
        ).click()

    def test_delete_notifications(self):
        driver = login("http://127.0.0.1:8000/profile/settings")
        WebDriverWait(driver, 3).until(
            expected_conditions.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    ".pageWrapper .tabsContainer button",
                )
            )
        )
        driver.find_elements(
            By.CSS_SELECTOR,
            ".pageWrapper .tabsContainer button",
        )[2].click()
        # initial_source_notifications = len(
        #     driver.find_elements(By.CSS_SELECTOR, ".tabsContentActive .contentWrapper")
        # )
        # driver.find_elements(By.CSS_SELECTOR, ".contentWrapper .notificationButton")[
        #     0
        # ].click()
        initial_stock_notifications = len(
            driver.find_elements(
                By.CSS_SELECTOR,
                ".tabsContentActive .notificationContainer .keywordContainer",
            )
        )
        driver.find_elements(
            By.CSS_SELECTOR,
            ".tabsContentActive .notificationContainer .keywordContainer .fa-times",
        )[0].click()
        sleep(1)
        assert (
            len(
                driver.find_elements(
                    By.CSS_SELECTOR,
                    ".tabsContentActive .notificationContainer .keywordContainer",
                )
            )
            == initial_stock_notifications - 1
        )
        initial_keyword_notifications = len(
            driver.find_elements(
                By.CSS_SELECTOR,
                ".tabsContentActive .notificationContainer:last-of-type .keywordContainer",
            )
        )
        driver.find_elements(
            By.CSS_SELECTOR,
            ".tabsContentActive .notificationContainer:last-of-type .keywordContainer .fa-times",
        )[0].click()
        sleep(1)
        assert (
            len(
                driver.find_elements(
                    By.CSS_SELECTOR,
                    ".tabsContentActive .notificationContainer:last-of-type .keywordContainer",
                )
            )
            == initial_keyword_notifications - 1
        )
