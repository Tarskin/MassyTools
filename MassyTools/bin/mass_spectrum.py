from pathlib import Path, PurePath
import logging
import numpy as np
import MassyTools.util.file_parser as file_parser


class MassSpectrum(object):
    def __init__(self, master):
        self.settings = master.settings
        self.process_parameters = master.process_parameters
        self.building_blocks = master.building_blocks
        self.logger = logging.getLogger(__name__)
        self.axes = master.axes
        self.filename = master.filename
        self.analytes = []
        self.data = None

    def baseline_correct(self):
        _, y_values = zip(*self.data)
        y_average = np.average(y_values)
        y_std = np.std(y_values)

        subset = [(x, y) for (x, y) in self.data if y >= y_average-y_std and
                  y <= y_average+y_std]
        x_subset, y_subset = zip(*subset)

        p = np.polynomial.polynomial.polyfit(x_subset, y_subset, 3)
        f = np.polynomial.polynomial.Polynomial(p)

        self.data = [(x, y-f(x)) for x, y in self.data]

    def calibrate(self):
        accurate_masses = []
        exact_masses = []
        for analyte in self.analytes:
            analyte.determine_background()
            for isotope in analyte.isotopes:
                if isotope.accurate_mass:
                    isotope.inherit_data_subset()
                    isotope.quantify_isotope()
                    sn = ((isotope.intensity - analyte.background_intensity) /
                        analyte.noise)
                    if sn >= self.settings.calibration_sn_cutoff:
                        accurate_masses.append(isotope.accurate_mass)
                        exact_masses.append(isotope.exact_mass)
                    else:
                        self.logger.warning(str(analyte.name)+" to low S/N")
        x_values, y_values = zip(*self.data)
        if len(accurate_masses) < self.settings.num_total:
            calibrated_x_values = x_values
            self.logger.warning(str(self.filename)+" not calibrated")
        else:
            calibration_parameters = np.polyfit(accurate_masses, exact_masses, 2)
            calibration_function = np.poly1d(calibration_parameters)
            calibrated_x_values = calibration_function(x_values)
        self.data = list(zip(calibrated_x_values, y_values))

    def normalize_mass_spectrum(self):
        x_array, y_array = zip(*self.data)
        maximum = max(y_array)
        normalized_y_array = [x/maximum for x in y_array]
        self.data = list(zip(x_array, normalized_y_array))

    def open_mass_spectrum(self):
        file_type = None
        with Path(self.filename).open() as fr:
            for line in fr:
                # Prototype (File Recognition)
                if 'utter_nonsense' in line:
                    file_type = 'Bruker'

        if file_type == None:
            try:
                file_parser.open_xy_spectrum(self)
            except Exception as e:
                self.logger.error(e)

    def plot_mass_spectrum(self):
        label = PurePath(self.filename).stem
        x_array, y_array = zip(*self.data)
        self.axes.plot(x_array, y_array, label=str(label))

    def save_mass_spectrum(self):
        with Path(self.filename).open('w') as fw:
            for data_point in self.data:
                fw.write(
                    str(format(data_point[0], '0.' +
                        str(self.settings.decimal_numbers)+'f'))+'\t' +
                    str(format(data_point[1], '0.' +
                        str(self.settings.decimal_numbers)+'f'))+'\n')

def finalize_plot(master):
    master.axes.set_xlabel('m/z [Th]')
    master.axes.set_ylabel('Intensity [au]')
    handles, labels = master.axes.get_legend_handles_labels()
    master.axes.legend(handles, labels)
    master.axes.get_xaxis().get_major_formatter().set_useOffset(False)
    master.canvas.draw_idle()
