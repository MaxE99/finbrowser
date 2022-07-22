# Django imports
from django.test import LiveServerTestCase
# Python imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from random import randrange

def login(next_page=False, smartphone=False):
    driver = webdriver.Chrome()
    driver.get("http://127.0.0.1:8000/registration/login/")
    if smartphone:
        driver.set_window_size(375, 667)
    else:
        driver.set_window_size(1920, 1080)
    driver.find_element(By.CSS_SELECTOR, '#id_login').send_keys('me-99@live.de')
    driver.find_element(By.CSS_SELECTOR, '#id_password').send_keys('testpw99')
    driver.find_element(By.CSS_SELECTOR, '#id_remember').click()
    driver.find_element(By.CSS_SELECTOR, '.primaryAction').click()
    sleep(1)
    assert "FinBrowser" in driver.title  
    if next_page:
        driver.get(next_page)
    return driver

def add_to_list(selector, driver):
    selector.find_element(By.CSS_SELECTOR, '.fa-ellipsis-h').click()
    sleep(3)
    selector.find_element(By.CSS_SELECTOR, '.addToListButton').click()
    sleep(1)
    selector.find_elements(By.CSS_SELECTOR, '.addToListForm .listSelectionContainer .listContainer label input')[0].click()
    selector.find_element(By.CSS_SELECTOR, '.addToListForm .saveButton').click()   
    sleep(1)
    assert "LISTS HAVE BEEN UPDATED!" in driver.find_element(By.CSS_SELECTOR, ".messages .success").get_attribute('innerText')

def highlight_content(selector, driver):
    selector.find_element(By.CSS_SELECTOR, '.fa-ellipsis-h').click()
    sleep(1)
    selector.find_element(By.CSS_SELECTOR, '.addToHighlightedButton').click()
    sleep(1)
    assert "ARTICLE HAS BEEN HIGHLIGHTED!" in driver.find_element(By.CSS_SELECTOR, ".messages li").get_attribute('innerText')  or "ARTICLE HAS BEEN UNHIGHLIGHTED!" in driver.find_element(By.CSS_SELECTOR, ".messages li").get_attribute('innerText')

def create_list(selector, driver):
    selector.find_element(By.CSS_SELECTOR, '.fa-ellipsis-h').click()
    sleep(1)
    selector.find_element(By.CSS_SELECTOR, '.addToListButton').click()
    sleep(1)
    selector.find_element(By.CSS_SELECTOR, '.addToListForm .createNewListButton').click()
    sleep(1) 
    form = selector.find_element(By.CSS_SELECTOR, '.createListMenu')
    form.find_element(By.CSS_SELECTOR, '#id_name').send_keys('TestList1107-123456')
    form.find_element(By.CSS_SELECTOR, '#id_is_public').click()
    sleep(1)
    form.find_element(By.CSS_SELECTOR, '.formSubmitButton').click()
    sleep(1)
    assert "TestList1107-123456" in driver.title or "YOU HAVE ALREADY CREATED A LIST WITH THAT NAME!" in driver.find_element(By.CSS_SELECTOR, ".messages .error").get_attribute('innerText')

def test_pagination(starturl, order, endurl):
    driver = login(starturl)
    pagination = driver.find_elements(By.CSS_SELECTOR, '.pagination .step-links')[order]
    pagination.find_elements(By.CSS_SELECTOR, 'a')[0].click()
    assert str(driver.current_url).endswith(endurl)   

################################################################################################################################

def test_add_to_list(next_page=False, smartphone=False):
    driver = login(next_page, smartphone)   
    selector = driver.find_elements(By.CSS_SELECTOR, '.contentColumnWrapper .smallFormContentWrapper .articleContainer')[5]
    add_to_list(selector, driver)    

def test_highlight_content(next_page=False, smartphone=False):
    driver = login(next_page, smartphone)
    selector = driver.find_elements(By.CSS_SELECTOR, '.contentColumnWrapper .smallFormContentWrapper .articleContainer')[5]
    highlight_content(selector, driver)

def test_create_list(next_page=False, smartphone=False):
    driver = login(next_page, smartphone) 
    selector = driver.find_elements(By.CSS_SELECTOR, '.contentColumnWrapper .smallFormContentWrapper .articleContainer')[5] 
    create_list(selector, driver)      

def test_open_source_profile(next_page=False, smartphone=False):
    driver = login(next_page, smartphone)
    driver.find_elements(By.CSS_SELECTOR, '.contentColumnWrapper .smallFormContentWrapper .articleContainer .rightContentSide .contentInfoContainer .sourceAndWebsiteContainer .sourceProfile')[5].click()
    sleep(1)
    assert "Profile | FinBrowser" in driver.title     

def test_open_source_profile_with_slider(next_page=False, smartphone=False): 
    driver = login(next_page, smartphone)
    driver.find_elements(By.CSS_SELECTOR, '.sliderWrapper .slider .contentWrapper .contentContainer .contentLink')[0].click()
    sleep(1)
    assert "Profile | FinBrowser" in driver.title  

def test_highlighting_content_is_working(next_page=False, smartphone=False):
    driver = login(next_page, smartphone)
    selector = driver.find_elements(By.CSS_SELECTOR, '.contentColumnWrapper .smallFormContentWrapper .articleContainer')[5]
    initial_highlighted_status = selector.find_element(By.CSS_SELECTOR, '.addToHighlightedButton').get_attribute("innerText")
    highlight_content(selector, driver)
    driver.refresh()
    sleep(1)
    selector = driver.find_elements(By.CSS_SELECTOR, '.contentColumnWrapper .smallFormContentWrapper .articleContainer')[5]
    selector.find_element(By.CSS_SELECTOR, '.fa-ellipsis-h').click()
    sleep(1)
    assert initial_highlighted_status != selector.find_element(By.CSS_SELECTOR, '.addToHighlightedButton').get_attribute("innerText")

def test_standard_use_cases(next_page=False, smartphone=False):
    test_add_to_list(next_page, smartphone)
    test_highlight_content(next_page, smartphone)
    test_create_list(next_page, smartphone)
    test_open_source_profile(next_page, smartphone)
    test_highlighting_content_is_working(next_page, smartphone)

########################################################################################################################################################


