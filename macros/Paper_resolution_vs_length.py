import ROOT
import numpy as np
import myStyle

## Defining Style
ROOT.gROOT.SetBatch( True )
myStyle.ForceStyle()
colors = myStyle.GetColors(True)

dict_resolutions = myStyle.resolutions2022

outdir = myStyle.getOutputDir("Paper2022")

# Sensors with 500um pitch and 200um metal width
list_of_sensors = ["EIC_W1_2p5cm_500up_200uw_215V", "EIC_W1_1cm_500up_200uw_255V", "EIC_W1_0p5cm_500up_200uw_1_4_245V"]

length = []
empty = [0]*len(list_of_sensors)
# positionres_oneStrip  = np.array([78.65, 84.13, 53.97]) # Sigma from fit to oneStrip 1DPlot
positionres_oneStrip  = [] # RMS from oneStrip onMetal 1DPlot
positionres_twoStrips = []
positionres_oneStripuncert  = []
positionres_twoStripsuncert = []

for name in list_of_sensors:
    length.append(myStyle.GetGeometry(name)['length'])
    positionres_oneStrip.append(dict_resolutions[name]['position_oneStripRMS'])
    positionres_oneStripuncert.append(0.01)
    positionres_twoStrips.append(dict_resolutions[name]['position_twoStrips'])
    positionres_twoStripsuncert.append(dict_resolutions[name]['position_twoStrips_E'])

length = np.asarray(length)
empty = np.asarray(empty)
positionres_oneStrip = np.asarray(positionres_oneStrip)
positionres_oneStripuncert = np.asarray(positionres_oneStripuncert)
positionres_twoStrips = np.asarray(positionres_twoStrips)
positionres_twoStripsuncert = np.asarray(positionres_twoStripsuncert)

# positionres_oneStrip  = np.array([78.65, 84.13, 53.97]) # Sigma from fit to oneStrip 1DPlot
# positionres_oneStrip  = np.array([72.09, 54.87, 52.91]) # RMS from oneStrip onMetal 1DPlot
# positionres_twoStrips = np.array([34.13, 18.53, 11.82])
# timingres = np.array([          39.57,  37.34,  34.20,  32.95,  32.55,  35.18])
# timingresweighted2 = np.array([ 35.84,  35.71,  32.67,  31.89,  31.15,  34.11])

# for i in range(0,len(length)):
#     positionres_twoStrips[i] = ROOT.TMath.Sqrt(positionres_twoStrips[i]*positionres_twoStrips[i]-36)
#     # timingres[i] = ROOT.TMath.Sqrt(timingres[i]*timingres[i]-100)
#     # timingresweighted2[i] = ROOT.TMath.Sqrt(timingresweighted2[i]*timingresweighted2[i]-100)

# empty = np.array([0,0,0])

# positionres_oneStripuncert  = np.array([0.18, 0.08, 0.21])
# positionres_oneStripuncert  = np.array([0.01, 0.01, 0.01])
# positionres_twoStripsuncert = np.array([0.16, 0.02, 0.02])
# timingresuncert = np.array([            2.58, 0.72, 0.60, 0.52, 0.54, 1.50])
# timingresweighted2uncert = np.array([   1.96, 0.50, 0.52, 0.47, 0.48, 1.36])

# for i in range(0,len(empty)):
#     positionres_twoStripsuncert[i] = positionres_twoStripsuncert[i]*ROOT.TMath.Sqrt(positionres_twoStrips[i]*positionres_twoStrips[i]+36)/positionres_twoStrips[i]
#     # timingresuncert[i] = timingresuncert[i]*ROOT.TMath.Sqrt(timingres[i]*timingres[i]+100)/timingres[i]
#     # timingresweighted2uncert[i] = timingresweighted2uncert[i]*ROOT.TMath.Sqrt(timingresweighted2[i]*timingresweighted2[i]+100)/timingresweighted2[i]

position_oneStrip_graph  = ROOT.TGraphErrors(length.size ,length.astype(np.double), positionres_oneStrip.astype(np.double), empty.astype(np.double), positionres_oneStripuncert.astype(np.double))
position_twoStrips_graph = ROOT.TGraphErrors(length.size ,length.astype(np.double), positionres_twoStrips.astype(np.double), empty.astype(np.double), positionres_twoStripsuncert.astype(np.double))
# time_graph = ROOT.TGraphErrors(length.size , length.astype(np.double), timingres.astype(np.double), empty.astype(np.double), timingresuncert.astype(np.double))
# time_weight_graph = ROOT.TGraphErrors(length.size , length.astype(np.double), timingresweighted2.astype(np.double), empty.astype(np.double), timingresweighted2uncert.astype(np.double))

