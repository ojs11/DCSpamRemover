import sys
sys.path.append('src')

if True:  # noqa
    from logging import getLogger
    from threading import Thread

    import tasks
    from common import *
    from events import events

logger = getLogger()

if __name__ == "__main__":
    from config import (config_file_exists, download_template,
                        watch_config_change)
    from logger import setup_logger
    from timedinput import timed_input
    from version import version

    if not config_file_exists():
        print("config.ini 파일이 없음. 다운로드...")
        download_template('config.ini')
        print("config.ini 파일을 수정한 후 다시 실행해주세요.")
        input("Press Enter to exit...")
        exit(0)

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

    thread_selenium = Thread(target=tasks.remover, daemon=True)
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
