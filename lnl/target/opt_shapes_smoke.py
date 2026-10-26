"""opt_shapes_smoke.py -- run the opt_shapes geometries and plate_stress() on synthetic legs (no Geant4 L9 table needed).

    ~/PycharmProjects/nTof_x17/.venv/bin/python lnl/target/opt_shapes_smoke.py

Added 2026-10-26 (AUDIT_2026-10-26.md §A3); the real trace is opt_shapes.main() on the L9 legs."""
import sys, numpy as np
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
import opt_shapes as S
rng = np.random.default_rng(1)
n = 20000
th = np.radians(rng.uniform(45, 135, n)); ph = rng.uniform(0, 2*np.pi, n)
u = np.c_[np.sin(th)*np.cos(ph), np.cos(th), np.sin(th)*np.sin(ph)]
V = np.c_[rng.normal(0, 2, n), np.zeros(n), rng.normal(0, 2, n)]
def med(geo, vf, u=u):
    p = vf(V); x = S.xx0(geo, p, u); return 100*np.median(x), 100*np.percentile(x, 84), 100*(x > 1).mean()
print('design flat        : med %.3f  p84 %.3f  >1%%: %.1f' % med(S.flat([('Mo', 8), ('Dia', 50)], 2), S.on_film))
print('dome R17.5 Cu200   : med %.2f  p84 %.2f  >1%%: %.1f' % med(S.dome(17.5), S.on_dome(17.5)))
print('dome R11 Cu300 rim : med %.2f  p84 %.2f  >1%%: %.1f' % med(S.dome(11.0, t_um=300, rim=(3, 3)), S.on_dome(11.0)))
print('dome R11 Cu200 rim : med %.2f  p84 %.2f  >1%%: %.1f' % med(S.dome(11.0, t_um=200, rim=(3, 3)), S.on_dome(11.0)))
for d in (50, 300, 500):
    g, nn = S.window(layers=(('Mo', 8), ('Dia', d)), tilt_deg=45, tube='Al', tube_t=0.5)
    print('window 45 dia%3d Al : med %.3f  p84 %.3f  >1%%: %.1f' % ((d,) + med(g, S.on_plane(nn))))
g, nn = S.window(layers=(('Mo', 8), ('Dia', 200)), R=10.0, tilt_deg=45, ring_mm=0.5, ring_w=5.0, ring_mat='Ti', tube='Al', tube_t=0.5)
print('window R10 Ti rings: med %.3f  p84 %.3f  >1%%: %.1f' % med(g, S.on_plane(nn)))
g, nn = S.window(layers=(('Mo', 8), ('Dia', 200)), R=10.0, tilt_deg=45, tube='Al', tube_t=0.5)
print('window R10 Cu rings: med %.3f  p84 %.3f  >1%%: %.1f' % med(g, S.on_plane(nn)))
# the tangent check: a leg exactly at 90 deg from the apex of the R17.5 Cu200 dome
u90 = np.array([[1.0, 0, 0]]); p = S.on_dome(17.5)(np.zeros((1, 3)))
print('90-deg leg, dome R17.5 t200: %.1f %% X0 (expect ~18)' % (100*S.xx0(S.dome(17.5), p, u90)[0]))
for t in (50, 100, 200, 300, 500):
    print('plate_stress diamond %3d um r 17.5: edge %4.0f centre %4.0f y %.3f mm | membrane-only %4.0f' % ((t,) + S.plate_stress(t, 17.5) + (S.membrane(t, 17.5)[0],)))
