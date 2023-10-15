import os
import time
from configparser import ConfigParser
from logging import getLogger

from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger = getLogger()


def parse_size(size):
    size = size.upper().replace(' ', '')
    if size.endswith('G'):
        return int(size[:-1]) * 1024 * 1024 * 1024
    elif size.endswith('M'):
        return int(size[:-1]) * 1024 * 1024
    elif size.endswith('K'):
        return int(size[:-1]) * 1024
    else:
        return int(size)


class Config(ConfigParser):
    def __init__(self, filename):
        super().__init__()
        self.read(filename, encoding='utf-8')

    def getByteSize(self, section: str, option: str, *, raw=False, vars=None, fallback=0):
        return parse_size(self.get(section, option, raw=raw, vars=vars, fallback=fallback))

    def getUpper(self, section: str, option: str, *, raw=False, vars=None, fallback=None):
        return self.get(section, option, raw=raw, vars=vars, fallback=fallback)

    def getlist(self, section: str, option: str, *, raw=False, vars=None, fallback: list = [], fallback_on_empty=False):
        v = self.get(section, option, raw=raw, vars=vars, fallback=fallback)
        if v == '' and fallback_on_empty:
            return fallback
        return v.split(',')

    def getListOrFalse(self, section: str, option: str) -> bool | list[str]:
        v = self.get(section, option, fallback=False)
        if not v:
            return []
        return v.split(",")

    def write(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            super().write(f)


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_event_time = 0

    def on_modified(self, ev: FileModifiedEvent):
        global _config

        _, fn = os.path.split(ev.src_path)
        if fn != _config_file_name:
            return
        current_time = time.time()
        if current_time - self.last_event_time <= 5:
            return

        self.last_event_time = current_time
        new_config = Config(_config_file_name)
        _config = new_config
        logger.info("Config file changed, reload config")


_config_file_name = "config.ini"
_config = Config(_config_file_name)


def get_config():
    global _config
    return _config


def create_config(path):
    return Config(path)


def watch_config_change():
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()
    return observer


def config_file_exists():
    return os.path.exists(_config_file_name)


def download_template(path):
    from urllib.request import urlopen

    url = "https://raw.githubusercontent.com/arwls1nzdw/DCSpamRemover/main/config.ini.template"
    r = urlopen(url)
    with open(path, 'wb') as f:
        f.write(r.read())
