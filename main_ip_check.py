import sys
sys.path.append('src')

if True:  # noqa
    import tasks
    from logger import setup_logger

if __name__ == "__main__":
    setup_logger()
    tasks.ip_checker()
