import logging
import os
from datetime import datetime, timedelta
from time import sleep

from selenium.common.exceptions import InvalidArgumentException, ElementClickInterceptedException
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait


class CookieBot(Chrome):
    upgrade_check_delta = 60 * 10  # 10 minutes
    building_check_delta = 60  # 1 minute

    def __init__(self, teardown=False, save_dir=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implicitly_wait(5)
        if not save_dir:
            raise InvalidArgumentException("Save directory mus be provided")
        self.running = False
        self.save_dir = save_dir
        self.teardown = teardown
        self.upgrade_next_check = datetime.now()
        self.building_next_check = datetime.now()
        self.save_next_check = datetime.now() + timedelta(minutes=5)

    def __exit__(self, *args):
        self.__create_save()
        if self.teardown:
            super().__exit__(*args)

    def start_farming(self):
        self.get('https://orteil.dashnet.org/cookieclicker/')
        self.__accept_cc()
        self.__load_save()
        self.__initialize_elements()
        self.__modify_options()

        self.running = True

        while self.running:
            self.__check_for_upgrades()
            self.__check_for_buildings()
            self.__check_for_popups()
            self.__click_main_cookie()
            self.__check_for_save()

        logging.info("Finished running!")

    def __check_for_buildings(self):
        if datetime.now() < self.building_next_check:
            return

        # find the most expensive thing that can be bought and buy it, do it until there is no money left to buy
        while affordable_buildings := self.find_elements_by_css_selector('.product.unlocked.enabled'):
            affordable_buildings.sort(
                key=lambda product: int(product.find_element_by_css_selector('span.price').text.replace(',', ''))
            )
            affordable_buildings[-1].click()

        self.building_next_check = datetime.now() + timedelta(seconds=self.building_check_delta)

    def __check_for_upgrades(self):
        if datetime.now() < self.upgrade_next_check:
            return

        # trigger jscript that shows whole upgrade list
        ActionChains(self).move_to_element_with_offset(
            self._upgrade_box, 0, int(self._upgrade_box.value_of_css_property('padding-top').split('px')[0])
        ).perform()

        while _ := self.find_elements_by_css_selector('.crate.upgrade.enabled'):
            self.find_element_by_id('upgrade0').click()
            sleep(0.05)

        self.upgrade_next_check = datetime.now() + timedelta(seconds=self.upgrade_check_delta)

    def __check_for_popups(self):
        pass

    def __accept_cc(self):
        """
        Accept cookie consent
        """
        try:
            elem = WebDriverWait(self, 5).until(lambda d: d.find_element_by_class_name('cc_btn_accept_all'))
            while True:
                try:
                    elem.click()
                    return
                except ElementClickInterceptedException:
                    continue
        except Exception:  # should never happen but who knows
            logging.error("Failed to accept cookies!")
            raise

    def __modify_options(self):
        """
        Modify all options that need modifying
        """
        # open options
        self.find_element_by_id('prefsButton').click()

        # disable price shortening
        self.find_element_by_id('formatButton').click()

        # close options menu
        self.find_element_by_css_selector('#menu>.close.menuClose').click()

    def __load_save(self):
        latest_save_data = self.__get_latest_save_data()
        if latest_save_data is None:
            return

        # open load dialog
        ActionChains(self).key_down(Keys.LEFT_CONTROL).send_keys('o').key_up(Keys.LEFT_CONTROL).perform()
        # paste save data in textarea
        self.find_element_by_id('textareaPrompt').send_keys(latest_save_data)
        self.find_element_by_id('promptOption0').click()

    def __create_save(self):
        # open options
        self.find_element_by_id('prefsButton').click()
        # click on export
        self.find_element_by_css_selector('a[onclick*="Game.ExportSave()"]').click()
        # get export value
        save_data = self.find_element_by_id('textareaPrompt').text
        # save to file

        with open(os.path.join(self.save_dir, datetime.now().isoformat()), 'w') as file:
            file.write(save_data)

        # close save window
        self.find_element_by_id('promptOption0').click()
        # close options menu
        self.find_element_by_css_selector('#menu>.close.menuClose').click()

    def __initialize_elements(self):
        # find and save all elements that will be accessed and will not disappear and reappear
        self._main_cookie = self.find_element_by_id('bigCookie')
        self._upgrade_box = self.find_element_by_id('upgrades')

    def __get_latest_save_data(self):
        # find latest save file if any
        files = os.listdir(self.save_dir)
        if files:
            files.sort()
            latest_file = files[-1]

            # read from file
            with open(os.path.join(self.save_dir, latest_file), 'r') as save_file:
                save_data = save_file.read()

            return save_data
        return None

    def __click_main_cookie(self):
        self._main_cookie.click()

    def __check_for_save(self):
        if datetime.now() < self.save_next_check:
            return

        self.__create_save()
        self.save_next_check = datetime.now() + timedelta(minutes=5)
