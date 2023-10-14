
import atexit
from config import get_config


def create():
    return create_chrome()


def create_chrome():
    from selenium.webdriver import Chrome
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.add_argument("--ignore-certificate-errors")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    if get_config().getboolean('selenium', 'headless', fallback=False):
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--headless")
    options.set_capability("pageLoadStrategy", "none")  # fucking google analytics

    driver = Chrome(options=options)
    driver.implicitly_wait(10)

    def onExit():
        try:
            driver.close()
        except:
            pass

    atexit.register(onExit)

    return driver
