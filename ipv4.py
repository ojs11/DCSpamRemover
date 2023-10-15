import csv
from dataclasses import dataclass
from functools import lru_cache

_data: list['IPV4'] = None


@dataclass
class IPV4:
    country: str
    start_ip: str
    end_ip: str
    assign_date: str
    name_kr: str
    name_en: str


def _get_data():
    global _data
    if _data:
        return _data

    try:
        _map = {}
        _data = []
        with open("ipv4.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)
            for r in reader:
                _data.append(IPV4(r[0], r[1], r[2], r[4], r[0], r[0]))
                _map[r[1]] = r[0]
    except FileNotFoundError:
        _data = []

    try:
        with open('ipv4-Kr.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for r in reader:
                if r[1] in _map:
                    _data[_map[r[1]]].name_kr = r[0]
                else:
                    _data.append(IPV4("KR", r[2], r[3], r[5], r[0], r[1]))
    except FileNotFoundError:
        pass

    return _data


def ip_to_int(ip):
    c = ip.count('.')
    if c < 3:
        ip += '.0' * (3 - c)
    return int.from_bytes(map(int, ip.split('.')), 'big')


@lru_cache(maxsize=2048)
def get_ip_data(ip):
    data = _get_data()

    ip = ip_to_int(ip)
    ret = []
    for d in data:
        si = ".".join(d.start_ip.split(".")[:2])
        ei = ".".join(d.end_ip.split(".")[:2])
        if ip_to_int(si) <= ip <= ip_to_int(ei):
            # 독립 사용자
            if d.country == "KR" and d.name_kr == "KR":
                continue

            ret.append(d)

    return ret
