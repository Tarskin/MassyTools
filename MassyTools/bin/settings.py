import configparser
import logging
from pathlib import Path


class Settings(object):
    def __init__(self, master):
        self.config = configparser.ConfigParser()
        self.logger = logging.getLogger(__name__)

        # Changeable via GUI (Mostly)
        self.mass_modifiers = ['free']
        self.charge_carrier = 'sodium'
        self.min_charge_state = 1
        self.max_charge_state = 1
        self.background_window = 20
        self.calibration_window = 0.4
        self.calibration_sn_cutoff = 9.0
        self.num_low_mass = 3
        self.num_medium_mass = 2
        self.num_high_mass = 0
        self.num_total = 5
        self.mass_window = 0.2
        self.sn_cutoff = 9.0
        self.min_total_contribution = 0.95

        # Changeable via source
        self.min_contribution = 0.0001
        self.background_chunks = 4
        self.epsilon = 0.1
        self.decimal_numbers = 8

        self.read_from_disk()

    def save_to_disk(self):
        try:
            self.config.add_section('General')
        except configparser.DuplicateSectionError as e:
            pass

        try:
            self.config.add_section('Calibration')
        except configparser.DuplicateSectionError as e:
            pass

        try:
            self.config.add_section('Quantitation')
        except configparser.DuplicateSectionError as e:
            pass

        if len(self.mass_modifiers) > 1:
            mass_modifiers = ','.join(self.mass_modifiers)
        else:
            mass_modifiers = str(self.mass_modifiers[0])
        self.config.set('General', 'Mass modifiers', str(mass_modifiers))
        self.config.set('General', 'Charge carrier', str(self.charge_carrier))
        self.config.set('General', 'Minimum charge state', str(self.min_charge_state))
        self.config.set('General', 'Maximum charge state', str(self.max_charge_state))
        self.config.set('General', 'Background window', str(self.background_window))
        self.config.set('Calibration', 'Mass window', str(self.calibration_window))
        self.config.set('Calibration', 'SN cutoff', str(self.calibration_sn_cutoff))
        self.config.set('Calibration', 'Min low mass', str(self.num_low_mass))
        self.config.set('Calibration', 'Min medium mass', str(self.num_medium_mass))
        self.config.set('Calibration', 'Min high mass', str(self.num_high_mass))
        self.config.set('Calibration', 'Min total', str(self.num_total))
        self.config.set('Quantitation', 'Mass window', str(self.mass_window))
        self.config.set('Quantitation', 'SN cutoff', str(self.sn_cutoff))
        self.config.set('Quantitation', 'Min isotopic contribution', str(self.min_total_contribution))
        with Path(Path.cwd() / 'MassyTools.ini').open('w') as config_file:
            self.config.write(config_file)

    def read_from_disk(self):
        if Path(Path.cwd() / 'MassyTools.ini').is_file():
            self.config.read('MassyTools.ini')
            try:
                self.mass_modifiers = self.config.get(
                        'General', 'Mass modifiers')
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                pass

            try:
                self.charge_carrier = self.config.get(
                        'General', 'Charge carrier')
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                pass

            try:
                self.min_charge_state = int(self.config.get(
                        'General', 'Minimum charge state'))
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                pass

            try:
                self.max_charge_state = int(self.config.get(
                        'General', 'Maximum charge state'))
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                pass

            try:
                self.background_window = int(self.config.getint(
                        'General', 'Background window'))
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                pass

            try:
                self.calibration_window = float(self.config.getfloat(
                        'Calibration', 'Mass window'))
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                pass

            try:
                self.calibration_sn_cutoff = int(self.config.getfloat(
                        'Calibration', 'SN cutoff'))
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                pass

            try:
                self.num_low_mass = int(self.config.getint(
                        'Calibration', 'Min low mass'))
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                pass

            try:
                self.num_medium_mass = int(self.config.getint(
                        'Calibration', 'Min medium mass'))
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                pass

            try:
                self.num_high_mass = int(self.config.getint(
                        'Calibration', 'Min high mass'))
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                pass

            try:
                self.num_total = int(self.config.getint(
                        'Calibration', 'Min total'))
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                pass

            try:
                self.mass_window = float(self.config.getfloat(
                        'Quantitation', 'Mass window'))
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                pass

            try:
                self.sn_cutoff = int(self.config.getfloat(
                        'Quantitation', 'SN cutoff'))
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                pass

            try:
                self.min_total_contribution = float(self.config.getfloat(
                        'Quantitation', 'Min isotopic contribution'))
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                pass

            try:
                self.mass_modifiers = self.mass_modifiers.split(',')
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                pass
