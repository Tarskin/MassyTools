# load libs
import xml.sax
import xml.dom.minidom
import base64
import zlib
import struct
import re
import os.path
import numpy
from copy import deepcopy

# compile basic patterns
SCAN_NUMBER_PATTERN = re.compile('scan=([0-9]+)')

class stopParsing(Exception):
    """ Exeption to stop parsing XML data.
    """
    pass

def _parseScanNumber(string):
    """ Parse real scan number from id tag.
    """

    # match scan number pattern
    match = SCAN_NUMBER_PATTERN.search(string)
    if not match:
        return None

    # convert to int
    try: return int(match.group(1))
    except: return None

class runHandler(xml.sax.handler.ContentHandler):
    """ Get whole run.
    """

    def __init__(self):
        self.data = {}
        self.currentID = None

        self._isSpectrum = False
        self._isPrecursor = False
        self._isBinaryDataArray = False
        self._isData = False

        self.tmpBinaryData = None
        self.tmpPrecision = None
        self.tmpCompression = None
        self.tmpArrayType = None
    # ----

    def startElement(self, name, attrs):
        """ Element started.
        """

        # get scan metadata
        if name == 'spectrum':
            self._isSpectrum = True

            # get scan ID
            self.currentID = None
            attribute = attrs.get('id', False)
            if attribute:
                self.currentID = _parseScanNumber(attribute)

            scan = {
                'title': '',
                'scanNumber': self.currentID,
                'parentScanNumber': None,
                'msLevel': None,
                'pointsCount': None,
                'polarity': None,
                'retentionTime': None,
                'lowMZ': None,
                'highMZ': None,
                'basePeakMZ': None,
                'basePeakIntensity': None,
                'totIonCurrent': None,
                'precursorMZ': None,
                'precursorIntensity': None,
                'precursorCharge': None,
                'spectrumType': 'unknown',
                
                'mzData': None,
                'mzPrecision': None,
                'mzCompression': None,
                'intData': None,
                'intPrecision': None,
                'intCompression': None,
            }

            # get points count
            attribute = attrs.get('defaultArrayLength', False)
            if attribute:
                scan['pointsCount'] = int(attribute)

            # add scan
            self.data[self.currentID] = scan

        # precursor tag
        elif name == 'precursor' and self._isSpectrum:
            self._isPrecursor = True

            # get parent scan number
            attribute = attrs.get('spectrumRef', False)
            if attribute:
                self.data[self.currentID]['parentScanNumber'] = _parseScanNumber(attribute)

        # binary aray tag
        elif name == 'binaryDataArray' and self._isSpectrum:
            self._isBinaryDataArray = True
            self.tmpBinaryData = []
            self.tmpPrecision = None
            self.tmpCompression = None
            self.tmpArrayType = None

        # data array tag
        elif name == 'binary' and self._isBinaryDataArray:
            self._isData = True

        # get precursor
        elif name == 'cvParam' and self._isPrecursor:
            paramName = attrs.get('name','')
            paramValue = attrs.get('value','')
            
            if paramName == 'selected ion m/z' and paramValue != None:
                self.data[self.currentID]['precursorMZ'] = float(paramValue)
            elif paramName == 'intensity' and paramValue != None:
                self.data[self.currentID]['precursorIntensity'] = float(paramValue)
            elif paramName == 'possible charge state' and paramValue != None:
                self.data[self.currentID]['precursorCharge'] = int(paramValue)
            elif paramName == 'charge state' and paramValue != None:
                self.data[self.currentID]['precursorCharge'] = int(paramValue)

        # get binary data metadata
        elif name == 'cvParam' and self._isBinaryDataArray:
            paramName = attrs.get('name','')
            paramValue = attrs.get('value','')

            # precision
            if paramName == '64-bit float':
                self.tmpPrecision = 64
            elif paramName == '32-bit float':
                self.tmpPrecision = 32

            # compression
            elif paramName == 'zlib compression':
                self.tmpCompression = 'zlib'
            elif paramName == 'no compression':
                self.tmpCompression = None

            # array type
            elif paramName == 'm/z array':
                self.tmpArrayType = 'mzArray'
            elif paramName == 'intensity array':
                self.tmpArrayType = 'intArray'

        # get scan metadata
        elif name == 'cvParam' and self._isSpectrum:
            paramName = attrs.get('name','')
            paramValue = attrs.get('value','')

            # data type
            if paramName == 'centroid spectrum':
                self.data[self.currentID]['spectrumType'] = 'discrete'
            elif paramName == 'profile spectrum':
                self.data[self.currentID]['spectrumType'] = 'continuous'

            # MS level
            elif paramName == 'ms level' and paramValue != None:
                self.data[self.currentID]['msLevel'] = int(paramValue)

            # polarity
            elif paramName == 'positive scan':
                self.data[self.currentID]['polarity'] = 1
            elif paramName == 'negative scan':
                self.data[self.currentID]['polarity'] = -1

            # total ion current
            elif paramName == 'total ion current' and paramValue != None:
                self.data[self.currentID]['totIonCurrent'] = max(0.0, float(paramValue))

            # base peak
            elif paramName == 'base peak m/z' and paramValue != None:
                self.data[self.currentID]['basePeakMZ'] = float(paramValue)
            elif paramName == 'base peak intensity' and paramValue != None:
                self.data[self.currentID]['basePeakIntensity'] = max(0.0, float(paramValue))

            # mass range
            elif paramName == 'lowest observed m/z' and paramValue != None:
                self.data[self.currentID]['lowMZ'] = float(paramValue)
            elif paramName == 'highest observed m/z' and paramValue != None:
                self.data[self.currentID]['highMZ'] = float(paramValue)

            # retention time
            elif paramName == 'scan start time' and paramValue != None:
                if attrs.get('unitName','') == 'minute':
                    self.data[self.currentID]['retentionTime'] = float(paramValue)*60
                elif attrs.get('unitName','') == 'second':
                    self.data[self.currentID]['retentionTime'] = float(paramValue)
                else:
                    self.data[self.currentID]['retentionTime'] = float(paramValue)*60
    # ----

    def endElement(self, name):
        """ Element ended.
        """

        # end spectrum element
        if name == 'spectrum':
            self._isSpectrum = False

        # end precursor element
        elif name == 'precursor':
            self._isPrecursor = False

        # stop reading peaks data
        elif name == 'binaryDataArray' and self._isSpectrum:
            self._isBinaryDataArray = False

            # mz array
            if self.tmpArrayType == 'mzArray':
                self.data[self.currentID]['mzData'] = ''.join(self.tmpBinaryData)
                self.data[self.currentID]['mzPrecision'] = self.tmpPrecision
                self.data[self.currentID]['mzCompression'] = self.tmpCompression

            # intensity array
            elif self.tmpArrayType == 'intArray':
                self.data[self.currentID]['intData'] = ''.join(self.tmpBinaryData)
                self.data[self.currentID]['intPrecision'] = self.tmpPrecision
                self.data[self.currentID]['intCompression'] = self.tmpCompression

            self.tmpBinaryData = None
            self.tmpPrecision = None
            self.tmpCompression = None

        # stop reading binary array
        elif name == 'binary':
            self._isData = False
    # ----

    def characters(self, ch):
        """ Grab characters.
        """

        # get peaks
        if self._isData:
            self.tmpBinaryData.append(ch)
    # ----

