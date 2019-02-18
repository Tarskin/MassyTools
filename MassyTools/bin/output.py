import logging
from datetime import datetime
from pathlib import Path, PurePath
import MassyTools.gui.version as version


class Output(object):
    def __init__(self, master):
        self.master = master
        self.logger = logging.getLogger(__name__)
        self.settings = master.settings
        self.output_parameters = master.output_parameters

        utc_datetime = datetime.utcnow()
        s = utc_datetime.strftime('%Y-%m-%d %H%M')
        self.filename = s + '_summary.txt'

    def build_header(self):
        header = ''
        for mass_spectrum in self.master.mass_spectra:
            for analyte in mass_spectrum.analytes:
                header = (header + '\t' + str(analyte.name) + ' [' +
                         str(analyte.charge) + 'z]')
            header = header + '\n'
            break

        header = header + 'Exact m/z'
        for mass_spectrum in self.master.mass_spectra:
            for analyte in mass_spectrum.analytes:
                for isotope in analyte.isotopes:
                    header = header + '\t' + str(isotope.exact_mass)
                    break
            header = header + '\n'
            break

        self.header = header

    def build_output_file(self):
        self.build_header()

        if self.output_parameters.absolute_intensity.get() == True:
            if self.output_parameters.background_subtraction.get() == True:
                self.write_back_sub_abs_peak_intensity()
            else:
                self.write_abs_peak_intensity()

        if self.output_parameters.relative_intensity.get() == True:
            if self.output_parameters.background_subtraction.get() == True:
                self.write_back_sub_rel_peak_intensity()
            else:
                self.write_rel_peak_intensity()

        if self.output_parameters.analyte_quality_criteria.get() == True:
            self.write_mass_accuracy()
            self.write_signal_to_noise()
            self.write_isotopic_pattern_quality()

        if self.output_parameters.spectral_quality_criteria.get() == True:
            self.write_non_quantified_fraction()

    def init_output_file(self):
        with Path(self.master.base_dir / Path(self.filename)).open(
                  'w') as fw:

            fw.write('MassyTools Metadata\n')
            fw.write('Version:\t'+str(version.version)+'\n')
            fw.write('Build:\t'+str(version.build)+'\n')
            fw.write('\n')

            fw.write('MassyTools Processing Parameters\n')
            fw.write('Charge Carrier:\t'+str(
                     self.settings.charge_carrier)+'\n')
            fw.write('Mass Modifier(s):')
            for modifier in self.settings.mass_modifiers:
                fw.write('\t'+str(modifier))
            fw.write('\n')
            fw.write('Background Window:\t'+str(
                     self.settings.background_window)+'\n')
            fw.write('Calibration Window:\t'+str(
                     self.settings.calibration_window)+'\n')
            fw.write('Number Low Mass Calibrants\t'+str(
                     self.settings.num_low_mass)+'\n')
            fw.write('Number Medium Mass Calibrants\t'+str(
                     self.settings.num_medium_mass)+'\n')
            fw.write('Number High Mass Calibrants\t'+str(
                     self.settings.num_high_mass)+'\n')
            fw.write('Mass Window:\t'+str(self.settings.mass_window)+
                     '\n')
            fw.write('Signal to Noise Cutoff:\t'+str(
                     self.settings.sn_cutoff)+'\n')
            fw.write('Minimum Total Isotopic Contribution:\t'+str(
                     self.settings.min_total_contribution)+'\n')
            fw.write('\n')

            fw.write('MassyTools Advanced Paramaters\n')
            fw.write('Minimum Isotopic Contribution:\t'+str(
                     self.settings.min_contribution)+'\n')
            fw.write('Sequential Background Regions:\t'+str(
                     self.settings.background_chunks)+'\n')
            fw.write('Epsilon:\t'+str(self.settings.epsilon)+'\n')
            fw.write('Decimal Numbers:\t'+str(
                     self.settings.decimal_numbers)+'\n')
            fw.write('\n')

    def write_abs_peak_intensity(self):
        with Path(self.master.base_dir / Path(self.filename)).open(
                  'a') as fw:

            fw.write('Intensities (Area)')
            fw.write(self.header)
            for mass_spectrum in self.master.mass_spectra:
                fw.write(str(PurePath(mass_spectrum.filename).stem))
                for analyte in mass_spectrum.analytes:
                    intensity = 0
                    for isotope in analyte.isotopes:
                        intensity += isotope.area
                    fw.write('\t'+str(intensity))
                fw.write('\n')
            fw.write('\n')

    def write_back_sub_abs_peak_intensity(self):
        with Path(self.master.base_dir / Path(self.filename)).open(
                  'a') as fw:

            fw.write('Background Subtracted Intensities (Area)')
            fw.write(self.header)
            for mass_spectrum in self.master.mass_spectra:
                fw.write(str(PurePath(mass_spectrum.filename).stem))
                for analyte in mass_spectrum.analytes:
                    intensity = 0
                    for isotope in analyte.isotopes:
                        intensity += (isotope.area -
                                      analyte.background_area)
                    fw.write('\t'+str(intensity))
                fw.write('\n')
            fw.write('\n')

    def write_back_sub_rel_peak_intensity(self):
        with Path(self.master.base_dir / Path(self.filename)).open(
                  'a') as fw:

            fw.write('Background Subtracted Relative Intensities (Area)')
            fw.write(self.header)
            for mass_spectrum in self.master.mass_spectra:
                fw.write(str(PurePath(mass_spectrum.filename).stem))
                total_intensity = 0
                for analyte in mass_spectrum.analytes:
                    for isotope in analyte.isotopes:
                        total_intensity += (isotope.area -
                                            analyte.background_area)
                for analyte in mass_spectrum.analytes:
                    intensity = 0
                    for isotope in analyte.isotopes:
                        intensity += (isotope.area -
                                      analyte.background_area)
                    intensity = intensity / total_intensity
                    fw.write('\t'+str(intensity))
                fw.write('\n')
            fw.write('\n')

    def write_isotopic_pattern_quality(self):
        with Path(self.master.base_dir / Path(self.filename)).open(
                  'a') as fw:

            fw.write('Isotopic Pattern Quality')
            fw.write(self.header)
            for mass_spectrum in self.master.mass_spectra:
                # TODO: This can probably be done without PurePath
                fw.write(str(PurePath(mass_spectrum.filename).stem))
                for analyte in mass_spectrum.analtes:
                    total_area = 0.
                    for isotope in analyte.isotopes:
                        total_intensity += (isotope.area -
                                            analyte.background_area)
                    ipq = 0.
                    for isotope in analyte.isotopes:
                        ipq += abs(isotope.fraction - ((isotope.area -
                                   analyte.background_area) /
                                   total_intensity))
                    fw.write('\t'+str(ipq))
                fw.write('\n')
            fw.write('\n')

    def write_mass_accuracy(self):
        with Path(self.master.base_dir / Path(self.filename)).open(
                  'a') as fw:

            fw.write('Mass Accuracy [ppm]')
            fw.write(self.header)
            for mass_spectrum in self.master.mass_spectra:
                fw.write(str(PurePath(mass_spectrum.filename).stem))
                for analyte in mass_spectrum.analytes:
                    for isotope in analyte.isotopes:
                        if isotope.accurate_mass:
                            # ((O-E)/E)*1^E6
                            mass_accuracy = (
                                ((isotope.accurate_mass -
                                isotope.exact_mass) /
                                isotope.exact_mass) * 1000000)
                            fw.write('\t'+str(mass_accuracy))
                fw.write('\n')
            fw.write('\n')

    def write_rel_peak_intensity(self):
        with Path(self.master.base_dir / Path(self.filename)).open(
                  'a') as fw:

            fw.write('Relative Intensities (Area)')
            fw.write(self.header)
            for mass_spectrum in self.master.mass_spectra:
                fw.write(str(PurePath(mass_spectrum.filename).stem))
                total_intensity = 0
                for analyte in mass_spectrum.analytes:
                    for isotope in analyte.isotopes:
                        total_intensity += isotope.area
                for analyte in mass_spectrum.analytes:
                    intensity = 0
                    for isotope in analyte.isotopes:
                        intensity += isotope.area
                    intensity = intensity / total_intensity
                    fw.write('\t'+str(intensity))
                fw.write('\n')
            fw.write('\n')

    def write_signal_to_noise(self):
        with Path(self.master.base_dir / Path(self.filename)).open(
                  'a') as fw:

            fw.write('Signal-to-Noise')
            fw.write(self.header)
            for mass_spectrum in self.master.mass_spectra:
                fw.write(str(PurePath(mass_spectrum.filename).stem))
                for analyte in mass_spectrum.analytes:
                    for isotope in analyte.isotopes:
                        if isotope.accurate_mass:
                            signal_to_noise = (
                                (isotope.maximum_intensity -
                                analyte.background_intensity) /
                                analyte.noise)
                            fw.write('\t'+str(signal_to_noise))
                fw.write('\n')
            fw.write('\n')

    def write_non_quantified_fraction(self):
        with Path(self.master.base_dir / Path(self.filename)).open(
                  'a') as fw:

            fw.write('Residual Intensity\n')
            for mass_spectrum in self.master.mass_spectra:
                fw.write(str(PurePath(mass_spectrum.filename).stem))
                total_spectrum_intensity = sum([x[1] for x in mass_spectrum.data])
                total_analyte_intensity = 0
                for analyte in mass_spectrum.analytes:
                    for isotope in analyte.isotopes:
                        total_analyte_intensity += isotope.total_intensity
                fw.write('\t'+str(total_analyte_intensity /
                                  total_spectrum_intensity)+'\n')
            fw.write('\n')
