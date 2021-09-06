import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DRIVER_DIR = os.path.join(ROOT_DIR, 'drivers')
INSTALLED_DRIVERS = {
    'chrome': os.path.join(DRIVER_DIR, 'chromedriver')
}
