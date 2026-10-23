# L9 target-option configs: tag|extra args (big plastics on every one)
BIGP="--big-plastic 75 75 5 --no-ls --sipm-readout 20 0"
declare -A CFG
CFG[al10_y120]="--target-y 120"
CFG[li20_dia1]="--film Li:1068 --backing Diamond:1000 --holder Cu:3"
CFG[li20_dia1_y120]="--film Li:1068 --backing Diamond:1000 --holder Cu:3 --target-y 120"
CFG[li20_mch_y120]="--film Li:1068 --backing Diamond:300+Water:300+Diamond:400 --holder Cu:5 --target-y 120"
CFG[dia50]="--backing Diamond:50 --holder Cu:2"
CFG[li20_dia50]="--film Li:1068 --backing Diamond:50 --holder Cu:2"
CFG[li20_ta_dia300]="--film Li:1068 --backing Ta:10+Diamond:300 --holder Cu:3"
CFG[cublock_y120]="--backing Cu:2000+Water:1000+Cu:1000 --holder none --target-y 120"
# second round (2026-10-22): can geometry rescue the 1 mm diamond? (TARGET_OPTIONS.md §7.2)
CFG2_li20_dia1_y180="--film Li:1068 --backing Diamond:1000 --holder Cu:3 --target-y 180"
CFG2_li20_dia1_r8="--film Li:1068 --backing Diamond:1000 --holder Cu:3 --holder-r 6:8"
CFG2_li20_dia1_r8_y120="--film Li:1068 --backing Diamond:1000 --holder Cu:3 --holder-r 6:8 --target-y 120"
# third round: the thin LNL design, a beam-stopping metal layer on a 50 µm diamond membrane
CFG2_li20_mo8_dia50="--film Li:1068 --backing Mo:8+Diamond:50 --holder Cu:2"
CFG2_li20_ta8_dia50="--film Li:1068 --backing Ta:8+Diamond:50 --holder Cu:2"
# fourth round (2026-10-23): Pierfrancesco asks for a copper substrate (easier to machine) instead of diamond
CFG2_li20_cu25="--film Li:1068 --backing Cu:25 --holder Cu:2"
CFG2_li20_cu100="--film Li:1068 --backing Cu:100 --holder Cu:2"
CFG2_li20_cu300="--film Li:1068 --backing Cu:300 --holder Cu:3"
CFG2_li20_cu1000="--film Li:1068 --backing Cu:1000 --holder Cu:3"
