import configparser
import logging
from pathlib import Path


class Settings(object):
    def __init__(self, master):
        self.config = configparser.ConfigParser()
        self.logger = logging.getLogger(__name__)
        self.mass_modifiers = ['free']
        self.charge_carrier = 'sodium'
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
        self.min_contribution = 0.0001
        self.epsilon = 0.1
        self.read()

    def save(self):
        try:
            self.config.add_section('General')
        except configparser.DuplicateSectionError as e:
            self.logger.error(e)
        try:
            self.config.add_section('Calibration')
        except configparser.DuplicateSectionError as e:
            self.logger.error(e)
        try:
            self.config.add_section('Quantitation')
        except configparser.DuplicateSectionError as e:
            self.logger.error(e)
        self.config.set('General', 'Mass modifiers', ','.join(self.mass_modifiers))
        self.config.set('General', 'Charge carrier', str(self.charge_carrier))
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
        with Path(Path.cwd() / 'HappyTools.ini').open('w') as config_file:
            self.config.write(config_file)

    def read(self):
        if Path(Path.cwd() / 'MassyTools.ini').is_file():
            self.config.read('MassyTools.ini')
            self.mass_modifiers = self.config.get('General', 'Mass modifiers')
            self.charge_carrier = self.config.get('General', 'Charge carrier')
            self.background_window = self.config.getint('General', 'Background window')
            self.calibration_window = self.config.getfloat('Calibration', 'Mass window')
            self.calibration_sn_cutoff = self.config.getfloat('Calibration', 'SN cutoff')
            self.num_low_mass = self.config.getint('Calibration', 'Min low mass')
            self.num_medium_mass = self.config.getint('Calibration', 'Min medium mass')
            self.num_high_mass = self.config.getint('Calibration', 'Min high mass')
            self.num_total = self.config.getint('Calibration', 'Min total')
            self.mass_window = self.config.getfloat('Quantitation', 'Mass window')
            self.sn_cutoff = self.config.getfloat('Quantitation', 'SN cutoff')
            self.min_total_contribution = self.config.getfloat('Quantitation', 'Min isotopic contribution')

        
