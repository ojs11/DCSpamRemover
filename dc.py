from functools import cached_property

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from interval import interval_human


def login(driver: WebDriver, gall_id: str, uid, pwd):
    driver.get(f"https://sign.dcinside.com/login?s_url=https%3A%2F%2Fgall.dcinside.com%2Fmgallery%2Fboard%2Flists%3Fid%3D{gall_id}&s_key=32")

    input_uid = driver.find_element(By.CSS_SELECTOR, 'input[name="user_id"]')
    input_uid.clear()
    input_uid.send_keys(uid)
    interval_human()

    input_pwd = driver.find_element(By.CSS_SELECTOR, 'input[name="pw"]')
    input_pwd.clear()
    input_pwd.send_keys(pwd)
    interval_human()

    login_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    login_btn.click()
    interval_human()

    try:
        da = driver.switch_to.alert
        da.accept()
        return False
    except:
        return True


def close_otp(driver: WebDriver):
    try:
        driver.find_element(By.CSS_SELECTOR, 'div#opt_use_pop button.popbtn_bgblueclose').click()
        interval_human()
    except:
        pass


def is_del_limit_exceeded(driver: WebDriver):
    del_btn = driver.find_element(By.CSS_SELECTOR, '#avoid_pop_avoid_del')
    return 'disabled' in del_btn.get_attribute('class')


def is_loggedIn(driver: WebDriver):
    try:
        login_btn = driver.find_element(By.CSS_SELECTOR, 'a.btn_top_loginout')
        if login_btn.text == "로그인":
            return False
        else:
            return True
    except:
        return False


def is_user_admin(driver: WebDriver):
    try:
        driver.find_element(By.CSS_SELECTOR, 'div.useradmin_btnbox > button:nth-child(3)')
        return True
    except:
        return False


class DCPostTR:
    def __init__(self, elem: WebElement):
        self._elem = elem

    def cache(self):
        [attr for attr in dir(self) if isinstance(getattr(self, attr), cached_property)]

    @cached_property
    def postId(self):
        val = self._elem.get_attribute('data-no')
        return int(val)

    @cached_property
    def title(self):
        return self._elem.find_element(By.CSS_SELECTOR, 'td.gall_tit').text

    @cached_property
    def writer_name(self):
        return self._elem.find_element(By.CSS_SELECTOR, 'td.gall_writer span.nickname').text

    @cached_property
    def writer_ip(self):
        val = self._elem.find_element(By.CSS_SELECTOR, 'td.gall_writer').get_attribute('data-ip')
        if val:
            return val
        return None

    @cached_property
    def writer_uid(self):
        val = self._elem.find_element(By.CSS_SELECTOR, 'td.gall_writer').get_attribute('data-uid')
        if val:
            return val
        return None

    @cached_property
    def category(self):
        try:
            return self._elem.find_element(By.CSS_SELECTOR, "td.gall_subject").text
        except:
            return None

    @cached_property
    def views(self):
        val = self._elem.find_element(By.CSS_SELECTOR, 'td.gall_count').text
        try:
            return int(val)
        except:
            return None

    @cached_property
    def recommends(self):
        val = self._elem.find_element(By.CSS_SELECTOR, 'td.gall_recommend').text
        try:
            return int(val)
        except:
            return None

    def click(self):
        try:
            self._elem.find_element(By.CSS_SELECTOR, 'a').click()
            return True, None
        except Exception as e:
            return False, e

    def click_checkbox(self):
        try:
            self._elem.find_element(By.CSS_SELECTOR, 'td.gall_chk input').click()
            return True, None
        except Exception as e:
            return False, e
