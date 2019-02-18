import tkinter as tk


class OutputWindow(object):
    def __init__(self, master):
        self.master = master
        self.output_parameters = master.output_parameters

        self.top = tk.Toplevel()
        self.top.protocol('WM_DELETE_WINDOW', self.close_output_settings)
        self.top.title('Output Options')

        select_all_button = tk.Button(self.top, text='Select All',
                           command=self.select_all_output_settings)
        select_all_button.grid(row=0, column=0, sticky=tk.W)
        select_none_button = tk.Button(self.top, text='Select None',
                         command=self.select_none_output_settings)
        select_none_button.grid(row=0, column=1, sticky=tk.E)

        text1 = tk.Label(self.top, text='Base Outputs', font='bold')
        text1.grid(row=1, column=0, sticky=tk.W)
        text2 = tk.Label(self.top, text='Output Modifiers', font='bold')
        text2.grid(row=1, column=1, sticky=tk.W)

        absolute_intensity_button = tk.Checkbutton(
                self.top, text=u'Analyte Intensity\u00B9',
                variable=self.output_parameters.absolute_intensity,
                onvalue=1, offvalue=0)
        absolute_intensity_button.grid(row=2, column=0, sticky=tk.W)
        background_subtraction_button = tk.Checkbutton(
                self.top, text=u'\u00B9Background Subtraction',
                variable=self.output_parameters.background_subtraction,
                onvalue=1, offvalue=0)
        background_subtraction_button.grid(row=2, column=1, sticky=tk.W)

        relative_intensity_button = tk.Checkbutton(
                self.top, text=u'Relative Intensity\u00B9',
                variable=self.output_parameters.relative_intensity,
                onvalue=1, offvalue=0)
        relative_intensity_button.grid(row=3, column=0, sticky=tk.W)

        analyte_quality_button = tk.Checkbutton(
                self.top, text='Analyte Quality Criteria',
                variable=self.output_parameters.analyte_quality_criteria,
                onvalue=1, offvalue=0)
        analyte_quality_button.grid(row=4, column=0, sticky=tk.W)

        spectral_quality_button = tk.Checkbutton(
                self.top, text='Spectral Quality Criteria',
                variable=self.output_parameters.spectral_quality_criteria,
                onvalue=1, offvalue=0)
        spectral_quality_button.grid(row=5, column=0, sticky=tk.W)

        pdf_report_button = tk.Checkbutton(
                self.top, text='Generate PDF reports',
                variable=self.output_parameters.pdf_report, onvalue=1,
                offvalue=0)
        pdf_report_button.grid(row=6, column=0, sticky=tk.W)

        ok = tk.Button(self.top,text = 'Ok', command=
                       self.close_output_settings)
        ok.grid(row=13, column=0, sticky = tk.W)
        save = tk.Button(self.top, text='Save', command=
                         self.save_output_settings)
        save.grid(row=13, column=1, sticky=tk.E)

        self.top.lift()

    def close_output_settings(self):
        self.top.destroy()

    def save_output_settings(self):
        self.output_parameters.save_to_disk()
    
    def select_all_output_settings(self):
        """Set all variables to on (1).
        """
        self.output_parameters.absolute_intensity.set(1)
        self.output_parameters.relative_intensity.set(1)
        self.output_parameters.background_subtraction.set(1)
        self.output_parameters.analyte_quality_criteria.set(1)
        self.output_parameters.spectral_quality_criteria.set(1)
        self.output_parameters.pdf_report.set(1)

    def select_none_output_settings(self):
        """Set all variables to off (0).
        """
        self.output_parameters.absolute_intensity.set(0)
        self.output_parameters.relative_intensity.set(0)
        self.output_parameters.background_subtraction.set(0)
        self.output_parameters.analyte_quality_criteria.set(0)
        self.output_parameters.spectral_quality_criteria.set(0)
        self.output_parameters.pdf_report.set(0)
