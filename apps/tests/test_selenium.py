# Django imports
from django.test import LiveServerTestCase
# Python imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from random import randrange

def login(next_page=False):
    driver = webdriver.Chrome()
    driver.get("http://127.0.0.1:8000/registration/login/")
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
    sleep(1)
    selector.find_element(By.CSS_SELECTOR, '.addToListButton').click()
    sleep(1)
    selector.find_elements(By.CSS_SELECTOR, '.addToListForm .listSelectionContainer .listContainer label input')[0].click()
    sleep(1)
    selector.find_element(By.CSS_SELECTOR, '.addToListForm .saveButton').click()   
    sleep(1)
    assert "LISTS HAVE BEEN UPDATED!" in driver.find_element(By.CSS_SELECTOR, ".messages .success").get_attribute('innerText')

def highlight_article(selector, driver):
    selector.find_element(By.CSS_SELECTOR, '.fa-ellipsis-h').click()
    sleep(1)
    selector.find_element(By.CSS_SELECTOR, '.addToHighlightedButton').click()
    sleep(1)
    assert "ARTICLE HAS BEEN HIGHLIGHTED!" in driver.find_element(By.CSS_SELECTOR, ".messages .success").get_attribute('innerText')  or "ARTICLE HAS BEEN UNHIGHLIGHTED!" in driver.find_element(By.CSS_SELECTOR, ".messages .success").get_attribute('innerText')

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

################################################################################################################################

def test_open_sector(next_page):
    driver = login(next_page)
    driver.find_elements(By.CSS_SELECTOR, '.articlesWrapper .articleContainer .articleSectorAndDateContainer a')[5].click()
    sleep(1)
    assert "Sector | FinBrowser" in driver.title   

def test_add_to_list_with_article_container(next_page):
    driver = login(next_page)
    selector = driver.find_elements(By.CSS_SELECTOR, '.articlesWrapper .articleContainer')[5]
    add_to_list(selector, driver)  

def test_highlight_article_with_article_container(next_page):
    driver = login(next_page)
    selector = driver.find_elements(By.CSS_SELECTOR, '.articlesWrapper .articleContainer')[5]
    highlight_article(selector, driver)

def test_create_list_with_article_container(next_page):
    driver = login(next_page) 
    selector = driver.find_elements(By.CSS_SELECTOR, '.articlesWrapper .articleContainer')[5]   
    create_list(selector, driver)

def test_add_to_list_with_tweet_container(next_page):
    driver = login(next_page)   
    selector = driver.find_elements(By.CSS_SELECTOR, '.twitterWrapper .smallFormContentWrapper .articleContainer')[5]
    add_to_list(selector, driver)    

def test_highlight_article_with_tweet_container(next_page):
    driver = login(next_page)
    selector = driver.find_elements(By.CSS_SELECTOR, '.twitterWrapper .smallFormContentWrapper .articleContainer')[5]
    highlight_article(selector, driver)

def test_create_list_with_tweet_container(next_page):
    driver = login(next_page) 
    selector = driver.find_elements(By.CSS_SELECTOR, '.twitterWrapper .smallFormContentWrapper .articleContainer')[5] 
    create_list(selector, driver)

def test_open_source_profile_with_article_container(next_page):
    driver = login(next_page)
    driver.find_elements(By.CSS_SELECTOR, '.articlesWrapper .articleContainer .authorImageContainer a')[5].click()
    sleep(1)
    assert "Profile | FinBrowser" in driver.title        

def test_open_source_profile_with_tweet_container(next_page):
    driver = login(next_page)
    driver.find_elements(By.CSS_SELECTOR, '.twitterWrapper .smallFormContentWrapper .articleContainer .rightContentSide .contentInfoContainer .sourceAndWebsiteContainer a')[5].click()
    sleep(1)
    assert "Profile | FinBrowser" in driver.title     

def test_open_source_profile_with_slider(next_page): 
    driver = login(next_page)
    driver.find_elements(By.CSS_SELECTOR, '.sliderWrapper .slider .contentWrapper .contentContainer .contentLink')[0].click()
    sleep(1)
    assert "Profile | FinBrowser" in driver.title  

def test_standard_use_cases(next_page=False):
    test_open_sector(next_page)
    test_add_to_list_with_article_container(next_page)
    test_highlight_article_with_article_container(next_page)
    test_create_list_with_article_container(next_page)
    test_add_to_list_with_tweet_container(next_page)
    test_highlight_article_with_tweet_container(next_page)
    test_create_list_with_tweet_container(next_page)
    test_open_source_profile_with_article_container(next_page)
    test_open_source_profile_with_tweet_container(next_page)

########################################################################################################################################################


