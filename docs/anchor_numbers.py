import numpy as np
ME=0.51099895
def hl(p,x):
    x=max(x,1e-12); b=p/np.sqrt(p*p+ME*ME)
    return np.degrees((13.6/(b*p))*np.sqrt(x)*(1+0.038*np.log(x)))

X0={'He3':70.7,'Al':24.01,'CFRP':42.70,'Air':36.62,'Mylar':39.95,'Kapton':40.56,'Cu':12.86,'Ti':16.16,'Be':65.19,'ArIso':19.55}
# ArIso X0 g/cm2 ~ Ar 19.55
def frac(gcm2,mat): return gcm2/X0[mat]

print("=== areal density matching ===")
rho500=62.7e-3  # g/cm3
print("nTOF gas along beam (L=4cm): %.4f g/cm2 = %.4e at/cm2"%(rho500*4, rho500*4/3.016*6.022e23))
for P,L in [(50,40),(25,40),(100,40),(50,30)]:
    rho=P*101325*3.016e-3/(8.314*293.15)/1000  # g/cm3
    print("  P=%3d bar L=%2d cm: rho=%.4f mg/cm3  areal=%.4f g/cm2  (x%.2f of nTOF)"%(P,L,rho*1e3,rho*L,rho*L/(rho500*4)))

print("\n=== radial exit budget ===")
def budget(name, layers, p=10.0):
    tot=sum(f for _,f in layers)
    print(f"-- {name}: total x/X0 = {tot*100:.3f} %   theta0(p=10)= {hl(p,tot):.2f} deg")
    for n,f in layers: print(f"     {n:32s} {f*100:7.4f} %  ({f/tot*100:4.1f}%)")
    return tot

rho_cfrp=1.55; rho_al=2.70; rho_ti=4.51
ntof=[("He3 500bar 1.0 cm", frac(rho500*1.0,'He3')),
      ("Al barrel 0.6 mm",  frac(rho_al*0.06,'Al')),
      ("CFRP 0.9 mm",       frac(rho_cfrp*0.09,'CFRP')),
      ("air 23.9 cm",       frac(1.205e-3*23.85,'Air')),
      ("Mylar 40um",        frac(1.40*0.004,'Mylar')),
      ("Kapton 50um",       frac(1.42*0.005,'Kapton')),
      ("Cu 9um",            frac(8.96*0.0009,'Cu'))]
t0=budget("n_TOF as built", ntof)

rho50=50*101325*3.016e-3/(8.314*293.15)/1000
g1=[("He3 50bar 5.0 cm",   frac(rho50*5.0,'He3')),
    ("Al liner 0.1 mm",    frac(rho_al*0.01,'Al')),
    ("CFRP 0.45 mm",       frac(rho_cfrp*0.045,'CFRP')),
    ("air 15 cm",          frac(1.205e-3*15,'Air')),
    ("Mylar 40um",         frac(1.40*0.004,'Mylar')),
    ("Kapton 50um",        frac(1.42*0.005,'Kapton')),
    ("Cu 9um",             frac(8.96*0.0009,'Cu'))]
t1=budget("GANIL 50 bar R=5cm, thin liner", g1)
print("   ratio theta0 = %.2f"%(hl(10,t1)/hl(10,t0)))

g2=[("He3 50bar 5.0 cm",   frac(rho50*5.0,'He3')),
    ("CFRP 0.45 mm only",  frac(rho_cfrp*0.045,'CFRP')),
    ("He bag 15 cm",       frac(0.1786e-3*15,'He3')),
    ("Mylar 25um",         frac(1.40*0.0025,'Mylar')),
    ("Kapton 50um",        frac(1.42*0.005,'Kapton')),
    ("Cu 9um",             frac(8.96*0.0009,'Cu'))]
t2=budget("GANIL aggressive (no liner, He bag)", g2)
print("   ratio theta0 = %.2f"%(hl(10,t2)/hl(10,t0)))

print("\n=== hoop load ===")
for P,R in [(500,1.0),(50,5.0),(50,4.5),(25,5.0)]:
    print("  P=%3d bar R=%.1f cm : P*R = %6.1f N/mm"%(P,R,P*0.1*R*10))

print("\n=== NFS rate scratch ===")
phi5=5.88e6  # n/cm2/s at 5 m, 8mm Be, 40 MeV d
for L in [8.,10.,12.,15.]:
    d=2.555+2*3.088e-3*(L*100-0)  # rough: collimator 25.55mm + divergence
    phi=phi5*(5/L)**2
    print("  L=%4.1f m: flux=%.2e n/cm2/s  spot~%.1f cm dia  (beam area %.0f cm2 -> %.2e n/s)"%(
        L,phi,d,np.pi*(d/2)**2,phi*np.pi*(d/2)**2))
nL=rho500*4/3.016*6.022e23
for sig in [1e-5,2e-5,5e-5]:
    R=1.0e6*np.pi*(8/2)**2*nL*sig*1e-24
    print("  sigma_ng=%.0f ub: captures/s=%.1f -> %.2e/day ; IPC/day=%.2e ; X17/day(0.025)=%.1f ; X17/day(ATOMKI 1.5e-3)=%.1f"%(
        sig*1e6,R,R*86400,R*86400*3.5e-3,R*86400*3.5e-3*0.025,R*86400*3.5e-3*1.46e-3))

print("\n=== TOF window at NFS ===")
mn=939.565
for L in [8.,12.]:
    for E in [0.2,1.0,2.0,5.0,20.0]:
        g=1+E/mn; b=np.sqrt(1-1/g**2)
        print("  L=%.0f m E=%5.1f MeV: t=%8.1f ns"%(L,E,L/(b*2.998e8)*1e9))