class NavigationTest(LiveServerTestCase):

    def test_navigation(self):
        driver = login()
        driver.find_elements(By.CSS_SELECTOR, '.mainNavigationLink a')[0].click()
        sleep(5)
        assert "FinBrowser | Feed" in driver.title
        driver.back()
        driver.find_element(By.CSS_SELECTOR, '.userSpace .fa-cog a').click()
        sleep(1)
        assert "FinBrowser | Settings" in driver.title

    def test_navigation_with_smartphone(self):
        driver = login("http://127.0.0.1:8000/", True)
        driver.find_element(By.CSS_SELECTOR, '.headerContainer .fa-bars').click()
        sleep(1)
        driver.find_elements(By.CSS_SELECTOR, '.horizontalNavigation .mainNavigationLink')[0].click()
        sleep(1)
        assert "FinBrowser | Feed" in driver.title
        driver.back()
        driver.find_elements(By.CSS_SELECTOR, '.horizontalNavigation .mainNavigationLink')[1].click()
        sleep(1)
        assert "FinBrowser | Lists" in driver.title
        driver.back()
        driver.find_elements(By.CSS_SELECTOR, '.horizontalNavigation .mainNavigationLink')[2].click()
        sleep(1)
        assert "FinBrowser | Sectors" in driver.title
        driver.back()
        driver.find_elements(By.CSS_SELECTOR, '.horizontalNavigation .mainNavigationLink')[3].click()
        sleep(1)
        assert "FinBrowser | Content" in driver.title
        driver.back()
        driver.find_elements(By.CSS_SELECTOR, '.horizontalNavigation .mainNavigationLink')[4].click()
        sleep(1)
        assert "FinBrowser | Settings" in driver.title
        driver.back()
        driver.find_elements(By.CSS_SELECTOR, '.horizontalNavigation .mainNavigationLink')[5].click()
        sleep(1)
        assert "FinBrowser | Notifications" in driver.title
        driver.back()
        driver.find_elements(By.CSS_SELECTOR, '.horizontalNavigation .mainNavigationLink')[6].click()
        sleep(1)
        assert "FinBrowser" == driver.title

    def test_navigation_anon_user(self):
        driver = webdriver.Chrome()
        driver.get("http://127.0.0.1:8000/")
        driver.set_window_size(1920, 1080)
        sleep(1)
        assert "FinBrowser" in driver.title
        driver.find_elements(By.CSS_SELECTOR, '.mainNavigationLink a')[0].click()
        sleep(1)
        assert "Login" in driver.title
        driver.back()
        driver.find_element(By.CSS_SELECTOR, '.userSpace .fa-cog a').click()
        sleep(1)
        assert "Login" in driver.title
        driver.back()
        driver.find_element(By.CSS_SELECTOR, '.userSpace .fa-bell').click()
        sleep(1)
        assert "Login" in driver.title
        driver.back()
        driver.find_elements(By.CSS_SELECTOR, 'footer li a')[0].click()
        sleep(1)
        assert "FinBrowser | Contact" in driver.title
        driver.find_elements(By.CSS_SELECTOR, 'footer li a')[1].click()
        sleep(1)
        assert "FinBrowser | Cookie Statement" in driver.title
        driver.find_elements(By.CSS_SELECTOR, 'footer li a')[2].click()
        sleep(1)
        assert "FinBrowser | Privacy Policy" in driver.title
        driver.find_elements(By.CSS_SELECTOR, 'footer li a')[3].click()
        sleep(1)
        assert "FinBrowser | Terms Of Service" in driver.title


class NotificationTest(LiveServerTestCase):

    def test_open_source_from_source_notifications(self):
        driver = login()
        driver.find_element(By.CSS_SELECTOR, '.userSpace .notificationBell').click()
        sleep(1)
        driver.find_elements(By.CSS_SELECTOR, '.activeNotificationContainer .articleContainer .sourceAndWebsiteContainer a')[0].click()
        assert "Profile | FinBrowser" in driver.title

    def test_standard_use_cases_for_source_notifications(self):
        driver = login()
        driver.find_element(By.CSS_SELECTOR, '.userSpace .notificationBell').click()
        content_container = driver.find_elements(By.CSS_SELECTOR, '.activeNotificationContainer .articleContainer')[0]
        highlight_content(content_container,driver)
        add_to_list(content_container,driver)
        create_list(content_container,driver)
        test_highlighting_content_is_working()

    def test_open_source_from_list_notifications(self):
        driver = login()
        driver.find_element(By.CSS_SELECTOR, '.userSpace .notificationBell').click()
        sleep(1)
        driver.find_elements(By.CSS_SELECTOR, '.notificationContainer .notificationHeadersContainer div')[-1].click()
        driver.find_elements(By.CSS_SELECTOR, '.activeNotificationContainer .articleContainer .sourceAndWebsiteContainer a')[0].click()
        assert "Profile | FinBrowser" in driver.title

    def test_standard_use_cases_for_list_notifications(self):
        driver = login()
        driver.find_element(By.CSS_SELECTOR, '.userSpace .notificationBell').click()
        sleep(1)
        driver.find_elements(By.CSS_SELECTOR, '.notificationContainer .notificationHeadersContainer div')[-1].click()
        content_container = driver.find_elements(By.CSS_SELECTOR, '.activeNotificationContainer .articleContainer')[0]
        highlight_content(content_container,driver)
        add_to_list(content_container,driver)
        create_list(content_container,driver)
        test_highlighting_content_is_working()

    def test_use_cases_with_smartphone(self):
        driver = login("http://127.0.0.1:8000/", True)
        driver.find_element(By.CSS_SELECTOR, '.headerContainer .fa-bars').click()
        sleep(1)
        driver.find_elements(By.CSS_SELECTOR, '.horizontalNavigation .mainNavigationLink')[5].click()
        sleep(1)
        tweet_container = driver.find_elements(By.CSS_SELECTOR, '.contentColumnWrapper .smallFormContentWrapper')[1]
        tweet_container.find_elements(By.CSS_SELECTOR, '.smallFormContentWrapper .articleContainer .sourceAndWebsiteContainer a')[0].click()
        assert "Profile | FinBrowser" in driver.title
        driver.back()
        content_container = tweet_container.find_elements(By.CSS_SELECTOR, '.articleContainer')[0]
        highlight_content(content_container,driver)
        add_to_list(content_container,driver)
        create_list(content_container,driver)
        test_highlighting_content_is_working()

