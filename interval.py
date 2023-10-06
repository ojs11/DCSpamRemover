from random import random
from time import sleep

from config import get_config


def interval_human():
    min = get_config().getfloat('interval.click', 'min')
    max = get_config().getfloat('interval.click', 'max')

    delay = random() * (max - min) + min
    delay = delay / 1000.0
    delay = round(delay, 2)

    sleep(delay)
