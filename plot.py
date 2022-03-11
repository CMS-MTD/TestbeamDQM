import ROOT
import time

class channelInfo:
    def __init__(self,channel,ampCut):
        self.channel = channel
        self.ampCut = ampCut

def main():

    # Should add argument parser here

    # Set if you want to see the TCanvas or make pdf fast
    #setBatch = True
    setBatch = False
    ROOT.gROOT.SetBatch(setBatch)
    
    # Open all root files
    path = "root://cmseos.fnal.gov//store/group/cmstestbeam/SensorBeam2022/LecroyScope/RecoData/TimingDAQRECO/RecoWithTracks/v1/"


    #runNumList = [str(x) for x in range(52507, 52520 + 1)] #lecroy
    runNumList = [str(x) for x in range(52953, 52968 + 1)] #lecroy
    #runNumList = ["34830"] #lecroy
    print("Attempting to processes the following runs:", runNumList)
    files = [path+"run"+runNum+"_info.root" for runNum in runNumList]

    # Open root file and chain them together
    t = ROOT.TChain("pulse")
    for f in files:
        t.Add(f)

    # Define configuration for the runs
    channels = [
        channelInfo("0", 50.0),
        channelInfo("1", 50.0),
        channelInfo("2", 50.0),
        channelInfo("3", 50.0),
        channelInfo("4", 50.0),
        channelInfo("5", 50.0),
        channelInfo("6", 50.0),
        channelInfo("7", 50.0),
    ]
    photek=7
    #beamXRange = "20, 0.0,10.0"
    #beamYRange = "20,5.0,10.0"
    beamXRange = "100,-5.0,2.0"
    beamYRange = "100,-7,0"

            
    # Make canvas
    c = ROOT.TCanvas("c","c",len(channels)*500,1000)
    c.Divide(len(channels), 4)
        
    # Plot amp dist.
    for i,ch in enumerate(channels):
        c.cd(i+1); ROOT.gPad.SetLogy()
        t.Draw("amp[%s]"%ch.channel,"","")
            
    # Plot LGAD position hit eff.
    zLow = 0.0
    zHigh = 1.0
    for i,ch in enumerate(channels):
        c.cd(i+1+len(channels))    
        #t.Draw("amp[{0}]>70:y_dut[0]:x_dut[0]>>h{0}(100,10.0,30.0, 100,10,30)".format(ch),"ntracks==1&&nplanes>10&&npix>1&&fabs(xResidBack)<500&&fabs(yResidBack)<500","profcolz")
        t.Draw("amp[{0}]>{1}:y_dut[7]:x_dut[7]>>h{0}({2}, {3})".format(ch.channel,ch.ampCut,beamXRange,beamYRange),"ntracks==1&&nplanes>=8","profcolz")
        #t.Draw("amp[{0}]<50&&amp[{0}]>15:y_dut[10]:x_dut[10]>>h{0}(50,14.0,23.0, 50,17.0,26.0)".format(ch),"ntracks==1&&nplanes>10&&npix>1&&fabs(xResidBack)<500&&fabs(yResidBack)<500","profcolz")
        h = getattr(ROOT,"h{}".format(ch.channel))
        h.GetZaxis().SetRangeUser(zLow,zHigh)


    #min_y = 10
    #max_y = 11
    ## overlay efficinecy
    #c.cd()
    #hists=[]
    #for i,ch in enumerate(channels):
    #    hname  = "amp[{}]>{}:x_dut[0]".format(ch.channel,ch.ampCut)
    #    yrange = "y_dut[0]>{} && y_dut[0]<{}".format(min_y,max_y)
    #    sel = yrange + track
    #    t.Draw(hname,sel,"prof")
    #    h = getattr(ROOT,"htemp{}".format(ch.channel))
    #    hists.append(h)

    # Plot time resolution 
    for i,ch in enumerate(channels):
        print(i,ch.channel)
        c.cd(i+1+2*len(channels))#; ROOT.gPad.SetLogy()
        #t.Draw("LP2_20[{0}]-LP2_20[{1}]>>htemp{0}(40,-0.1e-9,0.6e-9)".format(ch,photek),"amp[{0}]>20&&LP2_20[{0}]!=0&&amp[{1}]>70&&amp[{1}]<150&&LP2_20[{1}]!=0".format(ch,photek))
        #t.Draw("LP2_20[{0}]-LP2_20[{1}]>>htemp{0}".format(ch,photek),"amp[{0}]>20&&LP2_20[{0}]!=0&&amp[{1}]>70&&amp[{1}]<150&&LP2_20[{1}]!=0".format(ch,photek))
    
        rel_amp = ""
        #if i > 1 and i < 6 :
        #    rel_amp = "&& amp[{0}] > amp[{1}] && amp[{0}] > amp[{2}]".format(ch.channel,int(ch.channel)+1,int(ch.channel)-1) 
        #    print("adding rel amp {}: {}".format(ch.channel,rel_amp))
        track = "&& nplanes >= 8 && ntracks==1 "
        t.Draw("LP2_25[{0}]-LP2_30[{1}]>>htemp{0}(50,-1.5e-9,0.e-9)".format(ch.channel,photek),"amp[{0}]>{2}&&LP2_20[{0}]!=0&&LP2_20[{1}]!=0 {2} {3}".format(ch.channel,photek,ch.ampCut,rel_amp,track))
        #t.Draw("LP2_25[{0}]-LP2_30[{1}]>>htemp{0}(50,-10.0e-9,0.0e-9)".format(ch.channel,photek),"amp[{0}]>{2}&&LP2_20[{0}]!=0&&amp[{1}]>70&&amp[{1}]<350&&LP2_20[{1}]!=0 {2} {3}".format(ch.channel,photek,ch.ampCut,rel_amp,track))
        h = getattr(ROOT,"htemp{}".format(ch.channel))
        ROOT.gStyle.SetOptFit(1)
        fit = ROOT.TF1("fit%s"%ch.channel, "gaus")    
        fit.SetLineColor(ROOT.kRed)
        fit.Draw("same")    
        h.Fit(fit)
        fit.Draw("same")    

    # Plot number of simultanous "hits"
    countString = ""
    for i,ch in enumerate(channels):
        string = "amp[{0}]>{1}".format(ch.channel,ch.ampCut)
        if countString:
            countString += "+"+string
        else:
            countString = string
    i=0
    c.cd(i+1+3*len(channels))
    t.Draw("({0})>>nHits({1},0.0,{1})".format(countString,len(channels)),"")
    
    # Plot number of nPlanes
    i=1
    c.cd(i+1+3*len(channels))
    t.Draw("nplanes>>nPlanes(20,0.0,20)","")

    # Plot number of nPix
    i=2
    c.cd(i+1+3*len(channels))
    t.Draw("npix>>nPix(20,0.0,20)","")

    # Plot residBack
    #i=3
    #c.cd(i+1+3*len(channels))
    #t.Draw("fabs(yResidBack):fabs(xResidBack)","")

    # Plot beam position: x and Y
    i+=1
    c.cd(i+1+3*len(channels))
    t.Draw("y_dut[0]:x_dut[0]>>hbeam({0}, {1})".format(beamXRange,beamYRange),"ntracks==1&&nplanes>0","colz")

    # Plot beam position: x
    i+=1
    c.cd(i+1+3*len(channels))
    t.Draw("x_dut[0]>>hbeamX({0})".format(beamXRange),"ntracks==1&&nplanes>0")
    hbeamX = getattr(ROOT,"hbeamX")
    fitBeamX = ROOT.TF1("fitBeamX", "gaus")    
    fitBeamX.SetLineColor(ROOT.kRed)
    fitBeamX.Draw("same")    
    hbeamX.Fit(fitBeamX)
    fitBeamX.Draw("same")    

    # Plot beam position: y
    i+=1
    c.cd(i+1+3*len(channels))
    t.Draw("y_dut[0]>>hbeamY({0})".format(beamYRange),"ntracks==1&&nplanes>0")
    hbeamY = getattr(ROOT,"hbeamY")
    fitBeamY = ROOT.TF1("fitBeamY", "gaus")    
    fitBeamY.SetLineColor(ROOT.kRed)
    fitBeamY.Draw("same")    
    hbeamY.Fit(fitBeamY)
    fitBeamY.Draw("same")    

    # Plot baseline_RMS
    i+=1
    c.cd(i+1+3*len(channels)); ROOT.gPad.SetLogy()
    t.Draw("baseline_RMS","")

    # Save canvas as a pdf
    c.Print("dqm.pdf")

    # Keep code open forever if you want to see the TCanvas
    print("Finished making all histograms")
    if not setBatch:
        print("Safe to close")
        time.sleep(10**9)

if __name__ == '__main__':
    main()

