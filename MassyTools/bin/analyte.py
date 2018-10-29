import logging
from bisect import bisect_left, bisect_right


class Analyte(object):
    def __init__(self, master):
        self.logger = logging.getLogger(__name__)
        self.settings = master.settings

    def get_accurate_mass(self):
        x_data, y_data = zip(*self.data)
        left_border = bisect_left(x_data, self.exact_mass-
                                  self.settings.mass_window)
        right_border = bisect_right(x_data, self.exact_mass+
                                    self.settings.mass_window)
        max_index = max(y_data[left_border:right_border])+left_border
        self.accurate_mass = x_data[max_index]
