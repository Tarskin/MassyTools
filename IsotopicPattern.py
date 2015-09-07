#! /usr/bin/env python
import itertools
import math
import matplotlib.pyplot as plt

# The analyte that we will calculate the pattern for
Analyte = ['H5N4E1free1sodium1neg_electron1']


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
					'sulfurs':0}}
UNITS = BLOCKS.keys()

# The maximum distance between distinct isotopic masses to be 'pooled'
EPSILON = 0.5

# Mass Differences
C = [('13C',0.0107,1.00335)]
H = [('2H',0.00012,1.00628)]
N = [('15N',0.00364,0.99703)]
O18 = [('18O',0.00205,2.00425)]
O17 = [('17O',0.00038,1.00422)]
S33 = [('33S',0.0076,0.99939)]
S34 = [('34S',0.0429,1.9958)]
S36 = [('36S',0.0002,3.99501)]

# Calculate the fraction of elements in isotope X based on a binom dist.
def calcDistribution(element, number):
	fractions = []
	for count,i in enumerate(element):
		fTotal = 0
		for j in range(0,10):	
			nCk = math.factorial(number) / (math.factorial(j) * math.factorial(number - j))
			f = nCk * i[1]**j * (1 - i[1])**(number-j)
			fTotal += f
			fractions.append((i[2]*j,f))
			if fTotal > 0.99:
				break
	return fractions
	
# Call the function
def parseAnalyte(Analyte):
	results = []		
	for i in Analyte:
		mass = 0
		numCarbons = 0
		numHydrogens = 0
		numNitrogens = 0
		numOxygens = 0
		numSulfurs = 0
		totalElements = 0
		units = ["".join(x) for _,x in itertools.groupby(i,key=str.isdigit)]
		for index,j in enumerate(units):
			for k in UNITS:
					if j == k:
						mass += float(BLOCKS[k]['mass']) * float(units[index+1])
						numCarbons += int(BLOCKS[k]['carbons']) * int(units[index+1])
						numHydrogens += int(BLOCKS[k]['hydrogens']) * int(units[index+1])
						numNitrogens += int(BLOCKS[k]['nitrogens']) * int(units[index+1])
						numOxygens += int(BLOCKS[k]['oxygens']) * int(units[index+1])
						numSulfurs += int(BLOCKS[k]['sulfurs']) * int(units[index+1])
		# Calculate the distribution for the given value
		carbons = calcDistribution(C,numCarbons)
		hydrogens = calcDistribution(H,numHydrogens)
		nitrogens = calcDistribution(N,numNitrogens)
		oxygens17 = calcDistribution(O17,numOxygens)
		oxygens18 = calcDistribution(O18,numOxygens)
		sulfurs33 = calcDistribution(S33,numSulfurs)
		sulfurs34 = calcDistribution(S34,numSulfurs)
		sulfurs36 = calcDistribution(S36,numSulfurs)
	return ((mass,carbons,hydrogens,nitrogens,oxygens17,oxygens18,sulfurs33,sulfurs34,sulfurs36))
				
# Calculate the chance network
def getChanceNetwork((mass,carbons,hydrogens,nitrogens,oxygens17,oxygens18,sulfurs33,sulfurs34,sulfurs36)):
	totals = []
	for x in itertools.product(carbons,hydrogens,nitrogens,oxygens17,oxygens18,sulfurs33,sulfurs34,sulfurs36):
		i, j, k, l, m, n, o, p = x
		totals.append((mass+i[0]+j[0]+k[0]+l[0]+m[0]+n[0]+o[0]+p[0],
					   i[1]*j[1]*k[1]*l[1]*m[1]*n[1]*o[1]*p[1]))
	return totals

# Merge the peaks based on specified 'Epsilon'
def mergeChances(totals):
	results = []
	newdata = {d: True for d in totals}
	for k, v in totals:
		if not newdata[(k,v)]: continue
		newdata[(k,v)] = False
		# use each piece of data only once
		keys,values = [k*v],[v]
		for kk, vv in [d for d in totals if newdata[d]]:
			if abs(k-kk) < EPSILON:
				keys.append(kk*vv)
				values.append(vv)
				newdata[(kk,vv)] = False
		results.append((sum(keys)/sum(values),sum(values)))
	return results

# Display the data
def displayIsotopicPattern(results):
	minVal = 10000
	maxVal = 0
	for i in results:
		if i[0] < minVal:
			minVal = i[0]
		if i[0] > maxVal:
			maxVal = i[0]
		plt.plot((i[0],i[0]),(0,i[1]),c='black')
	plt.plot((minVal,maxVal),(0,0),c='black')
	plt.show()

# Main
def main():
	distributions = parseAnalyte(Analyte)
	totals = getChanceNetwork(distributions)
	results = mergeChances(totals)
	displayIsotopicPattern(results)
	
if __name__ == "__main__":
	main()
