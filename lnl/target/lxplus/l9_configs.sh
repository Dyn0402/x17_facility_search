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
