import ROOT

class channelInfo:
    def __init__(self,channel,ampCut, highAmp):
        self.channel = channel
        self.ampCut = ampCut
        self.highAmp = highAmp 

def main():

    # Should add argument parser here

    # Set if you want to see the TCanvas or make pdf fast
    setBatch = True
    #setBatch = False
    ROOT.gROOT.SetBatch(setBatch)
    
    # Open all root files
    path = "root://cmseos.fnal.gov//store/group/cmstestbeam/2021_CMSTiming_ETL/LecroyScope/RecoData/TimingDAQRECO/RecoWithTracks/v2/"

    #271
    runNumList = [str(x) for x in range(34615, 34625 + 1)] #lecroy
    #runNumList = ["34615"] #lecroy

    print("Attempting to processes the following runs:", runNumList)
    files = [path+"run_scope"+runNum+"_converted.root" for runNum in runNumList]

    # Open root file and chain them together
    t = ROOT.TChain("pulse")
    for f in files:
        t.Add(f)

    # Define configuration for the runs
    channels = [
        channelInfo("1", 25.0, 90.0),
        channelInfo("2", 25.0, 90.0),
        channelInfo("3", 25.0, 90.0),
        channelInfo("4", 25.0, 90.0),
        #channelInfo("5", 30.0),
        #channelInfo("6", 30.0),
        channelInfo("7", 100.0, 100.0),
    ]
    photek=7
    beamXRange = "100,-7.0,-3.5"
    #beamXRange = "100,-9.0,-5"
    beamYRange = "100,9.0,11.5"

    #helpful defs
    goodtrack = "npix > 0 && ntracks==1 && nplanes > 10 && chi2<30"
            
    # Make canvas
    c = ROOT.TCanvas("c","c",900,800)
        
    # Plot amplitude sum 
    c.cd()
    dist="amp[1]+amp[2]+amp[3]+amp[4]"
    pos="x_dut[0]>-6.1&&x_dut[0]<5.3&&y_dut[0]>10.0&&y_dut[0]<10.8"
    hits="amp[1]>25&&amp[2]>25&&amp[3]>25&&amp[4]>25"
    sel=goodtrack + "&&" + pos + "&&" + hits
    t.Draw(dist+">>h(100,0,1000)",sel)

    h = getattr(ROOT,"h")
    h.GetXaxis().SetTitle("amplitude sum [mV]")
    ROOT.gStyle.SetOptFit(1)
    fit = ROOT.TF1("fit", "landau")    
    fit.SetLineColor(ROOT.kRed)
    fit.Draw("same")    
    h.Fit(fit)
    fit.Draw("same")    
    
    c.Print("allstrips_ampsum.png")

    # Plot amplitude comparison 
    c.cd()
    dist="amp[1]:amp[2]"
    sel=goodtrack+"&&amp[2]>20&&amp[1]>20&&x_dut[0]>-6.1&&x_dut[0]<5.3&&y_dut[0]>10.0&&y_dut[0]<10.8"
    t.Draw(dist+">>h(100,0,200,100,0,200)",sel,"COLZ")
    c.Print("amplidude_comparison.png")

    # Plot number of hits
    c.cd()
    dist="(amp[1]>{0})+(amp[2]>{0})+(amp[3]>{0})+(amp[4]>{0})".format(25)
    sel=goodtrack+"&&x_dut[0]>-6.1&&x_dut[0]<5.3&&y_dut[0]>10.0&&y_dut[0]<10.8"
    t.Draw(dist,sel)
    c.Print("allstrips_nhits.png")

    # wider x range
    sel=goodtrack+"&&x_dut[0]>-6.5&&x_dut[0]<-5&&y_dut[0]>10.0&&y_dut[0]<10.8&&amp[7]>100"
    t.Draw(dist+":x_dut[0]>>h(100,-6.5,-5,7,-0.5,6.5",sel,"COLZ")
    h = getattr(ROOT,"h")
    h.GetYaxis().SetTitle("n_{hits}, 40 mV")
    h.GetXaxis().SetTitle("x [mm]")
    c.Print("allstrips_nhits_vx.png")

    # Plot amp dist.
    c.SetLogy(1)
    for i,ch in enumerate(channels):
        c.cd() 
        t.Draw("amp[%s]"%ch.channel,"","")
        c.Print("channel_{}_amplitude.png".format(ch.channel))
            
    c.SetLogy(0)
    # Plot LGAD position hit eff.
    zLow = 0.0
    zHigh = 1.0
    for i,ch in enumerate(channels):
        c.cd()    

        t.Draw("amp[{0}]>{1}:y_dut[0]:x_dut[0]>>h{0}({2}, {3})".format(ch.channel,ch.ampCut,beamXRange,beamYRange),goodtrack,"profcolz")
        h = getattr(ROOT,"h{}".format(ch.channel))
        h.GetZaxis().SetRangeUser(zLow,zHigh)
        c.Print("channel_{}_hiteffLow.png".format(ch.channel))

        t.Draw("amp[{0}]>{1}:y_dut[0]:x_dut[0]>>h{0}({2}, {3})".format(ch.channel,ch.highAmp,beamXRange,beamYRange),goodtrack,"profcolz")
        h = getattr(ROOT,"h{}".format(ch.channel))
        h.GetZaxis().SetRangeUser(zLow,zHigh)
        c.Print("channel_{}_hiteffHigh.png".format(ch.channel))

    # Plot LGAD position mean amp versus x and y.
    zLow = 0.0
    zHigh = 300.0
    for i,ch in enumerate(channels):
        c.cd()    

        t.Draw("amp[{0}]:y_dut[0]:x_dut[0]>>h{0}({2}, {3})".format(ch.channel,ch.ampCut,beamXRange,beamYRange),goodtrack,"profcolz")
        h = getattr(ROOT,"h{}".format(ch.channel))
        h.GetZaxis().SetRangeUser(zLow,zHigh)
        c.Print("channel_{}_meanamp_xy.png".format(ch.channel))

    # Plot LGAD position hit eff.
    yLow = 9.8
    yHigh = 10.8 
    hists=[]
    for i,ch in enumerate(channels):

        c.cd()    

        hname="mean_amp_{}".format(ch.channel)
        hist = ROOT.TH2F(hname,";x [mm];amp [mV]", 100,-6.5,-5, 100,0,300) 
        dist="amp[{}]:x_dut[0]".format(ch.channel)
        sel="y_dut[0]>{}&&y_dut[0]<{}&&{}".format(yLow,yHigh,goodtrack)
        t.Project(hname,dist,sel,"colz")
    
        prof = hist.ProfileX("{}_prof".format(hname))
        prof.SetLineColor(i+1)
        prof.Draw()
        h = getattr(ROOT,hname)
        c.Print("channel_{}_meanamp_x.png".format(ch.channel))
        hists.append(prof)

    c.cd()
    ROOT.gStyle.SetOptStat(0)
    for i,hist in enumerate(hists): 
        if i==7: continue 
        elif i==0: 
            hist.Draw("hist")
            hist.SetMaximum(150)
            hist.SetMinimum(0)
            hist.GetYaxis().SetTitle("mean amp [mV]")
        else: hist.Draw("histsame")
    c.Print("allchannels_meanamp_x.png")
    ROOT.gStyle.SetOptStat(1)

    # Plot time resolution 
    for i,ch in enumerate(channels):
        print(i,ch.channel)
        c.cd()#; ROOT.gPad.SetLogy()
        #t.Draw("LP2_20[{0}]-LP2_20[{1}]>>htemp{0}(40,-0.1e-9,0.6e-9)".format(ch,photek),"amp[{0}]>20&&LP2_20[{0}]!=0&&amp[{1}]>70&&amp[{1}]<150&&LP2_20[{1}]!=0".format(ch,photek))
        #t.Draw("LP2_20[{0}]-LP2_20[{1}]>>htemp{0}".format(ch,photek),"amp[{0}]>20&&LP2_20[{0}]!=0&&amp[{1}]>70&&amp[{1}]<150&&LP2_20[{1}]!=0".format(ch,photek))
    
        rel_amp = ""
        #if i > 1 and i < 6 :     
        #    rel_amp = "&& amp[{0}] > amp[{1}] && amp[{0}] > amp[{2}]".format(ch.channel,int(ch.channel)+1,int(ch.channel)-1) 
        #    print("adding rel amp {}: {}".format(ch.channel,rel_amp))
        t.Draw("LP2_20[{0}]-LP2_20[{1}]>>htemp{0}(50,-11.0e-9,-10.0e-9)".format(ch.channel,photek),"amp[{0}]>{2}&&LP2_20[{0}]!=0&&amp[{1}]>70&&amp[{1}]<350&&LP2_20[{1}]!=0&&{3} {4}".format(ch.channel,photek,ch.highAmp,goodtrack,rel_amp))
        h = getattr(ROOT,"htemp{}".format(ch.channel))
        ROOT.gStyle.SetOptFit(1)
        fit = ROOT.TF1("fit%s"%ch.channel, "gaus")    
        fit.SetLineColor(ROOT.kRed)
        fit.Draw("same")    
        h.Fit(fit)
        fit.Draw("same")    

        c.Print("channel_{}_timeres.png".format(ch.channel))

    # Plot number of simultanous "hits"
    countString = ""
    for i,ch in enumerate(channels):
        string = "amp[{0}]>{1}".format(ch.channel,ch.ampCut)
        if countString:
            countString += "+"+string
        else:
            countString = string
    i=0
    c.cd()
    t.Draw("({0})>>nHits({1},0.0,{1})".format(countString,len(channels)),"")
    c.Print("n_simultaneous_hits.png")
    
    # Plot number of nPlanes
    c.cd()
    t.Draw("nplanes>>nPlanes(20,0.0,20)","")

    # Plot number of nPix
    c.cd()
    t.Draw("npix>>nPix(20,0.0,20)","")

    # Plot residBack
    c.cd()
    t.Draw("fabs(yResidBack):fabs(xResidBack)","")

    # Plot beam position: x
    c.cd()
    t.Draw("x_dut[0]>>hbeamX({0})".format(beamXRange),"ntracks==1&&nplanes>10")
    hbeamX = getattr(ROOT,"hbeamX")
    fitBeamX = ROOT.TF1("fitBeamX", "gaus")    
    fitBeamX.SetLineColor(ROOT.kRed)
    fitBeamX.Draw("same")    
    hbeamX.Fit(fitBeamX)
    fitBeamX.Draw("same")    
    c.Print("beam_position_x.png")

    # Plot beam position: y
    c.cd()
    t.Draw("y_dut[0]>>hbeamY({0})".format(beamYRange),"ntracks==1&&nplanes>10")
    hbeamY = getattr(ROOT,"hbeamY")
    fitBeamY = ROOT.TF1("fitBeamY", "gaus")    
    fitBeamY.SetLineColor(ROOT.kRed)
    fitBeamY.Draw("same")    
    hbeamY.Fit(fitBeamY)
    fitBeamY.Draw("same")    
    c.Print("beam_position_y.png")

    # Plot beam position: x and Y
    c.cd()
    t.Draw("y_dut[0]:x_dut[0]>>hbeam({0}, {1})".format(beamXRange,beamYRange),"ntracks==1&&nplanes>10","colz")
    c.Print("beam_position_xy.png")


    # Keep code open forever if you want to see the TCanvas
    print("Finished making all histograms")

if __name__ == '__main__':
    main()

