# L14 (2026-11-11): the one-piece Al end cap with a flat face at 45° (x17_facility_search lnl/target/TARGET_REVIEW.md
# §6.1), and the Al ogive with Cu plated over the whole inside at 0.4 mm.  tag|extra args.
# Binary: bin/mx17_full_sim_culiner_812488b (branch lnl_culiner; it has the L10 window options).
#  * the cap is the L10 window geometry with the diamond replaced by Al and the Mo by Cu, no glue, and the Ti rings
#    shrunk to a 10 µm Al skin 0.5 mm wide (the code needs a ring; this makes the face one piece with the 0.5 mm
#    end-piece wall: the stack spans the bore + the wall);
#  * the face is 45° to the beam, so 8.5 µm of Cu along the normal is 12 µm along the beam, and Li:748 µg/cm²
#    (14 µm along the normal) is 20 µm along the beam, as in L10.  Thinner Li is a yield change (analysis), not a
#    geometry change;
#  * beam line as photographed, as in l10_configs.sh (LINE_WIN).
BIGP="--big-plastic 75 75 5 --no-ls --sipm-readout 20 0"
ASB=""
LINE_WIN="Al:10:15:-57:-55,PVC:15:33:-66:-55,PVC:21:24:-204:-66,Al:20.5:40:-224:-204,SS:17.4:19.05:-659:-224,SS:31:57:-659:-624"
LINE_OG="Al:19.05:30:-68:-63,SS:17.4:19.05:-620:-68,SS:31:57:-620:-585"
CAP="--shape window --win-ring Al:0.01:0.5 --win-glue 0 --win-plane 10:45 --film Li:748 --line $LINE_WIN"
declare -A CFG
CFG[cap45al400cu]="$CAP --backing Cu:8.5+Al:400 --win-endpiece Al:0.5:55"
CFG[cap45al500cu]="$CAP --backing Cu:8.5+Al:500 --win-endpiece Al:0.5:55"
# lever: a 0.3 mm end-piece wall (the ring width follows the wall)
CFG[cap45al400cu_ep03]="--shape window --win-ring Al:0.01:0.3 --win-glue 0 --win-plane 10:45 --film Li:748 --line $LINE_WIN --backing Cu:8.5+Al:400 --win-endpiece Al:0.3:55"
# the Al ogive with Cu over the whole inside (plated), 0.4 mm wall (L12 ran 0.3 mm only)
CFG[ogAl400cu12]="--shape ogive --film Li:1068 --line $LINE_OG --ogive Al:400+Cu:12"
XRAY="0.00805:1,0.00891:1,0.0175:1,0.0196:1,0.0045:1"
