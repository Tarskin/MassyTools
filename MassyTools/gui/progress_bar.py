import tkinter as tk
import tkinter.ttk as ttk


class SimpleProgressBar(object):
    def __init__(self, master):
        root = master.root
        self.counter = tk.IntVar()
        self.bar = ttk.Progressbar(root, orient="horizontal",
                                   length=1000, mode="determinate",
                                   variable=self.counter, maximum=100)

    def update_progress_bar(self):
        self.bar.update()

    def reset_bar(self):
        self.counter.set(0)
        self.bar.update()

    def fill_bar(self):
        self.counter.set(100)
        self.bar.update()
