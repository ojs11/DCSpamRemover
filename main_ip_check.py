import time
from logging import getLogger
from urllib.parse import urlparse, urlunparse

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By

import dc
import ipv4
from config import get_config
from logger import setup_logger

import webdriver

logger = getLogger()

if __name__ == "__main__":
    driver = webdriver.create()

    gall_id = get_config().get('gallery', 'id')
    gall_url = urlparse(f"https://gall.dcinside.com/mgallery/board/lists?id={gall_id}")

    setup_logger()

    last_pid = 0
    while True:
        driver.get(urlunparse(gall_url))

        time.sleep(5)

        posts = driver.find_elements(By.CSS_SELECTOR, 'tr.us-post[data-no]')
        posts = map(lambda p: dc.DCPostTR(p), posts)
        posts = filter(lambda p: p.postId > last_pid, posts)
        posts = filter(lambda p: p.writer_uid is None, posts)
        posts = filter(lambda p: p.post_type != "icon_notice", posts)
        posts = list(posts)

        for p in posts:
            ip = ipv4.get_ip_data(p.writer_ip)
            if len(ip) == 0:
                logger.info(f"pid={p.postId}, title={p.title[:3]}..., ip={p.writer_ip}, Country=? name_en=? name_kr=?")
            elif isinstance(ip, list):
                c = ",".join(set(map(lambda i: i.country, ip)))
                e = ",".join(set(map(lambda i: i.name_en, ip)))
                k = ",".join(set(map(lambda i: i.name_kr, ip)))
                logger.info(f"pid={p.postId}, title={p.title[:3]}..., ip={p.writer_ip}, Country={c} name_en={e} name_kr={k}")

        if len(posts) > 0:
            last_pid = max(map(lambda p: p.postId, posts))

        time.sleep(30)
