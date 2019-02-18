from MassyTools.gui.tooltip import create_tooltip
import tkinter as tk

class SettingsWindow(object):
    def __init__(self, master):
        self.settings = master.settings
        self.create_window()

    def close_settings_window(self):
        self.store_settings()
        self.root.destroy()

    def save_settings(self):
        self.store_settings()
        self.settings.save_to_disk()

    def store_settings(self):
        self.settings.calibration_window = float(
            self.calibration_window.get()
        )
        self.settings.calibration_sn_cutoff = float(
            self.calibration_sn.get()
        )
        self.settings.num_low_mass = int(
            self.calibration_min_low.get()
        )
        self.settings.num_medium_mass = int(
            self.calibration_min_medium.get()
        )
        self.settings.num_high_mass = int(
            self.calibration_min_high.get()
        )
        self.settings.num_total = int(
            self.calibration_min_total.get()
        )
        self.settings.mass_window = float(
            self.extraction_mass_window.get()
        )
        self.settings.background_window = int(
            self.extraction_background_window.get()
        )
        self.settings.sn_cuttoff = float(
            self.extraction_qc_sn.get()
        )
        self.settings.min_total_contribution = float(
            self.extraction_min_total.get()
        )

    def create_window(self):
        root = tk.Toplevel()
        root.protocol( "WM_DELETE_WINDOW", self.close_settings_window)

        calibration_label = tk.Label(root, text="Calibration parameters",
                                     font="bold")
        calibration_label.grid(row=1, columnspan=2, sticky=tk.W)

        calibration_window_label = tk.Label(root, text="m/z window for "+
                                            "calibration")
        calibration_window_label.grid(row=2, column=0, sticky=tk.W)
        calibration_window = tk.Entry(root)
        calibration_window.insert(0, self.settings.calibration_window)
        calibration_window.grid(row=2, column=1, sticky=tk.W)

        calibration_sn_label = tk.Label(root, text="Minimal S/N for "+
                                        "calibration")
        calibration_sn_label.grid(row=3, column=0, sticky=tk.W)
        calibration_sn = tk.Entry(root)
        calibration_sn.insert(0, self.settings.calibration_sn_cutoff)
        calibration_sn.grid(row=3, column=1, sticky=tk.W)

        calibration_min_low_label = tk.Label(root, text="Minimal number of "+
                                             "calibrants in low m/z range")
        calibration_min_low_label.grid(row=4, column=0, sticky=tk.W)
        calibration_min_low = tk.Entry(root)
        calibration_min_low.insert(0, self.settings.num_low_mass)
        calibration_min_low.grid(row=4, column=1, sticky=tk.W)

        calibration_min_medium_label = tk.Label(root, text="Minimal number "+
                                                "of calibrants in medium m/z "+
                                                "range")
        calibration_min_medium_label.grid(row=5, column=0, sticky=tk.W)
        calibration_min_medium = tk.Entry(root)
        calibration_min_medium.insert(0, self.settings.num_medium_mass)
        calibration_min_medium.grid(row=5, column=1, sticky=tk.W)

        calibration_min_high_label = tk.Label(root, text="Minimal number of "+
                                              "calibrants in high m/z range")
        calibration_min_high_label.grid(row=6, column=0, sticky=tk.W)
        calibration_min_high = tk.Entry(root)
        calibration_min_high.insert(0, self.settings.num_high_mass)
        calibration_min_high.grid(row=6, column=1, sticky=tk.W)

        calibration_min_total_label = tk.Label(root, text="Minimal number "+
                                               "of calibrants")
        calibration_min_total_label.grid(row=7, column=0, sticky=tk.W)
        calibration_min_total = tk.Entry(root)
        calibration_min_total.insert(0, self.settings.num_total)
        calibration_min_total.grid(row=7, column=1, sticky=tk.W)

        extraction_label = tk.Label(root, text="Extraction & QC Parameters",
                                    font="bold")
        extraction_label.grid(row=8, columnspan=2, sticky=tk.W)
        extraction_mass_window_label = tk.Label(root, text="m/z window for "+
                                                "quantitation")
        extraction_mass_window_label.grid(row=9, column=0, sticky=tk.W)
        extraction_mass_window = tk.Entry(root)
        extraction_mass_window.insert(0, self.settings.mass_window)
        extraction_mass_window.grid(row=9, column=1, sticky=tk.W)

        extraction_min_total_label = tk.Label(root, text="Minimum isotopic "+
                                              "fraction")
        extraction_min_total_label.grid(row=10, column=0, sticky=tk.W)
        extraction_min_total = tk.Entry(root)
        extraction_min_total.insert(0, self.settings.min_total_contribution)
        extraction_min_total.grid(row=10, column=1, sticky=tk.W)

        extraction_background_window_label = tk.Label(root, text="Background "+
                                                      "detection window")
        extraction_background_window_label.grid(row=11, column=0, sticky=tk.W)
        extraction_background_window = tk.Entry(root)
        extraction_background_window.insert(0, self.settings.background_window)
        extraction_background_window.grid(row=11, column=1, sticky=tk.W)

        extraction_qc_sn_label = tk.Label(root, text="S/N cutoff for "+
                                          "spectral QC")
        extraction_qc_sn_label.grid(row=12, column=0, sticky=tk.W)
        extraction_qc_sn = tk.Entry(root)
        extraction_qc_sn.insert(0, self.settings.sn_cutoff)
        extraction_qc_sn.grid(row=12, column=1, sticky=tk.W)

        ok = tk.Button(root,text='Ok', command=
                            self.close_settings_window)
        ok.grid(row=13, column=0, sticky=tk.W)
        save = tk.Button(root, text='Save', command=self.save_settings)
        save.grid(row=13, column=1, sticky=tk.E)

        # Tooltips
        create_tooltip(calibration_window_label, "The mass window in Dalton "+
                       "around the specified exact m/z of a calibrant, that "+
                       "MassyTools uses to determine the accurate mass.")
        create_tooltip(calibration_sn_label, "The minimum S/N of a calibrant "+
                       "to be included in the calibration.")
        create_tooltip(calibration_min_low_label, "The minimum number of "+
                       "calibrants in the low m/z range that have a S/N "+
                       "higher than the minimum S/N for calibration to occur.")
        create_tooltip(calibration_min_medium_label, "The minimum number of "+
                       "calibrants in the medium m/z range that have a S/N "+
                       "higher than the minimum S/N for calibration to occur.")
        create_tooltip(calibration_min_high_label, "The minimum number of "+
                       "calibrants in the high m/z range that have a S/N "+
                       "higher than the minimum S/N for calibration to occur.")
        create_tooltip(calibration_min_total_label, "The minimum number of "+
                       "calibrants in the whole m/z range that have a S/N "+
                       "higher than the minimum S/N for calibration to occur.")
        create_tooltip(extraction_mass_window_label, "The m/z window in "+
                       "Thomson around the specified exact m/z of a feature "+
                       "that MassyTools will use for quantitation. For "+
                       "example, a value of 0.1 results in MassyTools "+
                       "quantifying 999.9 to 1000.1 for a feature with a m/z "+
                       "value of 1000.")
        create_tooltip(extraction_min_total_label, "The minimum fraction of "+
                       "the theoretical isotopic pattern that MassyTools "+
                       "will use for quantitation. For example, a value of "+
                       "0.95 means that MassyTools will quantify isotopes "+
                       "until the sum of the quantified isotopes exceeds "+
                       "0.95 of the total theoretcal isotopic pattern.")
        create_tooltip(extraction_background_window_label, "The mass window "+
                       "in Dalton that MassyTools is allowed to use to "+
                       "determine the local background and noise for each "+
                       "analyte. For example, a value of 10 means that "+
                       "MassyTools will use the region betwee 990 and 1010 "+
                       "m/z for an analyte with an exact m/z of 1000.")
        create_tooltip(extraction_qc_sn_label, "The minimal S/N that an "+
                       "analyte has to have to be included in the analyte QC"+
                       ", e.g. the fraction of analyte intensity above S/N X"+
                       ", where X is the value specified here.")

        # Self assignment
        self.root = root
        self.calibration_window = calibration_window
        self.calibration_sn = calibration_sn
        self.calibration_min_low = calibration_min_low
        self.calibration_min_medium = calibration_min_medium
        self.calibration_min_high = calibration_min_high
        self.calibration_min_total = calibration_min_total
        self.extraction_mass_window = extraction_mass_window
        self.extraction_min_total =  extraction_min_total
        self.extraction_background_window = extraction_background_window
        self.extraction_qc_sn = extraction_qc_sn
