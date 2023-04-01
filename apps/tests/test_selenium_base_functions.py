# Python imports
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By


class UrlHasChanged:
    def __init__(self, old_url):
        self.old_url = old_url

    def __call__(self, driver):
        return driver.current_url != self.old_url


def login(next_page=False, smartphone=False):
    driver = webdriver.Chrome()
    driver.get("http://127.0.0.1:8000/registration/login/")
    if smartphone:
        driver.set_window_size(375, 667)
    else:
        driver.set_window_size(1920, 1080)
    driver.find_element(By.CSS_SELECTOR, "#id_login").send_keys("me-99@live.de")
    driver.find_element(By.CSS_SELECTOR, "#id_password").send_keys("testpw99")
    driver.find_element(By.CSS_SELECTOR, "#id_remember").click()
    driver.find_element(By.CSS_SELECTOR, ".primaryAction").click()
    assert driver.title == "FinBrowser | Feed"
    if next_page:
        driver.get(next_page)
    return driver


def test_add_to_list(next_page=False, smartphone=False):
    driver = login(next_page, smartphone)
    selector = driver.find_elements(
        By.CSS_SELECTOR,
        ".pageWrapper .smallFormContentWrapper .articleContainer",
    )[0]
    selector.find_element(
        By.CSS_SELECTOR,
        ".pageWrapper .smallFormContentWrapper .articleContainer .fa-ellipsis-h",
    ).click()
    WebDriverWait(driver, 3).until(
        expected_conditions.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                ".pageWrapper .smallFormContentWrapper .articleOptionsContainer .addToListButton",
            )
        )
    ).click()
    WebDriverWait(driver, 3).until(
        expected_conditions.element_to_be_clickable(
            (By.CSS_SELECTOR, ".fullScreenPlaceholder .addToListForm")
        )
    )
    driver.find_elements(
        By.CSS_SELECTOR,
        ".fullScreenPlaceholder .addToListForm .listSelectionContainer .listContainer",
    )[0].click()
    driver.find_element(
        By.CSS_SELECTOR, ".fullScreenPlaceholder .addToListForm .saveButton"
    ).click()
    WebDriverWait(driver, 1).until(
        expected_conditions.invisibility_of_element_located(
            (By.CSS_SELECTOR, ".fullScreenPlaceholder .addToListForm")
        )
    )


def test_highlight_content(next_page=False, smartphone=False):
    driver = login(next_page, smartphone)
    selector = driver.find_elements(
        By.CSS_SELECTOR,
        ".pageWrapper .smallFormContentWrapper .articleContainer",
    )[0]
    selector.find_element(
        By.CSS_SELECTOR,
        ".pageWrapper .smallFormContentWrapper .articleContainer .fa-ellipsis-h",
    ).click()
    WebDriverWait(driver, 3).until(
        expected_conditions.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                ".pageWrapper .smallFormContentWrapper .articleOptionsContainer .addToHighlightedButton",
            )
        )
    ).click()
    WebDriverWait(driver, 1).until(
        expected_conditions.invisibility_of_element_located(
            (
                By.CSS_SELECTOR,
                ".pageWrapper .smallFormContentWrapper .articleOptionsContainer",
            )
        )
    )


def test_open_source_profile(next_page=False, smartphone=False):
    driver = login(next_page, smartphone)
    driver.find_elements(
        By.CSS_SELECTOR,
        ".pageWrapper .smallFormContentWrapper .articleContainer .rightContentSide .contentInfoContainer .sourceAndWebsiteContainer .sourceProfile",
    )[0].click()
    assert driver.current_url.startswith("http://127.0.0.1:8000/source/")


# def test_open_article(next_page=False, smartphone=False):
#     driver = login(next_page, smartphone)
#     driver.find_elements(
#         By.CSS_SELECTOR,
#         ".pageWrapper .smallFormContentWrapper .articleContainer .contentLink",
#     )[0].click()
#     driver.switch_to.window(driver.window_handles[1])
#     assert "FinBrowser" not in driver.title

# def test_source_subscription(next_page=False, smartphone=False):
#     driver = login(next_page, smartphone)
#     driver.find_elements(".slider .contentWrapper")


def test_standard_use_cases(next_page=False, smartphone=False):
    test_add_to_list(next_page, smartphone)
    test_highlight_content(next_page, smartphone)
    test_open_source_profile(next_page, smartphone)
    # test_open_article(next_page, smartphone)
