#!/bin/bash
# PIXE thick-target K x-ray yields (x17_facility_search lnl/target/CU_LINER.md): TestEm5, emstandard_opt4
export G4FORCE_RUN_MANAGER_TYPE=Serial
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh >/dev/null 2>&1
P=/afs/cern.ch/work/d/dneff/pixe_check
cd $_CONDOR_SCRATCH_DIR 2>/dev/null || cd /tmp
for xs in Empirical ECPSSR_FormFactor ECPSSR_ANSTO; do
 for mat in G4_Cu G4_Mo G4_Ti; do
  for e in 0.30 0.45 0.60 0.75 0.87 1.00 1.10; do
   tag=${mat}_${e/./p}_${xs}
   cat > m.mac <<EOM
/control/verbose 0
/run/numberOfThreads 1
/run/verbose 0
/testem/det/setAbsMat $mat
/testem/det/setAbsThick 60 um
/testem/det/setAbsYZ 1 mm
/testem/phys/addPhysics emstandard_opt4
/run/setCut 1 um
/process/em/pixe true
/process/em/augerCascade false
/process/em/deexcitationIgnoreCut true
/process/em/pixeXSmodel $xs
/run/initialize
/testem/gun/setDefault
/gun/particle proton
/gun/energy $e MeV
/analysis/setFileName $tag
/analysis/setDefaultFileType csv
/analysis/h1/set 55 3000 0 30 keV
/run/printProgress 0
/run/beamOn 200000
EOM
   $P/build/TestEm5 m.mac > $tag.log 2>&1
   cp ${tag}*h1_55*.csv $P/out/ 2>/dev/null || cp ${tag}*.csv $P/out/ 2>/dev/null
   rm -f ${tag}*.csv
   tail -3 $tag.log > $P/out/$tag.tail; rm -f $tag.log
  done
 done
done
