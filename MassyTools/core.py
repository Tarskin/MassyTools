from dataclasses import dataclass, field
import itertools
import logging
import math
from bisect import bisect_left, bisect_right
from operator import itemgetter
from pathlib import Path, PurePath

import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline

from MassyTools.blocks import load_building_blocks
from MassyTools.bin import elemental_abundances


ELEMENT_KEYS = ("carbons", "hydrogens", "nitrogens", "oxygens", "sulfurs")
ELEMENT_BLOCKS = {
    "carbons": "_C",
    "hydrogens": "_H",
    "nitrogens": "_N",
    "oxygens": "_O",
    "sulfurs": "_S",
}
COMPOSITION_ALIASES = {
    "C": "carbons",
    "H": "hydrogens",
    "N": "nitrogens",
    "O": "oxygens",
    "S": "sulfurs",
}


@dataclass
class AnalysisSettings:
    mass_modifiers: list = field(default_factory=lambda: ["free"])
    charge_carrier: str = "sodium"
    min_charge_state: int = 1
    max_charge_state: int = 1
    background_window: int = 20
    calibration_window: float = 0.4
    calibration_sn_cutoff: float = 9.0
    num_total: int = 5
    mass_window: float = 0.2
    sn_cutoff: float = 9.0
    min_total_contribution: float = 0.95
    min_contribution: float = 0.0001
    background_chunks: int = 4
    epsilon: float = 0.1
    decimal_numbers: int = 8


@dataclass
class Isotope:
    exact_mass: float
    fraction: float
    charge: int = 1
    analyte: object = None
    data_subset: list = field(default_factory=list)
    accurate_mass: float = None
    area: float = None
    maximum_intensity: float = None
    total_intensity: float = None

    def inherit_data_subset(self, mass_window=None):
        if self.analyte is None:
            raise ValueError("Cannot inherit data without an analyte parent.")
        if mass_window is None:
            mass_window = self.analyte.settings.mass_window / self.charge

        x_data, y_data = zip(*self.analyte.data_subset)
        left_border = bisect_left(x_data, self.exact_mass - mass_window)
        right_border = bisect_right(x_data, self.exact_mass + mass_window)
        self.data_subset = list(zip(x_data[left_border:right_border],
                                    y_data[left_border:right_border]))
        return self

    def get_accurate_mass(self):
        if not self.data_subset:
            return None
        x_subset, y_subset = zip(*self.data_subset)
        x_interpolation = np.linspace(x_subset[0], x_subset[-1],
                                      int(2500 * (x_subset[-1] - x_subset[0])))
        f = InterpolatedUnivariateSpline(x_subset, y_subset)
        y_interpolation = f(x_interpolation)
        max_index = np.where(y_interpolation == max(y_interpolation))
        self.accurate_mass = float(x_interpolation[max_index][0])
        return self.accurate_mass

    def quantify(self):
        if not self.data_subset:
            return self
        self.maximum_intensity = -math.inf
        self.total_intensity = 0
        self.area = 0.0
        x_subset, _ = zip(*self.data_subset)
        average_spacing = (x_subset[-1] - x_subset[0]) / len(x_subset)
        for _, intensity in self.data_subset:
            self.area += intensity * average_spacing
            self.maximum_intensity = max(self.maximum_intensity, intensity)
            self.total_intensity += intensity
        return self

    def to_dict(self):
        return {
            "exact_mass": self.exact_mass,
            "fraction": self.fraction,
            "charge": self.charge,
            "accurate_mass": self.accurate_mass,
            "area": self.area,
            "maximum_intensity": self.maximum_intensity,
            "total_intensity": self.total_intensity,
        }


