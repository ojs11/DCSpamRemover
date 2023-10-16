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


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        for ip in sys.argv[1].split(","):
            print("IP:", ip)
            for d in get_ip_data(ip):
                print(d)
            print("====================================")
    else:
        import re
        import sys
        import tkinter as tk
        from concurrent.futures import ThreadPoolExecutor

        root = tk.Tk()

        width = 1000
        height = 400
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()

        root.title("IPV4")
        root.geometry(f"{width}x{height}+{(ws - width) // 2}+{(hs - height) // 2}")

        # input frame
        frame = tk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="IP").pack(side=tk.LEFT)
        ip = tk.StringVar()

        ip_input = tk.Entry(frame, textvariable=ip)
        ip_input.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # result listbox frame
        result_frame = tk.Frame(root)
        result_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(result_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox = tk.Listbox(result_frame, yscrollcommand=scrollbar.set)
        listbox.pack(fill=tk.BOTH, expand=True)

        scrollbar.config(command=listbox.yview)

        ip_pattern = "\w{1,3}\.\w{1,3}"
        search_result = []
        search_thread_pool = ThreadPoolExecutor(max_workers=1)

        def do_search():
            global search_result

            if not re.match(ip_pattern, ip.get()):
                return

            search_result = get_ip_data(ip.get())
            root.event_generate('<<UpdateListbox>>', when='tail')

        def do_search_thread():
            global search_thread

            if not re.match(ip_pattern, ip.get()):
                return

            listbox.delete(0, tk.END)
            listbox.insert(tk.END, "Searching...")
            search_thread_pool.submit(do_search)

        def update_listbox(_: tk.Event):
            listbox.delete(0, tk.END)

            if len(search_result) == 0:
                listbox.insert(tk.END, "Not Found")
                return

            for d in search_result:
                listbox.insert(tk.END, d)

        delayed_function_id = None

        def on_key_change(*_):
            global delayed_function_id
            if delayed_function_id:
                root.after_cancel(delayed_function_id)
            delayed_function_id = root.after(600, do_search_thread)

        root.bind('<<UpdateListbox>>', update_listbox)
        ip_input.bind("<KeyRelease>", on_key_change)
        ip_input.bind("<Return>", lambda _: do_search_thread())

        tk.Button(frame, text="Search", command=do_search).pack(side=tk.LEFT)

        root.mainloop()
