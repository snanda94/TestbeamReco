from ROOT import TFile,TTree,TCanvas,TH1D,TH1F,TH2F,TLatex,TMath,\
TEfficiency,TGraphAsymmErrors,TLegend,gROOT,gStyle, gPad, kWhite, kBlack
import os
from stripBox import getStripBox
import optparse
import myStyle
import langaus
import myFunctions as mf

gROOT.SetBatch( True )
gStyle.SetOptFit(1011)
colors = myStyle.GetColors(True)

## Defining Style
myStyle.ForceStyle()


class HistoInfo:
    def __init__(self, inHistoName, f, outHistoName, yMax=30.0,
                 xlabel="", ylabel="Position resolution [#mum]",
                 sensor="", center_position = 0.0):
        self.inHistoName = inHistoName
        self.f = f
        self.outHistoName = outHistoName
        self.yMax = yMax
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.sensor = sensor
        self.center_position = center_position
        self.th2 = self.getTH2(f, inHistoName, sensor)
        self.th1 = self.getTH1(outHistoName)

    def getTH2(self, f, name, sensor, axis='zx'):
        th3 = f.Get(name)
        th2 = th3.Project3D(axis)

        # # Rebin low statistics sensors
        # if sensor=="BNL2020":
        #     th2.RebinX(5)
        # elif sensor=="BNL2021":
        #     th2.RebinX(10)
        # # if "1cm_500up_300uw" in sensor:
        # #     th2.RebinX(2)

        return th2

    def getTH1(self, hname):
        htitle = ";%s;%s"%(self.xlabel, self.ylabel)
        nxbin = self.th2.GetXaxis().GetNbins()
        xmin, xmax = mf.get_shifted_limits(self.th2, self.center_position)

        # Create and define th1 default style
        th1 = TH1D(hname, htitle, nxbin, xmin, xmax)
        # th1.SetStats(0)
        th1.SetMinimum(0.0001)
        th1.SetMaximum(self.yMax)
        # th1.SetLineWidth(3)
        # th1.SetLineColor(kBlack)
        # # th1.GetXaxis().SetRangeUser(-xlength,xlength)

        return th1


# Construct the argument parser
parser = optparse.OptionParser("usage: %prog [options]\n")
parser.add_option('-x','--xlength', dest='xlength', default = 2.5, help="Limit x-axis in final plot")
parser.add_option('-y','--ylength', dest='ylength', default = 150, help="Max Amp value in final plot")
parser.add_option('-D', dest='Dataset', default = "", help="Dataset, which determines filepath")
parser.add_option('-d', dest='debugMode', action='store_true', default = False, help="Run debug mode")
parser.add_option('-t', dest='useTight', action='store_true', default = False, help="Use tight cut for pass")
options, args = parser.parse_args()

dataset = options.Dataset
outdir = myStyle.getOutputDir(dataset)
inputfile = TFile("%s%s_Analyze.root"%(outdir,dataset))

sensor_Geometry = myStyle.GetGeometry(dataset)

sensor = sensor_Geometry['sensor']

xlength = float(options.xlength)
ylength = float(options.ylength)
debugMode = options.debugMode

is_tight = options.useTight

# Get position of the central channel in the "x" direction
position_center = mf.get_central_channel_position(inputfile, "x")

outdir = myStyle.GetPlotsDir(outdir, "Amplitude/")

# TODO: Add per channel plots
# indices = mf.get_existing_indices(inputfile, "amplitude_vs_xy_channel")
# for index in indices:
#     channel_element = ["amplitude_vs_xy_channel%s"%index, "deltaX_oneStripCh%s"%index, "tracker"]
#     list_htitles.append(channel_element)

# Save list with histograms to draw
list_htitles = [
    # [hist_input_name, short_output_name, y_axis_title]
    ["amplitude_vs_xy", "Amplitude", "MPV signal amplitude [mV]"],
    ["amplitudeDefault_vs_xy", "AmplitudeDefault", "MPV signal amplitude [mV]"],
]

# Use tight cut histograms
if (is_tight):
    print(" >> Using tight cuts!")
    for titles in list_htitles:
        titles[0]+= "_tight"

