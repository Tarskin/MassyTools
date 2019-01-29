import tkinter as tk


class OutputParameters(object):
    def __init__(self, master):
        self.absolute_intensity = tk.IntVar()
        self.relative_intensity = tk.IntVar()
        self.background_subtraction = tk.IntVar()
        self.analyte_quality_criteria = tk.IntVar()
        self.spectral_quality_criteria = tk.IntVar()
