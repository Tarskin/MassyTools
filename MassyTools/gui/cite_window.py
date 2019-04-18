import tkinter as tk


class CiteWindow(object):
    INFORMATION = ("To cite MassyTools, please use the following reference:"+
                   "\n\nMassyTools: A High-Throughput Targeted Data "+
                   "Processing Tool for Relative Quantitation and Quality "+
                   "Control Developed for Glycomic and Glycoproteomic "+
                   "MALDI-MS. Bas C. Jansen, Karli R. Reiding, Albert Bondt, "+
                   "Agnes L. Hipgrave Ederveen, Magnus Palmblad, David "+
                   "Falck, and Manfred Wuhrer. Journal of Proteome Research "+
                   "2015: 14 (12), 5088-5098. DOI: 10.1021/acs.jproteome."+
                   "5b00658.")
    def __init__(self):
        root = tk.Toplevel()
        frame = tk.Frame(root)

        root.title("Citing MassyTools")
        root.resizable(width=False, height=False)
        root.protocol("WM_DELETE_WINDOW", self.close)

        about = tk.Label(frame, text=self.INFORMATION, justify=tk.LEFT,
                         wraplength=250)

        about.pack()
        frame.pack()
        root.lift()

        self.root = root

    def close(self):
        self.root.destroy()
