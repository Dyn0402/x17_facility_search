# L11 (2026-10-27): Pierfrancesco's ogive (his 27 Oct CAD), the light shells with a Mo liner, and the 45° window
# with its tube out of the leptons' way (x17_facility_search lnl/target/SHAPES_GEANT.md §10).  tag|extra args.
# Branch lnl_ogive (from lnl_shapes).  Beam line as photographed (TARGET_OPTIONS §18), as in l10_configs.sh.
#  * the ogive's Ø50 base sits on an Al adapter ring (r 19.05-30, 5 mm) at y = -68...-63 and the DN40 steel line;
#    its mount is out of the arms' view (r < 1.13 d), so the bare-base variant is a diagnostic only;
#  * window end pieces: Be 0.5 mm (full set), Al 0.25, CFRP 0.5, and 16 mm Al straight on the grey flange (diagnostics);
#  * the "wide adapter": a 2 mm Al plate r 10-30 in the window plane, then a 0.5 mm Al tube r 30 cut on the window
#    plane, 60 mm long, the grey flange behind it (moved back so the tube clears it).
BIGP="--big-plastic 75 75 5 --no-ls --sipm-readout 20 0"
ASB=""
LINE_CUP="PVC:15:33:-27:-16,PVC:21:24:-165:-27,Al:20.5:40:-185:-165,SS:17.4:19.05:-620:-185,SS:31:57:-620:-585"
LINE_WIN="Al:10:15:-57:-55,PVC:15:33:-66:-55,PVC:21:24:-204:-66,Al:20.5:40:-224:-204,SS:17.4:19.05:-659:-224,SS:31:57:-659:-624"
LINE_WIN16="Al:10:15:-18:-16,PVC:15:33:-27:-16,PVC:21:24:-165:-27,Al:20.5:40:-185:-165,SS:17.4:19.05:-620:-185,SS:31:57:-620:-585"
LINE_WIDE="PVC:15:33:-72:-61,PVC:21:24:-210:-72,Al:20.5:40:-230:-210,SS:17.4:19.05:-665:-230,SS:31:57:-665:-630"
LINE_OG="Al:19.05:30:-68:-63,SS:17.4:19.05:-620:-68,SS:31:57:-620:-585"
OG="--shape ogive --film Li:1068"
WIN="--shape window --win-ring Ti:0.5:5 --win-glue 0.1 --win-plane 10:45 --film Li:748 --backing Mo:8+Diamond:200"
declare -A CFG
CFG[ogCu200]="$OG --ogive Cu:200 --line $LINE_OG"
CFG[ogBe200mo8]="$OG --ogive Be:200+Mo:8 --line $LINE_OG"
CFG[ogAl200mo8]="$OG --ogive Al:200+Mo:8 --line $LINE_OG"
# 300 um shells (TARGET_OPTIONS §20: Al 200 um buckles at ~1.8 bar; Be 300 and Al 300 recommended)
CFG[ogBe300mo8]="$OG --ogive Be:300+Mo:8 --line $LINE_OG"
CFG[ogAl300mo8]="$OG --ogive Al:300+Mo:8 --line $LINE_OG"
CFG[domeBe200mo8]="--shape dome --film Li:1068 --dome Be:11:200+Mo:8 --dome-rim 4:5 --line $LINE_CUP"
CFG[win45be]="$WIN --win-endpiece Be:0.5:55 --line $LINE_WIN"
# the L9 flat design with a buildable chamber (TARGET_OPTIONS §21: CFRP 0.4 mm × 600 buckles at 0.35 bar): 1 mm, 300 mm long
CFG[flat1mm]="--film Li:1068 --backing Mo:8+Diamond:50 --holder Cu:2 --chamber CFRP:1.0:25 --chamber-len 150 --dump-dist 120"
CFG[win45wide]="$WIN --win-plate Al:2:30 --win-endpiece Al:0.5:60:30 --line $LINE_WIDE"
# diagnostics (X17 only, big plastics)
declare -A DIAG
DIAG[ogCu200bare]="$OG --ogive Cu:200"
DIAG[epAl025]="$WIN --win-endpiece Al:0.25:55 --line $LINE_WIN"
DIAG[epCfrp05]="$WIN --win-endpiece CFRP:0.5:55 --line $LINE_WIN"
DIAG[ep16]="$WIN --win-endpiece Al:0.5:16 --line $LINE_WIN16"
# γ-line response library (26 lines, as L10) and the K x-ray lines (Cu K 8.05/8.9, Mo K 17.5/19.6, Ti K 4.5 keV)
LIB="0.2:1,0.3:1,0.478:1,0.67:1,0.85:1,1.0:1,1.3:1,1.63:1,2.0:1,2.37:1,3.0:1,3.5:1,4.44:1,5.0:1,6.13:1,7.0:1,8.06:1,9.0:1,10.0:1,11.0:1,12.0:1,13.0:1,14.0:1,15.1:1,16.1:1,17.64:1"
XRAY="0.00805:1,0.00891:1,0.0175:1,0.0196:1,0.0045:1"
