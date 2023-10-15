import dc
import ipv4

import logging

logger = logging.getLogger()


def log_post(prefix: str, post: dc.DCPostTR):
    ip = ipv4.get_ip_data(post.writer_ip)
    if len(ip) == 0:
        logger.info(f"{prefix} pid={post.postId}, title={post.title}, ip={post.writer_ip}, Country=? name_en=? name_kr=?")
    elif isinstance(ip, list):
        c = ",".join(set(map(lambda i: i.country, ip)))
        e = ",".join(set(map(lambda i: i.name_en, ip)))
        k = ",".join(set(map(lambda i: i.name_kr, ip)))
        logger.info(f"{prefix} pid={post.postId}, title={post.title}, ip={post.writer_ip}, Country={c} name_en={e} name_kr={k}")
