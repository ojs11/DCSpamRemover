from threading import Event


events = {
    'reload': Event(),
    'exit': Event()
}
