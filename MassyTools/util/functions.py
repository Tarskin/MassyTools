from pathlib import Path
import math

def get_peak_list(file_handle):
    peaks = []
    with Path(file_handle).open() as fr:
        for line in fr:
            line = line.rstrip().split()
            peaks.append({'name':str(line[0]), 'exact mass':float(line[-1])})
    return peaks

def calculate_elemental_isotopic_pattern(element, number):
    fractions = []
    for i in element:
        last_fraction = 0.
        j = 0
        while j <= number:
            nCk = math.factorial(number) / (math.factorial(j) * math.factorial(number - j))
            f = nCk * i[1]**j * (1 - i[1])**(number-j)
            fractions.append((i[2]*j, f))
            j += 1
            # use min_contribution from settings
            if f <= 0.0001 and f < last_fraction:
                break
            last_fraction = f
    return fractions
