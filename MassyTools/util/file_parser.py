from pathlib import Path

def open_xy_spectrum(master):
    data_buffer = []
    with Path(master.filename).open() as fr:
        for line in fr:
            line = line.rstrip().split()
            data_buffer.append((float(line[0]), float(line[-1])))
    master.data = data_buffer
