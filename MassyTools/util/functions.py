from pathlib import Path

def get_peak_list(file_handle):
    peaks = []
    with Path(file_handle).open() as fr:
        for line in fr:
            line = line.rstrip().split()
            peaks.append({'name':str(line[0]), 'exact m/z':float(line[-1])})
    return peaks
