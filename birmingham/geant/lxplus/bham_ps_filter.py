#!/usr/bin/env python3
"""bham_ps_filter.py <gun.csv> <out.csv>: keep the exit-plane records inside the experimental room footprint that interacted (TARGET_GEANT.md §3)."""
import sys, numpy as np
# keep phase-space rows inside the experimental room's footprint (|x| < 2500, -1700 < z < 2500) and collided
src, dst = sys.argv[1], sys.argv[2]
n = k = 0
with open(src) as f, open(dst, 'w') as g:
    for line in f:
        if not line[0].isdigit():
            g.write(line); continue
        p = line.split(',')
        n += 1
        x, z, unc = float(p[2]), float(p[4]), int(p[9])
        if abs(x) < 2500 and -1700 < z < 2500 and not unc:
            g.write(line); k += 1
print(dst, n, k)