class MainSearchTest(LiveServerTestCase):

    def test_open_list(self):
        driver = login()
        driver.find_element(By.CSS_SELECTOR, '.mainSearchWrapper .mainSearchContainer .mainInputSearch').send_keys('f')
        sleep(2)
        driver.find_elements(By.CSS_SELECTOR, '#mainAutocomplete_result .searchResult a')[0].click()
        assert 'List | FinBrowser' in driver.title

    def test_open_source(self):
        driver = login()
        driver.find_element(By.CSS_SELECTOR, '.mainSearchWrapper .mainSearchContainer .mainInputSearch').send_keys('f')
        sleep(2)
        driver.find_elements(By.CSS_SELECTOR, '#mainAutocomplete_result .searchResult a')[4].click()
        assert 'Profile | FinBrowser' in driver.title

    def test_click_search_button(self):
        driver = login()
        driver.find_element(By.CSS_SELECTOR, '.mainSearchWrapper .mainSearchContainer .mainInputSearch').send_keys('Test123')
        driver.find_element(By.CSS_SELECTOR, '.mainSearchWrapper .mainSearchContainer .fa-search').click()
        sleep(1)
        assert 'Test123' in driver.title

    def test_search_with_smartphone(self):
        driver = login("http://127.0.0.1:8000/", True)
        driver.find_element(By.CSS_SELECTOR, '.mainSearchWrapper .mainSearchContainer .mainInputSearch').send_keys('f')
        sleep(2)
        driver.find_elements(By.CSS_SELECTOR, '#mainAutocomplete_result .searchResult a')[0].click()
        assert 'List | FinBrowser' in driver.title
        driver.find_element(By.CSS_SELECTOR, '.mainSearchWrapper .mainSearchContainer .mainInputSearch').send_keys('f')
        sleep(2)
        driver.find_elements(By.CSS_SELECTOR, '#mainAutocomplete_result .searchResult a')[4].click()
        assert 'Profile | FinBrowser' in driver.title
        driver.find_element(By.CSS_SELECTOR, '.mainSearchWrapper .mainSearchContainer .mainInputSearch').send_keys('Test123')
        driver.find_element(By.CSS_SELECTOR, '.mainSearchWrapper .mainSearchContainer .fa-search').click()
        sleep(1)
        assert 'Test123' in driver.title

class MainTest(LiveServerTestCase):
    
    def test_main_standard_use_cases(self):
        test_standard_use_cases()
        test_open_source_profile_with_slider()
        test_standard_use_cases("http://127.0.0.1:8000/", True)

    def test_paginations(self):
        test_pagination("http://127.0.0.1:8000/", 0, '?articles_of_the_week=2')
        test_pagination("http://127.0.0.1:8000/", 1, '?audio_of_the_week=2')
        test_pagination("http://127.0.0.1:8000/", 2, '?trending_topic_articles=2')
        test_pagination("http://127.0.0.1:8000/", 3, '?energy_crisis_tweets=2')
        test_pagination("http://127.0.0.1:8000/", 4, '?macro_tweets=2')


class FeedTest(LiveServerTestCase):
    
    def test_main_standard_use_cases(self):
        test_standard_use_cases("http://127.0.0.1:8000/feed/")
        test_standard_use_cases("http://127.0.0.1:8000/feed/", True)

    def test_create_list(self):
        driver = login("http://127.0.0.1:8000/feed/")
        while driver.find_element(By.CSS_SELECTOR, '.sliderWrapper .slider .interactionWrapper').is_displayed() == False:
            driver.find_element(By.CSS_SELECTOR, '.sliderWrapper .rightHandle').click()
            sleep(1)
        driver.find_element(By.CSS_SELECTOR, '.sliderWrapper .slider .interactionWrapper .createListButton').click()
        sleep(1)
        form = driver.find_element(By.CSS_SELECTOR, '.sliderWrapper .slider .interactionWrapper .createListMenu')
        form.find_element(By.CSS_SELECTOR, '#id_name').send_keys('TestList1107-123456')
        form.find_element(By.CSS_SELECTOR, '#id_is_public').click()
        sleep(1)
        form.find_element(By.CSS_SELECTOR, '.formSubmitButton').click()
        sleep(1)
        assert "TestList1107-123456" in driver.title or "YOU HAVE ALREADY CREATED A LIST WITH THAT NAME!" in driver.find_element(By.CSS_SELECTOR, ".messages .error").get_attribute('innerText')

    def test_my_list_open_list(self):
        driver = login("http://127.0.0.1:8000/feed/")
        driver.find_elements(By.CSS_SELECTOR, '.sliderWrapper .slider .contentWrapper')[0].click()
        sleep(1)
        assert "List | FinBrowser" in driver.title

    def test_subscribed_lists_subscribe_to_lists(self):
        driver = login("http://127.0.0.1:8000/feed/")
        slider_wrapper = driver.find_elements(By.CSS_SELECTOR, '.sliderWrapper')[1]
        while slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .interactionWrapper').is_displayed() == False:
            slider_wrapper.find_element(By.CSS_SELECTOR, '.rightHandle').click()
            sleep(1)
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .interactionWrapper .addListsButton').click()
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .addListsForm #textInput').send_keys("Test")
        sleep(1)
        list_name = slider_wrapper.find_elements(By.CSS_SELECTOR, '.slider .addListsForm #searchResultsContainer .searchResult span')[0].get_attribute("innerText")
        slider_wrapper.find_elements(By.CSS_SELECTOR, '.slider .addListsForm #searchResultsContainer .searchResult')[0].click()
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .addListsForm #textInput').send_keys("Test")
        sleep(1)
        slider_wrapper.find_elements(By.CSS_SELECTOR, '.slider .addListsForm #searchResultsContainer .searchResult')[0].click()
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .addListsForm #textInput').send_keys("Test")
        sleep(1)
        slider_wrapper.find_elements(By.CSS_SELECTOR, '.slider .addListsForm #searchResultsContainer .searchResult')[0].click()
        slider_wrapper.find_elements(By.CSS_SELECTOR, '.slider .addListsForm .selectionContainer .searchResult .fa-trash')[2].click()
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .addListsForm .formSubmitButton').click()
        sleep(1)
        driver.refresh()
        slider_wrapper = driver.find_elements(By.CSS_SELECTOR, '.sliderWrapper')[1]
        while slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .interactionWrapper').is_displayed() == False:
            slider_wrapper.find_element(By.CSS_SELECTOR, '.rightHandle').click()
            sleep(1)
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .interactionWrapper .addListsButton').click()
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .addListsForm #textInput').send_keys("Test")
        sleep(1)
        assert list_name != slider_wrapper.find_elements(By.CSS_SELECTOR, '.slider .addListsForm #searchResultsContainer .searchResult span')[0].get_attribute("innerText")

    def test_subscribed_lists_open_list(self):
        driver = login("http://127.0.0.1:8000/feed/")
        slider_wrapper = driver.find_elements(By.CSS_SELECTOR, '.sliderWrapper')[1]
        slider_wrapper.find_elements(By.CSS_SELECTOR, '.sliderWrapper .slider .contentWrapper')[0].click()
        sleep(1)
        assert "List | FinBrowser" in driver.title

    def test_subscribed_sources_subscribe_to_sources(self):
        driver = login("http://127.0.0.1:8000/feed/")
        slider_wrapper = driver.find_elements(By.CSS_SELECTOR, '.sliderWrapper')[2]
        while slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .interactionWrapper').is_displayed() == False:
            slider_wrapper.find_element(By.CSS_SELECTOR, '.rightHandle').click()
            sleep(1)
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .interactionWrapper .addSourcesButton').click()
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .addSourcesForm #textInput').send_keys("Test")
        sleep(1)
        source_name = slider_wrapper.find_elements(By.CSS_SELECTOR, '.slider .addSourcesForm #searchResultsContainer .searchResult span')[0].get_attribute("innerText")
        slider_wrapper.find_elements(By.CSS_SELECTOR, '.slider .addSourcesForm #searchResultsContainer .searchResult')[0].click()
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .addSourcesForm #textInput').send_keys("Test")
        sleep(1)
        slider_wrapper.find_elements(By.CSS_SELECTOR, '.slider .addSourcesForm #searchResultsContainer .searchResult')[0].click()
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .addSourcesForm #textInput').send_keys("Test")
        sleep(1)
        slider_wrapper.find_elements(By.CSS_SELECTOR, '.slider .addSourcesForm #searchResultsContainer .searchResult')[0].click()
        slider_wrapper.find_elements(By.CSS_SELECTOR, '.slider .addSourcesForm .selectionContainer .searchResult .fa-trash')[2].click()
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .addSourcesForm .formSubmitButton').click()
        sleep(1)   
        driver.refresh()
        slider_wrapper = driver.find_elements(By.CSS_SELECTOR, '.sliderWrapper')[2]
        while slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .interactionWrapper').is_displayed() == False:
            slider_wrapper.find_element(By.CSS_SELECTOR, '.rightHandle').click()
            sleep(1)
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .interactionWrapper .addSourcesButton').click()
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .addSourcesForm #textInput').send_keys("Test")
        sleep(1)
        assert source_name != slider_wrapper.find_elements(By.CSS_SELECTOR, '.slider .addSourcesForm #searchResultsContainer .searchResult span')[0].get_attribute("innerText")     

    def test_subscribed_sources_open_source(self):
        driver = login("http://127.0.0.1:8000/feed/")
        slider_wrapper = driver.find_elements(By.CSS_SELECTOR, '.sliderWrapper')[2]
        slider_wrapper.find_elements(By.CSS_SELECTOR, '.sliderWrapper .slider .contentWrapper')[0].click()
        sleep(1)
        assert "Profile | FinBrowser" in driver.title      

    def test_paginations(self):
        test_pagination("http://127.0.0.1:8000/feed/", 0, '?subscribed_content=2')
        test_pagination("http://127.0.0.1:8000/feed/", 1, '?highlighted_content=2')
        test_pagination("http://127.0.0.1:8000/feed/", 2, '?newest_tweets=2')