@dataclass
class Analyte:
    name: str
    charge: int = 1
    composition: dict = None
    settings: AnalysisSettings = field(default_factory=AnalysisSettings)
    building_blocks: dict = field(default_factory=load_building_blocks)
    spectrum: object = None
    data_subset: list = field(default_factory=list)
    isotopes: list = field(default_factory=list)
    distributions: list = field(default_factory=list)
    isotopic_pattern: list = field(default_factory=list)
    mass: float = 0.0
    background_area: float = None
    background_intensity: float = None
    noise: float = None

    def __post_init__(self):
        if self.composition is None:
            self.composition = self.composition_from_blocks(self.name)
        else:
            self.composition = self.normalize_composition(self.composition)
            self.calculate_mass_from_composition()
        self.base_composition = dict(self.composition)
        self.base_mass = self.mass
        self.base_total_number_units = self.total_number_units
        self.base_number_sialic_acids = self.number_sialic_acids

    @classmethod
    def from_chnos(cls, name, carbons=0, hydrogens=0, nitrogens=0, oxygens=0,
                   sulfurs=0, **kwargs):
        return cls(
            name=name,
            composition={
                "carbons": carbons,
                "hydrogens": hydrogens,
                "nitrogens": nitrogens,
                "oxygens": oxygens,
                "sulfurs": sulfurs,
            },
            **kwargs,
        )

    @property
    def number_carbons(self):
        return self.composition["carbons"]

    @property
    def number_hydrogens(self):
        return self.composition["hydrogens"]

    @property
    def number_nitrogens(self):
        return self.composition["nitrogens"]

    @property
    def number_oxygens(self):
        return self.composition["oxygens"]

    @property
    def number_sulfurs(self):
        return self.composition["sulfurs"]

    def composition_from_blocks(self, formula):
        units = ["".join(x) for _, x in itertools.groupby(formula,
                                                          key=str.isalpha)]
        composition = {key: 0 for key in ELEMENT_KEYS}
        self.mass = 0.0
        self.total_number_units = 0
        self.number_sialic_acids = 0

        for index, unit in enumerate(units):
            if not unit.isalpha():
                continue
            if unit not in self.building_blocks:
                raise ValueError(f"Unknown building block: {unit}")
            count = 1
            if index + 1 < len(units) and units[index + 1].isdigit():
                count = int(units[index + 1])
            block = self.building_blocks[unit]
            self.mass += block["mass"] * count
            for key in ELEMENT_KEYS:
                composition[key] += block[key] * count
            self.total_number_units += count
            if unit == "S":
                self.number_sialic_acids += count
        return composition

    def normalize_composition(self, composition):
        normalized = {key: 0 for key in ELEMENT_KEYS}
        for key, value in composition.items():
            normalized_key = COMPOSITION_ALIASES.get(key, key)
            if normalized_key not in normalized:
                raise ValueError(f"Unknown elemental composition key: {key}")
            normalized[normalized_key] = int(value)
        return normalized

    def calculate_mass_from_composition(self):
        self.mass = 0.0
        for key, block_name in ELEMENT_BLOCKS.items():
            self.mass += self.building_blocks[block_name]["mass"] * self.composition[key]
        self.total_number_units = 0
        self.number_sialic_acids = 0

    def reset_composition(self):
        self.composition = dict(self.base_composition)
        self.mass = self.base_mass
        self.total_number_units = self.base_total_number_units
        self.number_sialic_acids = self.base_number_sialic_acids

    def attach_mass_modifiers(self):
        for modifier in list(self.settings.mass_modifiers) + (
                [self.settings.charge_carrier] * self.charge):
            if modifier == "Per":
                number_sites = (
                    self.composition["oxygens"] - (self.total_number_units * 2 - 2)
                    - 1 - self.number_sialic_acids
                )
                self.mass += self.building_blocks[modifier]["mass"] * number_sites
                self.composition["carbons"] += self.building_blocks[modifier]["carbons"] * number_sites
                self.composition["hydrogens"] += self.building_blocks[modifier]["hydrogens"] * number_sites * 2
                continue

            block = self.building_blocks[modifier]
            self.mass += block["mass"]
            for key in ELEMENT_KEYS:
                self.composition[key] += block[key]

    def calculate_isotopes(self):
        self.reset_composition()
        self.isotopes = []
        self.distributions = []
        self.isotopic_pattern = []
        self.attach_mass_modifiers()
        self.calculate_elemental_distributions()
        self.combine_distributions()
        self.merge_isotopic_pattern()
        self.sort_isotopic_pattern()
        self.attach_isotopes()
        return self.isotopes

    def calculate_elemental_distributions(self):
        self.distributions = {
            "carbons": self._calculate_elemental_pattern(
                elemental_abundances.carbon, self.composition["carbons"]),
            "hydrogens": self._calculate_elemental_pattern(
                elemental_abundances.hydrogen, self.composition["hydrogens"]),
            "nitrogens": self._calculate_elemental_pattern(
                elemental_abundances.nitrogen, self.composition["nitrogens"]),
            "oxygens17": self._calculate_elemental_pattern(
                elemental_abundances.oxygen17, self.composition["oxygens"]),
            "oxygens18": self._calculate_elemental_pattern(
                elemental_abundances.oxygen18, self.composition["oxygens"]),
            "sulfurs33": self._calculate_elemental_pattern(
                elemental_abundances.sulfur33, self.composition["sulfurs"]),
            "sulfurs34": self._calculate_elemental_pattern(
                elemental_abundances.sulfur34, self.composition["sulfurs"]),
            "sulfurs36": self._calculate_elemental_pattern(
                elemental_abundances.sulfur36, self.composition["sulfurs"]),
        }

    def combine_distributions(self):
        totals = []
        for items in itertools.product(
                self.distributions["carbons"], self.distributions["hydrogens"],
                self.distributions["nitrogens"], self.distributions["oxygens17"],
                self.distributions["oxygens18"], self.distributions["sulfurs33"],
                self.distributions["sulfurs34"], self.distributions["sulfurs36"]):
            mass_shift = sum(item[0] for item in items)
            fraction = math.prod(item[1] for item in items)
            totals.append(((self.mass + mass_shift) / self.charge, fraction))
        self.distributions = totals

    def merge_isotopic_pattern(self):
        results = []
        newdata = {d: True for d in self.distributions}
        for k, v in self.distributions:
            if not newdata[(k, v)]:
                continue
            newdata[(k, v)] = False
            keys, values = [k * v], [v]
            for kk, vv in [d for d in self.distributions if newdata[d]]:
                if abs(k - kk) < self.settings.epsilon:
                    keys.append(kk * vv)
                    values.append(vv)
                    newdata[(kk, vv)] = False
            results.append((sum(keys) / sum(values), sum(values)))
        self.isotopic_pattern = results

    def sort_isotopic_pattern(self):
        intermediate_results = sorted(self.isotopic_pattern, key=itemgetter(1),
                                      reverse=True)
        results = []
        total = 0.0
        for intermediate_result in intermediate_results:
            results.append(intermediate_result)
            total += intermediate_result[1]
            if total > self.settings.min_total_contribution:
                break
        self.isotopic_pattern = sorted(results, key=itemgetter(0))

    def attach_isotopes(self):
        self.isotopes = [
            Isotope(exact_mass=mass, fraction=fraction, charge=self.charge,
                    analyte=self)
            for mass, fraction in self.isotopic_pattern
        ]

    def inherit_data_subset(self):
        if self.spectrum is None or not self.spectrum.data:
            return self
        mass_window = self.settings.background_window + self.settings.mass_window
        x_data, y_data = zip(*self.spectrum.data)
        center_mass = max(self.isotopes, key=lambda isotope: isotope.fraction).exact_mass
        left_border = bisect_left(x_data, center_mass - mass_window)
        right_border = bisect_right(x_data, center_mass + mass_window)
        self.data_subset = list(zip(x_data[left_border:right_border],
                                    y_data[left_border:right_border]))
        return self

    def determine_background(self):
        if not self.data_subset:
            return self
        background_point = math.inf
        x_data, y_data = zip(*self.data_subset)
        center_mass = max(self.isotopes, key=lambda isotope: isotope.fraction).exact_mass
        for windows in range(-self.settings.background_window,
                             self.settings.background_window,
                             self.settings.background_chunks):
            values = []
            averages = []
            for j in range(windows, windows + self.settings.background_chunks):
                curr_mass = center_mass + j * elemental_abundances.carbon[0][2]
                left_edge = bisect_left(x_data, curr_mass - self.settings.mass_window)
                right_edge = bisect_right(x_data, curr_mass + self.settings.mass_window)
                values.extend(y_data[left_edge:right_edge])
                averages.append(np.average(y_data[left_edge:right_edge]))
            if values and np.average(values) < background_point:
                background_point = np.average(values)
                self.background_intensity = np.average(values)
                self.background_area = np.average(averages)
                self.noise = np.std(values)
        return self

    def to_dict(self, include_isotopes=True):
        result = {
            "name": self.name,
            "charge": self.charge,
            "composition": dict(self.base_composition),
            "modified_composition": dict(self.composition),
            "mass": self.mass,
            "background_area": self.background_area,
            "background_intensity": self.background_intensity,
            "noise": self.noise,
        }
        if include_isotopes:
            result["isotopes"] = [isotope.to_dict() for isotope in self.isotopes]
        return result

    def _calculate_elemental_pattern(self, element, number):
        fractions = []
        for isotope in element:
            last_fraction = 0.0
            for count in range(number + 1):
                n_choose_k = (
                    math.factorial(number) /
                    (math.factorial(count) * math.factorial(number - count))
                )
                fraction = (
                    n_choose_k * isotope[1] ** count *
                    (1 - isotope[1]) ** (number - count)
                )
                fractions.append((isotope[2] * count, fraction))
                if (fraction <= self.settings.min_contribution and
                        fraction < last_fraction):
                    break
                last_fraction = fraction
        return fractions