# List with histograms using HistoInfo class
all_histoInfos = []
for titles in list_htitles:
    hname, outname, ytitle = titles
    info_obj = HistoInfo(hname, inputfile, outname, yMax=ylength, ylabel=ytitle,
                         sensor=dataset, center_position=position_center)
    all_histoInfos.append(info_obj)

canvas = TCanvas("cv","cv",1000,800)
canvas.SetGrid(0,1)
gStyle.SetOptStat(0)

if debugMode:
    outdir_q = myStyle.CreateFolder(outdir, "q_AmpVsX0/")

# Get total number of bins in x-axis to loop over (all hists have the same number, in principle)
nbins = all_histoInfos[0].th2.GetXaxis().GetNbins()

print("Setting up Langaus")
fit = langaus.LanGausFit()
print("Setup Langaus")

# Loop over X bins
for i in range(1, nbins+1):
    for info_entry in all_histoInfos:
        totalEvents = info_entry.th2.GetEntries()
        # TODO: Add support for px projection in case of use of use_center_y option
        tmpHist = info_entry.th2.ProjectionY("py",i,i)
        myRMS = tmpHist.GetRMS()
        myMean = tmpHist.GetMean()
        nEvents = tmpHist.GetEntries()
        value = myMean

        # Define minimum of bin's entries to be fitted
        minEvtsCut = totalEvents/nbins

        if (i == 1):
            msg_nentries = "%s: nEvents > %.2f "%(info_entry.inHistoName, minEvtsCut)
            msg_nentries+= "(Total events: %i)"%(totalEvents)
            print(msg_nentries)

        #Do fit
        if(nEvents > minEvtsCut):
            # tmpHist.Rebin(2)
            if (myMean > 50):
                tmpHist.Rebin(5)
            else:
                tmpHist.Rebin(10)

            myLanGausFunction = fit.fit(tmpHist, fitrange=(myMean-1*myRMS, myMean+3*myRMS))
            myMPV = myLanGausFunction.GetParameter(1)
            value = myMPV

            # For Debugging
            if (debugMode):
                tmpHist.Draw("hist")
                myLanGausFunction.Draw("same")
                canvas.SaveAs("%sq_%s%i.gif"%(outdir_q, info_entry.outHistoName, i))
                bin_center = info_entry.th1.GetXaxis().GetBinCenter(i)
                msg_amp = "Bin: %i (x center = %.3f)"%(i, bin_center)
                msg_amp+= " -> Amplitude: %.3f mV"%(value)
                print(msg_amp)
        else:
            value = 0.0

        value = value if (value>0.0) else 0.0

        info_entry.th1.SetBinContent(i, value)

# Define output file
output_path = "%sAmplitudeVsX"%(outdir)
if (is_tight):
    output_path+= "_tight"
output_path+= ".root"

outputfile = TFile(output_path,"RECREATE")

# Define hist for axes style
htemp = TH1F("htemp", "", 1, -xlength, xlength)
htemp.SetStats(0)
htemp.GetXaxis().SetTitle("Track x position [mm]")
htemp.GetYaxis().SetRangeUser(0.0, ylength)
htemp.GetYaxis().SetTitle("MPV signal amplitude [mV]")
htemp.SetLineColor(colors[2])

# TODO: Add function that changes the margins and updates GetMargin() and GetCenter()
# Define legend
pad_center = myStyle.GetPadCenter()
pad_margin = myStyle.GetMargin()
# legend = TLegend(pad_center-0.20, 2*pad_margin+0.01, pad_center+0.20, 2*pad_margin+0.16)
# legend.SetBorderSize(0)
# # legend.SetFillColor(kWhite)
# legend.SetTextFont(myStyle.GetFont())
# legend.SetTextSize(myStyle.GetSize()-20)

