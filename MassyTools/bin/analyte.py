import itertools
import logging
import sys
import numpy as np
from bisect import bisect_left, bisect_right
from operator import itemgetter
import MassyTools.util.functions as functions
import MassyTools.bin.elemental_abundances as elemental_abundances
from MassyTools.bin.isotope import Isotope


class Analyte(object):
    def __init__(self, master):
        self.master = master
        self.logger = logging.getLogger(__name__)
        self.settings = master.settings
        self.process_parameters = master.process_parameters
        self.building_blocks = master.building_blocks

        self.name = master.peak['name']
        self.data_subset = None
        self.distributions = None
        self.isotopic_pattern = None
        self.background_area = None
        self.background_intensity = None
        self.noise = None
        self.isotopes = []

    def inherit_data_subset(self):
        mass_window = self.settings.background_window+self.settings.mass_window

        x_data, y_data = zip(*self.master.mass_spectrum.data)
        max_fraction = max(isotope.fraction for isotope in self.isotopes)
        for isotope in self.isotopes:
            if isotope.fraction == max_fraction:
                center_mass = isotope.exact_mass
        left_border = bisect_left(x_data, center_mass-mass_window)
        right_border = bisect_right(x_data, center_mass+mass_window)
        self.data_subset = list(zip(x_data[left_border:right_border],
                                y_data[left_border:right_border]))

    def calculate_isotopes(self):
        self.mass = 0.
        self.number_carbons = 0
        self.number_hydrogens = 0
        self.number_nitrogens = 0
        self.number_oxygens = 0
        self.number_sulfurs = 0
        self.number_sialic_acids = 0
        self.total_number_elements = 0
        self.total_number_units = 0

        self.determine_total_number_of_elements()
        self.attach_mass_modifiers()
        self.calculate_analyte_isotopic_pattern()

    def determine_total_number_of_elements(self):
        units = ["".join(x) for _, x in itertools.groupby(self.name,
                                                          key=str.isalpha)]
        for index, unit in enumerate(units):
            for block in self.building_blocks.keys():
                if unit == block:
                    self.mass += (self.building_blocks[block]['mass']
                                  *int(units[index+1]))
                    self.number_carbons += (self.building_blocks[block]
                                            ['carbons']*int(units[index+1]))
                    self.number_hydrogens += (self.building_blocks[block]
                                              ['hydrogens']*int(units[index+1]))
                    self.number_nitrogens += (self.building_blocks[block]
                                              ['nitrogens']*int(units[index+1]))
                    self.number_oxygens += (self.building_blocks[block]
                                            ['oxygens']*int(units[index+1]))
                    self.number_sulfurs += (self.building_blocks[block]
                                            ['sulfurs']*int(units[index+1]))
                    self.total_number_units += int(units[index+1])
                    if unit == 'S':
                        self.number_sialic_acids += int(units[index+1])

    def determine_background(self):
        background_point = sys.maxsize
        x_data, y_data = zip(*self.data_subset)

        max_fraction = max(isotope.fraction for isotope in self.isotopes)
        for isotope in self.isotopes:
            if isotope.fraction == max_fraction:
                center_mass = isotope.exact_mass

        for windows in range(-self.settings.background_window,
                             self.settings.background_window,
                             self.settings.background_chunks):

            values = []
            averages = []

            if (len(range(windows, windows+self.settings.background_chunks)) !=
                self.settings.background_chunks):
                break

            for j in range(windows, windows+self.settings.background_chunks):
                curr_mass = center_mass + j * elemental_abundances.carbon[0][2]
                left_edge = bisect_left(x_data, curr_mass-self.settings.mass_window)
                right_edge = bisect_right(x_data, curr_mass+self.settings.mass_window)
                values.extend(y_data[left_edge:right_edge])
                averages.append(np.average(y_data[left_edge:right_edge]))

            if np.average(values) < background_point:
                self.background_intensity = np.average(values)
                self.background_area = np.average(averages)
                self.noise = np.std(values)

    def attach_mass_modifiers(self):
        total_modifiers = list(self.settings.mass_modifiers)
        total_modifiers.append(self.settings.charge_carrier)

        # Modifiers that are independent of other modifiers
        for modifier in total_modifiers:
            if str(modifier) != "Per":
                self.mass += self.building_blocks[modifier]['mass']
                self.number_carbons += (self.building_blocks[modifier]
                                        ['carbons'])
                self.number_hydrogens += (self.building_blocks[modifier]
                                          ['hydrogens'])
                self.number_nitrogens += (self.building_blocks[modifier]
                                          ['nitrogens'])
                self.number_oxygens += (self.building_blocks[modifier]
                                        ['oxygens'])
                self.number_sulfurs += (self.building_blocks[modifier]
                                        ['sulfurs'])

        # Modifiers that can affect other modifiers
        # TODO: Test the permethylation after succesful refactoring!!
        for modifier in total_modifiers:
            if str(modifier) == "Per":
                number_sites = (
                    self.number_oxygens - (self.total_number_of_units * 2 - 2)
                    - 1 - (1 * self.number_sialic_acids)
                )
                self.number_carbons += (self.building_blocks[modifier]
                                        ['carbons'] * number_sites)
                self.number_hydrogens += (self.building_blocks[modifier]
                                          ['hydrogens'] * number_sites * 2)
                self.mass += (self.building_blocks[modifier]['mass'] *
                              number_sites)

    def calculate_analyte_isotopic_pattern(self):
        self.calculate_elemental_distributions()
        self.combine_distributions()
        self.merge_isotopic_pattern()
        self.sort_isotopic_pattern()
        self.attach_isotopes()

    def calculate_elemental_distributions(self):
        carbons = functions.calculate_elemental_isotopic_pattern(
                  elemental_abundances.carbon, self.number_carbons)
        hydrogens = functions.calculate_elemental_isotopic_pattern(
                  elemental_abundances.hydrogen, self.number_hydrogens)
        nitrogens = functions.calculate_elemental_isotopic_pattern(
                  elemental_abundances.nitrogen, self.number_nitrogens)
        oxygens17 = functions.calculate_elemental_isotopic_pattern(
                  elemental_abundances.oxygen17, self.number_oxygens)
        oxygens18 = functions.calculate_elemental_isotopic_pattern(
                  elemental_abundances.oxygen18, self.number_oxygens)
        sulfurs33 = functions.calculate_elemental_isotopic_pattern(
                  elemental_abundances.sulfur33, self.number_sulfurs)
        sulfurs34 = functions.calculate_elemental_isotopic_pattern(
                  elemental_abundances.sulfur34, self.number_sulfurs)
        sulfurs36 = functions.calculate_elemental_isotopic_pattern(
                  elemental_abundances.sulfur36, self.number_sulfurs)
        self.distributions = {'carbons': carbons, 'hydrogens': hydrogens,
                                'nitrogens': nitrogens, 'oxygens17': oxygens17,
                                'oxygens18': oxygens18, 'sulfurs33':sulfurs33,
                                'sulfurs34': sulfurs34, 'sulfurs36': sulfurs36}

    def combine_distributions(self):
        totals = []
        for x in itertools.product(
            self.distributions['carbons'], self.distributions['hydrogens'],
            self.distributions['nitrogens'], self.distributions['oxygens17'],
            self.distributions['oxygens18'], self.distributions['sulfurs33'],
            self.distributions['sulfurs34'], self.distributions['sulfurs36']
        ):
            i, j, k, l, m, n, o, p = x
            totals.append((self.mass+i[0]+j[0]+k[0]+l[0]+m[0]+n[0]+o[0]+p[0],
                           i[1]*j[1]*k[1]*l[1]*m[1]*n[1]*o[1]*p[1]))
        self.distributions = totals

    def attach_isotopes(self):
        for isotope in self.isotopic_pattern:
            isotope_buffer = Isotope(self)
            isotope_buffer.exact_mass = isotope[0]
            isotope_buffer.fraction = isotope[1]
            self.isotopes.append(isotope_buffer)

    def merge_isotopic_pattern(self):
        results = []
        newdata = {d: True for d in self.distributions}
        for k, v in self.distributions:
            if not newdata[(k, v)]: continue
            newdata[(k, v)] = False
            # use each piece of data only once
            keys, values = [k*v], [v]
            for kk, vv in [d for d in self.distributions if newdata[d]]:
                if abs(k-kk) < self.settings.epsilon:
                    keys.append(kk*vv)
                    values.append(vv)
                    newdata[(kk, vv)] = False
            results.append((sum(keys)/sum(values), sum(values)))
        self.isotopic_pattern = results

    def sort_isotopic_pattern(self):
        intermediate_results = sorted(self.isotopic_pattern, key=itemgetter(1),
                                      reverse=True)
        results = []
        totals = 0.
        for intermediate_result in intermediate_results:
            results.append(intermediate_result)
            totals += intermediate_result[1]
            if totals > self.settings.min_total_contribution:
                break
        results = sorted(results, key=itemgetter(0))
        self.isotopic_pattern = results
