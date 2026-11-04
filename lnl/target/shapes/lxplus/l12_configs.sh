# L12 (2026-11-04): the Al ogive with a Cu liner (x17_facility_search lnl/target/CU_LINER.md).  tag|extra args.
# Branch lnl_culiner (from lnl_ogive): --ogive-liner-r R puts the liner (and the film) only where the shell's inner
# radius is <= R (tip region), --li-mask-r R puts the vertices only where the beam lands at r <= R (Li evaporated
# through a mask).  Same beam line, samples and detectors as L11 (l11_configs.sh); references from L11: ogCu200,
# ogAl300mo8.
BIGP="--big-plastic 75 75 5 --no-ls --sipm-readout 20 0"
ASB=""
LINE_OG="Al:19.05:30:-68:-63,SS:17.4:19.05:-620:-68,SS:31:57:-620:-585"
OG="--shape ogive --film Li:1068 --line $LINE_OG"
declare -A CFG
# Cu over the whole inside (an electroplated shell), no mask: the simplest part
CFG[ogAl300cu12]="$OG --ogive Al:300+Cu:12"
# the proposed design: Cu only over the tip region (r <= 8 mm = 4σ of a σ 2 mm spot), Li masked to r <= 4 mm
CFG[ogAl300cu12r8m4]="$OG --ogive Al:300+Cu:12 --ogive-liner-r 8 --li-mask-r 4"
# x-ray levers: a thicker Al wall, a thicker Cu liner (self-absorption)
CFG[ogAl400cu12r8m4]="$OG --ogive Al:400+Cu:12 --ogive-liner-r 8 --li-mask-r 4"
CFG[ogAl300cu30r8m4]="$OG --ogive Al:300+Cu:30 --ogive-liner-r 8 --li-mask-r 4"
# comparator: a Ti stop (its 4.5 keV K x-rays do not escape; Ti takes up H)
CFG[ogAl300ti15r8m4]="$OG --ogive Al:300+Ti:15 --ogive-liner-r 8 --li-mask-r 4"
# the L11 Al + Mo ogive, only for its x-ray library (L11 ran Be + Mo only)
declare -A XCFG
XCFG[ogAl300mo8]="$OG --ogive Al:300+Mo:8"
LIB="0.2:1,0.3:1,0.478:1,0.67:1,0.85:1,1.0:1,1.3:1,1.63:1,2.0:1,2.37:1,3.0:1,3.5:1,4.44:1,5.0:1,6.13:1,7.0:1,8.06:1,9.0:1,10.0:1,11.0:1,12.0:1,13.0:1,14.0:1,15.1:1,16.1:1,17.64:1"
XRAY="0.00805:1,0.00891:1,0.0175:1,0.0196:1,0.0045:1"