for i,info_entry in enumerate(all_histoInfos):
    hist = info_entry.th1
    hist.SetLineColor(colors[0])
    hist.SetLineWidth(2)
    ymin = hist.GetMinimum()
    ymax = hist.GetMaximum()

    htemp.Draw("AXIS")
    # Define and draw gray bars in the background (Position of metallic sections)
    boxes = getStripBox(inputfile, ymin=ymin, ymax=ymax, strips=True, shift=position_center)
    for box in boxes:
        box.Draw()
    gPad.RedrawAxis("g")

    hist.Draw("hist same")
    # legend.AddEntry(hist, legend_name[i], "lep")

    hist.Write()

    htemp.Draw("AXIS same")
    # legend.Draw()

    # myStyle.BeamInfo()
    myStyle.SensorInfoSmart(dataset)

    save_path = "%s%s_vs_x"%(outdir, info_entry.outHistoName)
    if (is_tight):
        save_path+= "-tight"
    canvas.SaveAs("%s.gif"%save_path)
    canvas.SaveAs("%s.pdf"%save_path)

    canvas.Clear()

outputfile.Close()




# #Get 3D histograms
# channel_good_index = []
# th3_amplitude_vs_xy_ch = []
# for i in range(7):
#     hname = "amplitude_vs_xy_channel0"+str(i)
#     if inputfile.Get(hname):
#         channel_good_index.append(i)
#         th3_amplitude_vs_xy_ch.append(inputfile.Get(hname))

# th3_amplitude_vs_xy_channelall = inputfile.Get("totamplitude_vs_xy")

# shift = inputfile.Get("stripBoxInfo03").GetMean(1)

# #Build 2D amp vs x histograms
# list_th2_amplitude_vs_x = []
# for i,ch in enumerate(channel_good_index):
#     list_th2_amplitude_vs_x.append(th3_amplitude_vs_xy_ch[i].Project3D("zx"))

# list_th2_amplitude_vs_x.append(th3_amplitude_vs_xy_channelall.Project3D("zx"))

# #Build amplitude histograms
# th1 = th3_amplitude_vs_xy_ch[0].ProjectionX().Clone("th1")
# th1_Nbins = th1.GetXaxis().GetNbins()
# th1_Xmin = th1.GetXaxis().GetXmin()-shift
# th1_Xmax = th1.GetXaxis().GetXmax()-shift
# list_amplitude_vs_x = []

# for i,ch in enumerate(channel_good_index):
#     list_amplitude_vs_x.append(TH1F("amplitude_vs_x_channel0%i"%(ch),"", th1_Nbins, th1_Xmin, th1_Xmax))

# print ("Amplitude vs X: " + str(th1.GetXaxis().GetBinLowEdge(1)-shift) + " -> " + str(th1.GetXaxis().GetBinUpEdge(th1.GetXaxis().GetNbins())-shift))

# print("Setting up Langaus")
# fit = langaus.LanGausFit()
# print("Setup Langaus")
# canvas = TCanvas("cv","cv",1000,800)

# maxAmpChannels = []
# maxAmpALL = 0
# n_channels = 0
# for channel in range(0, len(list_amplitude_vs_x)):
#     # print("Channel : " + str(channel))
#     maxAmp = 0
#     totalEvents = list_th2_amplitude_vs_x[channel].GetEntries()
#     # Run across X-bins. ROOT convention: bin 0 - underflow, nbins+1 - overflow bin
#     for i in range(1, list_amplitude_vs_x[channel].GetXaxis().GetNbins()+1):
#         tmpHist = list_th2_amplitude_vs_x[channel].ProjectionY("py",i,i)
#         myTotalEvents=tmpHist.Integral()
#         myMean = tmpHist.GetMean()
#         myRMS = tmpHist.GetRMS()
#         value = myMean            
#         nEvents = tmpHist.GetEntries()

#         nXBins = th1_Nbins
#         minEvtsCut = totalEvents/nXBins
#         if i==1: print("Channel %i: nEvents > %.2f (Total events: %i; N bins: %i)"%(channel,minEvtsCut,totalEvents,nXBins))

#         if(nEvents > minEvtsCut):
#             #use coarser bins when the signal is bigger
#             if (myMean > 50) :
#                 tmpHist.Rebin(5)
#             else :
#                 tmpHist.Rebin(10)

#             myLanGausFunction = fit.fit(tmpHist, fitrange=(myMean-1*myRMS,myMean+3*myRMS))
#             myMPV = myLanGausFunction.GetParameter(1)
#             value = myMPV

#             ##For Debugging
#             #tmpHist.Draw("hist")
#             #myLanGausFunction.Draw("same")
#             #canvas.SaveAs(outdir+"q_"+str(i)+"_"+str(channel)+".gif")
#         else:
#             value = 0.0