class parseMZML():
    def __init__(self,path):
        self.path = path
        self._scans = None
        self._scanlist = None
        self._info = None

        # check path
        if not os.path.exists(path):
            raise IOError, 'File not found! --> ' + self.path

    def load(self):
        """ Load all scans into memory.
        """
        # init parser
        handler = runHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)

        # parse document
        try:
            document = file(self.path)
            parser.parse(document)
            document.close()
            self._scans = handler.data
        except xml.sax.SAXException:
            self._scans = False

        # make scanlist
        if self._scans:
            self._scanlist = deepcopy(self._scans)
            for scanNumber in self._scanlist:
                del self._scanlist[scanNumber]['mzData']
                del self._scanlist[scanNumber]['mzPrecision']
                del self._scanlist[scanNumber]['mzCompression']
                del self._scanlist[scanNumber]['intData']
                del self._scanlist[scanNumber]['intPrecision']
                del self._scanlist[scanNumber]['intCompression']
    # ----

    def _parsePoints(self, scanData):
        """ Parse spectrum data.
        """
        
        # check data
        if not scanData['mzData'] or not scanData['intData']:
            return []
        
        # decode data
        mzData = base64.b64decode(scanData['mzData'])
        intData = base64.b64decode(scanData['intData'])
        
        # decompress data
        if scanData['mzCompression'] == 'zlib':
            mzData = zlib.decompress(mzData)
        if scanData['intCompression'] == 'zlib':
            intData = zlib.decompress(intData)
        
        # get precision
        mzPrecision = 'f'
        intPrecision = 'f'
        if scanData['mzPrecision'] == 64:
            mzPrecision = 'd'
        if scanData['intPrecision'] == 64:
            intPrecision = 'd'
        
        # convert from binary
        count = len(mzData) / struct.calcsize('<' + mzPrecision)
        mzData = struct.unpack('<' + mzPrecision * count, mzData[0:len(mzData)])
        count = len(intData) / struct.calcsize('<' + intPrecision)
        intData = struct.unpack('<' + intPrecision * count, intData[0:len(intData)])
        
        # format
        if scanData['spectrumType'] == 'discrete':
            data = map(list, zip(mzData, intData))
        else:
            mzData = numpy.array(mzData)
            mzData.shape = (-1,1)
            intData = numpy.array(intData)
            intData.shape = (-1,1)
            data = numpy.concatenate((mzData,intData), axis=1)
            data = data.copy()
        
        return data
    # ----

def transformBinary(run, inputFile, outFolder, function):
    """ Transform m/z data with given calibration function.
    """
    data = run._parsePoints(run._scans[None])
    mzList,intList = zip(*data)
    mzArray = numpy.array(mzList)
    newArray = function(mzArray)
    if run._scans[None]['mzCompression'] == 'zlib':
        mzData = zlib.compress(newArray)
    mzData = base64.b64encode(mzData)
    parts = os.path.split(str(inputFile))
    output = "calibrated_"+str(parts[-1])
    output = os.path.join(outFolder, output)
    with open(output,'w') as fw:
        with open(inputFile,'r') as fr:
            copy = False
            for line in fr:
                if 'm/z array' in line:
                    copy = True
                if '</binaryDataArray>' in line:
                    copy = False
                if copy:
                    if '<binary>' in line:
                        front = line.split('<binary>')[0]
                        tail = line.split('</binary>')[-1]
                        line = str(front)+"<binary>"+str(mzData)+"</binary>"+str(tail)
                fw.write(line)
    # ----
