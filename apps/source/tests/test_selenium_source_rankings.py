# Django imports
from django.test import LiveServerTestCase

# Python imports
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from random import randrange


class SourceRankingTest(LiveServerTestCase):
    def test_open_profile_by_clicking_profile_img(self):
        driver = login("http://127.0.0.1:8000/sources")
        current_url = driver.current_url
        driver.find_element(
            By.CSS_SELECTOR, ".sourceRankingContainer .leftSide a"
        ).click()
        WebDriverWait(driver, 10).until(UrlHasChanged(current_url))
        assert driver.current_url.startswith("http://127.0.0.1:8000/source/")

    def test_open_profile_by_clicking_profile_img_small_screen(self):
        driver = login("http://127.0.0.1:8000/sources", True)
        current_url = driver.current_url
        driver.find_element(By.CSS_SELECTOR, ".secondRow .leftSideSecondRow a").click()
        WebDriverWait(driver, 10).until(UrlHasChanged(current_url))
        assert driver.current_url.startswith("http://127.0.0.1:8000/source/")

    def test_open_profile_by_clicking_name(self):
        driver = login("http://127.0.0.1:8000/sources")
        current_url = driver.current_url
        driver.find_element(By.CSS_SELECTOR, ".firstRow a").click()
        WebDriverWait(driver, 10).until(UrlHasChanged(current_url))
        assert driver.current_url.startswith("http://127.0.0.1:8000/source/")

    def test_open_sector(self):
        driver = login("http://127.0.0.1:8000/sources")
        current_url = driver.current_url
        driver.find_element(
            By.CSS_SELECTOR, ".infoWrapper .sectorInfoContainer a"
        ).click()
        WebDriverWait(driver, 10).until(UrlHasChanged(current_url))
        assert driver.current_url.startswith("http://127.0.0.1:8000/sector/")

    def test_open_website(self):
        driver = login("http://127.0.0.1:8000/sources")
        driver.find_element(
            By.CSS_SELECTOR, ".infoWrapper .websiteInfoContainer a"
        ).click()
        driver.switch_to.window(driver.window_handles[1])
        assert driver.current_url.startswith("http://127.0.0.1:8000") == False

    def test_clicking_tags(self):
        driver = login("http://127.0.0.1:8000/sources")
        second_source_ranking_container = driver.find_elements(
            By.CSS_SELECTOR, ".sourceRankingContainer"
        )[1]
        tag = second_source_ranking_container.find_element(
            By.CSS_SELECTOR, ".thirdRow .tag"
        )
        tag_name = tag.get_attribute("innerText")
        tag.click()
        assert tag_name == driver.find_element(
            By.CSS_SELECTOR, ".filterSidebar .selectedTagsContainer li"
        ).get_attribute("innerText")

    def test_subscribe_source(self):
        driver = login("http://127.0.0.1:8000/sources")
        second_source_ranking_container = driver.find_elements(
            By.CSS_SELECTOR, ".sourceRankingContainer"
        )[1]
        subscribe_button = second_source_ranking_container.find_element(
            By.CSS_SELECTOR, ".fourthRow .subscribeButton"
        )
        initial_subscribtion_status = subscribe_button.get_attribute("innerText")
        subscribe_button.click()
        driver = login("http://127.0.0.1:8000/sources")
        assert initial_subscribtion_status != subscribe_button.get_attribute(
            "innerText"
        )

    def test_add_to_list(self):
        driver = login("http://127.0.0.1:8000/sources")
        second_source_ranking_container = driver.find_elements(
            By.CSS_SELECTOR, ".sourceRankingContainer"
        )[1]
        WebDriverWait(second_source_ranking_container, 5).until(
            expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, ".fourthRow .sourceAddToListButton")
            )
        ).click()
        second_source_ranking_container.find_element(
            By.CSS_SELECTOR, ".fourthRow .addToListForm .formHeaderContainer"
        ).click()

    def test_filtering_websites(self):
        driver = login("http://127.0.0.1:8000/sources")
        driver.find_element(By.CSS_SELECTOR, ".filterSidebar .dropdown").click()
        driver.find_elements(By.CSS_SELECTOR, ".filterSidebar .dropdown ul li input")[
            0
        ].click()
        driver.find_elements(By.CSS_SELECTOR, ".filterSidebar .dropdown ul li input")[
            1
        ].click()
        driver.find_element(
            By.CSS_SELECTOR, ".filterSidebar .applyFilterButton"
        ).click()
        assert (
            driver.current_url
            == "http://127.0.0.1:8000/sources?website=SeekingAlpha&website=Spotify"
        )

    def test_filtering_sectors(self):
        driver = login("http://127.0.0.1:8000/sources")
        sector_dropdown = driver.find_elements(
            By.CSS_SELECTOR, ".filterSidebar .dropdown"
        )[1]
        sector_dropdown.click()
        sector_dropdown.find_elements(By.CSS_SELECTOR, "ul li input")[0].click()
        sector_dropdown.find_elements(By.CSS_SELECTOR, "ul li input")[1].click()
        driver.find_element(
            By.CSS_SELECTOR, ".filterSidebar .applyFilterButton"
        ).click()
        assert (
            driver.current_url
            == "http://127.0.0.1:8000/sources?sector=Defense&sector=Energy"
        )

    def test_filtering_tags(self):
        driver = login("http://127.0.0.1:8000/sources")
        driver.find_element(
            By.CSS_SELECTOR, ".filterSidebar .mainSearchContainer input"
        ).send_keys("Tag")
        WebDriverWait(driver, 2000).until(
            expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, ".filterSidebar .mainSearchWrapper .selectionList li")
            )
        ).click()
        driver.find_element(
            By.CSS_SELECTOR, ".filterSidebar .mainSearchContainer input"
        ).send_keys("N")
        WebDriverWait(driver, 2000).until(
            expected_conditions.element_to_be_clickable(
                (By.CSS_SELECTOR, ".filterSidebar .mainSearchWrapper .selectionList li")
            )
        ).click()
        driver.find_element(
            By.CSS_SELECTOR, ".filterSidebar .applyFilterButton"
        ).click()
        assert (
            driver.current_url == "http://127.0.0.1:8000/sources?tag=TagNr0&tag=TagNr1"
        )

    def test_filtering_other_criteria(self):
        driver = login("http://127.0.0.1:8000/sources")
        driver.find_element(
            By.CSS_SELECTOR, ".filterSidebar .applyFilterButton"
        ).click()
        content_type_container = driver.find_elements(
            By.CSS_SELECTOR, ".filterSidebar .selectContainer"
        )[3]
        paywall_container = driver.find_elements(
            By.CSS_SELECTOR, ".filterSidebar .selectContainer"
        )[4]
        top_sources_container = driver.find_elements(
            By.CSS_SELECTOR, ".filterSidebar .selectContainer"
        )[5]
        content_type_container.find_element(
            By.CSS_SELECTOR, ".choiceContainer input"
        ).click()
        paywall_container.find_element(
            By.CSS_SELECTOR, ".choiceContainer input"
        ).click()
        top_sources_container.find_element(By.CSS_SELECTOR, "input").click()
        driver.find_element(
            By.CSS_SELECTOR, ".filterSidebar .applyFilterButton"
        ).click()
        assert (
            driver.current_url
            == "http://127.0.0.1:8000/sources?content=Analysis&paywall=Yes&top_sources_only=on"
        )
