#from HappyTools.util.fitting import gauss_function
import MassyTools.gui.version as version
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages

#from bisect import bisect_left, bisect_right
#from datetime import datetime
#from matplotlib.backends.backend_pdf import PdfPages
#from numpy import linspace
#from pathlib import Path, PurePath
#from scipy.interpolate import InterpolatedUnivariateSpline


class Pdf(object):
    def __init__(self, master):
        self.master = master
        parent_dir = Path(master.filename).parent
        pdf_file = str(Path(master.filename).stem)+'.pdf'
        pdf = PdfPages(parent_dir / Path(pdf_file))

        self.pdf = pdf

    def attach_meta_data(self):
        meta_data = self.pdf.infodict()
        meta_data['Title'] = 'PDF Report for: '+str(
                Path(self.master.filename).stem)
        meta_data['Author'] = ('HappyTools version: '+
                               str(version.version)+' build: '+
                               str(version.build))
        meta_data['CreationDate'] = datetime.now()

    def plot_mass_spectrum(self):
        x_data, y_data = zip(*self.master.mass_spectrum.data)
        fig = plt.figure(figsize=(8,6))
        ax = fig.add_subplot(111)
        plt.plot(x_data, y_data)
        plt.title(str(self.master.mass_spectrum.filename))
        plt.xlabel('m/z')
        plt.ylabel('Intensity [au]')
        self.pdf.savefig(fig)
        plt.close(fig)

    def plot_mass_spectrum_peak(self):
        x_data, y_data = zip(*self.master.analyte.data_subset)
        background_intensity = self.master.analyte.background_intensity
        fig = plt.figure(figsize=(8,6))
        ax = fig.add_subplot(111)
        plt.plot(x_data, y_data, color='blue')
        plt.plot([x_data[0], x_data[-1]], [background_intensity,
                 background_intensity], alpha=0.5, color='red')
        plt.title(str(self.master.analyte.name))
        plt.xlabel('m/z')
        plt.ylabel('Intensity [au]')
        self.pdf.savefig(fig)
        plt.close(fig)

    #def plot_individual(self, master):
        #time, intensity = zip(*master.chrom.trace.chrom_data)
        #low = bisect_left(time, master.time-master.window)
        #high = bisect_right(time, master.time+master.window)

        #f = InterpolatedUnivariateSpline(time[low:high], intensity[low:high])

        #new_x = linspace(time[low], time[high], 2500*(time[high]-time[low]))
        #new_y = f(new_x)

        #if master.peak.coeff.size > 0:
            #new_gauss_x = linspace(time[low], time[high], 2500*(
                                   #time[high]-time[low]))
            #new_gauss_y = gauss_function(new_gauss_x, *master.peak.coeff)

        #fig =  plt.figure(figsize=(8, 6))
        #fig.add_subplot(111)
        #plt.plot(time[low:high], intensity[low:high], 'b*')
        #plt.plot((new_x[0],new_x[-1]),(
                  #master.peak.background,master.peak.background),'red')
        #plt.plot((new_x[0],new_x[-1]),(master.peak.background+
                  #master.peak.noise,master.peak.background+master.peak.noise),
                  #color='green')
        #plt.plot(new_x,new_y, color='blue',linestyle='dashed')
        #if master.peak.coeff.size > 0:
            #plt.plot(new_gauss_x, new_gauss_y, color='green',
                     #linestyle='dashed')
        #plt.plot((time[intensity[low:high].index(max(intensity[low:high]))+low],
                #time[intensity[low:high].index(max(intensity[low:high]))+low]),
                #(master.peak.background,max(intensity[low:high])),
                #color='orange',linestyle='dotted')
        #plt.plot((min(max(master.peak.center-master.peak.width,new_x[0]),
                  #new_x[-1]),max(min(master.peak.center+master.peak.width,
                  #new_x[-1]),new_x[0])), (master.peak.height,
                  #master.peak.height),color='red',linestyle='dashed')
        #plt.legend(['Raw Data','Background','Noise','Univariate Spline',
                    #'Gaussian Fit ('+str(int(master.peak.residual*100))+
                    #'%)','Signal (S/N '+'{0:.2f}'.format(
                    #master.peak.signal_noise)+')','FWHM: '+'{0:.2f}'.format(
                    #master.peak.fwhm)], loc='best')
        #plt.title('Detail view: '+str(master.peak.peak))
        #plt.xlabel('Retention Time [m]')
        #plt.ylabel('Intensity [au]')
        #self.pdf.savefig(fig)
        #plt.close(fig)

    def close_pdf(self):
        self.pdf.close()
