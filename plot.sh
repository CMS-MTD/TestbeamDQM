#!/bin/bash
while true
do
n=$(ls /eos/uscms/store/group/cmstestbeam/SensorBeam2022/LecroyScope/RecoData/TimingDAQRECO/RecoWithTracks/v3 | tail -n $2 | sed 2,$(($2-1))d | sed 's/[^0-9]//g' | sed ':a;N;$!ba;s/\n/ /g')
python plot.py $n $(($1*60))
sleep 2
done
