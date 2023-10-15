import re
from datetime import datetime


def extract_datetime(text):
    date_pattern = r'(\d{4}\.\d{2}\.\d{2} \d{2}\:\d{2})'
    matches = re.findall(date_pattern, text)

    if not matches:
        return None

    dt = datetime.strptime(matches[0], '%Y.%m.%d %H:%M')
    return dt
