# L10 (2026-10-27): Pierfrancesco's Cu hemisphere and the flat diamond window in Geant4
# (x17_facility_search lnl/target/SHAPES_GEANT.md).  tag|extra args.  Branch lnl_shapes.
# Beam line as photographed (TARGET_OPTIONS §18, opt_beamline.py): grey (PVC assumed) flange + tube,
# KF clamp, DN40 steel tube, DN63 flanges.  The window sits on a 55 mm Al end piece, so the line moves
# back 39 mm (the photo's cup is 16 mm deep); an Al reducer r 10-15 closes the gap to the grey flange.
BIGP="--big-plastic 75 75 5 --no-ls --sipm-readout 20 0"
ASB=""
LINE_CUP="PVC:15:33:-27:-16,PVC:21:24:-165:-27,Al:20.5:40:-185:-165,SS:17.4:19.05:-620:-185,SS:31:57:-620:-585"
LINE_WIN="Al:10:15:-57:-55,PVC:15:33:-66:-55,PVC:21:24:-204:-66,Al:20.5:40:-224:-204,SS:17.4:19.05:-659:-224,SS:31:57:-659:-624"
LINE_GLUED="SS:17.4:19.05:-620:-17.5,SS:31:57:-620:-585"
DOME="--shape dome --film Li:1068"
WIN="--shape window --win-ring Ti:0.5:5 --win-glue 0.1 --win-endpiece Al:0.5:55 --line $LINE_WIN"
declare -A CFG
CFG[dome200]="$DOME --dome Cu:11:200 --dome-rim 4:5 --line $LINE_CUP"
CFG[dome300]="$DOME --dome Cu:11:300 --dome-rim 4:5 --line $LINE_CUP"
CFG[dome200glued]="$DOME --dome Cu:17.5:200 --line $LINE_GLUED"
CFG[win45d200]="$WIN --win-plane 10:45 --film Li:748 --backing Mo:8+Diamond:200"
CFG[win45d300]="$WIN --win-plane 10:45 --film Li:748 --backing Mo:8+Diamond:300"
CFG[win0d200]="$WIN --win-plane 10:0 --film Li:1068 --backing Mo:8+Diamond:200"
CFG[win0d300]="$WIN --win-plane 10:0 --film Li:1068 --backing Mo:8+Diamond:300"
# γ-line response library: one isotropic γ per event from the beam spot, 26 lines (MeV), equal mix
LIB="0.2:1,0.3:1,0.478:1,0.67:1,0.85:1,1.0:1,1.3:1,1.63:1,2.0:1,2.37:1,3.0:1,3.5:1,4.44:1,5.0:1,6.13:1,7.0:1,8.06:1,9.0:1,10.0:1,11.0:1,12.0:1,13.0:1,14.0:1,15.1:1,16.1:1,17.64:1"
