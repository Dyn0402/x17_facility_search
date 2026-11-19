"""measured_timing.py -- the MEASURED arm-to-arm time resolution of the as-built MX17 scintillators, for every study here.

n_TOF beam-off cosmics crossing arms A and C (nTof_x17 ntof_cosmics/ac_tof_beamoff.py, 2026-11-19; report
ntof_cosmics/results/ac_tof/report.html): per arm, with the n_TOF readout (1 GS/s, official pulse fit), no beam:
    SiPM walls (4 bars ganged per channel, both ends)  0.52-0.64 ns, reference 0.60
    plastic bars (one PMT)                              0.95 ± 0.04 ns
Under beam the n_TOF pulse fit floors at ~4 ns per arm (the "5 ns" of older ILL scenarios); that is the readout, not
the detector.  A different readout (LNL: V1742 / CFD) is not covered: quote it as a scenario.

    from measured_timing import WALL_SIGMA_T_NS, PLASTIC_SIGMA_T_NS
"""
from __future__ import annotations

import json
import os
from pathlib import Path

TIMING_JSON = Path(os.environ.get('NTOF_X17', Path.home() / 'PycharmProjects' / 'nTof_x17')) \
    / 'ntof_cosmics' / 'results' / 'ac_tof' / 'timing.json'
_FALLBACK = {'wall_sipm': {'reference': 0.60, 'low': 0.519, 'high': 0.638}, 'plastic': {'reference': 0.95}}


def timing() -> dict:
    try:
        return json.loads(TIMING_JSON.read_text())
    except (OSError, ValueError):
        return _FALLBACK            # lxplus or a machine without nTof_x17: the same measured numbers


WALL_SIGMA_T_NS = float(timing()['wall_sipm']['reference'])
WALL_SIGMA_T_RANGE_NS = (float(timing()['wall_sipm']['low']), float(timing()['wall_sipm']['high']))
PLASTIC_SIGMA_T_NS = float(timing()['plastic']['reference'])
