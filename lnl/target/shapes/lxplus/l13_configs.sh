# L13 (2026-11-10): high-statistics AS-BUILT background templates for the floating-shape fit (L11/L12 had only
# ~2,200-3,500 two-arm rows per IPC sample and 18 selected EPC events).  Same geometry strings as L11 (ogCu200) and
# L12 (ogAl300cu12r8m4), copied verbatim from l11_configs.sh / l12_configs.sh; detector as built only (ASB="").
# Binary: bin/mx17_full_sim_culiner_812488b (branch lnl_culiner, which also has the L11 ogive options).
ASB=""
LINE_OG="Al:19.05:30:-68:-63,SS:17.4:19.05:-620:-68,SS:31:57:-620:-585"
declare -A CFG
# L11: OG="--shape ogive --film Li:1068";  CFG[ogCu200]="$OG --ogive Cu:200 --line $LINE_OG"
CFG[ogCu200]="--shape ogive --film Li:1068 --ogive Cu:200 --line $LINE_OG"
# L12: OG="--shape ogive --film Li:1068 --line $LINE_OG";  CFG[...]="$OG --ogive Al:300+Cu:12 --ogive-liner-r 8 --li-mask-r 4"
CFG[ogAl300cu12r8m4]="--shape ogive --film Li:1068 --line $LINE_OG --ogive Al:300+Cu:12 --ogive-liner-r 8 --li-mask-r 4"
