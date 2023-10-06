import configparser
import os
import time

from logging import getLogger

from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger = getLogger()


class Config:
    def __init__(self, filename):
        self._raw = configparser.ConfigParser()
        self._raw.read(filename, encoding='utf-8')

    def get(self, *args, **kwargs):
        return self._raw.get(*args, **kwargs)

    def getUpper(self, *args, **kwargs):
        return self._raw.get(*args, **kwargs).upper()

    def getint(self, *args, **kwargs):
        return self._raw.getint(*args, **kwargs)

    def getboolean(self, *args, **kwargs):
        return self._raw.getboolean(*args, **kwargs)

    def getfloat(self, *args, **kwargs):
        return self._raw.getfloat(*args, **kwargs)

    def getlist(self, *args, **kwargs):
        return [x.strip() for x in self._raw.get(*args, **kwargs).split(",")]


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


def watch_config_change():
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()
    return observer
