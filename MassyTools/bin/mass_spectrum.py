from pathlib import Path, PurePath
import logging
import tkinter.filedialog as filedialog


class MassSpectrum(object):
    def __init__(self, master):
        self.logger = logging.getLogger(__name__)
        self.axes = master.axes
        self.filename = master.filename
        self.open_mass_spectrum()

    def open_mass_spectrum(self):
        file_type = None
        with Path(self.filename).open() as fr:
            for line in fr:
                # Prototype (File Recognition)
                if 'utter_nonsense' in line:
                    file_type = 'Bruker'

        if file_type == None:
            try:
                self.open_xy_spectrum()
            except Exception as e:
                self.logger.error(e)

    def open_xy_spectrum(self):
        data_buffer = []
        with Path(self.filename).open() as fr:
            for line in fr:
                line = line.rstrip().split()
                data_buffer.append((float(line[0]), float(line[-1])))
        self.data = data_buffer

    def plot_mass_spectrum(self):
        label = PurePath(self.filename).stem
        x_array, y_array = zip(*self.data)
        self.axes.plot(x_array, y_array, label=str(label))

def finalize_plot(master):
    master.axes.set_xlabel('m/z [Th]')
    master.axes.set_ylabel('Intensity [au]')
    handles, labels = master.axes.get_legend_handles_labels()
    master.axes.legend(handles, labels)
    master.axes.get_xaxis().get_major_formatter().set_useOffset(False)
    master.canvas.draw_idle()
