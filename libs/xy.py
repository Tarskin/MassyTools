# load libs
from datetime import datetime
import math
import numpy
import os

def parseXY(inputFile, log):
    """ Read a given xy file and return the values as a zip.
    """
    with open(inputFile, 'r') as fr:
        x_array = []
        y_array = []
        for line in fr:
            if line[0] == '#':
                pass
            else:
                line = line.rstrip('\n')
                values = line.split()
                values = filter(None, values)
                x_array.append(float(values[0]))
                y_array.append(int(float(values[1])))
        if min(y_array) < 0.0:
            if log is True:
                with open('MassyTools.log', 'a') as fw:
                    fw.write(str(file)+" contained negative intensities, entire spectrum uplifted with "+str(min(y_array))+" intensity\n")
            offset = abs(math.ceil(min(y_array)))
            newList = [x + offset for x in y_array]
            y_array = newList
        return zip(x_array, y_array)

def transformXY(inputFile, outFolder, batch, log, f):
    """ Read and calibrate a given xy file based on the function 'f'.
    """
    if batch is False:
        output = tkFileDialog.asksaveasfilename()
        if output:
            pass
        else:
            tkMessageBox.showinfo("File Error", "No output file selected")
            return
    else:
        parts = os.path.split(str(inputFile))
        output = "calibrated_"+str(parts[-1])
        output = os.path.join(outFolder, output)

    if log is True:
        with open('MassyTools.log', 'a') as fw:
            fw.write(str(datetime.now())+"\tWriting output file: "+output+"\n")

    outputBatch = []
    data = parseXY(inputFile, log)
    mzList, intList = zip(*data)
    mzArray = numpy.array(mzList)
    newArray = f(mzArray)
    for index, i in enumerate(newArray):
        outputBatch.append(str(i)+" "+str(intList[index])+"\n")
    joinedOutput = ''.join(outputBatch)
    with open(output, 'w') as fw:
        fw.write(joinedOutput)
    if log is True:
        with open('MassyTools.log', 'a') as fw:
            fw.write(str(datetime.now())+"\tFinished writing output file: "+output+"\n")
