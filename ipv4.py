import csv

_data = None


def _get_data():
    global _data
    if _data:
        return _data

    with open('ipv4.csv', 'r', encoding='utf-8') as csv_file:
        _data = list(csv.reader(csv_file))

    _data.pop(0)
    for d in _data:
        d[1] = ip_to_int(d[1])
        d[2] = ip_to_int(d[2])

    return _data


def ip_to_int(ip_address):
    parts = ip_address.split('.')
    if len(parts) < 4:
        parts = parts + ['0'] * (4 - len(parts))
    ip_int = int(parts[0]) * 256**3 + int(parts[1]) * 256**2 + int(parts[2]) * 256 + int(parts[3])
    return ip_int


def int_to_ip(ip_int):
    ip_address = []
    for _ in range(4):
        ip_address.append(str(ip_int % 256))
        ip_int //= 256
    return '.'.join(ip_address[::-1])


def get_ip_country(ip_address):
    ip_int = ip_to_int(ip_address)
    data = _get_data()

    ret = []
    for d in data:
        if d[1] <= ip_int <= d[2]:
            ret.append(d[0])
    if len(ret) == 0:
        return "Unknown"
    elif len(ret) == 1:
        return ret[0]
    else:
        return ret
