import MassyTools.gui.version as version
from matplotlib.figure import Figure
from pathlib import Path
from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages


class Pdf(object):
    def __init__(self, master):
        self.master = master
        parent_dir = Path(master.filename).parent
        pdf_file = str(Path(master.filename).stem)+'.pdf'
        pdf = PdfPages(parent_dir / Path(pdf_file))

        fig = Figure(figsize=(8,6))
        axes = fig.add_subplot(111)
        axes.set_xlabel('m/z')
        axes.set_ylabel('Intensity [au]')

        self.fig = fig
        self.axes = axes
        self.pdf = pdf

    def attach_meta_data(self):
        meta_data = self.pdf.infodict()
        meta_data['Title'] = 'PDF Report for: '+str(
                Path(self.master.filename).stem)
        meta_data['Author'] = ('MassyTools version: '+
                               str(version.version)+' build: '+
                               str(version.build))
        meta_data['CreationDate'] = datetime.now()

    def plot_mass_spectrum(self):
        x_data, y_data = zip(*self.master.data)

        self.axes.clear()
        self.axes.plot(x_data, y_data)
        self.axes.set_title(str(self.master.filename))
        self.pdf.savefig(self.fig)

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

        for isotope in self.master.analyte.isotopes:
            if isotope.fraction == max_peak:
                iso_x, iso_y = zip(*isotope.data_subset)
                main_isotope = iso_x[iso_y.index(signal)]

        self.axes.clear()
        self.axes.plot(x_data, y_data, color='blue')
        self.axes.plot(
                [x_data[0], x_data[-1]],
                [background_intensity, background_intensity],
                alpha=0.5)
        self.axes.plot(
                [main_isotope, main_isotope],
                [background_intensity, signal],
                alpha=0.5)
        self.axes.legend(
                ['Raw Data', 'Background', 'Signal (S/N '+
                '{0:.2f}'.format(signal_to_noise)+')'], loc='best')
        self.axes.set_title(str(self.master.analyte.name))
        self.pdf.savefig(self.fig)

    def close_pdf(self):
        self.pdf.close()
