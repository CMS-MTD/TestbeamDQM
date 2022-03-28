#!/bin/bash
if [ "$1" == "" ] || [ "$2" == "" ]; then
echo "## PLOTTER.SH - WATCH SCRIPT FOR DQM PLOTS ##"
echo "Usage"
echo "./plot.sh <time per refresh (min.)> <last n runs>"
echo
echo "Example"
echo "Refresh every 30 minutes and grab last 10 runs on each refresh: ./plot.sh 30 10"
exit
fi
while true
do
if [ $2 -lt 3 ];
then
n=$(ls /eos/uscms/store/group/cmstestbeam/SensorBeam2022/LecroyScope/RecoData/TimingDAQRECO/RecoWithTracks/v3 | tail -n $2 | sed 's/[^0-9]//g' | sed ':a;N;$!ba;s/\n/ /g')
else
n=$(ls /eos/uscms/store/group/cmstestbeam/SensorBeam2022/LecroyScope/RecoData/TimingDAQRECO/RecoWithTracks/v3 | tail -n $2 | sed 2,$(($2-1))d | sed 's/[^0-9]//g' | sed ':a;N;$!ba;s/\n/ /g')
fi
if [ $2 -eq 1 ];
then
python plot.py $n $n $(($1*60))
else
python plot.py $n $(($1*60))
fi
ret=$?
if [ $ret -ne 0 ];
then
exit
fi
done