class ListTest(LiveServerTestCase):

    def test_list_filtering(self):
        driver = login("http://127.0.0.1:8000/lists/")
        driver.find_element(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #timeframe').click()
        driver.find_elements(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #timeframe option')[-1].click()
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #content').click()
        driver.find_elements(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #content option')[-1].click()
        sleep(1)
        action = webdriver.ActionChains(driver)
        action.move_to_element(driver.find_element(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #minimum_rating')).click().perform()
        driver.find_elements(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #minimum_rating option')[-1].click()
        sleep(1)
        action.move_to_element(driver.find_element(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #primary_source')).click().perform()
        driver.find_elements(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #primary_source option')[4].click()
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, '.searchButton').click()
        sleep(1)
        assert str(driver.current_url) == "http://127.0.0.1:8000/lists/365/Sources/2/Twitter/"

    def test_double_list_filtering(self):
        driver = login("http://127.0.0.1:8000/lists/")
        driver.find_element(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #timeframe').click()
        driver.find_elements(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #timeframe option')[-1].click()
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #content').click()
        driver.find_elements(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #content option')[-1].click()
        sleep(1)
        action = webdriver.ActionChains(driver)
        action.move_to_element(driver.find_element(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #minimum_rating')).click().perform()
        driver.find_elements(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #minimum_rating option')[-1].click()
        sleep(1)
        action.move_to_element(driver.find_element(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #primary_source')).click().perform()
        driver.find_elements(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #primary_source option')[4].click()
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, '.searchButton').click()
        sleep(1)
        assert str(driver.current_url) == "http://127.0.0.1:8000/lists/365/Sources/2/Twitter/"
        driver.find_element(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #timeframe').click()
        driver.find_elements(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #timeframe option')[3].click()
        sleep(1)
        action.move_to_element(driver.find_element(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #primary_source')).click().perform()
        driver.find_elements(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #primary_source option')[3].click()
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, '.searchButton').click()
        sleep(1)
        assert str(driver.current_url) == "http://127.0.0.1:8000/lists/90/Sources/2/Substack/"

    def test_list_search(self):
        driver = login("http://127.0.0.1:8000/lists/")
        driver.find_element(By.CSS_SELECTOR, '.searchContainer #search').send_keys("test")
        sleep(1)
        driver.find_elements(By.CSS_SELECTOR, '#autocomplete_list_results .searchResult a')[4].click()
        sleep(1)
        assert "List | FinBrowser" in driver.title

    def test_create_list(self):
        driver = login("http://127.0.0.1:8000/lists/")
        driver.find_element(By.CSS_SELECTOR, '.createListButton').click()
        sleep(1)
        form = driver.find_element(By.CSS_SELECTOR, '.searchResultsAndListCreationContainer .createListMenu')
        form.find_element(By.CSS_SELECTOR, '#id_name').send_keys('TestList1107-1234567')
        form.find_element(By.CSS_SELECTOR, '#id_is_public').click()
        sleep(1)
        form.find_element(By.CSS_SELECTOR, '.formSubmitButton').click()
        sleep(1)
        assert "TestList1107-1234567" in driver.title or "YOU HAVE ALREADY CREATED A LIST WITH THAT NAME!" in driver.find_element(By.CSS_SELECTOR, ".messages .error").get_attribute('innerText')

    def test_open_list(self):
        driver = login("http://127.0.0.1:8000/lists/")
        driver.find_elements(By.CSS_SELECTOR, '.listResultUpperCont a')[0].click()
        sleep(1)
        assert "List | FinBrowser" in driver.title

    def test_paginations(self):
        test_pagination("http://127.0.0.1:8000/lists/", 0, '?page=2')

    
class SectorTest(LiveServerTestCase):
    
    def test_open_sector(self):
        driver = login("http://127.0.0.1:8000/sectors/")
        driver.find_elements(By.CSS_SELECTOR, '.sliderWrapper .sliderHeader a')[0].click()
        sleep(1)
        assert "Sector | FinBrowser" in driver.title

    def test_open_source(self):
        driver = login("http://127.0.0.1:8000/sectors/")
        driver.find_elements(By.CSS_SELECTOR, '.slider .contentContainer a')[0].click()
        sleep(1)
        assert "Profile | FinBrowser" in driver.title


class ContentTest(LiveServerTestCase):

    def test_content_standard_use_cases(self):
        test_standard_use_cases("http://127.0.0.1:8000/content/")
        test_standard_use_cases("http://127.0.0.1:8000/content/", True)

    def test_content_filtering(self):
        driver = login("http://127.0.0.1:8000/content/")
        driver.find_element(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #timeframe').click()
        driver.find_elements(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #timeframe option')[-1].click()
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #sector').click()
        driver.find_elements(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #sector option')[1].click()
        sleep(1)
        action = webdriver.ActionChains(driver)
        action.move_to_element(driver.find_element(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #paywall')).click().perform()
        driver.find_elements(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #paywall option')[-1].click()
        sleep(1)
        action.move_to_element(driver.find_element(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #source')).click().perform()
        driver.find_elements(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #source option')[4].click()
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, '.searchButton').click()
        sleep(1)
        assert str(driver.current_url) == "http://127.0.0.1:8000/content/365/Defense/No/Twitter/"

    def test_double_content_filtering(self):
        driver = login("http://127.0.0.1:8000/content/")
        driver.find_element(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #timeframe').click()
        driver.find_elements(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #timeframe option')[-1].click()
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #sector').click()
        driver.find_elements(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #sector option')[1].click()
        sleep(1)
        action = webdriver.ActionChains(driver)
        action.move_to_element(driver.find_element(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #paywall')).click().perform()
        driver.find_elements(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #paywall option')[-1].click()
        sleep(1)
        action.move_to_element(driver.find_element(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #source')).click().perform()
        driver.find_elements(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #source option')[4].click()
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, '.searchButton').click()
        sleep(1)
        assert str(driver.current_url) == "http://127.0.0.1:8000/content/365/Defense/No/Twitter/"
        driver.find_element(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #timeframe').click()
        driver.find_elements(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #timeframe option')[3].click()
        sleep(1)
        action.move_to_element(driver.find_element(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #source')).click().perform()
        driver.find_elements(By.CSS_SELECTOR, '.filterBarMenu .selectContainer #source option')[3].click()
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, '.searchButton').click()
        sleep(1)
        assert str(driver.current_url) == "http://127.0.0.1:8000/content/90/Defense/No/Substack/"

    def test_content_search(self):
        driver = login("http://127.0.0.1:8000/content/")
        driver.find_element(By.CSS_SELECTOR, '.searchContainer #search').send_keys("test")
        sleep(1)
        assert len(driver.find_elements(By.CSS_SELECTOR, '#autocomplete_list_results .searchResult a')) == 10

    def test_paginations(self):
        test_pagination("http://127.0.0.1:8000/content/", 0, '?articles=2')
        test_pagination("http://127.0.0.1:8000/content/", 1, '?tweets=2')


class SearchResultTest(LiveServerTestCase):
    
    def test_standard_use_cases(self):
        test_standard_use_cases("http://127.0.0.1:8000/search_results/f")

    def test_pagination(self):
        driver = login("http://127.0.0.1:8000/search_results/f")
        pagination = driver.find_elements(By.CSS_SELECTOR, '.pagination .step-links')[0]
        pagination.find_elements(By.CSS_SELECTOR, 'a')[0].click()
        assert str(driver.current_url).endswith('=2')

    def test_open_list_from_list_tab(self):
        driver = login("http://127.0.0.1:8000/search_results/f")
        driver.find_elements(By.CSS_SELECTOR, '.searchCategories .searchCategoryTab')[1].click()
        slider = driver.find_elements(By.CSS_SELECTOR, '.slider')[0]
        slider.find_elements(By.CSS_SELECTOR, '.contentContainer')[0].click()
        sleep(1)
        assert "List | FinBrowser" in driver.title

    def test_open_source_from_source_tab(self):
        driver = login("http://127.0.0.1:8000/search_results/f")
        driver.find_elements(By.CSS_SELECTOR, '.searchCategories .searchCategoryTab')[2].click()
        slider = driver.find_elements(By.CSS_SELECTOR, '.slider')[1]
        slider.find_elements(By.CSS_SELECTOR, '.contentContainer')[0].click()
        sleep(1)
        assert "Profile | FinBrowser" in driver.title

    def test_open_list_from_search(self):
        driver = login("http://127.0.0.1:8000/search_results/f")
        search_bar = driver.find_elements(By.CSS_SELECTOR, '.mainSearchWrapper .mainSearchContainer .mainInputSearch')[1]
        search_bar.clear()
        search_bar.send_keys('f')
        sleep(2)
        driver.find_elements(By.CSS_SELECTOR, '#autocomplete_list_results .searchResult a')[0].click()
        sleep(1)
        assert 'List | FinBrowser' in driver.title

    def test_open_source_from_search(self):
        driver = login("http://127.0.0.1:8000/search_results/f")
        search_bar = driver.find_elements(By.CSS_SELECTOR, '.mainSearchWrapper .mainSearchContainer .mainInputSearch')[1]
        search_bar.clear()
        search_bar.send_keys('f')
        sleep(2)
        driver.find_elements(By.CSS_SELECTOR, '#autocomplete_list_results .searchResult a')[4].click()
        sleep(1)
        assert 'Profile | FinBrowser' in driver.title

    def test_search_button(self):
        driver = login("http://127.0.0.1:8000/search_results/f")
        search_bar = driver.find_elements(By.CSS_SELECTOR, '.mainSearchWrapper .mainSearchContainer .mainInputSearch')[1]
        search_bar.clear()
        search_bar.send_keys('this is a test')  
        driver.find_elements(By.CSS_SELECTOR, '.mainSearchWrapper .mainSearchContainer .fa-search')[1].click()
        sleep(1)
        assert 'this is a test' in driver.title      

    def test_paginations(self):
        test_pagination("http://127.0.0.1:8000/search_results/f", 0, '?filtered_articles=2')
        test_pagination("http://127.0.0.1:8000/search_results/f", 1, '?filtered_tweets=2')

class SettingsTest(LiveServerTestCase):
    
    def test_change_username(self):
        driver = login("http://127.0.0.1:8000/profile/settings")
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, '#id_username').clear()
        driver.find_element(By.CSS_SELECTOR, '#id_username').send_keys("Ebirdmax99Test")
        driver.find_element(By.CSS_SELECTOR, '.editSection .saveButton').click()
        assert "Ebirdmax99Test" == driver.find_element(By.CSS_SELECTOR, "#id_username").get_attribute('value')

    def test_change_email(self):
        driver = login("http://127.0.0.1:8000/profile/settings")
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, '#id_email').clear()
        driver.find_element(By.CSS_SELECTOR, '#id_email').send_keys("me-99@livetest.de")
        driver.find_element(By.CSS_SELECTOR, '.editSection .saveButton').click()
        assert "me-99@livetest.de" == driver.find_element(By.CSS_SELECTOR, "#id_email").get_attribute('value')

    def test_change_username_and_email(self):
        driver = webdriver.Chrome()
        driver.get("http://127.0.0.1:8000/registration/login/")
        driver.set_window_size(1920, 1080)
        driver.find_element(By.CSS_SELECTOR, '#id_login').send_keys('me-99@livetest.de')
        driver.find_element(By.CSS_SELECTOR, '#id_password').send_keys('testpw99')
        driver.find_element(By.CSS_SELECTOR, '#id_remember').click()
        driver.find_element(By.CSS_SELECTOR, '.primaryAction').click()
        driver.get("http://127.0.0.1:8000/profile/settings")
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, '#id_username').clear()
        driver.find_element(By.CSS_SELECTOR, '#id_username').send_keys("Ebirdmax99")
        driver.find_element(By.CSS_SELECTOR, '#id_email').clear()
        driver.find_element(By.CSS_SELECTOR, '#id_email').send_keys("me-99@live.de")
        driver.find_element(By.CSS_SELECTOR, '.editSection .saveButton').click()
        assert "Ebirdmax99" == driver.find_element(By.CSS_SELECTOR, "#id_username").get_attribute('value') and "me-99@live.de" == driver.find_element(By.CSS_SELECTOR, "#id_email").get_attribute('value')

    def test_add_social_link(self):
        driver = login("http://127.0.0.1:8000/profile/settings")
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, '.addSocialLinksContainer summary').click()        
        driver.find_elements(By.CSS_SELECTOR, '.addSocialLinksContainer .selectContainer ul li')[0].click() 
        driver.find_element(By.CSS_SELECTOR, '.addSocialLinksContainer input').send_keys("https://www.testlink.com")  
        sleep(1) 
        driver.find_element(By.CSS_SELECTOR, '.socialLinksWrapper .addSocialLinkButton').click() 
        sleep(1)
        assert "https://www.testlink.com" == driver.find_elements(By.CSS_SELECTOR, ".existingSocialContainer input")[-1].get_attribute('value')

    def test_change_social_link(self):
        driver = login("http://127.0.0.1:8000/profile/settings")
        sleep(1)
        driver.find_elements(By.CSS_SELECTOR, ".existingSocialContainer input")[-1].clear()
        driver.find_elements(By.CSS_SELECTOR, ".existingSocialContainer input")[-1].send_keys("https://www.newtestlink.com")
        driver.find_elements(By.CSS_SELECTOR, ".existingSocialContainer .saveSocialLinkChanges")[-1].click()
        sleep(1)
        assert "https://www.newtestlink.com" == driver.find_elements(By.CSS_SELECTOR, ".existingSocialContainer input")[-1].get_attribute('value')

    def test_delete_social_link(self):
        driver = login("http://127.0.0.1:8000/profile/settings")
        sleep(1)
        driver.find_elements(By.CSS_SELECTOR, ".existingSocialContainer .removeSocialLinkButton")[-1].click()
        sleep(1)
        assert len(driver.find_elements(By.CSS_SELECTOR, ".existingSocialContainer")) == 1

    def test_change_password(self):
        driver = login("http://127.0.0.1:8000/profile/settings")
        sleep(1)   
        driver.find_elements(By.CSS_SELECTOR, ".settingSidebar .settingOption")[1].click()     
        driver.find_element(By.CSS_SELECTOR, '#id_old_password').send_keys('testpw99')
        driver.find_element(By.CSS_SELECTOR, '#id_new_password1').send_keys('testpw1999')
        driver.find_element(By.CSS_SELECTOR, '#id_new_password2').send_keys('testpw1999')
        driver.find_element(By.CSS_SELECTOR, '.changePasswordForm .passwordChangeSubmit').click()
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, '.headerContainer .userProfile .fa-sort-down').click()
        driver.find_element(By.CSS_SELECTOR, '.headerContainer .profileWrapper .profileMenu form button').click()
        sleep(1)
        driver = webdriver.Chrome()
        driver.get("http://127.0.0.1:8000/registration/login/")
        driver.set_window_size(1920, 1080)
        driver.find_element(By.CSS_SELECTOR, '#id_login').send_keys('me-99@live.de')
        driver.find_element(By.CSS_SELECTOR, '#id_password').send_keys('testpw1999')
        driver.find_element(By.CSS_SELECTOR, '#id_remember').click()
        driver.find_element(By.CSS_SELECTOR, '.primaryAction').click()
        sleep(1)
        driver.get("http://127.0.0.1:8000/profile/settings")
        driver.find_elements(By.CSS_SELECTOR, ".settingSidebar .settingOption")[1].click() 
        driver.find_element(By.CSS_SELECTOR, '#id_old_password').send_keys('testpw1999')
        driver.find_element(By.CSS_SELECTOR, '#id_new_password1').send_keys('testpw99')
        driver.find_element(By.CSS_SELECTOR, '#id_new_password2').send_keys('testpw99')
        driver.find_element(By.CSS_SELECTOR, '.changePasswordForm .passwordChangeSubmit').click()

    def test_delete_source_notifications(self):
        driver = login("http://127.0.0.1:8000/profile/settings")
        sleep(1) 
        driver.find_elements(By.CSS_SELECTOR, ".settingSidebar .settingOption")[2].click()     
        sleep(1)
        source_notifications = driver.find_elements(By.CSS_SELECTOR, ".tabsContentActive .notificationContainer")[0]
        initial_amount_notifications = len(driver.find_elements(By.CSS_SELECTOR, ".notificationContainer .sourceContainer"))
        source_notifications.find_elements(By.CSS_SELECTOR, ".sourceContainer .iconContainer .fa-trash")[0].click()
        sleep(1)
        assert initial_amount_notifications > len(driver.find_elements(By.CSS_SELECTOR, ".notificationContainer .sourceContainer"))

    def test_delete_list_notifications(self):
        driver = login("http://127.0.0.1:8000/profile/settings")
        sleep(1) 
        driver.find_elements(By.CSS_SELECTOR, ".settingSidebar .settingOption")[2].click()     
        sleep(1)
        list_notifications = driver.find_elements(By.CSS_SELECTOR, ".tabsContentActive .notificationContainer")[1]
        initial_amount_notifications = len(driver.find_elements(By.CSS_SELECTOR, ".notificationContainer .sourceContainer"))
        list_notifications.find_elements(By.CSS_SELECTOR, ".sourceContainer .iconContainer .fa-trash")[0].click()
        sleep(1)
        assert initial_amount_notifications > len(driver.find_elements(By.CSS_SELECTOR, ".notificationContainer .sourceContainer"))    

    def test_change_privacy_settings(self):
        driver = login("http://127.0.0.1:8000/profile/settings")
        sleep(1)
        driver.find_elements(By.CSS_SELECTOR, ".settingSidebar .settingOption")[3].click()     
        sleep(1) 
        driver.find_element(By.CSS_SELECTOR, ".privacySettingsContainer #id_list_subscribtions_public").click()  
        driver.find_element(By.CSS_SELECTOR, ".changePrivacySettingsForm .privacySettingsChangeSubmit").click() 
        sleep(1)
        assert driver.find_element(By.CSS_SELECTOR, ".privacySettingsContainer #id_list_subscribtions_public").get_attribute('checked') == None
        assert driver.find_element(By.CSS_SELECTOR, ".privacySettingsContainer #id_subscribed_sources_public").get_attribute('checked') == "true"
        assert "PRIVACY SETTINGS HAVE BEEN UPDATED!" in driver.find_element(By.CSS_SELECTOR, ".messages .success").get_attribute('innerText')
        driver.find_elements(By.CSS_SELECTOR, ".settingSidebar .settingOption")[3].click() 
        driver.find_element(By.CSS_SELECTOR, ".privacySettingsContainer #id_list_subscribtions_public").click()  
        driver.find_element(By.CSS_SELECTOR, ".changePrivacySettingsForm .privacySettingsChangeSubmit").click() 


class SourceProfileTest(LiveServerTestCase):
    
    def test_change_notification_status(self):
        driver = login("http://127.0.0.1:8000/source/walter-bloomberg")
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, ".notificationAndSubscribtionContainer .fa-bell").click()  
        sleep(1)
        assert "NOTIFICATION HAS BEEN ADDED!" in driver.find_element(By.CSS_SELECTOR, ".messages li").get_attribute('innerText') or "NOTIFICATION HAS BEEN REMOVED!" in driver.find_element(By.CSS_SELECTOR, ".messages li").get_attribute('innerText')

    def test_add_source_to_list(self):
        driver = login("http://127.0.0.1:8000/source/walter-bloomberg")
        sleep(1)     
        driver.find_element(By.CSS_SELECTOR, ".notificationAndSubscribtionContainer .addSourceToListButton").click()     
        driver.find_elements(By.CSS_SELECTOR, ".addSourceToListForm .listSelectionContainer .listContainer label input")[0].click() 
        driver.find_elements(By.CSS_SELECTOR, ".addSourceToListForm .saveButton")[0].click() 

    def test_change_subscription_status(self):
        driver = login("http://127.0.0.1:8000/source/walter-bloomberg")
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, ".notificationAndSubscribtionContainer .subscribeButton").click()  
        sleep(1)
        assert "SOURCE HAS BEEN SUBSCRIBED!" in driver.find_element(By.CSS_SELECTOR, ".messages li").get_attribute('innerText') or "SOURCE HAS BEEN UNSUBSCRIBED!" in driver.find_element(By.CSS_SELECTOR, ".messages li").get_attribute('innerText')        

    def test_rate_source(self):
        driver = login("http://127.0.0.1:8000/source/walter-bloomberg")
        sleep(1)
        rating = randrange(3)
        driver.find_element(By.CSS_SELECTOR, ".ratingsWrapper .openRateListButton").click()    
        driver.find_elements(By.CSS_SELECTOR, ".rate-formUpperContainer .rate-form .rankingStar")[rating].click() 
        sleep(1)   
        assert "checked" in driver.find_elements(By.CSS_SELECTOR, ".ratedContainer .ratedStar")[rating].get_attribute('class').split()

    def test_open_list_from_included_in_list(self):
        driver = login("http://127.0.0.1:8000/source/walter-bloomberg")
        sleep(1) 
        driver.find_elements(By.CSS_SELECTOR, ".slider .contentContainer a")[0].click()  
        sleep(1)
        assert "List | FinBrowser" in driver.title      

    def test_standard_use_cases_tweet_container(self):
        test_add_to_list("http://127.0.0.1:8000/source/walter-bloomberg")
        test_highlight_content("http://127.0.0.1:8000/source/walter-bloomberg")
        test_create_list("http://127.0.0.1:8000/source/walter-bloomberg")
        test_open_source_profile("http://127.0.0.1:8000/source/walter-bloomberg")
        test_add_to_list("http://127.0.0.1:8000/source/walter-bloomberg", True)
        test_highlight_content("http://127.0.0.1:8000/source/walter-bloomberg", True)
        test_create_list("http://127.0.0.1:8000/source/walter-bloomberg", True)
        test_open_source_profile("http://127.0.0.1:8000/source/walter-bloomberg", True)

    def test_paginations(self):
        test_pagination("http://127.0.0.1:8000/source/walter-bloomberg", 0, '?latest_articles=2')
        test_pagination("http://127.0.0.1:8000/source/joe-albano", 0, '?latest_articles=2')


class SectorTest(LiveServerTestCase):

    def test_standard_use_cases(self):
        test_standard_use_cases("http://127.0.0.1:8000/sector/defense")
        test_standard_use_cases("http://127.0.0.1:8000/sector/defense", True)

    def test_paginations(self):
        test_pagination("http://127.0.0.1:8000/sector/defense", 0, '?articles_from_sector=2')
        test_pagination("http://127.0.0.1:8000/sector/defense", 1, '?tweets_from_sector=2')


class UserProfileTest(LiveServerTestCase):
    
    def test_highlighed_articles_container(self):
        test_add_to_list("http://127.0.0.1:8000/profile/ebirdmax99")
        test_highlight_content("http://127.0.0.1:8000/profile/ebirdmax99")
        test_create_list("http://127.0.0.1:8000/profile/ebirdmax99")
        test_open_source_profile("http://127.0.0.1:8000/profile/ebirdmax99")
        test_add_to_list("http://127.0.0.1:8000/profile/ebirdmax99", True)
        test_highlight_content("http://127.0.0.1:8000/profile/ebirdmax99", True)
        test_create_list("http://127.0.0.1:8000/profile/ebirdmax99", True)
        test_open_source_profile("http://127.0.0.1:8000/profile/ebirdmax99", True)

    def test_paginations(self):
        test_pagination("http://127.0.0.1:8000/profile/ebirdmax99", 0, '?page=2')


class ListDetailTest(LiveServerTestCase):

    def test_standard_use_cases(self):
        test_standard_use_cases("http://127.0.0.1:8000/list/ebirdmax99/test0207-2")
        test_standard_use_cases("http://127.0.0.1:8000/list/ebirdmax99/test0207-2", True)

    def test_change_notification_status(self):
        driver = login("http://127.0.0.1:8000/list/ebirdmax99/test0207-2")
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, ".notificationAndSubscribtionContainer .fa-bell").click()  
        sleep(1)
        assert "NOTIFICATION HAS BEEN ADDED!" in driver.find_element(By.CSS_SELECTOR, ".messages li").get_attribute('innerText') or "NOTIFICATION HAS BEEN REMOVED!" in driver.find_element(By.CSS_SELECTOR, ".messages li").get_attribute('innerText')

    def test_paginations(self):
        test_pagination("http://127.0.0.1:8000/list/ebirdmax99/test0207-2", 0, '?latest_articles=2')
        test_pagination("http://127.0.0.1:8000/list/ebirdmax99/test0207-2", 1, '?highlighted_content=2')
        test_pagination("http://127.0.0.1:8000/list/ebirdmax99/test0207-2", 2, '?newest_tweets=2')

    def test_change_list_name(self):
        driver = login("http://127.0.0.1:8000/list/ebirdmax99/test0207-2")
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, ".editButton").click()  
        driver.find_element(By.CSS_SELECTOR, ".nameChangeContainer #id_name").clear()
        driver.find_element(By.CSS_SELECTOR, ".nameChangeContainer #id_name").send_keys("test0207-new")
        driver.find_element(By.CSS_SELECTOR, ".notificationAndSubscribtionContainer .buttonContainer input").click()
        assert str(driver.find_element(By.CSS_SELECTOR, "h3").get_attribute('innerText')) == "test0207-new"
        driver.find_element(By.CSS_SELECTOR, ".editButton").click()
        driver.find_element(By.CSS_SELECTOR, ".nameChangeContainer #id_name").clear()
        driver.find_element(By.CSS_SELECTOR, ".nameChangeContainer #id_name").send_keys("Test0207-2")
        driver.find_element(By.CSS_SELECTOR, ".notificationAndSubscribtionContainer .buttonContainer input").click()
    
    def test_rate_list(self):
        driver = login("http://127.0.0.1:8000/list/abcmailcom/favorite-twitter-accounts")
        sleep(1)
        rating = randrange(3)
        driver.find_element(By.CSS_SELECTOR, ".ratingsWrapper .rateListButton").click()    
        driver.find_elements(By.CSS_SELECTOR, ".rate-formUpperContainer .rate-form .rankingStar")[rating].click() 
        sleep(1)   
        assert "checked" in driver.find_elements(By.CSS_SELECTOR, ".ratedContainer .ratedStar")[rating].get_attribute('class').split()

    def test_change_subscription_status(self):
        driver = login("http://127.0.0.1:8000/list/abcmailcom/favorite-twitter-accounts")
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, ".notificationAndSubscribtionContainer .subscribeButton").click()  
        sleep(1)
        assert "LIST SUBSCRIPTION ADDED!" in driver.find_element(By.CSS_SELECTOR, ".messages li").get_attribute('innerText') or "LIST SUBSCRIPTION REMOVED!" in driver.find_element(By.CSS_SELECTOR, ".messages li").get_attribute('innerText') 

    def test_remove_source(self):
        driver = login("http://127.0.0.1:8000/list/ebirdmax99/test0207-2")
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, ".editButton").click() 
        source_container = driver.find_elements(By.CSS_SELECTOR, ".slider .contentContainer")[0]
        initital_first_source_name = source_container.find_element(By.CSS_SELECTOR, ".contentName").get_attribute('innerText')
        source_container.find_element(By.CSS_SELECTOR, ".sourceDeleteOption").click()
        sleep(1)
        driver.refresh()
        sleep(1)
        assert initital_first_source_name != driver.find_elements(By.CSS_SELECTOR, ".slider .contentContainer")[0].find_element(By.CSS_SELECTOR, ".contentName").get_attribute('innerText')

    def test_add_source(self):
        driver = login("http://127.0.0.1:8000/list/ebirdmax99/test0207-2")
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, ".editButton").click() 
        slider_wrapper = driver.find_element(By.CSS_SELECTOR, '.sliderWrapper')
        while slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .interactionWrapper').is_displayed() == False:
            slider_wrapper.find_element(By.CSS_SELECTOR, '.leftHandle').click()
            sleep(1)
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .interactionWrapper .addSourcesButton').click()
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .addSourcesForm #textInput').send_keys("Test")
        sleep(1)
        source_name = slider_wrapper.find_elements(By.CSS_SELECTOR, '.slider .addSourcesForm #searchResultsContainer .searchResult span')[0].get_attribute("innerText")
        slider_wrapper.find_elements(By.CSS_SELECTOR, '.slider .addSourcesForm #searchResultsContainer .searchResult')[0].click()
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .addSourcesForm #textInput').send_keys("Test")
        sleep(1)
        slider_wrapper.find_elements(By.CSS_SELECTOR, '.slider .addSourcesForm #searchResultsContainer .searchResult')[0].click()
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .addSourcesForm #textInput').send_keys("Test")
        sleep(1)
        slider_wrapper.find_elements(By.CSS_SELECTOR, '.slider .addSourcesForm #searchResultsContainer .searchResult')[0].click()
        slider_wrapper.find_elements(By.CSS_SELECTOR, '.slider .addSourcesForm .selectionContainer .searchResult .fa-trash')[2].click()
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .addSourcesForm .formSubmitButton').click()
        sleep(1)        
        driver.refresh()
        driver.find_element(By.CSS_SELECTOR, ".editButton").click() 
        slider_wrapper = driver.find_element(By.CSS_SELECTOR, '.sliderWrapper')
        while slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .interactionWrapper').is_displayed() == False:
            slider_wrapper.find_element(By.CSS_SELECTOR, '.leftHandle').click()
            sleep(1)
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .interactionWrapper .addSourcesButton').click()
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .addSourcesForm #textInput').send_keys("Test")
        sleep(1)
        assert source_name != slider_wrapper.find_elements(By.CSS_SELECTOR, '.slider .addSourcesForm #searchResultsContainer .searchResult span')[0].get_attribute("innerText")