class NavigationTest(LiveServerTestCase):
    
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
        sleep(1)
        driver.find_elements(By.CSS_SELECTOR, '.mainNavigationLink a')[1].click()
        sleep(1)
        assert "Lists" in driver.title
        driver.find_elements(By.CSS_SELECTOR, '.mainNavigationLink a')[2].click()
        sleep(1)
        assert "Sectors" in driver.title
        driver.find_elements(By.CSS_SELECTOR, '.mainNavigationLink a')[3].click()
        sleep(1)
        assert "Content" in driver.title
        driver.find_element(By.CSS_SELECTOR, '.userSpace .fa-cog a').click()
        sleep(1)
        assert "Login" in driver.title
        driver.back()
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, '.mainSearchWrapper .mainSearchContainer .mainInputSearch').send_keys('Test123')
        driver.find_element(By.CSS_SELECTOR, '.mainSearchWrapper .mainSearchContainer .fa-search').click()
        sleep(1)
        assert 'Test123' in driver.title


class MainTest(LiveServerTestCase):
    
    def test_main_standard_use_cases(self):
        test_standard_use_cases()
        test_open_source_profile_with_slider(False)


class FeedTest(LiveServerTestCase):
    
    def test_main_standard_use_cases(self):
        test_standard_use_cases("http://127.0.0.1:8000/feed/")

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
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .interactionWrapper .addSourcesButton ').click()
        slider_wrapper.find_element(By.CSS_SELECTOR, '.slider .addSourcesForm #textInput').send_keys("Test")
        sleep(1)
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

    def test_subscribed_sources_open_source(self):
        driver = login("http://127.0.0.1:8000/feed/")
        slider_wrapper = driver.find_elements(By.CSS_SELECTOR, '.sliderWrapper')[2]
        slider_wrapper.find_elements(By.CSS_SELECTOR, '.sliderWrapper .slider .contentWrapper')[0].click()
        sleep(1)
        assert "Profile | FinBrowser" in driver.title      

    def test_pagination_article_container(self):
        driver = login("http://127.0.0.1:8000/feed/")
        pagination = driver.find_elements(By.CSS_SELECTOR, '.pagination .step-links')[0]
        pagination.find_elements(By.CSS_SELECTOR, 'a')[0].click()
        assert str(driver.current_url).endswith('=2')

    def test_pagination_highlighted_article_container(self):
        driver = login("http://127.0.0.1:8000/feed/")
        pagination = driver.find_elements(By.CSS_SELECTOR, '.pagination .step-links')[1]
        pagination.find_elements(By.CSS_SELECTOR, 'a')[0].click()
        assert str(driver.current_url).endswith('=2')

    def test_pagination_tweet_container(self):
        driver = login("http://127.0.0.1:8000/feed/")
        pagination = driver.find_elements(By.CSS_SELECTOR, '.pagination .step-links')[2]
        pagination.find_elements(By.CSS_SELECTOR, 'a')[0].click()
        assert str(driver.current_url).endswith('=2')

    def test_add_external_articles(self):
        driver = login("http://127.0.0.1:8000/feed/")
        driver.find_element(By.CSS_SELECTOR, '.addExternalLinkButton').click()
        driver.find_element(By.CSS_SELECTOR, '.addExternalLinksContainer #id_website_name').send_keys("www.test.com")
        driver.find_element(By.CSS_SELECTOR, '.addExternalLinksContainer #id_title').send_keys("TestTitle")
        driver.find_element(By.CSS_SELECTOR, '.addExternalLinksContainer #id_link').send_keys("https://www.finbrowser.io/")
        driver.find_element(By.CSS_SELECTOR, '.addExternalLinksContainer #id_pub_date').send_keys("04/04/2021")
        driver.find_element(By.CSS_SELECTOR, '.addExternalLinksContainer .formSubmitButton').click()
        sleep(1)
        assert "ARTICLE HAS BEEN ADDED!" in driver.find_element(By.CSS_SELECTOR, ".messages .success").get_attribute('innerText')
    

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

    # def test_list_search(self):
    #     driver = login("http://127.0.0.1:8000/lists/")
    #     driver.find_element(By.CSS_SELECTOR, '.searchContainer #search').send_keys("test")
    #     driver.find_elements(By.CSS_SELECTOR, '#autocomplete_list_results .searchResult a')[4].click()

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

    def test_list_pagination(self):
        driver = login("http://127.0.0.1:8000/lists/")
        pagination = driver.find_element(By.CSS_SELECTOR, '.pagination .step-links')
        pagination.find_elements(By.CSS_SELECTOR, 'a')[0].click()
        assert str(driver.current_url).endswith('=2')

    
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

    # def test_content_search(self):
    #     driver = login("http://127.0.0.1:8000/content/")
    #     driver.find_element(By.CSS_SELECTOR, '.searchContainer #search').send_keys("test")
    #     driver.find_elements(By.CSS_SELECTOR, '#autocomplete_list_results .searchResult a')[4].click()
    #     sleep(1)
    #     assert "Profile | FinBrowser" in driver.title

    def test_articles_pagination(self):
        driver = login("http://127.0.0.1:8000/content/")
        pagination = driver.find_elements(By.CSS_SELECTOR, '.pagination .step-links')[0]
        pagination.find_elements(By.CSS_SELECTOR, 'a')[0].click()
        assert str(driver.current_url).endswith('=2')

    def test_tweets_pagination(self):
        driver = login("http://127.0.0.1:8000/content/")
        pagination = driver.find_elements(By.CSS_SELECTOR, '.pagination .step-links')[1]
        pagination.find_elements(By.CSS_SELECTOR, 'a')[0].click()
        assert str(driver.current_url).endswith('=2')


