from pathlib import Path

from MassyTools.bin.mass_spectrum import MassSpectrum
from MassyTools.bin.output import Output
from MassyTools.gui.batch_process_progress_window import BatchProcessProgressWindow
from MassyTools.util.functions import get_peak_list


class BatchProcess(object):
    def __init__(self, master):
        self.master = master
        self.process_parameters = master.process_parameters
        self.output_parameters = master.output_parameters
        self.base_dir = self.process_parameters.data_folder  # Icky, but required to make this work
        self.building_blocks = master.building_blocks  # Should refactor to not need this
        self.settings = master.settings
        self.logger = master.logger
        self.axes = master.axes  # Should refactor to not need this


        # Placeholders
        self.reference = None
        self.files = None
        self.filename = None
        self.process_window = None
        self.mass_spectra = None

        # Batch process specific settings
        self.calibration_filetypes = ['*.xy']
        self.quantitation_filetypes = ['*.xy']
        self.exclusion_files = []

    def batch_process(self):
        if self.process_parameters.data_folder:

            # Progress Window
            self.process_window = BatchProcessProgressWindow(self)
            self.process_window.create_window()

            # Calibration
            if self.process_parameters.calibration_file:
                self.process_parameters.calibration = True

                self.peak_list = get_peak_list(
                        self.process_parameters.calibration_file)
                self.files = self.get_calibration_files()

                # Read data
                self.read_data()

                # Perform calibration
                progress = self.process_window.calibration_progress_bar
                for index, mass_spectrum in enumerate(self.mass_spectra):
                    progress.counter.set(
                            (float(index) / len(self.mass_spectra))*100)
                    progress.update_progress_bar()
                    mass_spectrum.process_mass_spectrum()
                    mass_spectrum.calibrate()
                progress.fill_bar()

                # Wrap up
                self.process_parameters.calibration = False

            # Quantitation
            if self.process_parameters.quantitation_file:
                self.process_parameters.quantitation = True

                self.peak_list = get_peak_list(
                        self.process_parameters.quantitation_file)
                self.files = self.get_quantitation_files()

                # Read data
                if not self.mass_spectra:
                    self.mass_spectra = self.read_data()

                # Perform quantitation
                progress = self.process_window.quantitation_progress_bar
                for index, mass_spectrum in enumerate(self.mass_spectra):
                    progress.counter.set(
                            (float(index) / len(self.mass_spectra))*100)
                    progress.update_progress_bar()
                    mass_spectrum.process_mass_spectrum()
                    mass_spectrum.quantify_mass_spectrum()
                progress.fill_bar()

                # Generate summary file
                output = Output(self)
                output.init_output_file()
                output.build_output_file()

                # Wrap up
                self.process_parameters.quantitation = False

            # Report generation
            if self.output_parameters.pdf_report.get() == True:
                progress = self.process_window.report_progress_bar
                for index, mass_spectrum in enumerate(self.mass_spectra):
                    progress.counter.set(
                            (float(index) / len(self.mass_spectra))*100)
                    progress.update_progress_bar()
                    mass_spectrum.generate_pdf_report()
                progress.fill_bar()

    def read_data(self):
        data = []
        progress = self.process_window.reading_progress_bar
        for index, filename in enumerate(self.files):
            progress.counter.set((float(index) / len(self.files))*100)
            progress.update_progress_bar()
            self.filename = Path(filename)
            mass_spectrum = MassSpectrum(self)
            mass_spectrum.open_mass_spectrum()
            data.append(mass_spectrum)
        progress.fill_bar()
        self.mass_spectra = data

    def get_calibration_files(self):
        calibration_files = []
        for files in self.calibration_filetypes:
            for file in Path(
                    self.process_parameters.data_folder).glob(files):
                if file not in self.exclusion_files:
                    calibration_files.append(Path(
                            self.process_parameters.data_folder) /
                            file)
        return calibration_files

    def get_quantitation_files(self):
        quantitation_files = []
        for files in self.quantitation_filetypes:
            for file in Path(self.process_parameters.data_folder).glob(files):
                if file not in self.exclusion_files:
                    quantitation_files.append(Path(
                            self.process_parameters.data_folder) /
                            file)
        return quantitation_files
