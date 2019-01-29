#! /usr/bin/env python
#
# Copyright 2014-2019 Bas C. Jansen
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
from pathlib import Path, PurePath

# Third Party Imports
import matplotlib
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk
)
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

# Application Specific Imports
import MassyTools.gui.version as version
import MassyTools.gui.progress_bar as progressbar
import MassyTools.util.requirement_checker as req_check
import MassyTools.util.functions as functions
from MassyTools.gui.settings_window import SettingsWindow
from MassyTools.gui.about_window import AboutWindow
from MassyTools.gui.cite_window import CiteWindow
from MassyTools.bin.analyte import Analyte
from MassyTools.bin.mass_spectrum import MassSpectrum, finalize_plot
from MassyTools.bin.output import Output
from MassyTools.bin.process_parameters import ProcessParameters
from MassyTools.bin.output_parameters import OutputParameters
from MassyTools.bin.settings import Settings


class MassyToolsGui(object):
    @classmethod
    def run(cls):
        root = tk.Tk()
        MassyToolsGui(root)
        root.mainloop()

    def __init__(self, master):
        # Inherit Tk() root object
        self.root = master
        self.read_building_blocks()

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
        NavigationToolbar2Tk(canvas, master)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=tk.YES)
        canvas.draw()

        tk.Frame(master)
        master.title("MassyTools "+str(version.version))
        progress = progressbar.SimpleProgressBar(self)
        progress.bar.pack()
        if (Path.cwd() / 'ui' / 'Icon.ico').is_file():
            master.iconbitmap(default='./ui/Icon.ico')

        menu = tk.Menu(master)
        master.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='File', menu=file_menu)
        file_menu.add_command(label='Open Input File', command=
                              self.open_mass_spectrum)
        file_menu.add_command(label='Baseline Correct', command=
                              self.baseline_correct)
        file_menu.add_command(label='Normalize', command=
                              self.normalize_mass_spectrum)
        file_menu.add_command(label='Save', command=
                              self.save_mass_spectrum)

        calib_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='Calibration', menu=calib_menu)
        calib_menu.add_command(label='Open Calibration File', command=
                               self.open_calibration_file)
        calib_menu.add_command(label='Open Exclusion File', command=
                               self.foo)
        calib_menu.add_command(label='Calibrate', command=
                               self.calibrate_mass_spectrum)

        quantitation_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='Quantitation', menu=quantitation_menu)
        quantitation_menu.add_command(label='Open Quantitation File',
                                      command=self.open_quantitation_file)
        quantitation_menu.add_command(label='Quantify', command=
                                      self.quantify_mass_spectrum)

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
        curation_menu.add_command(label='Spectral Curation', command=
                                  self.foo)
        curation_menu.add_command(label='Analyte Curation', command=
                                  self.foo)

        settings_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='Settings', menu=settings_menu)
        settings_menu.add_command(label='Settings', command=
                                  self.settings_window)

        info_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='Information', menu=info_menu)
        info_menu.add_command(label='About MassyTools', command=
                              self.about_window)
        info_menu.add_command(label='Citing MassyTools', command=
                              self.cite_window)

        self.logger = logging.getLogger(__name__)
        self.base_dir = Path.cwd()
        self.settings = Settings(self)
        self.process_parameters = ProcessParameters(self)
        self.output_parameters = OutputParameters(self)
        self.axes = background_image
        self.canvas = canvas
        self.progress = progress

    # Placeholder
    def foo(self):
        raise NotImplementedError

    # Actual Functions
    def about_window(self):
        try:
            AboutWindow()
        except Exception as e:
            self.logger.error(e)

    def baseline_correct(self):
        try:
            self.axes.clear()
            for mass_spectrum in self.mass_spectra:
                mass_spectrum.baseline_correct()
                mass_spectrum.plot_mass_spectrum()
            finalize_plot(self)
        except Exception as e:
            self.logger.error(e)

    def calibrate_mass_spectrum(self):
        try:
            self.progress.reset_bar()
            self.process_parameters.calibration = True

            peak_list = functions.get_peak_list(
                self.process_parameters.calibration_file)
            self.peak_list = peak_list
            self.determine_and_attach_analytes()

            for index, mass_spectrum in enumerate(self.mass_spectra):
                mass_spectrum.calibrate()
                self.progress.counter.set((float(index) / len(
                                           self.mass_spectra))*100)
                self.progress.update_progress_bar()
            self.progress.fill_bar()

            self.axes.clear()
            for mass_spectrum in self.mass_spectra:
                mass_spectrum.plot_mass_spectrum()
            finalize_plot(self)

            self.process_parameters.calibration = False

            if not self.process_parameters.calibration_file:
                messagebox.showinfo('Warning','No Calibration File '+
                                    'Selected')
        except Exception as e:
            self.logger.error(e)

    def quantify_mass_spectrum(self):
        try:
            self.progress.reset_bar()
            self.process_parameters.quantitation = True

            peak_list = functions.get_peak_list(
                self.process_parameters.quantitation_file)
            self.peak_list = peak_list
            self.determine_and_attach_analytes()
            for index, mass_spectrum in enumerate(self.mass_spectra):
                self.progress.counter.set((float(index) / len(
                                           self.mass_spectra))*100)
                self.progress.update_progress_bar()
                for analyte in mass_spectrum.analytes:
                    analyte.determine_background()
                    max_fraction = max(isotope.fraction for isotope in
                                       analyte.isotopes)
                    for isotope in analyte.isotopes:
                        if isotope.fraction == max_fraction:
                            isotope.get_accurate_mass()
                        isotope.quantify_isotope()
            self.progress.fill_bar()

            self.output = Output(self)
            self.output.init_output_file()
            self.output.build_header()
            self.output.build_output_file()

            self.process_parameters.quantitation = False

        except Exception as e:
            self.logger.error(e)

    def determine_and_attach_analytes(self):
        try:
            analytes = []
            for peak in self.peak_list:
                self.peak = peak
                analyte_buffer = Analyte(self)
                analyte_buffer.calculate_isotopes()
                analytes.append(analyte_buffer)

            for mass_spectrum in self.mass_spectra:
                self.mass_spectrum = mass_spectrum
                self.mass_spectrum.analytes = analytes
                for analyte in self.mass_spectrum.analytes:
                    analyte.inherit_data_subset()
                    max_fraction = max(isotope.fraction for isotope in
                                       analyte.isotopes)
                    for isotope in analyte.isotopes:
                        isotope.inherit_data_subset()
                        if isotope.fraction == max_fraction:
                            isotope.get_accurate_mass()
        except Exception as e:
            self.logger.error(e)

    def cite_window(self):
        try:
            CiteWindow()
        except Exception as e:
            self.logger.erorr(e)

    def normalize_mass_spectrum(self):
        try:
            for mass_spectrum in self.mass_spectra:
                mass_spectrum.normalize_mass_spectrum()

            if self.mass_spectra:
                self.axes.clear()
                for mass_spectrum in self.mass_spectra:
                    mass_spectrum.plot_mass_spectrum()
                finalize_plot(self)
        except Exception as e:
            self.logger.error(e)

    def open_calibration_file(self):
        try:
            cal_file = filedialog.askopenfilename(title='Select '+
                                                  'Calibration File')
            self.process_parameters.calibration_file = cal_file
        except Exception as e:
            self.logger.error(e)

    def open_mass_spectrum(self):
        try:
            data_buffer = []
            files = filedialog.askopenfilenames(title='Select Mass '+
                                                'Spectrum File(s)')
            for file in files:
                self.filename = file
                mass_spec_buffer = MassSpectrum(self)
                mass_spec_buffer.open_mass_spectrum()
                data_buffer.append(mass_spec_buffer)
            self.mass_spectra = data_buffer

            if self.mass_spectra:
                self.axes.clear()
                for mass_spectrum in self.mass_spectra:
                    mass_spectrum.plot_mass_spectrum()
                finalize_plot(self)
        except Exception as e:
            messagebox.showinfo('Warning','The selected files could '+
                                'not be opened.')
            self.logger.error(e)

    def open_quantitation_file(self):
        try:
            quant_file = filedialog.askopenfilename(title=
                                                    'Select Quantitation File')
            self.process_parameters.quantitation_file = quant_file
        except Exception as e:
            self.logger.error(e)

    def read_building_blocks(self):
        building_blocks = {}
        block_folder = Path.cwd() / 'blocks'
        for file in block_folder.glob('*.block'):
            block = PurePath(file).stem
            keys = []
            values = []
            with open(file,'r') as fr:
                for line in fr:
                    foo = line.rstrip().split()
                    key = foo[0]
                    value = " ".join(foo[1:])
                    keys.append(key)
                    try:
                        float(value)
                        try:
                            value = int(value)
                        except ValueError:
                            value = float(value)
                    except ValueError:
                        value = str(value)
                    values.append(value)
            building_blocks[block] = dict(zip(keys,values))
        self.building_blocks = building_blocks

    def save_mass_spectrum(self):
        try:
            for mass_spectrum in self.mass_spectra:
                mass_spectrum.save_mass_spectrum()
        except Exception as e:
            self.logger.error(e)

    def settings_window(self):
        try:
            SettingsWindow(self)
        except Exception as e:
            self.logger.error(e)

if __name__ == "__main__":
    MassyToolsGui.run()