# class SearchResultTest(LiveServerTestCase):
#     pass
# 1. Open Source in Article
# 2. Open Sector
# 3. Search mit anklicken
# 4. Pagination
# 5. Open Source in Tab
# 6. Open List in Tab

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
        test_add_to_list_with_tweet_container("http://127.0.0.1:8000/source/walter-bloomberg")
        test_highlight_article_with_tweet_container("http://127.0.0.1:8000/source/walter-bloomberg")
        test_create_list_with_tweet_container("http://127.0.0.1:8000/source/walter-bloomberg")
        test_open_source_profile_with_tweet_container("http://127.0.0.1:8000/source/walter-bloomberg")

    def test_tweets_pagination(self):
        driver = login("http://127.0.0.1:8000/source/walter-bloomberg")
        pagination = driver.find_elements(By.CSS_SELECTOR, '.pagination .step-links')[0]
        pagination.find_elements(By.CSS_SELECTOR, 'a')[0].click()
        assert str(driver.current_url).endswith('=2')

    def test_standard_use_cases_article_container(self):
        test_open_sector("http://127.0.0.1:8000/source/joe-albano")
        test_add_to_list_with_article_container("http://127.0.0.1:8000/source/joe-albano")
        test_highlight_article_with_article_container("http://127.0.0.1:8000/source/joe-albano")
        test_create_list_with_article_container("http://127.0.0.1:8000/source/joe-albano")
        test_open_source_profile_with_article_container("http://127.0.0.1:8000/source/joe-albano")

    def test_articles_pagination(self):
        driver = login("http://127.0.0.1:8000/source/joe-albano")
        pagination = driver.find_elements(By.CSS_SELECTOR, '.pagination .step-links')[0]
        pagination.find_elements(By.CSS_SELECTOR, 'a')[0].click()
        assert str(driver.current_url).endswith('=2')


class SectorTest(LiveServerTestCase):

    def test_standard_use_cases(self):
        test_standard_use_cases("http://127.0.0.1:8000/sector/defense")
    
    def test_articles_pagination(self):
        driver = login("http://127.0.0.1:8000/sector/defense")
        pagination = driver.find_elements(By.CSS_SELECTOR, '.pagination .step-links')[0]
        pagination.find_elements(By.CSS_SELECTOR, 'a')[0].click()
        assert str(driver.current_url).endswith('=2')

    def test_tweets_pagination(self):
        driver = login("http://127.0.0.1:8000/sector/defense")
        pagination = driver.find_elements(By.CSS_SELECTOR, '.pagination .step-links')[1]
        pagination.find_elements(By.CSS_SELECTOR, 'a')[0].click()
        assert str(driver.current_url).endswith('=2')


class UserProfileTest(LiveServerTestCase):
    
    def test_highlighed_articles_container(self):
        test_open_sector("http://127.0.0.1:8000/profile/ebirdmax99")
        test_add_to_list_with_article_container("http://127.0.0.1:8000/profile/ebirdmax99")
        test_highlight_article_with_article_container("http://127.0.0.1:8000/profile/ebirdmax99")
        test_create_list_with_article_container("http://127.0.0.1:8000/profile/ebirdmax99")
        test_open_source_profile_with_article_container("http://127.0.0.1:8000/profile/ebirdmax99")


class ListTest(LiveServerTestCase):

    def test_standard_use_cases(self):
        test_standard_use_cases("http://127.0.0.1:8000/list/ebirdmax99/test0207-2")

    def test_change_notification_status(self):
        driver = login("http://127.0.0.1:8000/list/ebirdmax99/test0207-2")
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, ".notificationAndSubscribtionContainer .fa-bell").click()  
        sleep(1)
        assert "NOTIFICATION HAS BEEN ADDED!" in driver.find_element(By.CSS_SELECTOR, ".messages li").get_attribute('innerText') or "NOTIFICATION HAS BEEN REMOVED!" in driver.find_element(By.CSS_SELECTOR, ".messages li").get_attribute('innerText')

    def test_paginations(self):
        driver = login("http://127.0.0.1:8000/list/ebirdmax99/test0207-2")
        pagination = driver.find_elements(By.CSS_SELECTOR, '.pagination .step-links')[0]
        pagination.find_elements(By.CSS_SELECTOR, 'a')[0].click()
        assert str(driver.current_url).endswith('=2')
        pagination = driver.find_elements(By.CSS_SELECTOR, '.pagination .step-links')[1]
        pagination.find_elements(By.CSS_SELECTOR, 'a')[0].click()
        assert str(driver.current_url).endswith('=2')
        pagination = driver.find_elements(By.CSS_SELECTOR, '.pagination .step-links')[2]
        pagination.find_elements(By.CSS_SELECTOR, 'a')[0].click()
        assert str(driver.current_url).endswith('=2')
        pagination = driver.find_elements(By.CSS_SELECTOR, '.pagination .step-links')[3]
        pagination.find_elements(By.CSS_SELECTOR, 'a')[0].click()
        assert str(driver.current_url).endswith('=2')

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
