import logging
import numpy as np
from bisect import bisect_left, bisect_right
from scipy.interpolate import InterpolatedUnivariateSpline


class Isotope(object):
    def __init__(self, master):
        self.master = master
        self.logger = logging.getLogger(__name__)
        self.settings = master.settings
        self.parameters = master.parameters
        self.data_subset = None
        self.fraction = None
        self.exact_mass = None
        self.accurate_mass = None
        self.intensity = None

    def inherit_data_subset(self):
        if self.parameters.calibration == True:
            mass_window = self.settings.calibration_window
        if self.parameters.quantitation == True:
            mass_window = self.settings.mass_window

        x_data, y_data = zip(*self.master.data_subset)
        left_border = bisect_left(x_data, self.exact_mass-mass_window)
        right_border = bisect_right(x_data, self.exact_mass+mass_window)
        x_subset = x_data[left_border:right_border]
        y_subset = y_data[left_border:right_border]
        self.data_subset = list(zip(x_subset, y_subset))

    def get_accurate_mass(self):
        x_subset, y_subset = zip(*self.data_subset)
        x_interpolation = np.linspace(x_subset[0], x_subset[-1],
                                      2500*(x_subset[-1]-x_subset[0]))
        f = InterpolatedUnivariateSpline(x_subset, y_subset)
        y_interpolation = f(x_interpolation)
        max_value = max(y_interpolation)
        max_index = np.where(y_interpolation == max_value)
        self.accurate_mass = float(x_interpolation[max_index][0])

    def quantify_isotope(self):
        x_subset, _ = zip(*self.data_subset)
        average_spacing = (x_subset[-1] - x_subset[0]) / len(x_subset)
        for datapoint in self.data_subset:
            self.intensity += datapoint[1] * average_spacing
