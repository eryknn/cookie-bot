import os
from datetime import datetime

from selenium.common.exceptions import InvalidArgumentException, ElementClickInterceptedException
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait


class CookieBot(Chrome):

    def __init__(self, teardown=False, save_dir=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.implicitly_wait(5)
        if not save_dir:
            raise InvalidArgumentException("Save directory mus be provided")
        self.save_dir = save_dir
        self.teardown = teardown

    def __exit__(self, *args):
        self.__create_save()
        if self.teardown:
            super().__exit__(*args)

    def start_farming(self):
        self.get('https://orteil.dashnet.org/cookieclicker/')
        self.__accept_cc()
        self.__load_save()
        self.__initialize_elements()

        for _ in range(400):
            self.__click_main_cookie()

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
            print("Failed to accept cookies!")
            raise

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

    def __initialize_elements(self):
        # find and save all elements that will be accessed and will not disappear and reappear
        self._main_cookie = self.find_element_by_id('bigCookie')

    def __click_main_cookie(self):
        self._main_cookie.click()

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
