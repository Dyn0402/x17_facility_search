#!/bin/bash
# one TestEm5 PIXE run: mat E(MeV) xsmodel nprot seed tag  (single-threaded)
export G4FORCE_RUN_MANAGER_TYPE=Serial
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh >/dev/null 2>&1
P=/afs/cern.ch/work/d/dneff/pixe_check
cd $_CONDOR_SCRATCH_DIR
cat > m.mac <<EOM
/control/verbose 0
/run/verbose 0
/random/setSeeds $5 $(($5+7))
/testem/det/setAbsMat $1
/testem/det/setAbsThick 60 um
/testem/det/setAbsYZ 1 mm
/testem/phys/addPhysics emstandard_opt4
/run/setCut 1 um
/process/em/pixe true
/process/em/augerCascade false
/process/em/deexcitationIgnoreCut true
/process/em/pixeXSmodel $3
/run/initialize
/testem/gun/setDefault
/gun/particle proton
/gun/energy $2 MeV
/analysis/setFileName $6
/analysis/setDefaultFileType csv
/analysis/h1/set 55 3000 0 30 keV
/run/printProgress 0
/run/beamOn $4
EOM
$P/build/TestEm5 m.mac > run.log 2>&1
cp $6*h55.csv $P/outmo/
rm -f *.csv run.log m.mac
