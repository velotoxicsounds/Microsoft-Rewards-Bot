#! /usr/lib/python3.6
# ms_rewards.py - Searches for results via pc bing browser and mobile, completes quizzes on pc bing browser
# Version 2019.04.03

# TODO replace sleeps with minimum sleeps for explicit waits to work, especially after a page redirect
# FIXME mobile version does not require re-sign in, but pc version does, why?
# FIXME Known Cosmetic Issue - logged point total caps out at the point cost of the item on wishlist
import json
import os
import random
import re
import time
from datetime import datetime, timedelta

import requests
from requests.exceptions import RequestException
from selenium.common.exceptions import WebDriverException, TimeoutException, \
    ElementClickInterceptedException, ElementNotVisibleException, \
    ElementNotInteractableException, NoSuchElementException, UnexpectedAlertPresentException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from tabulate import tabulate

from rewardsbot.driver import Driver
from rewardsbot.logger import RewardsLogger, RewardsSearchHist


class RewardsBot(object):
    # URLs
    LOGIN_URL = "https://login.live.com"
    BING_URL = "https://bing.com"
    DASHBOARD_URL = 'https://account.microsoft.com/rewards/dashboard'
    POINT_TOTAL_URL = 'https://bing.com/rewardsapp/bepflyoutpage?style=chromeextension'

    # user agents for edge/pc and mobile
    PC_USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                     'AppleWebKit/537.36 (KHTML, like Gecko) '
                     'Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134')
    MOBILE_USER_AGENT = ('Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; WebView/3.0) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) coc_coc_browser/64.118.222 '
                         'Chrome/52.0.2743.116 Mobile Safari/537.36 Edge/15.15063')

    # Web Driver Wait times
    WEB_DRIVER_WAIT_LONG = 15
    WEB_DRIVER_WAIT_SHORT = 5

    def __init__(self, email, password, config):
        self.email = email
        self.user = email.split('@')[0].replace('.', '')
        self.password = password
        self.config = config
        self.ol = RewardsLogger(level=config.log_level, name=email)
        self.driver = None

    def driver_setup(self, user_agent):
        """
        This is used to setup the driver for each run of the script
        :param user_agent: Add the user agent for browsing
        """
        if self.driver:
            self.driver.quit()
        driver_init = Driver(self.config)
        self.driver = driver_init.get_webdriver(user_agent=user_agent)

    def find_by_id(self, obj_id):
        """
        Searches for elements matching ID
        :param obj_id:
        :return: List of all nodes matching provided ID
        """
        return self.driver.find_elements_by_id(obj_id)

    def find_by_xpath(self, selector):
        """
        Finds elements by xpath
        :param selector: xpath string
        :return: returns a list of all matching selenium objects
        """
        return self.driver.find_elements_by_xpath(selector)

    def find_by_class(self, selector):
        """
        Finds elements by class name
        :param selector: Class selector of html obj
        :return: returns a list of all matching selenium objects
        """
        return self.driver.find_elements_by_class_name(selector)

    def find_by_css(self, selector):
        """
        Finds nodes by css selector
        :param selector: CSS selector of html node obj
        :return: returns a list of all matching selenium objects
        """
        return self.driver.find_elements_by_css_selector(selector)

    def wait_until_visible(self, by_, selector, time_to_wait=10):
        """
        Searches for selector and if found, end the loop
        Else, keep repeating every 2 seconds until time elapsed, then refresh page
        :param by_: string which tag to search by
        :param selector: string selector
        :param time_to_wait: int time to wait
        :return: Boolean if selector is found
        """
        start_time = time.time()
        while (time.time() - start_time) < time_to_wait:
            if self.driver.find_elements(by=by_, value=selector):
                return True
            self.driver.refresh()  # for other checks besides points url
            time.sleep(self.WEB_DRIVER_WAIT_SHORT)
        return False

    def wait_until_clickable(self, by_, selector, time_to_wait=10):
        """
        Waits 5 seconds for element to be clickable
        :param by_:  BY module args to pick a selector
        :param selector: string of xpath, css_selector or other
        :param time_to_wait: Int time to wait
        :return: None
        """
        try:
            WebDriverWait(self.driver, time_to_wait).until(ec.element_to_be_clickable((by_, selector)))
        except TimeoutException:
            self.ol.logger.exception(msg=f'{selector} element Not clickable - Timeout Exception', exc_info=False)
            self.screenshot(selector)
            self.driver.refresh()
        except UnexpectedAlertPresentException:
            # FIXME
            self.driver.switch_to.alert.dismiss()
            # self.ol.logger.exception(
            # msg=f'{selector} element Not Visible - Unexpected Alert Exception', exc_info=False
            # )
            # screenshot(selector)
            # self.driver.refresh()
        except WebDriverException:
            self.ol.logger.exception(msg=f'Webdriver Error for {selector} object')
            self.screenshot(selector)
            self.driver.refresh()

    def send_key_by_name(self, name, key):
        """
        Sends key to target found by name
        :param name: Name attribute of html object
        :param key: Key to be sent to that object
        :return: None
        """
        try:
            self.driver.find_element_by_name(name).send_keys(key)
        except (ElementNotVisibleException, ElementClickInterceptedException, ElementNotInteractableException):
            self.ol.logger.exception(msg=f'Send key by name to {name} element not visible or clickable.')
        except NoSuchElementException:
            self.ol.logger.exception(msg=f'Send key to {name} element, no such element.')
            self.screenshot(name)
            self.driver.refresh()
        except WebDriverException:
            self.ol.logger.exception(msg=f'Webdriver Error for send key to {name} object')

    def send_key_by_id(self, obj_id, key):
        """
        Sends key to target found by id
        :param obj_id: ID attribute of the html object
        :param key: Key to be sent to that object
        :return: None
        """
        try:
            self.driver.find_element_by_id(obj_id).send_keys(key)
        except (ElementNotVisibleException, ElementClickInterceptedException, ElementNotInteractableException):
            self.ol.logger.exception(msg=f'Send key by ID to {obj_id} element not visible or clickable.')
        except NoSuchElementException:
            self.ol.logger.exception(msg=f'Send key by ID to {obj_id} element, no such element')
            self.screenshot(obj_id)
            self.driver.refresh()
        except WebDriverException:
            self.ol.logger.exception(msg=f'Webdriver Error for send key by ID to {obj_id} object')

    def click_by_class(self, selector):
        """
        Clicks on node object selected by class name
        :param selector: class attribute
        :return: None
        """
        try:
            self.driver.find_element_by_class_name(selector).click()
        except (ElementNotVisibleException, ElementClickInterceptedException, ElementNotInteractableException):
            self.ol.logger.exception(msg=f'Send key by class to {selector} element not visible or clickable.')
        except WebDriverException:
            self.ol.logger.exception(msg=f'Webdriver Error for send key by class to {selector} object')

    def click_by_id(self, obj_id):
        """
        Clicks on object located by ID
        :param obj_id: id tag of html object
        :return: None
        """
        try:
            self.driver.find_element_by_id(obj_id).click()
        except (ElementNotVisibleException, ElementClickInterceptedException, ElementNotInteractableException):
            self.ol.logger.exception(msg=f'Click by ID to {obj_id} element not visible or clickable.')
        except WebDriverException:
            self.ol.logger.exception(msg=f'Webdriver Error for click by ID to {obj_id} object')

    def clear_by_id(self, obj_id):
        """
        Clear object found by id
        :param obj_id: ID attribute of html object
        :return: None
        """
        try:
            self.driver.find_element_by_id(obj_id).clear()
        except (ElementNotVisibleException, ElementNotInteractableException):
            self.ol.logger.exception(msg=f'Clear by ID to {obj_id} element not visible or clickable.')
        except NoSuchElementException:
            self.ol.logger.exception(msg=f'Send key by ID to {obj_id} element, no such element')
            self.screenshot(obj_id)
            self.driver.refresh()
        except WebDriverException:
            self.ol.logger.exception(msg='Error.')

    def main_window(self):
        """
        Closes current window and switches focus back to main window
        :return: None
        """
        try:
            for i in range(1, len(self.driver.window_handles)):
                self.driver.switch_to.window(self.driver.window_handles[i])
                self.driver.close()
        except WebDriverException:
            self.ol.logger.error('Error when switching to main_window')
        finally:
            self.driver.switch_to.window(self.driver.window_handles[0])

    def screenshot(self, selector):
        """
        Snaps screenshot of webpage when error occurs
        :param selector: The name, ID, class, or other attribute of missing node object
        :return: None
        """
        self.ol.logger.exception(msg=f'{selector} cannot be located.')
        screenshot_file_name = f'{datetime.now().strftime("%Y%m%d%%H%M%S")}_{selector}.png'
        screenshot_file_path = os.path.join('logs', screenshot_file_name)
        self.driver.save_screenshot(screenshot_file_path)

    def latest_window(self):
        """
        Switches to newest open window
        :return:
        """
        self.driver.switch_to.window(self.driver.window_handles[-1])

    @staticmethod
    def get_dates():
        """
        Returns a list of 5 dates from today to 22 days ago in year, month, day format
        :return: list of string of dates in year, month, day format
        """
        dates = []
        for i in range(0, 5):
            date = datetime.now() - timedelta(days=random.randint(0, 22))
            dates.append(date.strftime('%Y%m%d'))
        return dates

    def get_search_progress(self):
        """
        __search_progress elements are
        0 current web progress
        1 complete web progress
        2 current mobile progress
        3 complete mobile progress
        """
        search_progress = [0, -1, 0, -1]
        if len(self.driver.window_handles) == 1:  # open new tab
            self.driver.execute_script("window.open('about:blank');")
        self.latest_window()
        self.driver.get(self.POINT_TOTAL_URL)
        self.wait_until_visible(By.XPATH, '//*[@id="flyoutContent"]', self.WEB_DRIVER_WAIT_LONG)
        web_elements = self.driver.find_element_by_class_name('pcsearch')
        mobile_elements = self.driver.find_element_by_class_name('mobilesearch')
        if web_elements:
            # noinspection PyStatementEffect
            web_elements.location_once_scrolled_into_view  # Used for  mobile to scroll down
            search_progress[0], search_progress[1] = [int(i) for i in re.findall(r'(\d+)', web_elements.text)]
        if mobile_elements:
            search_progress[2], search_progress[3] = [int(i) for i in re.findall(r'(\d+)', mobile_elements.text)]

        self.main_window()
        self.ol.logger.debug(f'Web Search Progress: {search_progress[0]}/{search_progress[1]}')
        self.ol.logger.debug(f'Mobile Search Progress: {search_progress[2]}/{search_progress[3]}')

        return search_progress

    def update_search_queries(self, search_hist=None):
        dates = self.get_dates()
        search_queries = []
        for date in dates:
            try:
                url = f'https://trends.google.com/trends/api/dailytrends?hl=en-US&ed={date}&geo=US&ns=15'
                response = requests.get(url)
                response = json.loads(response.text[5:])
                for topic in response["default"]["trendingSearchesDays"][0]["trendingSearches"]:
                    search_queries.append(topic["title"]["query"].lower())
                    for related_topic in topic["relatedQueries"]:
                        search_queries.append(related_topic["query"].lower())
            except RequestException:
                self.ol.logger.error('Error retrieving google trends json.')
            except KeyError:
                self.ol.logger.error('Cannot parse, JSON keys are modified.')

        reduced_queries = set(search_queries).difference(search_hist)
        search_queries = list(reduced_queries)
        self.ol.logger.debug("# of search items: " + str(len(search_queries)))
        return search_queries

    def login(self, user_agent):
        self.driver_setup(user_agent)
        self.driver.get(self.LOGIN_URL)
        self.wait_until_clickable(By.NAME, 'loginfmt', self.WEB_DRIVER_WAIT_LONG)
        self.send_key_by_name('loginfmt', self.email)
        self.send_key_by_name('loginfmt', Keys.RETURN)
        self.ol.logger.debug("Sent Email Address.")
        self.wait_until_clickable(By.NAME, 'passwd', self.WEB_DRIVER_WAIT_LONG)
        self.send_key_by_name('passwd', self.password)
        self.ol.logger.debug("Sent Password.")
        # wait for 'sign in' button to be clickable and sign in
        self.send_key_by_name('passwd', Keys.RETURN)
        # Wait until logged in
        self.authenticator_screen()
        self.wait_until_visible(By.ID, 'loaded-home-banner-profile-section', self.WEB_DRIVER_WAIT_LONG)
        self.bing_login()
        self.ol.logger.debug("Successfully logged in")
        self.promotional_container()  # Check for a promotional container..

    def complete_search(self, pc=True, search_progress=None, search_hist=None):
        if pc:
            name = "PC"
        else:
            name = "Mobile"
        self.ol.logger.debug(f"Starting {name} search")
        search = self.search(pc=pc, search_progress=search_progress, search_hist=search_hist, search_queries=[])
        if search:
            self.ol.logger.debug(f"Successfully completed {name} search")
        else:
            self.ol.logger.warning(f"Failed to complete {name} search")

    def search(self, pc=False, search_count=0, search_progress=None, search_queries=None, search_hist=None):
        """
        Catch all search!
        :param pc: defaults to false as mobile needs to be specified
        :param search_count: initial part of the script for its loop
        :param search_progress: dictionary of integers
        :param search_queries: dictionary of search terms
        :param search_hist: dictionary of search history
        :return: loops
        """
        if search_count == 0:
            self.driver.get(self.BING_URL)
        elif search_count == 4:
            self.ol.logger.warning("Failed to complete search")
            return False
        search_progress_count = 0
        while True:
            if search_count > 0:
                search_progress = self.get_search_progress()
            if pc:
                current_progress = search_progress[0]
                complete_progress = search_progress[1]
            else:
                current_progress = search_progress[2]
                complete_progress = search_progress[3]

            if complete_progress > 0:
                break
            search_progress_count += 1
            if search_progress_count == 4:
                self.ol.logger.warning("Failed to complete search - no search progress")

                return False

        if len(search_queries) == 0:
            search_queries = self.update_search_queries(search_hist=search_hist)

        if current_progress < complete_progress:
            while True:
                search_queries_count = 0
                while True:
                    if len(search_queries) > 0:
                        break
                    else:
                        search_queries = self.update_search_queries(search_hist=search_hist)
                        search_queries_count += 1
                        if search_queries_count == 6:
                            self.ol.logger.warning("Failed to complete search - no topics to search")
                            return False
                        continue

                try:
                    query = search_queries.pop(0)
                    search_box = self.driver.find_element_by_id("sb_form_q")
                    search_box.clear()
                    # send query
                    search_box.send_keys(query, Keys.RETURN)  # unique search term
                    self.ol.logger.debug(f'Searched for: {query}')
                    search_hist.append(query)
                except UnexpectedAlertPresentException:
                    self.ol.logger.debug("Found Alert, Attempting to Close")
                    self.driver.switch_to_alert().dismiss()
                # sleep for a few seconds
                time.sleep(random.uniform(3, 5))
                current_progress += 5
                if current_progress >= complete_progress:
                    break
        else:
            return True

        return self.search(
            pc=pc, search_count=search_count + 1, search_queries=search_queries, search_hist=search_hist
        )

    def identify_quiz(self):
        # test for drag or drop or regular quiz
        if self.find_by_id('rqAnswerOptionNum0'):
            self.ol.logger.debug(msg='Drag and Drop Quiz identified.')
            self.drag_and_drop_quiz()
        # look for lightning quiz indicator
        elif self.find_by_id('rqAnswerOption0'):
            self.ol.logger.debug(msg='Lightning Quiz identified.')
            self.lightning_quiz()

    def hp_trivia(self):
        choices = self.find_by_class('trivia_option')
        # click answer
        if choices:
            random.choice(choices).click()
            time.sleep(self.WEB_DRIVER_WAIT_SHORT)
        self.wait_until_clickable(By.ID, 'check', self.WEB_DRIVER_WAIT_LONG)
        self.click_by_id('check')
        time.sleep(self.WEB_DRIVER_WAIT_SHORT)
        self.click_quiz()

    def iter_dailies(self):
        """
        Iterates through all outstanding dailies
        :return: None
        """
        self.driver.get(self.DASHBOARD_URL)
        self.wait_until_visible(By.CLASS_NAME, 'rewardsContent', self.WEB_DRIVER_WAIT_LONG)
        open_offers = self.driver.find_elements_by_xpath('//span[contains(@class, "mee-icon-AddMedium")]')
        if open_offers:
            self.ol.logger.debug(msg=f'Number of incomplete offers: {len(open_offers)}')
            # get common parent element of open_offers
            parent_elements = [open_offer.find_element_by_xpath('..//..//..//..') for open_offer in open_offers]
            # get points links from parent, # finds ng-transclude descendant of selected node
            offer_links = [
                parent.find_element_by_xpath(
                    'div[contains(@class,"actionLink")]//descendant::a'
                ) for parent in parent_elements
            ]
            # iterate through the dailies
            for offer in offer_links:
                self.ol.logger.debug(msg='Detected offer.')
                # click and switch focus to latest window
                offer.click()
                self.latest_window()
                time.sleep(self.WEB_DRIVER_WAIT_SHORT)
                # check for sign-in prompt
                self.sign_in_prompt()
                # check for poll by ID

                if self.find_by_id('btoption0'):
                    self.ol.logger.debug(msg='Poll identified.')
                    self.daily_poll()
                # check for quiz by checking for ID
                elif self.find_by_id('rqStartQuiz'):
                    self.click_by_id('rqStartQuiz')
                    self.identify_quiz()
                elif self.find_by_id('btOverlay'):
                    self.ol.logger.debug(msg='Quiz already started trying again.')
                    self.identify_quiz()
                elif self.find_by_class('wk_Circle'):
                    self.ol.logger.debug(msg='Click Quiz identified.')
                    self.click_quiz()
                elif self.find_by_id('hp_trivia_container'):
                    self.ol.logger.debug(msg='Home Page Trivia identified')
                    self.hp_trivia()
                # else do scroll for exploring pages
                else:
                    self.ol.logger.debug(msg='Explore Daily identified.')
                    self.explore_daily()
            # check at the end of the loop to log if any offers are remaining
            self.driver.get(self.DASHBOARD_URL)
            self.wait_until_visible(By.TAG_NAME, 'body', self.WEB_DRIVER_WAIT_LONG)
            open_offers = self.driver.find_elements_by_xpath('//span[contains(@class, "mee-icon-AddMedium")]')
            if len(open_offers) > 0:
                self.ol.logger.debug(msg=f'Number of incomplete offers remaining: {len(open_offers)}')
        else:
            self.ol.logger.debug(msg='No dailies found.')

    def explore_daily(self):
        # needs try/except bc these functions don't have exception handling built in.
        try:
            # select html to send commands to
            html = self.driver.find_element_by_tag_name('html')
            # scroll up and down to trigger points
            for i in range(3):
                html.send_keys(Keys.END)
                html.send_keys(Keys.HOME)
            # exit to main window
            self.main_window()
        except TimeoutException:
            self.ol.logger.exception(msg='Explore Daily Timeout Exception.')
        except (ElementNotVisibleException, ElementClickInterceptedException, ElementNotInteractableException):
            self.ol.logger.exception(msg='Element not clickable or visible.')
        except WebDriverException:
            self.ol.logger.exception(msg='Error.')

    def daily_poll(self):
        """
        Randomly clicks a poll answer, returns to main window
        :return: None
        """
        time.sleep(self.WEB_DRIVER_WAIT_SHORT)
        # click poll option
        choices = ['btoption0', 'btoption1']  # new poll format
        self.click_by_id(random.choice(choices))
        time.sleep(self.WEB_DRIVER_WAIT_SHORT)
        # close window, switch to main
        self.main_window()

    def lightning_quiz(self):
        for question_round in range(10):
            self.ol.logger.debug(msg=f'Round# {question_round}')
            if self.find_by_id('rqAnswerOption0'):
                first_page = self.driver.find_element_by_id('rqAnswerOption0').get_attribute("data-serpquery")
                self.driver.get(f"https://www.bing.com{first_page}")
                time.sleep(self.WEB_DRIVER_WAIT_SHORT)
                for i in range(10):
                    if self.find_by_id(f'rqAnswerOption{i}'):
                        self.driver.execute_script(f"document.querySelector('#rqAnswerOption{i}').click();")
                        self.ol.logger.debug(msg=f'Clicked {i}')
                        time.sleep(self.WEB_DRIVER_WAIT_SHORT)
            # let new page load
            time.sleep(self.WEB_DRIVER_WAIT_SHORT)
            if self.find_by_id('quizCompleteContainer'):
                break
        # close the quiz completion splash
        quiz_complete = self.find_by_css('.cico.btCloseBack')
        if quiz_complete:
            quiz_complete[0].click()
        time.sleep(self.WEB_DRIVER_WAIT_SHORT)
        self.main_window()

    def click_quiz(self):
        # start the quiz, iterates 10 times
        for i in range(10):
            if self.find_by_css('.cico.btCloseBack'):
                self.find_by_css('.cico.btCloseBack')[0].click()[0].click()
                self.ol.logger.debug(msg='Quiz popped up during a click quiz...')
            choices = self.find_by_class('wk_Circle')
            # click answer
            if choices:
                random.choice(choices).click()
                time.sleep(self.WEB_DRIVER_WAIT_SHORT)
            # click the 'next question' button
            self.wait_until_clickable(By.ID, 'check', self.WEB_DRIVER_WAIT_LONG)
            self.click_by_id('check')
            # if the green check mark reward icon is visible, end loop
            time.sleep(self.WEB_DRIVER_WAIT_SHORT)
            if self.find_by_css('span[class="rw_icon"]'):
                break
        self.main_window()

    def drag_and_drop_quiz(self):
        """
        Checks for drag quiz answers and exits when none are found.
        :return: None
        """
        for i in range(100):
            try:
                # find possible solution buttons
                drag_option = self.find_by_class('rqOption')
                # find any answers marked correct with correctAnswer tag
                right_answers = self.find_by_class('correctAnswer')
                # remove right answers from possible choices
                if right_answers:
                    drag_option = [x for x in drag_option if x not in right_answers]
                if drag_option:
                    # select first possible choice and remove from options
                    choice_a = random.choice(drag_option)
                    drag_option.remove(choice_a)
                    # select second possible choice from remaining options
                    choice_b = random.choice(drag_option)
                    ActionChains(self.driver).drag_and_drop(choice_a, choice_b).perform()
            except (WebDriverException, TypeError):
                self.ol.logger.debug(msg='Unknown Error.')
                continue
            finally:
                time.sleep(self.WEB_DRIVER_WAIT_SHORT)
                if self.find_by_id('quizCompleteContainer'):
                    break
        # close the quiz completion splash
        time.sleep(self.WEB_DRIVER_WAIT_SHORT)
        quiz_complete = self.find_by_css('.cico.btCloseBack')
        if quiz_complete:
            quiz_complete[0].click()
        time.sleep(self.WEB_DRIVER_WAIT_SHORT)
        self.main_window()

    def promotional_container(self):
        if self.find_by_class('promotional-container'):
            self.driver.find_element_by_xpath('//*[@id="promo-item"]//descendant::ng-transclude').click()

    def bing_login(self):
        self.driver.get(self.BING_URL)
        time.sleep(self.WEB_DRIVER_WAIT_SHORT)
        sign_in_prompt = self.find_by_class('simpleSignIn')
        if sign_in_prompt:
            self.ol.logger.debug("Detected Sign-In Prompt")
            self.driver.find_element_by_link_text('Sign in').click()
            self.ol.logger.debug("Clicked Sign-in prompt")
            time.sleep(self.WEB_DRIVER_WAIT_SHORT)
            self.main_window()

    def sign_in_prompt(self):
        time.sleep(self.WEB_DRIVER_WAIT_SHORT)
        sign_in_prompt = self.find_by_class('simpleSignIn')
        if sign_in_prompt:
            self.ol.logger.debug("Detected Sign-In Prompt")
            self.driver.find_element_by_link_text('Sign in').click()
            self.ol.logger.debug("Clicked Sign-in prompt")
            time.sleep(self.WEB_DRIVER_WAIT_SHORT)

    def print_stats(self):
        self.main_window()
        self.driver.get(self.DASHBOARD_URL)
        time.sleep(self.WEB_DRIVER_WAIT_LONG)
        stats = self.driver.find_elements_by_xpath('//mee-rewards-counter-animation//span')
        pe = len(stats) - 1
        # points = [int(i) for i in re.findall(r'(\d+)', stats[pe].text)]
        points_earned = stats[pe].text.replace("/", "of")
        streak_count = stats[pe - 2].text
        streak_details = stats[pe - 1].text  # streak details, ex. how many days remaining, bonus earned
        avail_points = stats[pe - 4].text
        lifetime_points = stats[pe - 3].text
        stats_message = [
            ["Completed for user", self.user],
            ["Points earned", points_earned],
            ["Streak count", streak_count],
            ["Streak Details", streak_details],
            ["Available points", avail_points],
            ["Lifetime Points", lifetime_points]
        ]
        self.ol.logger.info("\n" + tabulate(stats_message, tablefmt="fancy_grid"))

    def click_email_links(self):
        """
        Receives list of string URLs and clicks through them.
        Manual mode only, quizzes are still in flux and not standardized yet.
        :return: None
        """
        for link in self.config.email_links:
            self.driver.get(link)
            input('Press any key to continue.')

    def authenticator_screen(self):
        time.sleep(self.WEB_DRIVER_WAIT_SHORT)
        authenticator_intro = self.find_by_id('authenticatorIntro')
        if authenticator_intro:
            self.ol.logger.debug("Authenticator Advertisement was located")
            self.driver.find_element_by_link_text('No thanks').click()
            self.ol.logger.debug("Clicked the No thanks button")
            time.sleep(self.WEB_DRIVER_WAIT_SHORT)
            self.main_window()

    def dailyrewards(self):
        self.ol.logger.info(f"Started For user: {self.email}")
        self.run_it()
        self.ol.logger.debug(f"Completed For user: {self.email}")

    def run_it(self):
        try:
            search_hist = RewardsSearchHist(config=self.config).get(self.email)
            if self.config.pc or self.config.all or self.config.quiz or self.config.mobile:
                self.login(self.PC_USER_AGENT)
                search_progress = self.get_search_progress()
                if search_progress[0] != search_progress[1]:
                    self.complete_search(pc=True, search_progress=search_progress, search_hist=search_hist)
                else:
                    self.ol.logger.debug("Web Search has already been complete")
                if self.config.all or self.config.quiz:
                    self.iter_dailies()  # Do Quiz's etc
                if self.config.all or self.config.mobile:
                    if search_progress[2] != search_progress[3]:
                        self.login(self.MOBILE_USER_AGENT)
                        self.complete_search(pc=False, search_progress=search_progress, search_hist=search_hist)
                    else:
                        self.ol.logger.debug("Mobile Search has already been complete")
                self.print_stats()
                RewardsSearchHist(config=self.config).save(search_hist, self.email)
        except KeyboardInterrupt:
            self.driver.quit()
        except WebDriverException:
            self.ol.logger.info(msg=f'WebDriverException while executing', exc_info=True)
        finally:
            if self.driver:
                self.driver.quit()
                self.ol.logger.debug(msg="WebDriver Quit")
