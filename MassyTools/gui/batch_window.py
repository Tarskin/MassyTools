from pathlib import Path
import tkinter as tk

from MassyTools.gui.output_window import OutputWindow
from MassyTools.gui.tooltip import create_tooltip
from MassyTools.util.batch_process import BatchProcess


class BatchWindow(object):
    def __init__(self, master):
        self.master = master
        self.output_parameters = master.output_parameters
        self.process_parameters = master.process_parameters
        self.logger = master.logger
        self.settings = self.master.settings

        data_folder_var = tk.StringVar()
        data_folder_var.set(
                self.process_parameters.data_folder)
        calibration_file_var = tk.StringVar()
        calibration_file_var.set(
                self.process_parameters.calibration_file)
        quantitation_file_var = tk.StringVar()
        quantitation_file_var.set(
                self.process_parameters.quantitation_file)

        top = tk.Toplevel()
        top.title('Batch Process')
        top.protocol('WM_DELETE_WINDOW', self.close)

        calibration_button = tk.Button(top, text='Calibration File',
                                      width=20,
                                      command=self.set_calibration_file)
        calibration_button.grid(row=1, column=0, sticky=tk.W)
        calibration_label = tk.Label(top, textvariable=
                                     calibration_file_var, width=20)
        calibration_label.grid(row=1, column=1)

        analyte_button = tk.Button(top, text='Analyte File',
                                  width=20,
                                  command=self.set_analyte_file)
        analyte_button.grid(row=2, column=0, sticky=tk.W)
        analyte_label = tk.Label(top, textvariable=
                                 quantitation_file_var, width=20)
        analyte_label.grid(row=2, column=1)

        batch_button = tk.Button(top, text='Batch Directory',
                                 width=20, command=self.set_batch_folder)
        batch_button.grid(row=3, column=0, sticky=tk.W)
        batch_label = tk.Label(top, textvariable=data_folder_var,
                               width=20)
        batch_label.grid(row=3, column=1, sticky=tk.W)

        output_button = tk.Button(top, text='Output Options',
                                  command=self.open_output_window)
        output_button.grid(row=4, column=0, columnspan=2,
                           sticky=tk.E+tk.W)

        run_button = tk.Button(top, text='Run', width=20,
                               command=self.run)
        run_button.grid(row=5, column=0, sticky=tk.W)
        close_button = tk.Button(top, text='Close', width=20,
                                 command=self.close)
        close_button.grid(row=5, column=1, sticky=tk.E)

        self.top = top
        self.top = top
        self.data_folder_var = data_folder_var
        self.calibration_file_var = calibration_file_var
        self.quantitation_file_var = quantitation_file_var

        # Tooltips
        create_tooltip(
            calibration_button, 'This button will allow you to select ' +
            'your calibration file, the program expects a tab separated ' +
            'text file where each line consists contains at least a '+
            'composition.')

        create_tooltip(
            analyte_button, 'This button will allow you to select your ' +
            'analyte file, the program expects a tab separated text file ' +
            'where each line contains at least a composition')

        create_tooltip(
            batch_button, 'This button will allow you to select the ' +
            'folder where the mass spectra are stored that MassyTools will ' +
            'process.')

        create_tooltip(
            output_button, 'This button will open another window in ' +
            'which you can select which outputs you want MassyTools to show ' +
            'in the final summary.')

    def close(self):
        self.top.destroy()

    def open_output_window(self):
        OutputWindow(self)
        pass

    def run(self):
        """Start the batch process.
        """
        try:
            # Placeholder
            BatchProcess(self)
        except Exception as e:
            self.logger.error(e)

    def set_batch_folder(self):
        """Ask for the batch folder.
        """
        self.data_folder_var.set(Path(
                tk.filedialog.askdirectory(title='Data Folder')))
        self.process_parameters.data_folder = self.data_folder_var.get()

    def set_calibration_file(self):
        """Ask for the calibration file.
        """
        self.calibration_file_var.set(
                tk.filedialog.askopenfilename(title='Calibration File'))
        self.process_parameters.calibration_file = self.calibration_file_var.get()

    def set_analyte_file(self):
        """Ask for the analyte file.
        """
        self.quantitation_file_var.set(
                tk.filedialog.askopenfilename(title='Quantitation File'))
        self.process_parameters.quantitation_file = self.quantitation_file_var.get()