#         value = value if(value>0.0) else 0.0

#         if value > maxAmp:
#             maxAmp = value

#         #print(myTotalEvents)
#         #print ("Bin : " + str(i) + " -> " + str(value))

#         list_amplitude_vs_x[channel].SetBinContent(i,value)
#     ### print("Channel : " + str(channel) + "; Max Amplitude = " + str(maxAmp) + " [mV]")
#     #print("Channel: %i; Max Amplitude = %.3f [mV]"%(channel, maxAmp))
#     maxAmpChannels.append(maxAmp)
#     maxAmpALL+=maxAmp
#     if maxAmp!=0: n_channels+=1

# maxAmpAvg = maxAmpALL/n_channels
# # print("Average Max Amplitude = " + str(maxAmpAvg) + "; N of non-empty channels: " + str(n_channels))
# print("Average Max Amplitude = %.2f [mV]; N of non-empty channels: %i"%(maxAmpAvg, n_channels))

# # Define amplitude correction
# for i in range(0,len(maxAmpChannels)):
#     # print("Channel number; {:0.2f}, Max Amp: {:0.2f}, Average Max Amplitude: {:0.2f}, Amp. Correction: {:0.4f}".format(i, maxAmpChannels[i], maxAmpAvg, maxAmpAvg/maxAmpChannels[i]))
#     print("Channel %i:   Max Amp: %0.3f, Amp. Correction: %0.4f"%(i, maxAmpChannels[i], maxAmpAvg/maxAmpChannels[i]))

                    
# # Save amplitude histograms
# outputfile = TFile("%sPlotAmplitudeVsX.root"%(outdir),"RECREATE")
# # for channel in range(0, len(list_amplitude_vs_x)):
# #     list_amplitude_vs_x[channel].Write()

# for hist in list_amplitude_vs_x:
#     hist.Write()

# outputfile.Close()


# #Make final plots
# plotfile = TFile("%sPlotAmplitudeVsX.root"%(outdir),"READ")
# plotList_amplitude_vs_x  = []
# for i,ch in enumerate(channel_good_index):
#     plot_amplitude = plotfile.Get("amplitude_vs_x_channel0%i"%ch)
#     plot_amplitude.SetLineWidth(2)
#     plot_amplitude.SetLineColor(colors[i])
#     plotList_amplitude_vs_x.append(plot_amplitude)


# totalAmplitude_vs_x = TH1F("htemp","",1,-xlength,xlength)
# totalAmplitude_vs_x.Draw("hist")
# totalAmplitude_vs_x.SetStats(0)
# totalAmplitude_vs_x.SetTitle("")
# totalAmplitude_vs_x.GetXaxis().SetTitle("Track x position [mm]")
# totalAmplitude_vs_x.GetYaxis().SetTitle("MPV signal amplitude [mV]")
# totalAmplitude_vs_x.SetLineWidth(2)

# totalAmplitude_vs_x.SetMaximum(ylength)

# boxes = getStripBox(inputfile,0,ylength-10.0,False, 18, True, shift)
# for box in boxes:
#    box.Draw()
# totalAmplitude_vs_x.Draw("AXIS same")
# totalAmplitude_vs_x.Draw("hist same")


# legend = TLegend(2*myStyle.GetMargin()+0.02,1-myStyle.GetMargin()-0.02-0.2,1-myStyle.GetMargin()-0.02,1-myStyle.GetMargin()-0.02)
# legend.SetNColumns(3)
# legend.SetTextFont(myStyle.GetFont())
# legend.SetTextSize(myStyle.GetSize())
# legend.SetBorderSize(0)
# legend.SetFillColor(kWhite)

# for i,ch in enumerate(channel_good_index):
#     plotList_amplitude_vs_x[i].Draw("histsame")
#     legend.AddEntry(plotList_amplitude_vs_x[i], "Strip %i"%(ch+1))
# legend.Draw();

# # myStyle.BeamInfo()
# myStyle.SensorInfoSmart(dataset)

# canvas.SaveAs(outdir+"TotalAmplitude_vs_x_"+sensor+".gif")
# canvas.SaveAs(outdir+"TotalAmplitude_vs_x_"+sensor+".pdf")

