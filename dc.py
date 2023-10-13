from functools import cached_property

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from interval import interval_human

import utils


def _click(elem):
    elem.click()
    interval_human()


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


def restrict_anonymous(
    driver: WebDriver,
    gall_id: str,
    restrcit_gall_proxy: bool,
    restrict_gall_mobile: bool,
    restrict_media_proxy: bool,
    restrict_media_mobile: bool,
    restrict_media_all: bool,
):
    url = f"https://gall.dcinside.com/mgallery/management/gallery?id={gall_id}"
    if driver.current_url != url:
        driver.get(url)

    btn = driver.find_element(By.CSS_SELECTOR, ".nonmember > div:nth-child(2) > div:nth-child(2) > button:nth-child(1)")
    if (btn.is_displayed()):
        _click(btn)

    if restrcit_gall_proxy:
        div = driver.find_element(By.CSS_SELECTOR, "div.cont_inr.set.proxy")
        ab = div.find_element(By.CSS_SELECTOR, 'div.select_box')
        _click(ab)
        _click(ab.find_element(By.CSS_SELECTOR, 'ul > li:last-child'))
        _click(div.find_element(By.CSS_SELECTOR, '.update_time'))

    if restrict_gall_mobile:
        div = driver.find_element(By.CSS_SELECTOR, "div.cont_inr.set.mobile")
        ab = div.find_element(By.CSS_SELECTOR, 'div.select_box')
        _click(ab)
        _click(ab.find_element(By.CSS_SELECTOR, 'ul > li:last-child'))
        _click(div.find_element(By.CSS_SELECTOR, '.update_time'))

    if restrict_media_proxy or restrict_media_mobile or restrict_media_all:
        div = driver.find_element(By.CSS_SELECTOR, "div.cont_inr.img_block")
        if restrict_media_proxy:
            _vpn = driver.find_element(By.CSS_SELECTOR, '#img_block_vpn')
            if not _vpn.is_selected():
                _click(_vpn)
        if restrict_media_mobile:
            _mobile = driver.find_element(By.CSS_SELECTOR, '#img_block_mobile')
            if not _mobile.is_selected():
                _click(_mobile)
        if restrict_media_all:
            _all = driver.find_element(By.CSS_SELECTOR, '#img_block_all')
            if not _all.is_selected():
                _click(_all)

        ab = div.find_element(By.CSS_SELECTOR, 'div.select_box')
        _click(ab)
        _click(ab.find_element(By.CSS_SELECTOR, 'ul > li:last-child'))
        _click(div.find_element(By.CSS_SELECTOR, '.update_time'))

    dt_proxy = utils.extract_datetime(driver.find_element(By.CSS_SELECTOR, '.proxy_txt').text)
    dt_mobile = utils.extract_datetime(driver.find_element(By.CSS_SELECTOR, '.mobile_txt').text)
    dt_media = utils.extract_datetime(driver.find_element(By.CSS_SELECTOR, '.img_block_txt').text)

    _click(driver.find_element(By.CSS_SELECTOR, '.nonmember .set_save'))

    return (dt_proxy, dt_mobile, dt_media)


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

    @cached_property
    def post_type(self):
        """
            Type of post

            1. icon_notice   : 공지글
            2. icon_txt      : 일반글
            3. icon_pic      : 이미지 첨부글
            4. icon_movie    : 동영상 첨부글
            5. icon_ai       : AI 이미지
            6. icon_recomimg : 개념글

            None if error
        """
        try:
            return self._elem.get_attribute("data-type")
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