@dataclass
class Spectrum:
    name: str = None
    filename: str = None
    data: list = field(default_factory=list)
    settings: AnalysisSettings = field(default_factory=AnalysisSettings)
    building_blocks: dict = field(default_factory=load_building_blocks)
    experiment: object = None
    analytes: list = field(default_factory=list)
    logger: object = field(default_factory=lambda: logging.getLogger(__name__))

    def load_xy(self, filename=None):
        if filename is not None:
            self.filename = filename
        data = []
        with Path(self.filename).open() as fr:
            for line in fr:
                parts = line.rstrip().split()
                if parts:
                    data.append((float(parts[0]), float(parts[-1])))
        self.data = data
        if self.name is None:
            self.name = PurePath(self.filename).stem
        return self

    def add_analyte(self, name, charge=1, composition=None):
        analyte = Analyte(name=name, charge=charge, composition=composition,
                          settings=self.settings,
                          building_blocks=self.building_blocks,
                          spectrum=self)
        self.analytes.append(analyte)
        return analyte

    def process_analytes(self):
        for analyte in self.analytes:
            analyte.calculate_isotopes()
            if not self.data:
                continue
            analyte.inherit_data_subset()
            for isotope in analyte.isotopes:
                isotope.inherit_data_subset()
            most_abundant = max(analyte.isotopes, key=lambda item: item.fraction)
            most_abundant.get_accurate_mass()
        return self

    def baseline_correct(self):
        _, y_values = zip(*self.data)
        y_average = np.average(y_values)
        y_std = np.std(y_values)
        subset = [(x, y) for (x, y) in self.data
                  if y_average - y_std <= y <= y_average + y_std]
        x_subset, y_subset = zip(*subset)
        p = np.polynomial.polynomial.polyfit(x_subset, y_subset, 3)
        f = np.polynomial.polynomial.Polynomial(p)
        self.data = [(x, y - f(x)) for x, y in self.data]
        return self

    def normalize(self):
        x_values, y_values = zip(*self.data)
        maximum = max(y_values)
        self.data = list(zip(x_values, [y / maximum for y in y_values]))
        return self

    def quantify(self):
        for analyte in self.analytes:
            analyte.determine_background()
            for isotope in analyte.isotopes:
                isotope.quantify()
        return self

    def to_dict(self, include_data=False):
        result = {
            "name": self.name,
            "filename": self.filename,
            "analytes": [analyte.to_dict() for analyte in self.analytes],
        }
        if include_data:
            result["data"] = self.data
        return result


@dataclass
class Experiment:
    name: str
    settings: AnalysisSettings = field(default_factory=AnalysisSettings)
    building_blocks: dict = field(default_factory=load_building_blocks)
    spectra: list = field(default_factory=list)

    def add_spectrum(self, name=None, filename=None, data=None):
        spectrum = Spectrum(name=name, filename=filename, data=data or [],
                            settings=self.settings,
                            building_blocks=self.building_blocks,
                            experiment=self)
        if filename and not data:
            spectrum.load_xy(filename)
        self.spectra.append(spectrum)
        return spectrum

    def process(self):
        for spectrum in self.spectra:
            spectrum.process_analytes()
        return self

    def to_dict(self, include_data=False):
        return {
            "name": self.name,
            "spectra": [
                spectrum.to_dict(include_data=include_data)
                for spectrum in self.spectra
            ],
        }