# print("For Nominal Voltage")
# print("Position resolution: "+"{:.1f}".format(positionres_twoStrips[4])+" #pm "+"{:.1f}".format(positionres_twoStripsuncert[4]))
# print("Time W2 resolution: "+"{:.1f}".format(timingresweighted2[4])+" #pm "+"{:.1f}".format(timingresweighted2uncert[4]))

position_oneStrip_graph.SetMarkerColor(colors[0])
position_oneStrip_graph.SetMarkerStyle(20)
position_oneStrip_graph.SetMarkerSize(2)
position_oneStrip_graph.SetLineColor(colors[0])

position_twoStrips_graph.SetMarkerColor(colors[2])
position_twoStrips_graph.SetMarkerStyle(20)
position_twoStrips_graph.SetMarkerSize(2)
position_twoStrips_graph.SetLineColor(colors[2])

# time_graph.SetMarkerColor(ROOT.kBlack)
# time_graph.SetMarkerStyle(20)
# time_graph.SetMarkerSize(1)
# time_graph.SetLineColor(ROOT.kBlack)

# time_weight_graph.SetMarkerColor(ROOT.kBlue)
# time_weight_graph.SetMarkerStyle(20)
# time_weight_graph.SetMarkerSize(1)
# time_weight_graph.SetLineColor(ROOT.kBlue)

# c1 = ROOT.TCanvas( "c1", "c1", 0, 0, 800, 800)
c1 = ROOT.TCanvas("c1","c1",1000,800)
c1.SetGrid(0,1)

ROOT.gPad.SetTicks(1,1)
ROOT.gStyle.SetOptStat(0) 


hdummy = ROOT.TH1D("","",1,length.min()-5,length.max()+5)
hdummy.GetXaxis().SetTitle("Strip length [mm]")
hdummy.GetYaxis().SetTitle("Position resolution [#mum]")
hdummy.SetMaximum(90.0)
hdummy.SetMinimum(0.0001)
hdummy.Draw("AXIS")

# right_axis = ROOT.TGaxis(length.max()+5,0.0001,length.max()+5,70.0,0.0001,70.0,510,"+L")
# right_axis.UseCurrentStyle()
# right_axis.SetTitle("Time resolution [ps]")
# right_axis.SetLabelFont(myStyle.GetFont())
# right_axis.SetTitleFont(myStyle.GetFont())
# right_axis.SetLabelSize(myStyle.GetSize()-4)
# right_axis.SetTitleSize(myStyle.GetSize())
# right_axis.Draw()

# leg = ROOT.TLegend(2*myStyle.GetMargin()+0.01, 1-myStyle.GetMargin()-0.01-0.20, 2*myStyle.GetMargin()+0.01+0.25, 1-myStyle.GetMargin()-0.01)
leg = ROOT.TLegend(2*myStyle.GetMargin()+0.01, 1-myStyle.GetMargin()-0.01-0.20, 2*myStyle.GetMargin()+0.01+0.35, 1-myStyle.GetMargin()-0.01)
leg.SetTextFont(myStyle.GetFont())
leg.SetTextSize(myStyle.GetSize()-4)
# leg.AddEntry(time_graph, "#splitline{Single-channel Time}{Resolution}", "pl")
# leg.AddEntry(time_weight_graph, "#splitline{Multi-channel Time}{Resolution}", "pl")
leg.AddEntry(position_oneStrip_graph, "Exactly one strip reconstruction", "pl")
leg.AddEntry(position_twoStrips_graph, "Two strip reconstruction", "pl")

myStyle.BeamInfo()
# myStyle.SensorInfo("BNL2021", 285, False)
text = ROOT.TLatex()
text.SetTextSize(myStyle.GetSize()-4)
text.SetTextAlign(31)
text.DrawLatexNDC(1-myStyle.GetMargin()-0.005,1-myStyle.GetMargin()+0.01,"#bf{Varying length}")

leg.Draw()
ROOT.gPad.RedrawAxis("g")

position_oneStrip_graph.Draw("epl same")
position_twoStrips_graph.Draw("epl same")

# time_graph.Draw("epl same")
# time_weight_graph.Draw("epl same")

c1.SaveAs("%sresolution_vs_length_EIC.pdf"%(outdir))
