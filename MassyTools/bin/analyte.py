import itertools
import logging
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
        self.building_blocks = master.building_blocks

        self.name = master.peak['name']
        self.data_subset = None
        self.isotopes = []

    def inherit_data_subset(self):
        x_data, y_data = zip(*self.master.mass_spectrum.data)
        max_fraction = max(isotope.fraction for isotope in self.isotopes)
        for isotope in self.isotopes:
            if isotope.fraction == max_fraction:
                center_mass = isotope.exact_mass
        left_border = bisect_left(x_data, center_mass-self.settings.mass_window)
        right_border = bisect_right(x_data, center_mass+self.settings.mass_window)
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
        distributions = self.calculate_elemental_distributions(self)
        isotopic_pattern = combine_distributions(distributions)
        isotopic_pattern = merge_distributions(isotopic_pattern)
    
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
        return {'carbons': carbons, 'hydrogens': hydrogens,
                'nitrogens': nitrogens, 'oxygens17': oxygens17,
                'oxygens18': oxygens18, 'sulfurs33':sulfurs33,
                'sulfurs34': sulfurs34, 'sulfurs36': sulfurs36}

        # Merge
        intermediate_results = []
        newdata = {d: True for d in totals}
        for k, v in totals:
            if not newdata[(k, v)]: continue
            newdata[(k, v)] = False
            # use each piece of data only once
            keys, values = [k*v], [v]
            for kk, vv in [d for d in totals if newdata[d]]:
                if abs(k-kk) < self.settings.epsilon:
                    keys.append(kk*vv)
                    values.append(vv)
                    newdata[(kk, vv)] = False
            intermediate_results.append((sum(keys)/sum(values), sum(values)))
        
        # Sort
        intermediate_results = sorted(intermediate_results, key=itemgetter(1),
                                      reverse=True)
        results = []
        totals = 0.
        for intermediate_result in intermediate_results:
            results.append(intermediate_result)
            totals += intermediate_result[1]
            if totals > self.settings.min_total_contribution:
                break
        results = sorted(results, key=itemgetter(0))

        # Create isotopes and add them to analyte
        for result in results:
            isotope_buffer = Isotope(self)
            isotope_buffer.exact_mass = result[0]
            isotope_buffer.fraction = result[1]
            self.isotopes.append(isotope_buffer)

# Non class functions
def combine_distributions(distributions):
    totals = []
    #for x in itertools.product(carbons, hydrogens, nitrogens, oxygens17, oxygens18, sulfurs33, sulfurs34, sulfurs36):
    for x in itertools.product(
        distributions['carbons'], distributions['hydrogens'],
        distributions['nitrogens'], distributions['oxygens17'],
        distributions['oxygens18'], distributions['sulfurs33'],
        distrubtions['sulfurs34'], distributions['sulfurs36']
    ):
        i, j, k, l, m, n, o, p = x
        totals.append((self.mass+i[0]+j[0]+k[0]+l[0]+m[0]+n[0]+o[0]+p[0],
                       i[1]*j[1]*k[1]*l[1]*m[1]*n[1]*o[1]*p[1]))
    return totals

def merge_distributions(totals):
    intermediate_results = []
    newdata = {d: True for d in totals}
    for k, v in totals:
        if not newdata[(k, v)]: continue
        newdata[(k, v)] = False
        # use each piece of data only once
        keys, values = [k*v], [v]
        for kk, vv in [d for d in totals if newdata[d]]:
            if abs(k-kk) < self.settings.epsilon:
                keys.append(kk*vv)
                values.append(vv)
                newdata[(kk, vv)] = False
        intermediate_results.append((sum(keys)/sum(values), sum(values)))
    return intermediate_results
