#!/bin/bash
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh >/dev/null
python3 /afs/cern.ch/work/d/dneff/git/x17_trig/trig_reduce.py "$1" -o "$2"
