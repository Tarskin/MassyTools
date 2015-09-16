#! /usr/bin/env python
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from scipy.interpolate import interp1d
from scipy.optimize import fmin
from Tkinter import *
import fileinput
import glob
import itertools
import math
import matplotlib.pyplot as plt
import matplotlib
import os
import numpy
import sys
import tkFileDialog
import tkMessageBox
import ttk

# File
EXTENSION = ".xy"										# Extension of datafiles to be used during batch process
OUTPUT_FILE = "Summary.txt"								# Default name for the second half of the output file
SETTINGS_FILE = "Settings.txt"							# Default name for the measurement settings file

# Extraction Parameters
MASS_MODIFIERS = ['free']								# Mass modifiers applied to all analytes (Default is addition of H2O)
CHARGE_CARRIER = ['sodium']								# The Charge carrier of an analyte (Default is addition of a proton)
CALCULATION_WINDOW = 0.49								# Default range to sum around the calculated m/z
OUTER_BCK_BORDER = 20									# Maximum range to search for background signal
S_N_CUTOFF = 9											# Minimum signal to noise value of an analyte to be included in the percentage QC
MIN_TOTAL_CONTRIBUTION = 0.95							# Minimum total contribution of isotopes (of the total distribution) to be extracted

# Advanced Extraction Parameters (DO NOT CHANGE THESE UNLESS YOU KNOW WHAT YOU ARE DOING!!)
MIN_CONTRIBUTION = 0.0001								# Minimum contribution of an isotope to the total distribution to be included in the extraction

# Calibration Parameters
CALIBRATION_WINDOW = 0.4								# Default window for calibration (if no exclusion list is used)
CALIB_S_N_CUTOFF = 9									# Minimum signal to noise value for a calibrant to be included in the calibration
NUM_LOW_RANGE = 3										# Minimum number of calibrants in the first 1/3 of spectrum above specified S/N
NUM_MID_RANGE = 2										# Minimum number of calibrants in the second 1/3 of spectrum above specified S/N
NUM_HIGH_RANGE = 0										# Minimum number of calibrants in the third 1/3 of spectrum above specified S/N
NUM_TOTAL = 5											# Minimum number of calibrants in the whole spectrum above specified S/N

# The maximum distance between distinct isotopic masses to be 'pooled'
EPSILON = 0.5

# Isotopic Mass Differences
C = [('13C', 0.0107, 1.00335)]
H = [('2H', 0.00012, 1.00628)]
N = [('15N', 0.00364, 0.99703)]
O18 = [('18O', 0.00205, 2.00425)]
O17 = [('17O', 0.00038, 1.00422)]
S33 = [('33S', 0.0076, 0.99939)]
S34 = [('34S', 0.0429, 1.9958)]
S36 = [('36S', 0.0002, 3.99501)]

# Building block properties
BLOCKS = {	#######################
			# Structural Features #
			#######################
				###################
				# Monosaccharides #
				###################
					'F':{'mass':146.05790879894,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'Fucose',
						'carbons':6,
						'hydrogens':10,
						'nitrogens':0,
						'oxygens':4,
						'sulfurs':0},
					'H':{'mass':162.0528234185,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'Hexose',
						'carbons':6,
						'hydrogens':10,
						'nitrogens':0,
						'oxygens':5,
						'sulfurs':0},
					'N':{'mass':203.07937251951,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'N-Acetyl Hexosamine',
						'carbons':8,
						'hydrogens':13,
						'nitrogens':1,
						'oxygens':5,
						'sulfurs':0},
					'S':{'mass':291.09541650647,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'N-Acetyl Neuraminic Acid',
						'carbons':11,
						'hydrogens':17,
						'nitrogens':1,
						'oxygens':8,
						'sulfurs':0},
					'L':{'mass':273.08485182277,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'Lactonized N-Acetyl Neuraminic Acid',
						'carbons':11,
						'hydrogens':15,
						'nitrogens':1,
						'oxygens':7,
						'sulfurs':0},
					'M':{'mass':305.11106657061,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'Methylated N-Acetyl Neuraminic Acid',
						'carbons':12,
						'hydrogens':19,
						'nitrogens':1,
						'oxygens':8,
						'sulfurs':0},
					'E':{'mass':319.12671663475,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'Ethylated N-Acetyl Neuraminic Acid',
						'carbons':13,
						'hydrogens':21,
						'nitrogens':1,
						'oxygens':8,
						'sulfurs':0},
				#########################
				# Mouse Monosaccharides #
				#########################
					'G':{'mass':307.0903311261,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'N-glycolyl Neuraminic Acid',
						'carbons':11,
						'hydrogens':17,
						'nitrogens':1,
						'oxygens':9,
						'sulfurs':0},
					'Gl':{'mass':289.0797664424,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'Lactonized N-glycolyl Neuraminic Acid',
						'carbons':11,
						'hydrogens':15,
						'nitrogens':1,
						'oxygens':8,
						'sulfurs':0},
					'Ge':{'mass':335.1216312544,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'Ethylated N-glycolyl Neuraminic Acid',
						'carbons':13,
						'hydrogens':21,
						'nitrogens':1,
						'oxygens':9,
						'sulfurs':0},
				#######################
				# Sugar Modifications #
				#######################
					'P':{'mass':79.96633088875,
						'available_for_mass_modifiers':1,
						'available_for_charge_carrier':0,
						'human_readable_name':'Phosphate',
						'carbons':0,
						'hydrogens':1,
						'nitrogens':0,
						'oxygens':3,
						'sulfurs':0},
					'Su':{'mass':79.95681485868,
						'available_for_mass_modifiers':1,
						'available_for_charge_carrier':0,
						'human_readable_name':'Sulfate',
						'carbons':0,
						'hydrogens':0,
						'nitrogens':0,
						'oxygens':3,
						'sulfurs':1},
					'Ac':{'mass':42.0105646837,
						'available_for_mass_modifiers':1,
						'available_for_charge_carrier':0,
						'human_readable_name':'Acetyl',
						'carbons':2,
						'hydrogens':2,
						'nitrogens':0,
						'oxygens':1,
						'sulfurs':0},
				##############################
				# Reducing End Modifications #
				##############################
					'aa':{'mass':139.06332853255,
						'available_for_mass_modifiers':1,
						'available_for_charge_carrier':0,
						'human_readable_name':'2-aminobenzoic acid label',
						'carbons':7,
						'hydrogens':9,
						'nitrogens':1,
						'oxygens':2,
						'sulfurs':0},
					'ab':{'mass':138.07931294986,
						'available_for_mass_modifiers':1,
						'available_for_charge_carrier':0,
						'human_readable_name':'2-aminobenzamide label',
						'carbons':7,
						'hydrogens':10,
						'nitrogens':2,
						'oxygens':1,
						'sulfurs':0},
					'free':{'mass':18.0105646837,
						'available_for_mass_modifiers':1,
						'available_for_charge_carrier':0,
						'human_readable_name':'Water',
						'carbons':0,
						'hydrogens':2,
						'nitrogens':0,
						'oxygens':1,
						'sulfurs':0},
			###################
			# Charge Carriers #
			###################
					#################
					# Positive Mode #
					#################
					'sodium':{'mass':22.98922070,
						'available_for_mass_modifiers':1,
						'available_for_charge_carrier':1,
						'human_readable_name':'Sodium',
						'carbons':0,
						'hydrogens':0,
						'nitrogens':0,
						'oxygens':0,
						'sulfurs':0},
					'potassium':{'mass':38.9631581,
						'available_for_mass_modifiers':1,
						'available_for_charge_carrier':1,
						'human_readable_name':'Potassium',
						'carbons':0,
						'hydrogens':0,
						'nitrogens':0,
						'oxygens':0,
						'sulfurs':0},
					'proton':{'mass':1.007276466812,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':1,
						'human_readable_name':'Proton',
						'carbons':0,
						'hydrogens':0,
						'nitrogens':0,
						'oxygens':0,
						'sulfurs':0},
					#################
					# Negative Mode #
					#################
					'protonLoss':{'mass':-1.007276466812,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':1,
						'human_readable_name':'Proton Loss',
						'carbons':0,
						'hydrogens':0,
						'nitrogens':0,
						'oxygens':0,
						'sulfurs':0},
					'chloride':{'mass':34.969402,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':1,
						'human_readable_name':'Chloride',
						'carbons':0,
						'hydrogens':0,
						'nitrogens':0,
						'oxygens':0,
						'sulfurs':0},
					'acetate':{'mass':59.013851,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':1,
						'human_readable_name':'Acetate',
						'carbons':2,
						'hydrogens':3,
						'nitrogens':0,
						'oxygens':2,
						'sulfurs':0},
					'formate':{'mass':44.998201,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':1,
						'human_readable_name':'Formate',
						'carbons':1,
						'hydrogens':1,
						'nitrogens':0,
						'oxygens':2,
						'sulfurs':0},
					'electron':{'mass':0.00054857990946,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':1,
						'human_readable_name':'Electron',
						'carbons':0,
						'hydrogens':0,
						'nitrogens':0,
						'oxygens':0,
						'sulfurs':0},
			############
			# Elements #
			############
					'_H':{'mass':1.007825,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'Hydrogen',
						'carbons':0,
						'hydrogens':1,
						'nitrogens':0,
						'oxygens':0,
						'sulfurs':0},
					'_C':{'mass':12.000000,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'Carbon',
						'carbons':1,
						'hydrogens':0,
						'nitrogens':0,
						'oxygens':0,
						'sulfurs':0},
					'_N':{'mass':14.003074,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'Nitrogen',
						'carbons':0,
						'hydrogens':0,
						'nitrogens':1,
						'oxygens':0,
						'sulfurs':0},
					'_O':{'mass':15.994915,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'Oxygen',
						'carbons':0,
						'hydrogens':0,
						'nitrogens':0,
						'oxygens':1,
						'sulfurs':0},
					'_S':{'mass':31.972071,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'Sulfur',
						'carbons':0,
						'hydrogens':0,
						'nitrogens':0,
						'oxygens':0,
						'sulfurs':1},
					'_P':{'mass':30.973761,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'Potassium',
						'carbons':0,
						'hydrogens':0,
						'nitrogens':0,
						'oxygens':0,
						'sulfurs':0},
					'_F':{'mass':18.998403,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'Fluor',
						'carbons':0,
						'hydrogens':0,
						'nitrogens':0,
						'oxygens':0,
						'sulfurs':0},
					'_Na':{'mass':22.989770,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'Sodium',
						'carbons':0,
						'hydrogens':0,
						'nitrogens':0,
						'oxygens':0,
						'sulfurs':0},
					'_K':{'mass':38.963708,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'Kalium',
						'carbons':0,
						'hydrogens':0,
						'nitrogens':0,
						'oxygens':0,
						'sulfurs':0},
			#################
			# Custom Blocks #
			#################
					'Q':{'mass':4135.882086,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'Custom',
						'carbons':177,
						'hydrogens':270,
						'nitrogens':50,
						'oxygens':59,
						'sulfurs':3},
					'R':{'mass':2962.590442,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'Custom',
						'carbons':128,
						'hydrogens':219,
						'nitrogens':37,
						'oxygens':41,
						'sulfurs':1},
					'T':{'mass':2346.1348023,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'Custom',
						'carbons':101,
						'hydrogens':163,
						'nitrogens':27,
						'oxygens':33,
						'sulfurs':2},
					'U':{'mass':2183.0709257,
						'available_for_mass_modifiers':0,
						'available_for_charge_carrier':0,
						'human_readable_name':'Custom',
						'carbons':92,
						'hydrogens':154,
						'nitrogens':26,
						'oxygens':33,
						'sulfurs':2}}
UNITS = BLOCKS.keys()


################################################
# Custom navigation toolbar class (unfinished) #
################################################
class NavToolBar(NavigationToolbar2TkAgg):

	def __init__(self, canvas, root, parent):
		self.canvas = canvas
		self.root = root
		self.parent = parent
		NavigationToolbar2TkAgg.__init__(self, canvas, root)


#############################################
# Class definitions (used for storing data) #
#############################################
class Results():

	def __init__(self, name, calibrated, total, totalBck, totalInt, analytes):
		self.name = name
		self.calibrated = calibrated
		self.total = total
		self.totalBck = totalBck
		self.totalInt = totalInt
		self.analytes = analytes


class analyteResult():

	def __init__(self, composition, mass, distribution, background, noise, ppm, isotopes):
		self.composition = composition
		self.mass = mass
		self.distribution = distribution
		self.background = background
		self.noise = noise
		self.ppm = ppm
		self.isotopes = isotopes


class isotopeResult():

	def __init__(self, area, SN, QC):
		self.area = area
		self.SN = SN
		self.QC = QC


class Analyte():

	def __init__(self, composition, mass, window, isotopes, backgroundPoint, backgroundArea, noise):
		self.composition = composition
		self.mass = mass
		self.window = window
		self.isotopes = isotopes
		self.backgroundPoint = backgroundPoint
		self.backgroundArea = backgroundArea
		self.noise = noise
		self.ppm = None


