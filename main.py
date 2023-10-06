import time
from logging import getLogger
from random import random
from threading import Event, Thread
from urllib.parse import urlparse, urlunparse

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoAlertPresentException

import dc
from config import get_config
from interval import interval_human

logger = getLogger()

events = {
    'reload': Event(),
    'exit': Event()
}


def main_selenium():
    options = ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    if get_config().getboolean('selenium', 'headless'):
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--headless")
    options.set_capability("pageLoadStrategy", "none")  # fucking google analytics

    driver = Chrome(options=options)
    driver.implicitly_wait(10)

    def task_check_driver_alive():
        nonlocal driver

        time.sleep(5)
        while True:
            try:
                driver.switch_to.alert.text
                time.sleep(1)
            except NoAlertPresentException:
                pass
            except Exception:
                break

        events['reload'].set()
        events['exit'].set()

    Thread(target=task_check_driver_alive, daemon=True).start()

    try:
        gall_id = get_config().get('gallery', 'id')
        gall_url = urlparse(f"https://gall.dcinside.com/mgallery/board/lists?id={gall_id}")

        loops = 0
        interval = get_config().getfloat('interval.refresh', 'min')
        removals = 0
        last_time = time.time()
        elapsed_time = 2e-20
        while driver and not events['exit'].is_set():
            try:
                driver.title
            except:
                logger.info("사용자가 브라우저를 종료함.")
                break

            loops += 1

            if events['exit'].is_set():
                events['reload'].clear()

            curr_url = urlparse(driver.current_url)
            if curr_url.path != gall_url.path:
                driver.get(urlunparse(gall_url))

            # 로그인
            if not dc.is_loggedIn(driver):
                config = get_config()
                r = dc.login(driver, gall_id, config.get('user', 'uid'), config.get('user', 'pwd'))
                if not r:
                    logger.info("로그인 실패. 1시간 후 재시도")
                    events['reload'].wait(3600)
                    continue
                else:
                    logger.info("로그인 성공")
                last_time = time.time()

            hour = int(elapsed_time / 3600)
            minute = max(0, int(elapsed_time / 60) % 60)
            rmpt, rmpu = removals/(max(elapsed_time/60, 1)), 'm'
            if rmpt > 0 and rmpt < 1:
                rmpt, rmpu = removals/elapsed_time, 's'

            logger.info(f"{loops}th loop. elapsed {hour}h {minute}m. {removals} removed. ({rmpt:.1f}/{rmpu})")
            logger.info("게시글 목록을 불러오는 중")
            driver.get(urlunparse(gall_url))

            dc.close_otp(driver)

            if not dc.is_user_admin(driver):
                logger.error("권한이 없는 것 같습니다. 1시간 후 재시도")
                events['reload'].wait(3600)
                driver.refresh()
                last_time = time.time()
                continue

            if dc.is_del_limit_exceeded(driver):
                logger.info("일일 삭제 횟수 제한이 초과 되었습니다. 6시간 후 재시도")
                events['reload'].wait(3600*6)
                last_time = time.time()
                continue

            posts = driver.find_elements(By.CSS_SELECTOR, 'tr.us-post[data-no]')
            posts = map(lambda p: dc.DCPostTR(p), posts)
            posts = filter(lambda p: p.writer_uid is None, posts)
            posts = filter(lambda p: p.writer_ip in get_config().getlist('gallery', 'ip_blacklist'), posts)
            posts = list(posts)

            if len(posts) == 0:
                rand_size = get_config().getfloat('interval.refresh', 'rand')
                interval = random() * rand_size + interval
                interval = interval * get_config().getfloat('interval.refresh', 'mul')
                interval = min(interval, get_config().getint('interval.refresh', 'max'))
                logger.info(f"삭제할 게시글이 없음. {interval:.2f}s 대기...")
                events['reload'].wait(interval)
                continue
            else:
                interval = get_config().getfloat('interval.refresh', 'min')

            logger.info(f"삭제할 게시글 수 : {len(posts)}")
            for post in posts:
                post.cache()
                dc.DCPostTR(driver.find_element(By.CSS_SELECTOR, f'tr.ub-content[data-no="{post.postId}"]')).click_checkbox()
                interval_human()

            driver.find_element(By.CSS_SELECTOR, 'div.useradmin_btnbox > button:nth-child(3)').click()
            interval_human()

            if get_config().getboolean('gallery', 'no_mercy'):
                hour_btn = driver.find_elements(By.CSS_SELECTOR, '.block_sel.time > span > input:not(.disabled)')[-1]
            else:
                hour_btn = driver.find_element(By.CSS_SELECTOR, f'#avoid_pop_avoid_hour{get_config().getint("gallery", "block_hour")}')
            block_hour = int(hour_btn.get_attribute('value'))
            hour_btn.click()
            interval_human()

            driver.find_element(By.CSS_SELECTOR, '#avoid_pop_avoid_reason_4').click()  # 도배
            interval_human()

            driver.find_element(By.CSS_SELECTOR, '#avoid_pop_avoid_del').click()  # 차단 및 삭제
            interval_human()

            driver.find_element(By.CSS_SELECTOR, '#avoid_pop > div > div.btn_box > button').click()
            interval_human()

            try:
                da = driver.switch_to.alert
                if da.text == "시스템 오류로 작업이 중지되었습니다. 잠시 후 다시 이용해 주세요.":
                    logger.info("이미 삭제되었습니다.")
                    da.accept()
                elif da.text == "차단 및 삭제되었습니다.":
                    da.accept()
                    for post in posts:
                        logger.info(f"삭제 및 {block_hour}시간 차단 성공 : pid={post.postId}, title={post.title}, writer={post.writer_name}, ip={post.writer_ip}")
                    removals += len(posts)
                else:
                    logger.warning(f"삭제 및 차단 실패. 예기치 못한 알림 : {da.text}")
                    da.accept()
                interval_human()
            except Exception as e:
                logger.error(f"알림 처리중 예기지 못한 오류 발생 : {e}")
                continue

            end_time = time.time()
            elapsed_time += end_time - last_time
            last_time = end_time
    except Exception as e:
        if driver:
            logger.error(f"예기치 못한 오류 발생 : {e}")

    driver = None
    events['exit'].set()


if __name__ == "__main__":
    from config import watch_config_change
    from logger import setup_logger
    from timedinput import timed_input
    from version import version

    commands = {
        'reload': lambda: events['reload'].set(),
        'r': lambda: events['reload'].set(),
        'exit': lambda: events['exit'].set(),
        'e': lambda: events['exit'].set(),
    }

    print(f"DCSpamRemover {version}")
    print("1. reload(r): 즉시 새로고침")
    print("2.   exit(e): 프로그램 종료")
    print("===================================")

    setup_logger()
    watch_config_change()

    thread_selenium = Thread(target=main_selenium, daemon=True)
    thread_selenium.start()

    cmd = None
    while not events['exit'].is_set():
        try:
            cmd = timed_input(timeout=5) or ''
            cmd = cmd.lower().strip()
        except KeyboardInterrupt:
            cmd = "exit"
        except:
            break

        op = commands.get(cmd, lambda: None)()

    events['exit'].set()
