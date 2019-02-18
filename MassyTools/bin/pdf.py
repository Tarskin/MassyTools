import MassyTools.gui.version as version
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages


class Pdf(object):
    def __init__(self, master):
        self.master = master
        parent_dir = Path(master.mass_spectrum.filename).parent
        pdf_file = str(Path(master.mass_spectrum.filename).stem)+'.pdf'
        pdf = PdfPages(parent_dir / Path(pdf_file))

        self.pdf = pdf

    def attach_meta_data(self):
        meta_data = self.pdf.infodict()
        meta_data['Title'] = 'PDF Report for: '+str(
                Path(self.master.filename).stem)
        meta_data['Author'] = ('HappyTools version: '+
                               str(version.version)+' build: '+
                               str(version.build))
        meta_data['CreationDate'] = datetime.now()

    def plot_mass_spectrum(self):
        x_data, y_data = zip(*self.master.mass_spectrum.data)
        fig = plt.figure(figsize=(8,6))
        fig.add_subplot(111)
        plt.plot(x_data, y_data)
        plt.title(str(self.master.mass_spectrum.filename))
        plt.xlabel('m/z')
        plt.ylabel('Intensity [au]')
        self.pdf.savefig(fig)
        plt.close(fig)

    def plot_mass_spectrum_peak(self):
        x_data, y_data = zip(*self.master.analyte.data_subset)
        max_peak = 0.
        for isotope in self.master.analyte.isotopes:
            if isotope.fraction > max_peak:
                max_peak = isotope.fraction
                signal = isotope.maximum_intensity
        signal_to_noise = (
                (signal - self.master.analyte.background_intensity) /
                self.master.analyte.noise)
        background_intensity = self.master.analyte.background_intensity

        fig = plt.figure(figsize=(8,6))
        fig.add_subplot(111)
        plt.plot(x_data, y_data, color='blue')
        plt.plot([x_data[0], x_data[-1]], [background_intensity,
                 background_intensity], alpha=0.5)
        for isotope in self.master.analyte.isotopes:
            if isotope.fraction == max_peak:
                iso_x, iso_y = zip(*isotope.data_subset)
                x_coord = iso_x[iso_y.index(signal)]
        plt.plot([x_coord, x_coord], [background_intensity, signal],
                 alpha=0.5)
        plt.legend(['Raw Data', 'Background', 'Signal (S/N '+
                '{0:.2f}'.format(signal_to_noise)+')'], loc='best')
        plt.title(str(self.master.analyte.name))
        plt.xlabel('m/z')
        plt.ylabel('Intensity [au]')
        self.pdf.savefig(fig)
        plt.close(fig)

    def close_pdf(self):
        self.pdf.close()
