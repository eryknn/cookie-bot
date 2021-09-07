from selenium.webdriver.chrome.options import Options

from conf import INSTALLED_DRIVERS, SAVE_DIR
from cookiebot import CookieBot


def run():
    options = Options()
    options.add_experimental_option("detach", True)

    with CookieBot(teardown=False, save_dir=SAVE_DIR, executable_path=INSTALLED_DRIVERS['chrome'], options=options) as bot:
        bot.start_farming()


if __name__ == '__main__':
    run()
