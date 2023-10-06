
from threading import Thread


class _TimedInputThread(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.result = None

    def run(self):
        try:
            self.result = input()
        except:
            return None


_input_thread = _TimedInputThread()
_input_thread.start()


def timed_input(timeout: float):
    global _input_thread

    if not _input_thread.is_alive():
        _input_thread.run()
    _input_thread.join(timeout)

    if _input_thread.is_alive():
        return None
    else:
        return _input_thread.result
