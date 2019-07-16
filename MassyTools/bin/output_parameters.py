import configparser
import logging
import tkinter as tk
from pathlib import Path


class OutputParameters(object):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.logger = logging.getLogger(__name__)

        self.absolute_intensity = tk.IntVar()
        self.relative_intensity = tk.IntVar()
        self.background_subtraction = tk.IntVar()
        self.analyte_quality_criteria = tk.IntVar()
        self.spectral_quality_criteria = tk.IntVar()
        self.pdf_report = tk.IntVar()

        self.read_from_disk()

    def save_to_disk(self):
        try:
            self.config.add_section('Output')
        except configparser.DuplicateSectionError as e:
            self.logger.error(e)
        self.config.set('Output', 'Absolute Intensity',
                        str(self.absolute_intensity.get()))
        self.config.set('Output', 'Relative Intensity',
                        str(self.relative_intensity.get()))
        self.config.set('Output', 'Background Subtraction',
                        str(self.background_subtraction.get()))
        self.config.set('Output', 'Analyte Quality Criteria',
                        str(self.analyte_quality_criteria.get()))
        self.config.set('Output', 'Spectral Quality Criteria',
                        str(self.spectral_quality_criteria.get()))
        self.config.set('Output', 'PDF Reports',
                        str(self.pdf_report.get()))
        with Path(Path.cwd() / 'MassyTools.ini').open('w') as config_file:
            self.config.write(config_file)

    def read_from_disk(self):
        if Path(Path.cwd() / 'MassyTools.ini').is_file():
            self.config.read('MassyTools.ini')

            try:
                self.absolute_intensity.set(int(
                    self.config.get('Output', 'Absolute Intensity')))
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                pass

            try:
                self.relative_intensity.set(int(
                    self.config.get('Output', 'Relative Intensity')))
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                pass

            try:
                self.background_subtraction.set(int(
                    self.config.get('Output', 'Background Subtraction')))
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                pass

            try:
                self.analyte_quality_criteria.set(int(
                    self.config.get('Output', 'Analyte Quality Criteria')))
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                pass

            try:
                self.spectral_quality_criteria.set(int(
                    self.config.get('Output', 'Spectral Quality Criteria')))
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                pass

            try:
                self.pdf_report.set(int(
                    self.config.get('Output', 'PDF Reports')))
            except (configparser.NoSectionError,
                    configparser.NoOptionError):
                pass
