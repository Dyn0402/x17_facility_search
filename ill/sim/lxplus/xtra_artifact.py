# Follow-up diagnostics for the slide summary (FEASIBILITY_SIM.md section 8): cosmic
# arm pairs / dt / chord angle / line-to-centre distance, ceiling-floor veto coverage,
# X17 segment collinearity + muon resolution toy, vertex-y acceptance and lepton
# cos(theta) per cell.  Run on lxplus in .../x17_ill/analysis (LCG_106) ->
# xtra_artifact.json (copied to ill/sim/analysis_v3/).
import json, math, numpy as np, sim_feasibility as SF
from pathlib import Path
E = Path("/eos/experiment/ntof/data/x17/ill")
out = {}
def ang(a, b):
    c = (a*b).sum(-1)/np.linalg.norm(a,axis=-1)/np.linalg.norm(b,axis=-1)
    return np.degrees(np.arccos(np.clip(c,-1,1)))
# ---- cosmics
k1 = SF.load_table(E/"contracts", "K1", "G5")
live = k1["N_sim"]*SF.COSMIC_S_PER_MU
m, th, es, dt, pe = SF.two_arm_events(k1, "sipm2", 12.0)
ok = SF.arm_ok(k1, "sipm2"); Ea = np.where(ok, SF.arm_E(k1), -1.0)
o = np.argsort(-Ea,1); r=np.arange(len(Ea)); a1,a2=o[:,0],o[:,1]
g = k1["gpos"]
for a in range(4):
    p = g[:,a][np.isfinite(g[:,a,0])]
    print("arm",a,"mean gpos",p.mean(0).round(1), "n", len(p))
A = g[r,a1][m]; B = g[r,a2][m]; w = pe[m]
pairs = {}
for i,j in zip(a1[m],a2[m]):
    k = tuple(sorted((int(i),int(j)))); pairs[k]=pairs.get(k,0)+1
print("arm pairs", pairs)
out["cos_rate_Hz"] = float(w.sum()/live)
out["cos_armpairs"] = {f"{k[0]}{k[1]}": v for k,v in pairs.items()}
adt = np.abs(dt[m])
out["cos_dt_hist"] = np.histogram(adt, np.arange(0,6.01,0.25), weights=w)[0].tolist()
out["cos_theta_hist"] = np.histogram(th[m], SF.BINS, weights=w)[0].tolist()
d = B - A; d /= np.linalg.norm(d,axis=1)[:,None]
# pointing mismatch: angle between muon line and the radial chord from the cell centre
psiA = ang(d, A); psiA = np.minimum(psiA, 180-psiA)
psiB = ang(d, B); psiB = np.minimum(psiB, 180-psiB)
out["cos_psi_min_pct"] = np.percentile(np.minimum(psiA,psiB),[10,50,90]).tolist()
# distance of the muon line from the cell centre
dca = np.linalg.norm(np.cross(A, d),axis=1)
out["cos_dca_pct"] = np.percentile(dca,[10,50,90]).tolist()
out["cos_dca_hist"] = np.histogram(dca, np.arange(0,301,10), weights=w)[0].tolist()
# floor / ceiling veto: z is vertical. extrapolate muon line to planes z = +-H
for H in (600, 1000):
    dz = np.where(np.abs(d[:,2])>1e-6, d[:,2], 1e-6)
    res = {}
    for side, zp in (("floor",-H),("ceiling",H)):
        t = (zp - A[:,2])/dz; P = A + t[:,None]*d
        for L in (1000, 2000, 3000):
            inside = (np.abs(P[:,0])<L/2)&(np.abs(P[:,1])<L/2)
            res[f"{side}_{L}"] = float((w*inside).sum()/w.sum())
    out[f"veto_H{H}"] = res
out["cos_zenith_pct"] = np.percentile(np.degrees(np.arccos(np.abs(d[:,2]))),[10,50,90]).tolist()
# ---- signal: segment collinearity & pointing (ideal PCA directions)
for cfg in ("G1","G5"):
    z = SF.load_s1(E/"S1"/"summary", cfg, "X17")
    s = SF.s1_select(z, "sipm2", 12.0)
    f1, f2 = z["em_fit"][s], z["ep_fit"][s]
    lineang = ang(f1, f2); lineang = np.minimum(lineang, 180-lineang)   # angle between the two segments as lines
    out[f"{cfg}_X17_lineang_pct"] = np.percentile(lineang,[1,5,10,50]).tolist()
    out[f"{cfg}_X17_lineang_hist"] = np.histogram(lineang, np.arange(0,91,2.5))[0].tolist()
    for c in (5,10,15,20,25,30):
        out[f"{cfg}_X17_eff_lineang_gt{c}"] = float((lineang>c).mean())
    # line through the two MM hits: distance from cell centre
    P1, P2 = z["em_P"][s], z["ep_P"][s]
    dd = P2-P1; dd /= np.linalg.norm(dd,axis=1)[:,None]
    dca_s = np.linalg.norm(np.cross(P1, dd),axis=1)
    out[f"{cfg}_X17_dca_hist"] = np.histogram(dca_s, np.arange(0,301,10))[0].tolist()
    out[f"{cfg}_X17_lepKE"] = np.percentile(np.minimum(z["em_ke"][s],z["ep_ke"][s]),[10,50,90]).tolist()
# collinearity on cosmics with a resolution model: segments are exactly parallel in truth,
# measured line angle ~ |N(0, sqrt2 sigma)| in 2D -> Rayleigh with scale sqrt2*sigma
rng = np.random.default_rng(3)
res={}
for sig in (2,5,10,15,20):
    v = rng.normal(0, math.sqrt(2)*sig, (200000,2)); la = np.hypot(v[:,0],v[:,1])
    res[sig] = {c: float((la>c).mean()) for c in (5,10,15,20,25,30)}
out["cos_lineang_leak_vs_sigma"] = res
# ---- vertex positions and acceptance vs depth, per config; radius effect via backward lepton polar angle
for cfg in ("G1","G2","G3","G4","G5","G6"):
    z = SF.load_s1(E/"S1"/"summary", cfg, "X17")
    s = SF.s1_select(z, "sipm2", 12.0)
    V = z["V"]
    out[f"{cfg}_N"] = z["N"]; out[f"{cfg}_rows"] = int(len(V)); out[f"{cfg}_acc"] = float(s.sum()/z["N"])
    out[f"{cfg}_vy_acc_hist"] = np.histogram(V[s,1], np.arange(-60,301,5))[0].tolist()
    out[f"{cfg}_vy_rows_hist"] = np.histogram(V[:,1], np.arange(-60,301,5))[0].tolist()
    rr = np.hypot(V[:,0],V[:,2])
    out[f"{cfg}_vr_rows_pct"] = np.percentile(rr,[50,90,99]).tolist()
    # lepton polar angle wrt beam axis (+y), true initial dir, accepted events
    cy = np.concatenate([z["em_d0"][s,1], z["ep_d0"][s,1]])
    out[f"{cfg}_lep_cosy_acc_hist"] = np.histogram(cy, np.linspace(-1,1,21))[0].tolist()
    # chord, all rows with both legs in gaps (any) vs accepted vs y bins
json.dump(out, open("xtra_artifact.json","w"), indent=1)
print(json.dumps({k:v for k,v in out.items() if not k.endswith("hist")}, indent=1))
