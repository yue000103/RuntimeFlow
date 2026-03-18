"""屏幕状态浮窗 — 右下角置顶小窗口，贯穿录制/回放全生命周期"""

import threading
import queue
import tkinter as tk


class StatusOverlay:
    """右下角状态浮窗，支持倒计时 → 进行中 → 结束的完整生命周期"""

    def __init__(self):
        self._cmd_queue: queue.Queue = queue.Queue()
        self._ready = threading.Event()
        self._done = threading.Event()
        self._root = None
        self._thread = threading.Thread(target=self._run)
        self._thread.start()
        self._ready.wait()

    def _run(self):
        root = tk.Tk()
        self._root = root
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.85)
        root.configure(bg="#1a1a2e")

        frame = tk.Frame(root, bg="#1a1a2e", padx=20, pady=12)
        frame.pack()

        self._title_label = tk.Label(
            frame, text="", font=("Microsoft YaHei", 11),
            fg="#aaaaaa", bg="#1a1a2e",
        )
        self._title_label.pack()

        self._num_label = tk.Label(
            frame, text="", font=("Consolas", 48, "bold"),
            fg="#ffffff", bg="#1a1a2e",
        )
        self._num_label.pack()

        self._sub_label = tk.Label(
            frame, text="", font=("Microsoft YaHei", 10),
            fg="#666666", bg="#1a1a2e",
        )
        self._sub_label.pack()

        self._reposition()
        self._ready.set()
        self._poll_commands()
        root.mainloop()
        # mainloop 退出后，在 tk 线程内完成清理
        try:
            root.destroy()
        except Exception:
            pass
        self._root = None
        self._done.set()

    def _reposition(self):
        root = self._root
        root.update_idletasks()
        w = root.winfo_reqwidth()
        h = root.winfo_reqheight()
        sx = root.winfo_screenwidth()
        sy = root.winfo_screenheight()
        root.geometry(f"{w}x{h}+{sx - w - 30}+{sy - h - 60}")

    def _poll_commands(self):
        try:
            while True:
                cmd = self._cmd_queue.get_nowait()
                cmd()
        except queue.Empty:
            pass
        if self._root:
            self._root.after(50, self._poll_commands)

    def _send(self, fn):
        self._cmd_queue.put(fn)

    def update(self, title: str, number: str = "", subtitle: str = ""):
        def _do():
            self._title_label.config(text=title)
            self._num_label.config(text=number)
            self._sub_label.config(text=subtitle)
            self._reposition()
        self._send(_do)

    def close(self, delay_s: float = 0):
        def _quit():
            if delay_s > 0:
                self._root.after(int(delay_s * 1000), self._root.quit)
            else:
                self._root.quit()
        self._send(_quit)
        self._thread.join(timeout=delay_s + 5)

    def countdown(self, seconds: int, title: str, subtitle: str = ""):
        finished = threading.Event()
        self.update(title, str(seconds), subtitle)

        def _tick(remaining):
            if remaining <= 0:
                finished.set()
                return
            self.update(title, str(remaining), subtitle)
            self._root.after(1000, lambda: _tick(remaining - 1))

        def _start():
            self._root.after(1000, lambda: _tick(seconds - 1))

        self._send(_start)
        finished.wait()