class Isotope():

	def __init__(self, isotope, mass, obsArea, expArea, sn, maxIntensity, qc):
		self.isotope = isotope
		self.mass = mass
		self.obsArea = obsArea
		self.expArea = expArea
		self.sn = sn
		self.maxIntensity = maxIntensity
		self.qc = qc


###############################
# Start of actual application #
###############################
class App():

	def __init__(self, master):
		# VARIABLES
		self.master = master
		self.absoluteIntensity = IntVar()
		self.absoluteIntensityBackground = IntVar()
		self.analyteBackground = IntVar()
		self.analNoise = IntVar()
		self.relativeIntensity = IntVar()
		self.relativeIntensityBackground = IntVar()
		self.correctedRelativeIntensityBackground = IntVar()
		self.percentageSpectrum = IntVar()
		self.percentageAnalytes = IntVar()
		self.percentage = IntVar()
		self.percentageBackground = IntVar()
		self.maxSignalNoise = IntVar()
		self.isoAbsoluteIntensity = IntVar()
		self.ppmQC = IntVar()
		self.qcScore = IntVar()
		self.isoSignalNoise = IntVar()
		self.batchProcessing = 0
		self.batchWindow = 0
		self.measurementWindow = 0
		self.outputWindow = 0
		self.inputFile = ""
		self.calibrationFile = ""
		self.exclusionFile = ""
		self.compositionFile = ""
		self.batchFolder = ""
		self.qualityFile = ""
		self.log = True
		# Attempt to retrieve previously saved settings from settingsfile
		if os.path.isfile('./'+str(SETTINGS_FILE)):
			with open(SETTINGS_FILE,'r') as fr:
				for line in fr:
					line = line.rstrip('\n')
					chunks = line.split()
					if chunks[0] == "MASS_MODIFIERS":
						global MASS_MODIFIERS
						MASS_MODIFIERS = []
						for i in chunks[1:]:
							MASS_MODIFIERS.append(i)
					if chunks[0] == "CHARGE_CARRIER":
						global CHARGE_CARRIER
						CHARGE_CARRIER = []
						CHARGE_CARRIER.append(chunks[1])
		# Nose can be determined in multiple ways
		# Options are 'RMS' and 'MM'
		self.noise = "RMS"
		self.noiseQC = False
		self.batch = False
		self.fig = matplotlib.figure.Figure(figsize=(8, 6))
		# The MassyTools Logo (created by Rosina Plomp, 2015)
		if os.path.isfile('./UI.png'):
			background_image = self.fig.add_subplot(111)
			image = matplotlib.image.imread('./UI.png')
			background_image.axis('off')
			self.fig.set_tight_layout(True)
			background_image.imshow(image)
		# The Canvas
		self.canvas = FigureCanvasTkAgg(self.fig, master=master)
		self.toolbar = NavigationToolbar2TkAgg(self.canvas, root)
		self.canvas.get_tk_widget().pack(fill=BOTH, expand=YES)
		self.canvas.draw()

		# FRAME
		frame = Frame(master)
		master.title("MassyTools 0.1.8.0")
		if os.path.isfile('./Icon.ico'):
			master.iconbitmap(default='./Icon.ico')

		# VARIABLE ENTRIES

		# BUTTONS

		# MENU
		menu = Menu(root)
		root.config(menu=menu)

		filemenu = Menu(menu, tearoff=0)
		menu.add_cascade(label="File", menu=filemenu)
		filemenu.add_command(label="Open Input File", command=self.openFile)

		calibmenu = Menu(menu, tearoff=0)
		menu.add_cascade(label="Calibrate", menu=calibmenu)
		calibmenu.add_command(label="Open Calibration File", command=self.openCalibrationFile)
		calibmenu.add_command(label="Open Exclusion File", command=self.openExclusionFile)
		calibmenu.add_command(label="Calibrate", command=self.calibrateData)

		extractionmenu = Menu(menu, tearoff=0)
		menu.add_cascade(label="Extraction", menu=extractionmenu)
		extractionmenu.add_command(label="Open Composition File", command=self.openCompositionFile)
		extractionmenu.add_command(label="Extract", command=self.extractCompositions)

		qualitymenu = Menu(menu, tearoff=0)
		menu.add_cascade(label="QC", menu=qualitymenu)
		qualitymenu.add_command(label="Open Quality Control File", command=self.openQualityFile)
		qualitymenu.add_command(label="Calculate QC", command=self.singularQualityControl)

		menu.add_command(label="Batch Process", command=lambda: self.batchPopup(self))

		menu.add_command(label="About MassyTools", command=lambda: self.infoPopup())

	def infoPopup(self):
		top = self.top = Toplevel()
		information = ("MassyTools Version 0.1.8.0\n\n"
					   "Written by Bas Jansen, bas.c.jansen@gmail.com\n"
					   "Art by Rosina Plomp, h.r.plomp@lumc.nl\n\n"
					   "MassyTools is designed to be a complete toolkit for\n"
					   "all 2 dimensional mass spectrometry experiments.\n"
					   "The software can both be ran in single spectrum\n"
					   "and batch processing modes. The software can perform\n"
					   "data calibration, data extraction and quality score\n"
					   "calculations (a modification of the Nicolardi et al,\n"
					   "2010 publication).\n\n"
					   "This software is released under the Apache 2.0 License,\n"
					   "Full details regarding this license can be found at\n"
					   "the following URL:\n\n"
					   "http://www.apache.org/licenses/LICENSE-2.0")
		self.about = Label(top, text=information, justify=LEFT)
		self.about.pack()
		top.lift()

	def batchPopup(self, master):
		""" This function creates a pop up box in which all the parameters
		for a batch process can be set and visualized. The window can
		access and set the masters exclusionFile, calibrationFile,
		compositionFile and batchFolder variables. The window can also
		call the outputPopup function (to specify the contents of final
		summary) and start the actual batchProcess function.

		INPUT: None
		OUTPUT: None
		"""
		if master.batchWindow == 1:
			return
		master.batchWindow = 1
		self.calFile = StringVar()
		self.exclFile = StringVar()
		self.compFile = StringVar()
		self.folder = StringVar()

		def calibrationButton():
			master.openCalibrationFile()
			self.calFile.set(master.calibrationFile)

		def exclusionButton():
			master.openExclusionFile()
			self.exclFile.set(master.exclusionFile)

		def compositionButton():
			master.openCompositionFile()
			self.compFile.set(master.compositionFile)

		def batchButton():
			master.openBatchFolder()
			self.folder.set(master.batchFolder)

		def close(self):
			master.batchWindow = 0
			top.destroy()

		top = self.top = Toplevel()
		top.protocol("WM_DELETE_WINDOW", lambda: close(self))
		self.calib = Button(top, text="Calibration File", width=25, command=lambda: calibrationButton())
		self.calib.grid(row=0, column=0, sticky=W)
		self.cal = Label(top, textvariable=self.calFile, width=25)
		self.cal.grid(row=0, column=1, padx=25)
		self.exclus = Button(top, text="Exclusion File", width=25, command=lambda: exclusionButton())
		self.exclus.grid(row=1, column=0, sticky=W)
		self.exc = Label(top, textvariable=self.exclFile, width=25)
		self.exc.grid(row=1, column=1)
		self.compos = Button(top, text="Composition File", width=25, command=lambda: compositionButton())
		self.compos.grid(row=2, column=0, sticky=W)
		self.com = Label(top, textvariable=self.compFile, width=25)
		self.com.grid(row=2, column=1)
		self.batchDir = Button(top, text="Batch Directory", width=25, command=lambda: batchButton())
		self.batchDir.grid(row=3, column=0, sticky=W)
		self.batch = Label(top, textvariable=self.folder, width=25)
		self.batch.grid(row=3, column=1)
		self.measurement = Button(top, text="Measurement Setup", width=25, command=lambda: master.measurementPopup(master))
		self.measurement.grid(row=4, column=0,columnspan=2)
		self.output = Button(top, text="Output Format", width=25, command=lambda: master.outputPopup(master))
		self.output.grid(row=5, column=0, columnspan=2)
		self.run = Button(top, text="Run Batch Process", width=25, command=lambda: master.batchProcess(master))
		self.run.grid(row=6, column=0, columnspan=2)
		# top.lift()
		# Couple the attributes to button presses
		top.attributes("-topmost", True)

	def measurementPopup(self,master):
		""" This function creates a pop up box to specify how the analytes
		were measured, referring to the charge carrier and mass modifiers.
		<STILL IN DEVELOPMENT>

		INPUT: None
		OUTPUT: None
		"""
		options = []
		self.chargeCarrierVar = StringVar()
		self.chargeCarrierVar.set(CHARGE_CARRIER[0])

		def onselect1(evt):
			w = evt.widget
			index = int(w.curselection()[0])
			value = w.get(index)
			master.selected.insert(END,value)
			master.avail.delete(index)

		def onselect2(evt):
			w = evt.widget
			index = int(w.curselection()[0])
			value = w.get(index)
			master.selected.delete(index)
			master.avail.insert(END,value)

		def close(self):
			global MASS_MODIFIERS			# Evil... I know
			global CHARGE_CARRIER			# Ditto
			MASS_MODIFIERS = []
			values = master.selected.get(0, END)
			for i in values:
				for j in UNITS:
					if str(i) == BLOCKS[j]['human_readable_name'] and BLOCKS[j]['available_for_mass_modifiers']:
						MASS_MODIFIERS.append(j)
			CHARGE_CARRIER = []
			for i in UNITS:
				if str(i) == master.chargeCarrierVar.get() and BLOCKS[i]['available_for_charge_carrier'] == 1:
					CHARGE_CARRIER.append(i)
			master.measurementWindow = 0
			top.destroy()

		def save(self):
			global MASS_MODIFIERS			# Evil... I know
			global CHARGE_CARRIER			# Ditto
			MASS_MODIFIERS = []
			values = master.selected.get(0, END)
			for i in values:
				for j in UNITS:
					if str(i) == BLOCKS[j]['human_readable_name'] and BLOCKS[j]['available_for_mass_modifiers']:
						MASS_MODIFIERS.append(j)
			CHARGE_CARRIER = []
			for i in UNITS:
				if str(i) == master.chargeCarrierVar.get() and BLOCKS[i]['available_for_charge_carrier'] == 1:
					CHARGE_CARRIER.append(i)
			with open(SETTINGS_FILE,'w') as fw:
				fw.write("MASS_MODIFIERS")
				for i in MASS_MODIFIERS:
					fw.write("\t"+str(i))
				fw.write("\nCHARGE_CARRIER\t"+str(CHARGE_CARRIER[0])+"\n")

		if master.measurementWindow == 1:
			return

		master.measurementWindow = 1
		top = self.top = Toplevel()
		top.protocol( "WM_DELETE_WINDOW", lambda: close(self))
		self.charge = Label(top, text = "Charge", width = 10)
		self.charge.grid(row = 0, column = 0, sticky = W)
		self.min = Label(top, text = "Min", width = 5)
		self.min.grid(row=0, column = 1, sticky = W)
		self.minCharge = Spinbox(top, from_= 1, to = 3, width = 5)
		self.minCharge.grid(row = 0, column = 2, sticky = W)
		self.max = Label(top, text = "Max", width = 5)
		self.max.grid(row = 0, column = 3, sticky = W)
		self.maxCharge = Spinbox(top, from_ = 1, to=3, width=5)
		self.maxCharge.grid(row = 0, column = 4, sticky = W)
		# Construct charge carrier option menu
		for i in UNITS:
			if BLOCKS[i]['available_for_charge_carrier'] == 1:
				options.append(i)
		self.chargeCarrier = OptionMenu(top, self.chargeCarrierVar, *options)
		self.chargeCarrier.grid(row = 0, column = 5, sticky = W)
		self.availMass = Label(top, text = "Available")
		self.availMass.grid(row = 1, column = 1, sticky = W)
		self.selectMass = Label(top, text = "Selected")
		self.selectMass.grid(row = 1, column = 3, sticky = W)
		self.massMod = Label(top, text = "Mass Mods")
		self.massMod.grid(row = 2, column = 0, sticky = W)
		self.avail = Listbox(top)
		self.avail.grid(row = 2, column = 1, columnspan = 2, sticky = W)
		self.avail.bind('<<ListboxSelect>>',onselect1)
		self.selected = Listbox(top)
		self.selected.grid(row = 2, column = 3, columnspan = 2, sticky = W)
		self.selected.bind('<<ListboxSelect>>',onselect2)
		# Construct mass modifier list box
		for i in UNITS:
			if i in MASS_MODIFIERS:
				self.selected.insert(END,BLOCKS[i]['human_readable_name'])
			elif BLOCKS[i]['available_for_mass_modifiers'] == 1:
				self.avail.insert(END,BLOCKS[i]['human_readable_name'])
		self.ok = Button(top,text = 'Ok', command = lambda: close(self))
		self.ok.grid(row = 3, column = 0, sticky = W)
		self.save = Button(top, text = 'Save', command = lambda: save(self))
		self.save.grid(row = 3, column = 5, sticky = E)

	def outputPopup(self, master):
		""" This function creates a pop up box to specify what output
		should be shown in the final summary. The default value for all
		variables is off (0) and by ticking a box it is set to on (1).

		INPUT: None
		OUTPUT: None
		"""
		if master.outputWindow == 1:
			return
		master.outputWindow = 1

		def select_all(self):
			master.absoluteIntensity.set(1)
			master.absoluteIntensityBackground.set(1)
			master.analyteBackground.set(1)
			master.analNoise.set(1)
			master.relativeIntensity.set(1)
			master.relativeIntensityBackground.set(1)
			master.correctedRelativeIntensityBackground.set(1)
			master.percentageSpectrum.set(1)
			master.percentageAnalytes.set(1)
			master.percentage.set(1)
			master.percentageBackground.set(1)
			master.maxSignalNoise.set(1)
			master.qcScore.set(1)
			master.ppmQC.set(1)
			master.isoSignalNoise.set(1)
			master.isoAbsoluteIntensity.set(1)

		def select_none(self):
			master.absoluteIntensity.set(0)
			master.absoluteIntensityBackground.set(0)
			master.analyteBackground.set(0)
			master.analNoise.set(0)
			master.relativeIntensity.set(0)
			master.relativeIntensityBackground.set(0)
			master.correctedRelativeIntensityBackground.set(0)
			master.percentageSpectrum.set(0)
			master.percentageAnalytes.set(0)
			master.percentage.set(0)
			master.percentageBackground.set(0)
			master.maxSignalNoise.set(0)
			master.qcScore.set(0)
			master.ppmQC.set(0)
			master.isoSignalNoise.set(0)
			master.isoAbsoluteIntensity.set(0)

		def close(self):
			master.outputWindow = 0
			top.destroy()

		top = self.top = Toplevel()
		top.protocol("WM_DELETE_WINDOW", lambda: close(self))
		self.all = Button(top, text="Select All", command=lambda: select_all(self))
		self.all.grid(row=0, column=0, sticky=W)
		self.none = Button(top, text="Select None", command=lambda: select_none(self))
		self.none.grid(row=0, column=1, sticky=E)
		self.ai = Checkbutton(top, text="Analyte Area", variable=master.absoluteIntensity, onvalue=1, offvalue=0)
		self.ai.grid(row=1, column=0, sticky=W)
		self.aiBck = Checkbutton(top, text="Analyte Area - Background Area", variable=master.absoluteIntensityBackground, onvalue=1, offvalue=0)
		self.aiBck.grid(row=2, column=0, sticky=W)
		self.Bck = Checkbutton(top, text="Analyte Background Area", variable=master.analyteBackground, onvalue=1, offvalue=0)
		self.Bck.grid(row=3, column=0, sticky=W)
		self.anNoise = Checkbutton(top, text="Analyte Noise", variable=master.analNoise, onvalue=1, offvalue=0)
		self.anNoise.grid(row=4, column=0, sticky=W)
		self.ri = Checkbutton(top, text="Relative Area", variable=master.relativeIntensity, onvalue=1, offvalue=0)
		self.ri.grid(row=5, column=0, sticky=W)
		self.riBck = Checkbutton(top, text="Relative Area - Background Area", variable=master.relativeIntensityBackground, onvalue=1, offvalue=0)
		self.riBck.grid(row=6, column=0, sticky=W)
		self.corRiBck = Checkbutton(top, text="Corrected Relative Area - Background Area", variable=master.correctedRelativeIntensityBackground, onvalue=1, offvalue=0)
		self.corRiBck.grid(row=7, column=0, sticky=W)
		self.percSpec = Checkbutton(top, text="Fraction of spectrum explained by analytes", variable=master.percentageSpectrum, onvalue=1, offvalue=0)
		self.percSpec.grid(row=8, column=0, sticky=W)
		self.percAnal = Checkbutton(top, text="Fraction of analytes above S/N Cutoff", variable=master.percentageAnalytes, onvalue=1, offvalue=0)
		self.percAnal.grid(row=9, column=0, sticky=W)
		self.perc = Checkbutton(top, text="Fraction of Analytes Area above S/N Cutoff", variable=master.percentage, onvalue=1, offvalue=0)
		self.perc.grid(row=10, column=0, sticky=W)
		self.percBck = Checkbutton(top, text="Fraction of Analytes Area - Background Area above S/N Cutoff", variable=master.percentageBackground, onvalue=1, offvalue=0)
		self.percBck.grid(row=11, column=0, sticky=W)
		self.sn = Checkbutton(top, text="Maximum S/N", variable=master.maxSignalNoise, onvalue=1, offvalue=0)
		self.sn.grid(row=12, column=0, sticky=W)
		self.qc = Checkbutton(top, text="Quality Score", variable=master.qcScore, onvalue=1, offvalue=0)
		self.qc.grid(row=13, column=0, sticky=W)
		self.ppm = Checkbutton(top, text="PPM Error", variable=master.ppmQC, onvalue=1, offvalue=0)
		self.ppm.grid(row=14, column=0, sticky=W)
		self.isosn = Checkbutton(top, text="Isotope S/N", variable=master.isoSignalNoise, onvalue=1, offvalue=0)
		self.isosn.grid(row=15, column=0, sticky=W)
		self.isoai = Checkbutton(top, text="Isotope Area - Background Area", variable=master.isoAbsoluteIntensity, onvalue=1, offvalue=0)
		self.isoai.grid(row=16, column=0, sticky=W)
		self.button = Button(top, text='Ok', command=lambda: close(self))
		self.button.grid(row=17, column=0, columnspan=2)
		top.lift()

	def openFile(self):
		""" This function opens a Tkinter filedialog, asking the user
		to select a file. The chosen file is then read (by the readData
		function) and the read data is used to plot the selected spectrum
		on the screen (by the plotData function).

		INPUT: None
		OUTPUT: None
		"""
		file_path = tkFileDialog.askopenfilename()
		if not file_path:
			pass
		else:
			setattr(self, 'inputFile', file_path)
			data = self.readData(self.inputFile)
			self.plotData(data)

	def openCalibrationFile(self):
		""" This function opens a Tkinter filedialog, asking the user
		to select a file. The chosen file is then set to the
		self.calibrationFile variable.

		INPUT: None
		OUTPUT: None
		"""
		file_path = tkFileDialog.askopenfilename()
		if not file_path:
			pass
		else:
			setattr(self, 'calibrationFile', file_path)

	def openCompositionFile(self):
		""" This function opens a Tkinter filedialog, asking the user
		to select a file. The chosen file is then set to the
		self.compositionFile variable.

		INPUT: None
		OUTPUT: None
		"""
		file_path = tkFileDialog.askopenfilename()
		if not file_path:
			pass
		else:
			setattr(self, 'compositionFile', file_path)

	def openExclusionFile(self):
		""" This function opens a Tkinter filedialog, asking the user
		to select a file. The chosen file is then set to the
		self.exclusionFile variable.

		INPUT: None
		OUTPUT: None
		"""
		file_path = tkFileDialog.askopenfilename()
		if not file_path:
			pass
		else:
			setattr(self, 'exclusionFile', file_path)

	def openQualityFile(self):
		""" This function opens a Tkinter filedialog, asking the user
		to select a file. The chosen file is then set to the
		self.qualityFile variable.

		INPUT: None
		OUTPUT: None
		"""
		file_path = tkFileDialog.askopenfilename()
		if not file_path:
			pass
		else:
			setattr(self, 'qualityFile', file_path)

	def openBatchFolder(self):
		""" This function opens a Tkinter filedialog, asking the user
		to select a directory. The chosen directory is then set to the
		self.batchFolder variable.

		INPUT: None
		OUTPUT: None
		"""
		folder_path = tkFileDialog.askdirectory()
		if not folder_path:
			pass
		else:
			setattr(self, 'batchFolder', folder_path)

	def batchProcess(self, master):
		""" This function controlls the batch analysis functionality.
		The function first checks if at least one meaningful file is
		selected and if not gives a 'File Error'. The function will then
		perform first the calibration (if self.calibrationFile is set)
		and then the extraction (if self.compositionFile is set). The
		quality control is performed during the extraction (using the
		self.compositionFile as the input analytes).

		INPUT: None
		OUTPUT: None
		"""
		# Safety feature (prevents batchProcess from being started multiple times)
		if master.batchProcessing == 1:
			# Destroy progress bar
			barWindow.destroy()
			tkMessageBox.showinfo("Error Message", "Batch Process already running")
			return
		master.batchProcessing = 1
		#####################
		# PROGRESS BAR CODE #
		#####################
		self.calPerc = StringVar()
		self.extPerc = StringVar()
		self.calPerc.set("0%")
		self.extPerc.set("0%")
		# barWindow = Tk()
		barWindow = self.top = Toplevel()
		barWindow.title("Progress Bar")
		cal = Label(barWindow, text="Calibration", padx=25)
		cal.grid(row=0, column=0, sticky="W")
		ft = ttk.Frame(barWindow)
		ft.grid(row=1, columnspan=2, sticky="")
		perc1 = Label(barWindow, textvariable=self.calPerc)
		perc1.grid(row=0, column=1, padx=25)
		progressbar = ttk.Progressbar(ft, length=100, mode='determinate')
		progressbar.grid(row=1, columnspan=2, sticky="")
		ext = Label(barWindow, text="Extraction", padx=25)
		ext.grid(row=2, column=0, sticky="W")
		ft2 = ttk.Frame(barWindow)
		ft2.grid(row=3, columnspan=2, sticky="")
		perc2 = Label(barWindow, textvariable=self.extPerc)
		perc2.grid(row=2, column=1, padx=25)
		progressbar2 = ttk.Progressbar(ft2, length=100, mode='determinate')
		progressbar2.grid(row=3, columnspan=2, sticky="")
		###################
		# END OF BAR CODE #
		###################
		results, filesGrabbed = ([] for i in range(2))
		self.batch = True
		if self.calibrationFile == "" and self.compositionFile == "":
			tkMessageBox.showinfo("File Error", "No calibration or composition file selected")
			# Clear the batchProcess lock
			master.batchProcessing = 0
			return
		# Initialize the composition file (to only calculate isotopic patterns once
		if self.compositionFile != "":
			self.initCompositionMasses(self.compositionFile)
		for file in glob.glob(str(self.batchFolder)+"/*" + EXTENSION):
			name = os.path.split(file)
			omittedFiles = ('calibrated', 'uncalibrated')
			if any(x in name[-1] for x in omittedFiles):
				pass
			else:
				filesGrabbed.append(file)
		for index, file in enumerate(filesGrabbed):
			self.inputFile = file
			if self.calibrationFile != "":  # and self.exclusionFile != "":
				# Update the calibration progress bar
				self.calPerc.set(str(int( (float(index) / float(len(filesGrabbed) ) ) *100))+"%")
				# print "CalPerc is now set to: "+str(self.calPerc.get())
				progressbar["value"] = int( (float(index) / float(len(filesGrabbed) ) ) *100)
				progressbar.update()
				if self.log is True:
					with open('MassyTools.log', 'a') as fw:
						fw.write(str(datetime.now())+"\tAttempting to calibrate "+str(self.inputFile)+"\n")
				self.calibrateData()
		# Ensure that calibration progress bar is filled at the end
		self.calPerc.set("100%")
		progressbar["value"] = 100
		del filesGrabbed[:]
		for file in glob.glob(str(self.batchFolder)+"/calibrated_*" + EXTENSION):
			omittedFiles = ('_calibrated', '_uncalibrated')
			if any(x in name[-1] for x in omittedFiles):
				pass
			else:
				filesGrabbed.append(file)
		for index, file in enumerate(filesGrabbed):
			self.inputFile = file
			if self.compositionFile != "":
				# Update the extraction progress bar
				self.extPerc.set(str(int( (float(index) / float(len(filesGrabbed) ) ) *100))+"%")
				progressbar2["value"] = int( (float(index) / float(len(filesGrabbed) ) ) *100)
				progressbar2.update()
				if self.log is True:
					with open('MassyTools.log', 'a') as fw:
						fw.write(str(datetime.now())+"\tExtracting values from "+str(self.inputFile)+"\n")
				compositions = self.calcCompositionMasses(self.compositionFile)
				compositions = self.extractData(self.inputFile, compositions)
				# Disabled to prevent spam, useful for in-depth analysis
				# self.calcErrorAll(file,compositions)
				if self.qcScore.get() == 1:
					self.qualityFile = self.compositionFile
					if self.log is True:
						with open('MassyTools.log', 'a') as fw:
							fw.write(str(datetime.now())+"\tAttempting to calculate QC values for "+str(self.inputFile)+"\n")
					compositions = self.qualityControl(compositions)
				self.writeResults(compositions)
		# Ensure that extraction progress bar is filled at the end
		self.extPerc.set("100%")
		progressbar2["value"] = 100
		self.combineResults()
		# Clear the batchProcess lock
		master.batchProcess = 0
		# Destroy progress bar
		barWindow.destroy()
		tkMessageBox.showinfo("Status Message", "Batch Process finished on "+str(datetime.now()))

	def checkMaximaSpacing(self, maxima, data):
		""" This function ensures that the observed local maxima
		(calibrants) are in accordance with the calibration rules (set
		at the top of the program). The function examines three distinct
		regions:

		start - ( ( end <-> start ) / 3 ) + start
		( ( end - start ) /3 ) + start <-> ( ( ( end-start)/3)*2 ) + start
		( ( ( end-start)/3)*2 ) + start <-> end

		The number of maxima in each region is summed and compared to
		NUM_LOW_RANGE, NUM_MID_RANGE and NUM_HIGH_RANGE. The sum of all
		regions is compared with NUM_TOTAL.

		INPUT 1: A list containing floats (the m/z of local maxima)
		INPUT 2: A list of (m/z, intensity) tuples
		OUTPUT: A Boolean (True if the check passes, False if not)
		"""
		countLow = 0
		countMid = 0
		countHigh = 0
		spectraRange = data[-1][0] - data[0][0]
		for i in maxima:
			if i > data[0][0] and i < data[0][0]+spectraRange/3:
				countLow += 1
			if i > data[0][0]+spectraRange/3 and i < (data[0][0]+(spectraRange/3)*2):
				countMid += 1
			if i > (data[0][0]+(spectraRange/3)*2) and i < data[-1][0]:
				countHigh += 1
		# Compare the observed number of calibrants with the 'desired' number
		if countLow >= NUM_LOW_RANGE and countMid >= NUM_MID_RANGE and countHigh >= NUM_HIGH_RANGE and countLow + countMid + countHigh >= NUM_TOTAL: #NUM_LOW_RANGE + NUM_MID_RANGE + NUM_HIGH_RANGE:
			return True
		else:
			return False

	def createInclusionList(self, potentialCalibrants):
		""" This function creates a simple inclusion list based on the
		potential calibrants that were supplied. This function is only
		called if the user did not supply an exclusion list. The function
		takes the list of potentialCalibrants and subtracts/adds the
		user defined CALIBRATION_WINDOW to the calibrant m/z and appends
		both values as a tuple to a list.

		INPUT: A list containing floats (the calibrant m/z's)
		OUTPUT: A list of float tuples (begin,end)
		"""
		included = []
		for i in potentialCalibrants:
			included.append((float(i)-CALIBRATION_WINDOW, float(i)+CALIBRATION_WINDOW))
		return included

	def calcDistribution(self, element, number):
		""" This function calculates the fraction of the total intensity
		that is present in each isotope of the given element based on
		a binomial distribution. The function takes the name of the
		element and the number of atoms of said element as an input and
		returns a list of (m/z,fraction) tuples. The number of isotopes
		that is returned is dependant on the distribution, once fractions
		fall below 0.01 the function stops.

		INPUT1: A string containing the code for the element (ie 33S)
		INPUT2: An integer listing the number of atoms
		OUTPUT: A list of float tuples (isotope m/z, isotope fraction).
		"""
		fractions = []
		for i in element:
			j = 0
			while j <= number:
				nCk = math.factorial(number) / (math.factorial(j) * math.factorial(number - j))
				f = nCk * i[1]**j * (1 - i[1])**(number-j)
				fractions.append((i[2]*j, f))
				j += 1
				if f <= MIN_CONTRIBUTION:
					break
		return fractions

	def parseAnalyte(self, Analyte):
		""" This function splits the Analyte input string into a parts
		and calculates the total number of each element of interest per
		Analyte. The function will then attach further elements based on
		the user specified mass modifiers before calling the isotopic
		distribution function. The function finally returns a list
		containing the analyte mass and distribution lists for each
		isotopic state.

		INPUT: A string containing the Analyte (ie 'H4N4')
		OUTPUT: A list containing the Analyte m/z followed by several
				other lists (1 for each isotopic state).
		"""
		results = []
		mass = 0
		numCarbons = 0
		numHydrogens = 0
		numNitrogens = 0
		numOxygens = 0
		numSulfurs = 0
		totalElements = 0
		units = ["".join(x) for _, x in itertools.groupby(Analyte, key=str.isalpha)]
		# Calculate the bass composition values
		for index, j in enumerate(units):
			for k in UNITS:
					if j == k:
						mass += float(BLOCKS[k]['mass']) * float(units[index+1])
						numCarbons += int(BLOCKS[k]['carbons']) * int(units[index+1])
						numHydrogens += int(BLOCKS[k]['hydrogens']) * int(units[index+1])
						numNitrogens += int(BLOCKS[k]['nitrogens']) * int(units[index+1])
						numOxygens += int(BLOCKS[k]['oxygens']) * int(units[index+1])
						numSulfurs += int(BLOCKS[k]['sulfurs']) * int(units[index+1])
		# Attach the mass modifier values
		totalMassModifiers = MASS_MODIFIERS + CHARGE_CARRIER
		for j in totalMassModifiers:
			mass += float(BLOCKS[j]['mass'])
			numCarbons += float(BLOCKS[j]['carbons'])
			numHydrogens += int(BLOCKS[j]['hydrogens'])
			numNitrogens += int(BLOCKS[j]['nitrogens'])
			numOxygens += int(BLOCKS[j]['oxygens'])
			numSulfurs += int(BLOCKS[j]['sulfurs'])
		# Calculate the distribution for the given value
		carbons = self.calcDistribution(C, numCarbons)
		hydrogens = self.calcDistribution(H, numHydrogens)
		nitrogens = self.calcDistribution(N, numNitrogens)
		oxygens17 = self.calcDistribution(O17, numOxygens)
		oxygens18 = self.calcDistribution(O18, numOxygens)
		sulfurs33 = self.calcDistribution(S33, numSulfurs)
		sulfurs34 = self.calcDistribution(S34, numSulfurs)
		sulfurs36 = self.calcDistribution(S36, numSulfurs)
		return ((mass, carbons, hydrogens, nitrogens, oxygens17, oxygens18, sulfurs33, sulfurs34, sulfurs36))

	def getChanceNetwork(self, (mass, carbons, hydrogens, nitrogens, oxygens17, oxygens18, sulfurs33, sulfurs34, sulfurs36)):
		""" This function calculates the total chance network based on
		all the individual distributions. The function multiplies all
		the chances to get a single chance for a single option.

		INPUT: A list containing the Analyte m/z followed by several
			   other lists (1 for each isotopic state).
		OUTPUT: A list of float tuples (isotopic m/z, isotopic chance)
		"""
		totals = []
		for x in itertools.product(carbons, hydrogens, nitrogens, oxygens17, oxygens18, sulfurs33, sulfurs34, sulfurs36):
			i, j, k, l, m, n, o, p = x
			totals.append((mass+i[0]+j[0]+k[0]+l[0]+m[0]+n[0]+o[0]+p[0],
						   i[1]*j[1]*k[1]*l[1]*m[1]*n[1]*o[1]*p[1]))
		return totals

	def mergeChances(self, totals):
		""" This function merges all the isotopic chances based on the
		specified resolution of the machine.

		INPUT: A list of float tuples (isotopic m/z, isotopic chance)
		OUTPUT: A sorted list of float tuples (isotopic m/z, isotopic
				chance).
		"""
		results = []
		newdata = {d: True for d in totals}
		for k, v in totals:
			if not newdata[(k, v)]: continue
			newdata[(k, v)] = False
			# use each piece of data only once
			keys, values = [k*v], [v]
			for kk, vv in [d for d in totals if newdata[d]]:
				if abs(k-kk) < EPSILON:
					keys.append(kk*vv)
					values.append(vv)
					newdata[(kk, vv)] = False
			results.append((sum(keys)/sum(values), sum(values)))
		return results

	def calibrateData(self):
		""" This function controls the calibration process. The function
		first checks if the self.calibrationFile variable was set (return
		a 'File Error' if not). The function then reads the
		self.calibrationFile to get a list of potentialCalibrants. The
		function then creates an inclusionList (based on an exclusionFile
		or the calibrants and a user defined window (CALIBRATION_WINDOW)).
		The function then reads the input file into a list of (m/z,int)
		tuples from which it attempts to find the local maxima (given
		the inclusionList). The actual observed m/z of the calibrants
		that passed the S/N Cutoff is then used to verify if enough
		calibrants were present (based on calibration rule at top of
		program). A 2nd degree polynomial is fitted through the pairs
		of expected m/z (actualCalibrants) and observed m/z (maximaMZ).
		The polynomial function is used to create a new datafile with
		transformed m/z values, the transformed spectrum is also shown
		on the main window (if the program is not running in batchProcess
		mode).

		INPUT: None
		OUTPUT: None
		"""
		if self.calibrationFile == "":
			tkMessageBox.showinfo("File Error", "No calibration file selected")
			return
		maximaMZ = []
		#window = self.calibrationMenu()
		potentialCalibrants = self.readCalibrants()
		if self.exclusionFile != "":
			included = self.readInclusionRange()
		else:
			included = self.createInclusionList(potentialCalibrants)
		data = self.readData(self.inputFile)
		maxima = self.getLocalMaxima(data, included)
		actualCalibrants = self.getObservedCalibrants(maxima, potentialCalibrants)
		if self.checkMaximaSpacing(actualCalibrants, data) is False:
			if self.log is True:
				with open('MassyTools.log', 'a') as fw:
					fw.write(str(datetime.now())+"\tNot enough datapoints for calibration\n")
			self.writeUncalibratedFile()
			return
		# Strip the m/z values from the maxima
		for i in maxima:
			if i[1] == 0:
				if self.log is True:
					with open('MassyTools.log', 'a') as fw:
						fw.write(str(datetime.now())+"\tUnexpected error!\n")
			else:
				maximaMZ.append(i[0])
		# Perform 2d degree polynomial fit
		z = numpy.polyfit(maximaMZ, actualCalibrants, 2)
		f = numpy.poly1d(z)
		y = f(maximaMZ)
		# Display the calibrated plot on the main screen
		if self.batch is False:
			self.plotChange(data, f)
		self.writeCalibration(y, actualCalibrants)
		# Call function to write away calibrated file
		# Ideally this would throw a pop up with calibration
		# parameters and display the calibration 'curve'
		self.transformFile(f)

	def writeCalibration(self, observed, expected):
		""" This function takes the calibrant observed m/z and expected
		m/z and calculates the PPM error after calibration from those
		values. The expected, observed m/z and ppm error are then written
		to a file (calibrated_{input_name}.error).

		INPUT 1: A list of m/z values (the observed m/z for calibrants)
		INPUT 2: A list of m/z values (the expected m/z for calibrants)
		OUTPUT: None
		"""
		errors = []
		name = os.path.split(str(self.inputFile))[-1]
		name = name.split(".")[0]
		name = "calibrated_"+name+str(".error")
		# Maybe replace batchFolder with outputFolder?
		name = os.path.join(self.batchFolder, name)
		with open(name, 'w') as fw:
			fw.write("Expected\tObserved\tPPM Error\n")
		for index, i in enumerate(observed):
			ppm = ((i-expected[index])/expected[index])*1000000
			errors.append((expected, i, ppm))
			with open(name, 'a') as fw:
				fw.write(str(expected[index])+"\t"+str(i)+"\t"+str(ppm)+"\n")
		if self.batch == 0:
			self.displayError(errors)

	def displayError(self, errors):
		""" This function takes the residual mass error (in ppm) after
		calibration and displays a graph visualize this difference. The
		graph is opened in a new window with it's own navigation bar.

		INPUT: A list of (expected m/z, observed m/z, ppm error) tuples
		OUTPUT: None
		"""
		root2 = Toplevel()
		fig2 = plt.Figure()
		canvas2 = FigureCanvasTkAgg(fig2, master=root2)
		toolbar2 = NavigationToolbar2TkAgg(canvas2, root2)
		canvas2.show()
		canvas2.get_tk_widget().pack(fill=BOTH, expand=YES)
		x_array = []
		y_array = []
		labels = []
		for counter, i in enumerate(errors):
			x_array.append(counter)
			labels.append(i[0])
			y_array.append(i[2])
		axes = fig2.add_subplot(111)
		axes.scatter(x_array, y_array)
		##################################################################
		# The following chunk is relevant if you wish to have labels and #
		# ticks on the y-axis											 #
		##################################################################
		"""print x_array[1],x_array[-1]
		self.axes.set_xticks((x_array[1],x_array[-1]),1)
		self.axes.set_xticklabels(labels,rotation=90)
		self.axes.set_xlabel('Analyte number (to be changed)')"""
		axes.tick_params(axis='x', which='both', bottom='off', top='off', labelbottom='off')
		axes.set_ylabel('Mass error (ppm)')
		axes.hlines(0, x_array[0]-0.5, x_array[-1]+0.5)
		axes.set_xlim(x_array[0]-0.5, x_array[-1]+0.5)
		for counter, i in enumerate(errors):
			axes.annotate(i[1], (x_array[counter]+0.1, y_array[counter]+0.1))
			axes.vlines(x_array[counter], 0, y_array[counter], linestyles='dashed')
		canvas2.draw()

	def writeUncalibratedFile(self):
		""" This function reads the uncalibrated data file and writes it
		away as an uncalibrated data file, this is important to have
		these files listed in the final output (summary).

		INPUT: None
		OUTPUT: None
		"""
		with open(self.inputFile, 'r') as fr:
			parts = os.path.split(str(self.inputFile))
			output = "uncalibrated_"+str(parts[-1])
			# Maybe change batchFolder into outputFolder
			output = os.path.join(self.batchFolder, output)
			with open(output, 'w') as fw:
				for line in fr:
					line = line.rstrip('\n')
					fw.write(line+"\n")

	def gaussFunction(self, x, *p):
		""" This function contains the guassian prototype used in
		scipy curve fitting.

		INPUT 1: Data ?
		INPUT 2: A set of starting variable values
		OUTPUT: A representation of the guassian function ?
		"""
		A, mu, sigma = p
		return A*numpy.exp(-(x-mu)**2/(2.*sigma**2))

	def getLocalMaxima(self, data, included):
		""" This function parses the data per entry of the included list.
		A set of binary searches is performed to find the elements of
		data belonging to the current calibrant (included list). A
		list of several windows in front of each calibrant region is
		examined to retrieve the background area, background intensity
		and average noise levels (required to determine calibrant S/N
		after background subtraction). A spline is fitted through the
		datapoints in the calibrant region from which the local maximum
		m/z coordinate is retrieved, the m/z value is appended to a list
		(maxima) if it is above the user specified S/N cutoff.

		INPUT 1: A list of (m/z, intensity) tuples
		INPUt 2: A list of (m/z, m/z) tuples
		OUTPUT: A list of floats ((m/z,intensity), the observed local maxima)
		"""
		maxima = []
		for i in included:
			backgroundValue = 1000000000
			noise = 0
			maximum = (0, 0)
			totals = []
			begin = self.search_right(data, i[0], len(data))
			end = self.search_left(data, i[1], len(data))
			# Create data subsets for each window
			for j in range(-OUTER_BCK_BORDER, OUTER_BCK_BORDER):
				windowIntensities = []
				begin2 = self.search_right(data, i[0]-j*C[0][2], len(data))
				end2 = self.search_left(data, i[1]-j*C[0][2], len(data))
				for k in data[begin2:end2]:
					windowIntensities.append(k[1])
				totals.append(windowIntensities)
			# Find the set of 5 consecutive windows with lowest average intensity
			for j in range(0, (2*OUTER_BCK_BORDER)-4):
				mix = totals[j]+totals[j+1]+totals[j+2]+totals[j+3]+totals[j+4]
				dev = numpy.std(mix)
				avg = numpy.average(mix)
				temp = []
				if avg < backgroundValue:
					backgroundValue = avg
					if self.noise == "RMS":
						noise = dev
					elif self.noise == "MM":
						minNoise = 10000000000000000000000
						maxNoise = 0
						for k in mix:
							if k > maxNoise:
								maxNoise = k
							if k < minNoise:
								minNoise = k
						noise = maxNoise - minNoise
					else:
						tkMessageBox.showinfo("Noise Error", "No valid noise method selected")
						return
			x_points = []
			y_points = []
			# Retrieve the x-coords and y-coords from the data structure for fitting
			for j in data[begin:end]:
				x_points.append(j[0])
				y_points.append(j[1])
			# Fit a cubic spline through the datapoints
			try:
				###########################################################
				# Residual chunk that was used for a guassian fit attempt #
				###########################################################
				"""p0 = [numpy.max(y_points), x_points[numpy.argmax(y_points)],0.1]
				coeff, var_matrix = curve_fit(self.gaussFunction, x_points, y_points, p0)
				newY = self.gaussFunction(newX, *coeff)
				for index, j in enumerate(newY):"""
				####################################################################
				# We multiply the number of bins with the actual window (to not    #
				# have major changes in returned maxima with different windows)    #
				####################################################################
				newX = numpy.linspace(x_points[0], x_points[-1], 2500*(x_points[-1]-x_points[0]))
				f = interp1d(x_points, y_points,  kind='cubic')
				ySPLINE = f(newX)
				###############################################
				# Plot Chunk (internal testing purposes ONLY) #
				###############################################
				"""fig =  plt.figure()
				ax = fig.add_subplot(111)
				plt.plot(x_points, y_points, 'b*')
				#plt.plot(newX,newY, 'b--')
				plt.plot(newX,ySPLINE,'r--')
				#plt.legend(['Raw Data','Guassian (All Points)','Cubic Spline'], loc='best')
				plt.legend(['Raw Data','Cubic Spline'], loc='best')
				plt.show()"""
				for index, j in enumerate(ySPLINE):
					if j > maximum[1]:
						maximum = (newX[index], j)
			# Use the highest intensity point, in case the gaussian fit failed
			except RuntimeError:
				if self.log is True:
					with open('MassyTools.log', 'a') as fw:
						fw.write("Guassian Curve Fit failed for calibrant: "+str(i)+", reverting to non fitted local maximum\n")
				for j in data[begin:end]:
					if j[1] > maximum[1]:
						maximum = (j[0], j[1])
			# Ensure that only peaks of S/N above the specified (CALIB_S_N_CUTOFF) are used for calibration
			if maximum[1] > backgroundValue + CALIB_S_N_CUTOFF * noise:
				maxima.append(maximum)
			else:
				if self.log is True:
					with open('MassyTools.log', 'a') as fw:
						fw.write(str(datetime.now())+"\t"+str(maximum)+" was not above cutoff: "+str(backgroundValue + CALIB_S_N_CUTOFF * noise)+"\n")
		return maxima

	def getObservedCalibrants(self, maxima, potentialCalibrants):
		""" This function compares the list of local maxima with the
		expected calibrants. The function will perceive the observed
		local maxima that is closest to a desired calibrant as being the
		m/z where the calibrant was observed in the spectrum. The
		function then appends the theoretical m/z value of a calibrants
		that were actually observed to a list (actualCalibrants) which
		is returned at the end of the function.

		INPUT 1: A list of floats containg the observed local maxima (of
		the spline fit within each inclusion range, assuming that they
		were above user specified S/N cut off).
		INPUT 2: A list of floats containing the theoretical m/z of all
		calibrants.
		OUTPUT: A list of floats containing the theoretical m/z of the
		calibrants which were near an oberved local maxima.
		"""
		actualCalibrants = []
		for i in maxima:
			diff = 4.0
			closest = 0
			for j in potentialCalibrants:
				if abs(float(j)-float(i[0])) < diff:
					diff = abs(float(j)-float(i[0]))
					closest = float(j)
			actualCalibrants.append(closest)
		return actualCalibrants

	def readInclusionRange(self):
		""" This function reads the exclusion file in a line by line
		method. The new line character ('\n') is stripped from each line
		prior to splitting the line on white space characters. The first
		2 elements read per line are then appended to a list (excluded).
		The excluded list is read and and is transformed to a new list
		(included) which contains the start and end point of a region
		to be read (for the calibration) per list entry (tuple).

		INPUT; None
		OUTPUT: A list of (m/z,m/z) tuples containg the regions to be
		screened for the calibrants.
		"""
		excluded = []
		included = []
		# Read the excluded regions
		with open(self.exclusionFile, 'r') as fr:
			for line in fr:
				line = line.rstrip('\n')
				values = line.split()
				values = filter(None,  values)
				excluded.append((values[0], values[1]))
		# Transform the excluded regions into included regions
		for index, i in enumerate(excluded):
			if index+1 < len(excluded):
				included.append((float(excluded[index][1]), float(excluded[index+1][0])))
		return included

	def readCalibrants(self):
		""" This file reads the calibrationFile, parses all lines that
		do not contain 'm/z' on the second index after a split on tabs.
		The second element of each line (the m/z) is appended to the list
		potentialCalibrants which is returned at the end of the function.

		INPUT: None
		OUTPUT: A list of floats (the m/z value of the calibrants)
		"""
		potentialCalibrants = []
		with open(self.calibrationFile, 'r') as fr:
			for line in fr:
				if line[0] == '#':
					pass
				else:
					line = line.rstrip('\n')
					line = line.split('\t')
					line = filter(None, line)
					if len(line) >= 2:
						potentialCalibrants.append(float(line[1]))
		return potentialCalibrants

	def transformFile(self, f):
		""" This function gets a single function as input, reads the
		raw data file and transforms the read m/z values in the raw data
		file with the given function. The transformed m/z values are
		stored in a calibrated_<inputfile>.EXTENSION file (if program is running
		in batchProcess mode) or asks the user for a filepath to save
		the calibrated file (if program is running in single spectrum mode).

		INPUT: a numpy polynomial (poly1d) function
		OUTPUT: a calibrated data file
		"""
		with open(self.inputFile, 'r') as fr:
			if self.batch is False:
				output = tkFileDialog.asksaveasfilename()
				if output:
					pass
				else:
					tkMessageBox.showinfo("File Error", "No output file selected")
					return
			else:
				parts = os.path.split(str(self.inputFile))
				output = "calibrated_"+str(parts[-1])
				# Maybe replace batchFolder without outputFolder?
				output = os.path.join(self.batchFolder, output)
			if self.log is True:
				with open('MassyTools.log', 'a') as fw:
					fw.write(str(datetime.now())+"\tWriting output file: "+output+"\n")
			# Prepare variables required for transformation
			outputBatch = []
			mzList = []
			intList = []
			for line in fr:
				line = line.rstrip('\n')
				values = line.split()
				mzList.append(float(values[0]))
				intList.append(int(values[1]))
			# Transform python list into numpy array
			mzArray = numpy.array(mzList)
			newArray = f(mzArray)
			# Prepare the output as a list
			for index, i in enumerate(newArray):
				outputBatch.append(str(i)+" "+str(intList[index])+"\n")
			# Join the output list elements
			joinedOutput = ''.join(outputBatch)
			with open(output, 'w') as fw:
				fw.write(joinedOutput)
			if self.log is True:
				with open('MassyTools.log', 'a') as fw:
					fw.write(str(datetime.now())+"\tFinished writing output file: "+output+"\n")

	def singularQualityControl(self):
		""" This function creates a list of Analyte instances based on
		a file with chemicals that are meant to be used for the QC. The
		function extracts the data related to the mentioned chemicals and
		calculates the QC value (based on Nicolardi S. et al, 2010).
		The method to display these values is currently not 'good' yet.

		INPUT: None
		OUTPUT: None
		"""
		if self.qualityFile == "":
			tkMessageBox.showinfo("File Error", "No QC file selected")
			return
		if self.inputFile == "":
			tkMessageBox.showinfo("File Error", "No data file selected")
			return
		peaks = self.calcCompositionMasses(self.qualityFile)
		peaks = self.extractData(self.inputFile, peaks)
		peaks = self.qualityControl(peaks)
		# TODO: How should we display this?

	def qualityControl(self, compositions):
		""" This function takes a list of Analyte instances and iterates
		through them. The function then calculates the fraction of the
		total intensity that should be present in each isotope and
		compares that to the fraction of the observed intensity that is
		present in that isotope. The function than performs a QC check
		on these values based on Nicolardi S. et al, 2010. The calculated
		QC value is added to the Analyte instance.

		INPUT: A list of Analyte instances
		OUTPUT: A list of Analyte instances
		"""
		for i in compositions:
			if self.batch == 0:
				print "Analyte: "+str(i.composition)
			total = 0
			for j in i.isotopes[1:]:
				total += j.maxIntensity
			if total == 0:
				if self.log is True:
					with open('MassyTools.log', 'a') as fw:
						fw.write(str(datetime.now())+"\tSkipping QC calculation for "+str(i.composition)+" due to the total area being 0\n")
				break
			for j in i.isotopes[1:]:
				if self.noiseQC is True:
					j.qc = float(((((j.maxIntensity - i.backgroundPoint)/total) - j.expArea)**2)/i.noise**2)
				else:
					j.qc = float((((j.maxIntensity - i.backgroundPoint)/total) - j.expArea)**2)
				# Temporary display?
				if self.batch == 0:
					print "Isotope: "+str(j.isotope)+"\tExpected: "+str("%.2f" % f)+"\tObserved: "+str("%.2f" % ((j.maxIntensity - i.backgroundPoint)/total))+"\tQC Score: "+str("%.2f" % j.qc)
		return compositions

	def extractCompositions(self):
		""" This function controls the data extraction that is performed
		in the GUI (visual) aspect of the program. The function first
		calls a function that will parse the composition file and create
		a list with Analyte instances. This list of Analyte instances is
		then given to the data extraction function which will parse the
		raw data file to extract the data belonging to the Analyte
		instances. The function finally hands the filled list of Analyte
		instances to a function that will write the results to a result
		file.

		INPUT: None
		OUTPUT: None
		"""
		if self.compositionFile == "":
			tkMessageBox.showinfo("File Error", "No composition file selected")
			return
		if self.inputFile == "":
			tkMessageBox.showinfo("File Error", "No data file selected")
			return
		self.initCompositionMasses(self.compositionFile)
		compositions = self.calcCompositionMasses(self.compositionFile)
		compositions = self.extractData(self.inputFile, compositions)
		self.writeResults(compositions)

	def initCompositionMasses(self, file):
		""" This function reads the composition file. Calculates the
		masses for the compositions read from the composition file.
		The function then calculates the mass and fraction of total
		ions that should be theoretically present in. The final output
		is a modified reference list containing each analyte's structure
		and window followed by a list of isotope m/z and isotopic
		fraction.

		INPUT: A string containing the path of the composition file
		OUTPUT: None
		"""
		lines = []
		compositions = []
		with open(file, 'r') as fr:
			for line in fr:
				line = line.rstrip()
				lines.append(line)
		# Chop composition into sub units and get exact mass & carbon count
		analyteFile = os.path.join(self.batchFolder, "analytes.ref")
		if os.path.exists(analyteFile) is True:
			print "USING EXISTING REFERENCE FILE"
			return
		print "PRE-PROCESSING REFERENCE FILE"
		print "THIS MAY TAKE A WHILE"
		# Get rid of a proton if a sodium or potassium was used as a mass modifier
		if 'sodium' in MASS_MODIFIERS:
			MASS_MODIFIERS.append('protonLoss')
		if 'potassium' in MASS_MODIFIERS:
			MASS_MODIFIERS.append('protonLoss')
		with open(analyteFile, 'w') as fw:
			for i in lines:
				isotopes = []
				i = i.split("\t")
				i = filter(None, i)
				if len(i) == 2:
					window = float(i[1])
				else:
					window = CALCULATION_WINDOW
				values = self.parseAnalyte(i[0])
				totals = self.getChanceNetwork(values)
				results = self.mergeChances(totals)
				results.sort(key=lambda x: x[0])
				fw.write(str(i[0])+"\t"+str(window))
				fTotal = 0
				for index, j in enumerate(results):
					fTotal += j[1]
					fw.write("\t"+str(j[0])+"\t"+str(j[1]))
					if fTotal >= MIN_TOTAL_CONTRIBUTION:
						fw.write("\n")
						break
		print "PRE-PROCESSING COMPLETE"

	def calcCompositionMasses(self, file):
		""" This function reads the composition file. Reads the
		masses and other relevant information from the composition file.
		The function calls the extractBackground function to get the
		information regarding each analyte's background and appends it
		to the list 'isotopes'. The function creates an instance of
		the Analyte class per composition and the isotopes list is attached
		to the Analyte class which itself is appended to a list which is
		returned at the end of the function.

		INPUT: A string containing the path of the composition file
		OUTPUT: A list filled with Analyte instances
		"""
		lines = []
		compositions = []
		data = self.readData(self.inputFile)
		#with open(file,'r') as fr:
		analyteFile = os.path.join(self.batchFolder, "analytes.ref")
		with open(analyteFile, 'r') as fr:
			for line in fr:
				line = line.rstrip()
				lines.append(line)
		# Chop composition into sub units and get exact mass & carbon count
		for i in lines:
			isotopes = []
			i = i.split("\t")
			i = filter(None, i)
			isoMasses = i[2::2]
			isoFractions = i[3::2]
			window = float(i[1])
			# Get background values
			backgroundPoint, backgroundArea, noise = self.extractBackground(data, float(i[2]), window)
			isotopes.append(Isotope(-1, 'background', backgroundArea, 0, backgroundArea/backgroundArea, 0, 0))
			# Include isotopes until the contribution of an isotope falls below 1%
			fTotal = 0  # Beta
			for index, j in enumerate(isoMasses):
				isotopes.append(Isotope(index, float(j), 0, float(isoFractions[index]), 0, 0, 0))
				fTotal += float(isoFractions[index])
				if fTotal >= MIN_TOTAL_CONTRIBUTION:
					break
			compositions.append(Analyte(i[0], float(i[2]), window, isotopes, backgroundPoint, backgroundArea, noise))
		return compositions

	###########################
	### DEPRECATED FUNCTION ###
	###########################
	def calcErrorAll(self, file, compositions):
		""" This function reads the calibrated datafile. Iterates over
		the list of Analyte instances, retrievers the peak center from
		the calibrated data and calculates the PPM error for all analytes.
		"""
		# Get the exact mass of highest isotope
		analyteFile = os.path.join(self.batchFolder, "analytes.ref")
		with open(analyteFile, 'r') as fr:
			analytes = []
			for line in fr:
				mass = 0
				area = 0
				isotopes = []
				line = line.split("\t")
				analyte = line[0]
				window = line[1]
				areas = line[3::2]
				masses = line[2::2]
				for index, j in enumerate(areas):
					if j > area:
						area = j
						mass = masses[index]
				analytes.append((analyte, mass, window, area))
		# Get the accurate mass of highest isotope
		data = self.readData(self.inputFile)
		inclusion = []
		exactMasses = []
		for i in analytes:
			inclusion.append((float(i[1])-float(i[2]), float(i[1])+float(i[2])))
			exactMasses.append(float(i[1]))
		maxima = self.getLocalMaxima(data, inclusion)
		# Create pairs and calculate the ppm error
		actualPeaks = self.getObservedCalibrants(maxima, exactMasses)
		errors = []
		for index, i in enumerate(maxima):
			ppm = ((i[0]-actualPeaks[index])/actualPeaks[index])*1000000
			errors.append((actualPeaks[index], i[0], ppm))
		outFile = os.path.split(str(self.inputFile))[-1]
		outFile = outFile.split(".")[0]
		outFile = outFile+".errorAll"
		with open(outFile, 'w') as fw:
			fw.write("Expected m/z\tObserved m\z\tPPM Error\n")
			for index, i in enumerate(errors):
				fw.write(str(i[0])+"\t"+str(i[1])+"\t"+str(i[2])+"\n")

	def extractData(self,  file,  compositions):
		""" This function reads the raw datafile. Iterates over the
		list of Analyte instances, retrieves the data for each Analyte
		instance from the raw data and stores it in the Analyte instance.
		The function also calls a function that will find the background
		area, background value and noise value by examining a user
		defined range of windows in front of the m/z belonging to the
		currently examined Analyte instance.

		INPUT 1: A string containg the path of the raw data file
		INPUT 2: A list of Analyte instances
		OUTPUT: A list of Analyte instances
		"""
		data = self.readData(self.inputFile)
		for i in compositions:
			# This is a 'heavy' calculation, only perform it if the user wanted it
			if self.ppmQC.get() == 1:
				# Get accurate mass of main isotope
				contribution = 0.0
				accurateMass = 0.0
				for j in i.isotopes[1:]:
					if j.expArea > contribution:
						contribution = j.expArea
						lowerEdge = j.mass - i.window
						upperEdge = j.mass + i.window
						begin = self.search_right(data, lowerEdge, len(data))
						end = self.search_left(data, upperEdge, len(data))
						if begin is None or end is None:
							pass
						else:
							x_points = []
							y_points = []
							for k in data[begin:end]:
								x_points.append(k[0])
								y_points.append(k[1])
							newX = numpy.linspace(x_points[0], x_points[-1], 1000)
							f = interp1d(x_points, y_points, kind='cubic')
							ySpline = f(newX)
							maximum = 0
							for index, k in enumerate(ySpline):
								if k > maximum:
									maximum = k
									accurateMass = newX[index]
							# Calculate ppm error and attach it to analyte
							i.ppm = ((accurateMass - j.mass) / j.mass) * 1000000
			else:
				i.ppm = "NA"
			# Start with second isotope to omit the 'background' isotope
			for j in i.isotopes[1:]:
				total = 0
				maxIntensity = 0
				currentMass = j.mass
				lowerEdge = currentMass - i.window
				upperEdge = currentMass + i.window
				begin = self.search_right(data, lowerEdge, len(data))
				end = self.search_left(data, upperEdge, len(data))
				# Check if the spectrum contained the target
				if begin is None or end is None:
					pass
				else:
					for k in data[begin:end]:
						# Approximate the area by multiplying intensity * m/z width
						total += k[1] * ((data[end][0] - data[begin][0]) / (end - begin))
						# Sum the intensities only
						# total += k[1]
						if k[1] > maxIntensity:
							maxIntensity = k[1]
					# I.noise is '0' if begin and end were None leading to a 0 division
					j.sn = (maxIntensity - i.backgroundPoint) / i.noise
					#with open('Values.txt','a') as fw:
					#	fw.write(str(i.composition)+"\t"+str(j.mass)+"\t"+str(maxIntensity)+"\t"+str(i.backgroundPoint)+"\t"+str(i.noise)+"\n")
				j.obsArea = total
				j.maxIntensity = maxIntensity
		return compositions

	def extractBackground(self, data, mass, window):
		""" This function will parse a region of the given data structure
		to identify the background and noise. This is done by examining
		a series of consecutive windows and taking the set with the lowest
		average as being a background region. This region is used to
		calculate the background area (intensity * m/z width), background
		and noise (both as intensity only). The function returns these
		values as a tuple.

		INPUT 1: A list of (m/z, intensity) tuples
		INPUT 2: A list of Analyte instances
		OUTPUT: A tuple of (Background, Background Area, Noise)
		"""
		backgroundPoint = 1000000000000000000000000000000000000000000000000000		# Ridiculous start value
		totals = []
		lowEdge = mass - window
		highEdge = mass + window
		for i in range(-OUTER_BCK_BORDER, OUTER_BCK_BORDER):
			windowAreas = []
			windowIntensities = []
			begin = self.search_right(data, lowEdge-i*C[0][2], len(data))
			end = self.search_left(data, highEdge-i*C[0][2], len(data))
			if begin is None or end is None:
				print "Specified m/z value of " + str(lowEdge) + " or " + str(highEdge) + " outside of spectra range"
				raw_input("Press enter to exit")
				sys.exit()
			for j in data[begin:end]:
				# Approximate the area by multiplying intensity * m/z width
				windowAreas.append(j[1] * ((data[end][0] - data[begin][0]) / (end - begin)))
				# Pure intensities are required to get the pure noise and background (non area)
				windowIntensities.append(j[1])
			totals.append((windowAreas, windowIntensities))
		# Find the set of 5 consecutive windows with lowest average intensity
		for i in range(0, (2*OUTER_BCK_BORDER)-4):
			mix = totals[i][1]+totals[i+1][1]+totals[i+2][1]+totals[i+3][1]+totals[i+4][1]
			avgBackground = numpy.average([sum(totals[i][0]), sum(totals[i+1][0]), sum(totals[i+2][0]), sum(totals[i+3][0]), sum(totals[i+4][0])])
			dev = numpy.std(mix)
			avg = numpy.average(mix)
			if avg < backgroundPoint:
				backgroundPoint = avg
				backgroundArea = avgBackground
				if self.noise == "RMS":
					noise = dev
				elif self.noise == "MM":
					minNoise = 10000000000000000000000
					maxNoise = 0
					for k in mix:
						if k > maxNoise:
							maxNoise = k
						if k < minNoise:
							minNoise = k
					noise = maxNoise - minNoise
				else:
					tkMessageBox.showinfo("Noise Error", "No valid noise method selected")
					return
		# Custom stuff to test a window of 1
		"""backgroundArea = numpy.average(sum(totals[i][0]))
		noise = numpy.std(totals[i][1])
		backgroundPoint = numpy.average(totals[i][1])"""
		return (backgroundPoint, backgroundArea, noise)

	def writeResults(self, results):
		""" This function takes a list of Analyte instances, iterates
		through the list and writes a line of results to an outputfile.
		The output file's default name is the input's file name.raw.
		The .raw files are what will be used in creating the summary
		output file later on during program execution.

		INPUT: A list of Analyte instances
		OUTPUT: A result file -> file_name.raw
		"""
		maxIsotope = 0
		if self.batch == 0:
			outFile = tkFileDialog.asksaveasfilename()
			if outFile:
				pass
			else:
				tkMessageBox.showinfo("File Error", "No output file selected")
				return
		else:
			outFile = os.path.split(str(self.inputFile))[-1]
			outFile = outFile.split(".")[0]
			outFile = outFile+".raw"
			# Maybe change batchFolder into outputFolder?
			outFile = os.path.join(self.batchFolder, outFile)
		for i in results:
			if len(i.isotopes) > maxIsotope:
				maxIsotope = len(i.isotopes)
		with open(outFile, 'w') as fw:
			name = str(self.inputFile).split("/")[-1]
			fw.write(name+"\n")
			fw.write("Composition\tMass\tWindow\tPercentage of Distribution\tTotal\tMaximum SN\tNoise\tPPM Error of Main Isotope\t")
			for i in range(-1, maxIsotope):
				fw.write("Iso_"+str(i)+"\tS/N Ratio\tQC Value\t")
			fw.write("\n")
			for i in results:
				maxSN = 0
				totalArea = 0.0
				for j in i.isotopes:
					totalArea += j.expArea
					if j.sn > maxSN:
						maxSN = j.sn
				fw.write(str(i.composition)+"\t"+str(i.mass)+"\t"+str(i.window)+"\t"+str(totalArea)+"\t"+str(sum(float(j.obsArea) for j in i.isotopes[1:]))+"\t"+str(maxSN)+"\t"+str(i.noise)+"\t"+str(i.ppm)+"\t")
				for j in i.isotopes:
					fw.write(str(j.obsArea)+"\t"+str(j.sn)+"\t"+str(j.qc)+"\t")
				fw.write("\n")

	def combineResults(self):
		""" This function first parses all the .raw result files and
		creates a list filled with Results instances from the read
		values. The function then iterates through the list of Results
		instances and writes the user selected values (output blocks)
		to the summary.txt file.

		INPUT: None
		OUTOUT: A file -> summary.txt"
		"""
		numIsotopes = 0
		counter = 0
		data = []

		# Construct the 'Mass' header
		header = "[M"
		if 'sodium' in CHARGE_CARRIER:
			header = header + "+Na"
		if 'potassium' in CHARGE_CARRIER:
			header = header + "+K"
		if 'proton' in CHARGE_CARRIER:
			header = header + "+H]+"
		if 'neg_electron' in CHARGE_CARRIER:
			header = header + "]+"
		if 'neg_proton' in CHARGE_CARRIER:
			header = header + "-H]-"

		# Read the raw files and construct the data structure
		# Maybe change batchFolder to outputFolder?
		rawFiles = os.path.join(self.batchFolder, "*.raw")
		for file in glob.glob(rawFiles):
			calibrated = 1
			with open(file, 'r') as fr:
				total = 0
				totalBck = 0
				values = []
				first_line = fr.readline()
				fr.readline()
				name = first_line.rstrip()
				name = os.path.split(str(name))[-1]
				if 'uncalibrated' in name:
					pass
				else:
					# Ensure that files that contained _ to begin with aren't broken
					name = name.split("calibrated_")[1]
					#name = name.split("calibrated_")[1:]
					#name = ''.join(name)
				name = name.split(".")[0]
				for line in fr:
					parts = line.split("\t")
					values.append(parts)
				# Custom addition for albert
				inputfile = name.split(".")[0]
				inputfile = "calibrated_"+inputfile + EXTENSION
				# Maybe change batchFolder to outputFolder?
				inputfile = os.path.join(self.batchFolder,inputfile)
				totalInt = self.getTotalArea(inputfile)
				analyteResults = []
				for i in values:
					isotopeResults = []
					total += float(i[4])
					# Sum all isotope - background values
					# Get all values for isotope 0 and up
					isotopes = i[11::3]
					sections = [i[x:x+3] for x in xrange(11, len(i), 3)]
					for j in sections:
						try:
							float(j[0])
							isotopeResults.append(isotopeResult(float(j[0]), float(j[1]), float(j[2])))
							if float(j[0]) > float(i[8]):
								totalBck += float(j[0]) - float(i[8])
						except ValueError:
							pass
					analyteResults.append(analyteResult(str(i[0]), float(i[1]), float(i[3]), float(i[8]), float(i[6]), str(i[7]), isotopeResults))
					# Get the value for the maximum number of isotopes to be listed in the output
					if len(isotopes) > numIsotopes:
						numIsotopes = len(isotopes)
			data.append(Results(name, calibrated, total, totalBck, totalInt, analyteResults))

		# Todo maybe rename the values in the below chunk for naming convention?
		rawFiles = os.path.join(self.batchFolder, "*.xy")
		for file in glob.glob(rawFiles):
			total = 0
			values = []
			calibrated = 0
			ppm = "NA"
			name = str(file)
			name = os.path.split(str(name))[-1]
			if 'uncalibrated' in name:
				name = name.split("uncalibrated_")[1]
				name = name.split(".")[0]
				data.append(Results(name, calibrated, total, total, total, values))

		################################################################
		# Sort the data list on the filename (alphabetical)			   #
		################################################################
		# The sorted list is used to write the actual data			   #
		################################################################
		# The unsorted list is used to write the first lines of each   #
		# Block (containing the metadata)							   #
		################################################################
		new = sorted(data, key=lambda Results: Results.name)

		# Write the data structure to the output file
		# Maybe change batchFolder with outputFolder?
		utc_datetime = datetime.utcnow()
		s = utc_datetime.strftime("%Y-%m-%d-%H%MZ")
		filename = s + "_" + OUTPUT_FILE
		summaryFile = os.path.join(self.batchFolder, filename)
		with open(os.path.join(self.batchFolder, summaryFile), 'w') as fw:
			# Write the parameters used during the processing
			fw.write("Processing Parameters\n")
			if self.calibrationFile != "":
				fw.write("Calibration window (peak detection)\t"+str(CALIBRATION_WINDOW)+"\n")
				fw.write("Minimum signal-to-noise ratio for calibrants\t"+str(CALIB_S_N_CUTOFF)+"\n")
				fw.write("Minimum number of calibrants in lower region of spectrum\t"+str(NUM_LOW_RANGE)+"\n")
				fw.write("Minimum number of calibrants in middle region of spectrum\t"+str(NUM_MID_RANGE)+"\n")
				fw.write("Minimum number of calibrants in upper region of spectrum\t"+str(NUM_HIGH_RANGE)+"\n")
				fw.write("Minimum number of calibrants throughout entire spectrum\t"+str(NUM_TOTAL)+"\n")
			if self.compositionFile != "":
				fw.write("Charge carrier used for all analytes\t")
				for i in CHARGE_CARRIER:
					fw.write(str(i)+"\t")
				fw.write("Mass modifiers applied to all analytes\t")
				for i in MASS_MODIFIERS:
					fw.write(str(i)+"\t")
				fw.write("\n")
				fw.write("Extraction width\t"+str(CALCULATION_WINDOW)+"\n")
				fw.write("Background detection window\t"+str(OUTER_BCK_BORDER)+"\n")
				fw.write("Minimum signal-to-noise ratio used in percentage based QC\t"+str(S_N_CUTOFF)+"\n")
				fw.write("Minimum fraction of total isotopic distribution used for extraction\t"+str(MIN_TOTAL_CONTRIBUTION)+"\n")
			fw.write("\n")

			########################################################
			# Absolute Intensity block (non background subtracted) #
			########################################################
			if self.absoluteIntensity.get() == 1:
				# Compositions
				for i in data:
					fw.write("Analyte Area\tCalibrated")
					for j in i.analytes:
						fw.write("\t"+str(j.composition))
					fw.write("\n")
					break
				# Calculated Mass
				for i in data:
					fw.write("\t"+str(header))
					for j in i.analytes:
						fw.write("\t"+str(j.mass))
					fw.write("\n")
					break
				# Absolute Intensity values
				for i in new:
					fw.write(str(i.name)+"\t"+str(i.calibrated))
					for j in i.analytes:
						total = 0
						for k in j.isotopes:
							total += k.area
						fw.write("\t"+str(total))
					fw.write("\n")
				fw.write("\n")

			####################################################
			# Absolute Intensity block (background subtracted) #
			####################################################
			if self.absoluteIntensityBackground.get() == 1:
				# Compositions
				for i in data:
					fw.write("Analyte Area - Background Area\tCalibrated")
					for j in i.analytes:
						fw.write("\t"+str(j.composition))
					fw.write("\n")
					break
				# Calculated Mass
				for i in data:
					fw.write("\t"+str(header))
					for j in i.analytes:
						fw.write("\t"+str(j.mass))
					fw.write("\n")
					break
				# Absolute Intensity values with background subtraction
				for i in new:
					fw.write(str(i.name)+"\t"+str(i.calibrated))
					for j in i.analytes:
						total = 0
						for k in j.isotopes:
							if k.area > j.background:
								total += k.area - j.background
						fw.write("\t"+str(total))
					fw.write("\n")
				fw.write("\n")

			############################
			# Analyte Background block #
			############################
			if self.analyteBackground.get() == 1:
				# Compositions
				for i in data:
					fw.write("Analyte Background Area\tCalibrated")
					for j in i.analytes:
						fw.write("\t"+str(j.composition))
					fw.write("\n")
					break
				# Calculated Mass
				for i in data:
					fw.write("\t"+str(header))
					for j in i.analytes:
						fw.write("\t"+str(j.mass))
					fw.write("\n")
					break
				# Absolute Intensity values
				for i in new:
					fw.write(str(i.name)+"\t"+str(i.calibrated))
					for j in i.analytes:
						fw.write("\t"+str(j.background))
					fw.write("\n")
				fw.write("\n")

			#######################
			# Analyte Noise block #
			#######################
			if self.analNoise.get() == 1:
				# Compositions
				for i in data:
					fw.write("Analyte Noise\tCalibrated")
					for j in i.analytes:
						fw.write("\t"+str(j.composition))
					fw.write("\tTotal Intensity\n")
					break
				# Calculated Mass
				for i in data:
					fw.write("\t"+str(header))
					for j in i.analytes:
						fw.write("\t"+str(j.mass))
					fw.write("\n")
					break
				# Actual Noise values
				for i in new:
					fw.write(str(i.name)+"\t"+str(i.calibrated))
					for j in i.analytes:
						fw.write("\t"+str(j.noise))
					fw.write("\n")
				fw.write("\n")

			############################
			# Relative Intensity block #
			############################
			if self.relativeIntensity.get() == 1:
				# Compositions
				for i in data:
					fw.write("Relative Area\tCalibrated")
					for j in i.analytes:
						fw.write("\t"+str(j.composition))
					fw.write("\tTotal Intensity\n")
					break
				# Calculated Mass
				for i in data:
					fw.write("\t"+str(header))
					for j in i.analytes:
						fw.write("\t"+str(j.mass))
					fw.write("\n")
					break
				# Actual Relative Intensity values
				for i in new:
					fw.write(str(i.name)+"\t"+str(i.calibrated))
					for j in i.analytes:
						total = 0
						for k in j.isotopes:
							total += k.area
						fw.write("\t"+str(total / i.total))
					if i.calibrated == 1:
						fw.write("\t"+str(i.total)+"\n")
					else:
						fw.write("\n")
				fw.write("\n")

			####################################################
			# Relative Intensity block (background subtracted) #
			####################################################
			if self.relativeIntensityBackground.get() == 1:
				# Compositions
				for i in data:
					fw.write("Relative Area - Background Area\tCalibrated")
					for j in i.analytes:
						fw.write("\t"+str(j.composition))
					fw.write("\tTotal Intensity\n")
					break
				# Calculated Mass
				for i in data:
					fw.write("\t"+str(header))
					for j in i.analytes:
						fw.write("\t"+str(j.mass))
					fw.write("\n")
					break
				# Actual Relative Intensity values
				for i in new:
					fw.write(str(i.name)+"\t"+str(i.calibrated))
					for j in i.analytes:
						total = 0
						for k in j.isotopes:
							if k.area > j.background:
								total += k.area - j.background
						fw.write("\t"+str(total / i.totalBck))
					if i.calibrated == 1:
						fw.write("\t"+str(i.totalBck)+"\n")
					else:
						fw.write("\n")
				fw.write("\n")

			#################################################################################
			# Corrected (for distribution) Relative Intensity block (background subtracted) #
			#################################################################################
			if self.correctedRelativeIntensityBackground.get() == 1:
				# Compositions
				for i in data:
					fw.write("Corrected Relative Area - Background Area\tCalibrated")
					for j in i.analytes:
						fw.write("\t"+str(j.composition))
					fw.write("\tTotal Intensity\n")
					break
				# Calculated Mass
				for i in data:
					fw.write("\t"+str(header))
					for j in i.analytes:
						fw.write("\t"+str(j.mass))
					fw.write("\n")
					break
				# Percentage of distribution
				for i in data:
					fw.write("\tFraction of Distribution")
					for j in i.analytes:
						fw.write("\t"+str(j.distribution))
					fw.write("\n")
					break
				# Actual corrected relative values
				# Get new total background subtracted intensity
				for i in new:
					totalBck = 0
					for j in i.analytes:
						totalAnal = 0
						for k in j.isotopes:
							if k.area > j.background:
								totalAnal += k.area - j.background
						corrTotal = totalAnal / j.distribution
						totalBck += corrTotal
					# Write the corrected values
					fw.write(str(i.name)+"\t"+str(i.calibrated))
					for j in i.analytes:
						totalAnal = 0
						for k in j.isotopes:
							if k.area > j.background:
								totalAnal += k.area - j.background
						corrTotal = totalAnal / j.distribution
						corrRelTotal = corrTotal / totalBck
						fw.write("\t"+str(corrRelTotal))
					try:
						fw.write("\t"+str(totalBck)+"\n")
					except UnboundLocalError:
						fw.write("\n")
				fw.write("\n")

			######################################
			# Percentage of spectrum in analytes #
			######################################
			if self.percentageSpectrum.get() == 1:
				# Compositions
				fw.write("Fraction of spectrum in analytes\tCalibrated\tFraction\n")
				# Actual fractions
				for i in new:
					if i.calibrated == 1:
						fw.write(str(i.name)+"\t"+str(i.calibrated)+"\t"+str(float(i.total)/float(i.totalInt))+"\n")
					else:
						fw.write(str(i.name)+"\t"+str(i.calibrated)+"\n")
				fw.write("\n")

			###############################################
			# Fraction of analytes above S_N_CUTOFF block #
			###############################################
			if self.percentageAnalytes.get() == 1:
				# Compositions
				fw.write("Fraction of Analyte above S/N cut-off ("+str(S_N_CUTOFF)+")\tCalibrated\tPercentage\n")
				# Get the fraction
				for i in new:
					number = 0
					for j in i.analytes:
						SN = 0
						for k in j.isotopes:
							if k.SN > SN:
								SN = k.SN
						if SN > S_N_CUTOFF:
							number += 1
					try:
						fraction = float(number) / float(len(i.analytes))
					except ZeroDivisionError:
						fraction = 0
					fw.write(str(i.name)+"\t"+str(i.calibrated)+"\t"+str(fraction)+"\n")
				fw.write("\n")

			############################################################################
			# Percentage of signals above S_N_CUTOFF block (non background subtracted) #
			############################################################################
			if self.percentage.get() == 1:
				# Compositions
				fw.write("Fraction of Analyte Area above S/N cut-off ("+str(S_N_CUTOFF)+")\tCalibrated\tPercentage\n")
				# Absolute Intensity values
				for i in new:
					if i.total == 0:
						percentage = 0.00
					else:
						intensity = 0
						for j in i.analytes:
							# Check if maximum S/N is above the cut-off
							SN = 0
							for k in j.isotopes:
								if k.SN > SN:
									SN = k.SN
							# Get the intensity if it is above the cut-off
							if SN > S_N_CUTOFF:
								for k in j.isotopes:
									intensity += k.area
						percentage = float(intensity) / float(i.total)
					fw.write(str(i.name)+"\t"+str(i.calibrated)+"\t"+str(percentage)+"\n")
				fw.write("\n")

			########################################################################
			# Percentage of signals above S_N_CUTOFF block (background subtracted) #
			########################################################################
			if self.percentageBackground.get() == 1:
				# Compositions
				fw.write("Fraction of Analyte Area - Background Area above S/N cut-off ("+str(S_N_CUTOFF)+")\tCalibrated\tPercentage\n")
				# Absolute Intensity values
				for i in new:
					if i.totalBck == 0:
						percentage = 0.00
					else:
						intensity = 0
						for j in i.analytes:
							# Check if maximum S/N is above the cut-off
							SN = 0
							for k in j.isotopes:
								if k.SN > SN:
									SN = k.SN
							# Get the intensity if it is above the cut-off
							if SN > S_N_CUTOFF:
								for k in j.isotopes:
									intensity += k.area - j.background
						percentage = float(intensity) / float(i.totalBck)
					fw.write(str(i.name)+"\t"+str(i.calibrated)+"\t"+str(percentage)+"\n")
				fw.write("\n")

			################################
			# Maximum Signal to nose block #
			################################
			if self.maxSignalNoise.get() == 1:
				# Compositions
				for i in data:
					fw.write("Maximum Signal-to-Noise\tCalibrated")
					for j in i.analytes:
						fw.write("\t"+str(j.composition))
					fw.write("\n")
					break
				# Calculated Mass
				for i in data:
					fw.write("\t"+str(header))
					for j in i.analytes:
						fw.write("\t"+str(j.mass))
					fw.write("\n")
					break
				# Actual S/N values
				for i in new:
					fw.write(str(i.name)+"\t"+str(i.calibrated))
					for j in i.analytes:
						SN = 0
						for k in j.isotopes:
							if k.SN > SN:
								SN = k.SN
						fw.write("\t"+str(SN))
					fw.write("\n")
				fw.write("\n")

			#######################
			# Quality Score block #
			#######################
			if self.qcScore.get() == 1:
				# Compositions
				for i in data:
					fw.write("Quality Score\tCalibrated\t")
					for j in i.analytes:
						fw.write(str(j.composition)+"\t")
					fw.write("\n")
					break
				# Calculated Mass
				for i in data:
					fw.write("\t"+str(header))
					for j in i.analytes:
						fw.write("\t"+str(j.mass))
					fw.write("\n")
					break
				# Summed QC (per Analyte) values
				for i in new:
					fw.write(str(i.name)+"\t"+str(i.calibrated))
					for j in i.analytes:
						qc = 0
						for k in j.isotopes:
							qc += k.QC
						fw.write("\t"+str(qc))
					fw.write("\n")
				fw.write("\n")

			###################
			# PPM Error block #
			###################
			if self.ppmQC.get() == 1:
				# Compositions
				for i in data:
					fw.write("PPM Error of main isotope\tCalibrated\t")
					for j in i.analytes:
						fw.write(str(j.composition)+"\t")
					fw.write("\n")
					break
				# Calculated Mass
				for i in data:
					fw.write("\t"+str(header))
					for j in i.analytes:
						fw.write("\t"+str(j.mass))
					fw.write("\n")
					break
				# Actual PPM Error
				for i in new:
					fw.write(str(i.name)+"\t"+str(i.calibrated))
					for j in i.analytes:
						fw.write("\t"+str(j.ppm))
					fw.write("\n")
				fw.write("\n")

			##################################
			# Isotopic Signal to noise block #
			##################################
			if self.isoSignalNoise.get() == 1:
				# TODO: This outputs 1 more isotope than I expect
				for i in range(0, numIsotopes):
					# Compositions
					for j in data:
						fw.write("SN Isotope "+str(int(i)+1)+"\tCalibrated")
						for k in j.analytes:
							fw.write("\t"+str(k.composition))
						fw.write("\n")
						break
					# Calculated mass
					for j in data:
						fw.write("\t"+str(header))
						for k in j.analytes:
							fw.write("\t"+str(k.mass))
						fw.write("\n")
						break
					# Actual Isotopic S/N value
					for j in new:
						fw.write(str(j.name)+"\t"+str(j.calibrated))
						for k in j.analytes:
							try:
								fw.write("\t"+str(k.isotopes[i].SN))
							except IndexError:
								fw.write("\t")
						fw.write("\n")
					fw.write("\n")

			#############################################################
			# Isotopic absolute intensity block (background subtracted) #
			#############################################################
			if self.isoAbsoluteIntensity.get() == 1:
				# TODO: This outputs 1 more isotope than I expect
				for i in range(0, numIsotopes):
					# Compositions
					for j in data:
						fw.write("Area Isotope "+str(int(i)+1)+" - Background Area\tCalibrated")
						for k in j.analytes:
							fw.write("\t"+str(k.composition))
						fw.write("\n")
						break
					# Calculated mass
					for j in data:
						fw.write("\t"+str(header))
						for k in j.analytes:
							fw.write("\t"+str(k.mass))
						fw.write("\n")
						break
					# Actual Isotopic S/N value
					for j in new:
						fw.write(str(j.name)+"\t"+str(j.calibrated))
						for k in j.analytes:
							try:
								if k.isotopes[1].area > k.background:
									fw.write("\t"+str(k.isotopes[i].area - k.background))
								else:
									fw.write("\t"+str(0))
							except IndexError:
								fw.write("\t")
						fw.write("\n")
					fw.write("\n")

	def search_left(self, array, target, high):
		""" This function takes a sorted array and searches for the
		index in that array where all elements beyond the index are
		smaller than the target and that all elements before the index
		are greater or equal to  the target. The function then returns
		the index.

		The return value a is such that all elements in array[:a] have
		element < target, and all e in array[a:] have element >= target.

		INPUT 1: A list of (m/z, intensity) tuples, sorted on m/z
		INPUT 2: A float containing the search target
		INPUT 3: An integer listing the farthest in the array that this
		function has to search (essential for arrays that contain 0's
		beyond the final datapoint, ie Numpy arrays).
		OUTPUT: An integer listing the array index
		"""
		if target >= array[0][0] and target <= array[high-1][0]:
			a = 0
			b = high-1
			while a < b:
				mid = (a+b)//2
				if array[mid][0] < target:
					a = mid + 1
				else:
					b = mid
			return a

	def search_right(self, array, target, high):
		""" This function takes a sorted array and searches for the
		index in that array where all elements beyond the index are
		greater or equal to the target and that all elements before the
		index are smaller than the target. The function then returns the
		index.

		The return value a is such that all elements in array[:a] have
		element <= target, and all e in array[a:] have element > target.

		INPUT 1: A list of (m/z, intensity) tuples, sorted on m/z
		INPUT 2: A float containing the search target
		INPUT 3: An integer listing the farthest in the array that this
		function has to search (essential for arrays that contain 0's
		beyond the final datapoint, ie Numpy arrays).
		OUTPUT: An integer listing the array index
		"""

		if target >= array[0][0] and target <= array[high-1][0]:
			a = 0
			b = high-1
			while a < b:
				mid = (a+b)//2
				if array[mid][0] > target:
					b = mid
				else:
					a = mid+1
			return a

	def readData(self, file):
		""" This function opens the specified file and parses it line
		by line. The new line ('\n') character is stripped from each line
		prior to the line being split (on any whitespace character).
		The first part of a line is appended to a list (x_array), the
		second part of a line is appended to a list (y_array). The
		function returns a list of tuples ( (x1,y1), (x2,y2) ) by using
		the zip functionality.

		INPUT: A string containing the filepath
		OUTPUT: A list of (m/z,int) tuples
		"""
		x_array = []
		y_array = []
		with open(file, 'r') as fr:
			for line in fr:
				if line[0] == '#':
					pass
				else:
					line = line.rstrip('\n')
					values = line.split()
					values = filter(None, values)
					#if float(values[1]) < 0.0:
						#print "ERROR: Negative intensity value: "+str(values[1])+" encountered in file: "+str(file)+"\n"
						#raw_input("Press enter to exit")
						#sys.exit()
					x_array.append(float(values[0]))
					y_array.append(float(values[1]))
		if min(y_array) < 0.0:
			if self.log is True:
				with open('MassyTools.log', 'a') as fw:
					fw.write(str(file)+" contained negative intensities, entire spectrum uplifted with "+str(min(y_array))+" intensity\n")
			offset = abs(math.ceil(min(y_array)))
			newList = [x + offset for x in y_array]
			y_array = newList
		return zip(x_array, y_array)

	def plotChange(self, data, f):
		""" This function takes an array of data. The function also
		takes the given function (f) and determines new x-coordinates
		by transforming the given x-coordinates with the given function.
		The function then prepares for plotting both data sets by
		clearing the main screen and creating a line (per dataset) on a
		new subplot.  which is finally shown on the screen.

		INPUT 1: A list of (m/z, intensity) tuples
		INPUT 2: A calibration function
		OUTPUT: None
		"""
		x_array = []
		x_new = []
		y_array = []
		for i in data:
			x_array.append(i[0])
			y_array.append(i[1])
		x_new = abs(f(x_array))
		self.fig.clear()
		self.axes = self.fig.add_subplot(111)
		self.line, = self.axes.plot(x_array, y_array)
		self.line, = self.axes.plot(x_new, y_array)
		self.canvas.draw()

	def plotData(self, data):
		""" This function takes an array of data. The function then
		prepares for plotting the data by clearing the main screen and
		creating a line on a new subplot which is finally shown on the
		screen.

		INPUT: A list of (m/z, intensity) tuples
		OUTPUT: None
		"""
		x_array = []
		y_array = []
		for i in data:
			x_array.append(i[0])
			y_array.append(i[1])
		self.fig.clear()
		self.axes = self.fig.add_subplot(111)
		self.line, = self.axes.plot(x_array, y_array)
		self.canvas.draw()

	#####################
	# CONSTRUCTION AREA #
	#####################
	""" This section contains functions, prototypes and ideas that I
	have had but that are currently not being used or not mature enough
	to be used in the stable version of this program.
	"""

	def openFiles(self, number):
		""" This function assigns the input string to the variable that
		is indicated by the input integer.

		INPUT 1: A string containing a filepath
		INPUT 2: A integer indicating the desired variable
		OUTPUT: None
		"""
		name = tkFileDialog.askopenfilename()
		ops = {
			1: 'deglycoData',
			2: 'peptideFile',
			3: 'mzML'
		}
		setattr(self, ops[number], name)

	def getTotalArea(self, file):
		""" This function reads a spectrum by calling the readData
		function. The function then attempts to calculate the total area
		for a spectrum by adding the intensity (element i) * m/z
		difference (between element i+1 and i). The function will use
		element -1 and element -2 once element i+1 does not exist (due
		to length of the array).

		INPUT: None
		OUTPUT: A float containing the total area for a spectrum.
		"""
		intensity = 0
		data = self.readData(file)
		for i in range(0, len(data)):
			try:
				intensity += float(data[i][1]) * (float(data[i+1][0]) - float(data[i][0]))
			except IndexError:
				intensity += float(data[i][1]) * (float(data[-1][0]) - float(data[-2][0]))
		return intensity
	#####################
	# CONSTRUCTION AREA #
	#####################

# Call the main app
root = Tk()
app = App(root)
root.mainloop()
