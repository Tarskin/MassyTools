#! /usr/bin/env python
#
# Copyright 2014-2018 Bas C. Jansen
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You should have received a copy of the Apache 2.0 license along
# with this program; if not, see
# http://www.apache.org/licenses/LICENSE-2.0

# Standard Library Imports
import logging
from pathlib import Path

# Third Party Imports
import matplotlib
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk
)
import tkinter as tk

# Application Specific Imports
import MassyTools.gui.version as version
import MassyTools.util.requirement_checker as req_check
from MassyTools.bin.mass_spectrum import MassSpectrum, finalize_plot

class MassyToolsGui(object):
    @classmethod
    def run(cls):
        root = tk.Tk()
        MassyToolsGui(root)
        root.mainloop()

    def __init__(self, master):

        logging.basicConfig(filename='MassyTools.log',
            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M', filemode='a',
            level=logging.WARNING)
        req_check.check_requirements()

        fig = matplotlib.figure.Figure(figsize=(8, 6))
        if (Path.cwd() / 'ui' / 'UI.png').is_file():
            background_image = fig.add_subplot(111)
            image = matplotlib.image.imread('./ui/UI.png')
            background_image.axis('off')
            fig.set_tight_layout(True)
            background_image.imshow(image, aspect='auto')
        canvas = FigureCanvasTkAgg(fig, master=master)
        toolbar = NavigationToolbar2Tk(canvas, master)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=tk.YES)
        canvas.draw()

        frame = tk.Frame(master)
        master.title("MassyTools "+str(version.version))
        if (Path.cwd() / 'ui' / 'Icon.ico').is_file():
            master.iconbitmap(default='./ui/Icon.ico')

        menu = tk.Menu(master)
        master.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='File', menu=file_menu)
        file_menu.add_command(label='Open Input File', command=
                              self.open_mass_spectrum)

        calib_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='Calibration', menu=calib_menu)
        calib_menu.add_command(label='Open Calibration File', command=self.foo)
        calib_menu.add_command(label='Open Exclusion File', command=self.foo)
        calib_menu.add_command(label='Calibrate', command=self.foo)

        quantitation_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='Quantitation', menu=quantitation_menu)
        quantitation_menu.add_command(label='Open Composition File',
                                   command=self.foo)
        quantitation_menu.add_command(label='Quantify', command=self.foo)

        quality_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='QC', menu=quality_menu)
        quality_menu.add_command(label='Open Quality Control File',
                                command=self.foo)
        quality_menu.add_command(label='Calculate QC', command=self.foo)

        batch_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='Batch Process', menu=batch_menu)
        batch_menu.add_command(label='Batch Process', command=self.foo)

        curation_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='Data Curation', menu=curation_menu)
        curation_menu.add_command(label='Spectral Curation', command=self.foo)
        curation_menu.add_command(label='Analyte Curation', command=self.foo)

        settings_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='Settings', menu=settings_menu)
        settings_menu.add_command(label='Settings', command=self.foo)

        about_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='About', menu=about_menu)
        about_menu.add_command(label='About MassyTools', command=self.foo)

        self.fig = fig
        self.axes = background_image
        self.canvas = canvas

    def foo(self):
        raise NotImplementedError

    def open_mass_spectrum(self):
        data_buffer = []
        files = tk.filedialog.askopenfilenames(title=
                                               'Select Mass Spectrum File(s)')
        for file in files:
            self.filename = file
            data_buffer.append(MassSpectrum(self))
        self.mass_spectra = data_buffer

        if self.mass_spectra:
            self.axes.clear()
            for mass_spectrum in self.mass_spectra:
                mass_spectrum.plot_mass_spectrum()
            finalize_plot(self)

if __name__ == "__main__":
    MassyToolsGui.run()
