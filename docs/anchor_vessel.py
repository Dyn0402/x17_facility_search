import numpy as np
ME=0.51099895
def hl(p,x):
    x=max(x,1e-12); b=p/np.sqrt(p*p+ME*ME)
    return np.degrees((13.6/(b*p))*np.sqrt(x)*(1+0.038*np.log(x)))
# X0 in g/cm2
X0={'He3':70.7,'Be':65.19,'CFRP':42.70,'Al':24.01,'Ti':16.16,'SS':13.84,'Ni':12.68,'Cu':12.86,'Mylar':39.95,'Kapton':40.56,'Air':36.62,'He4':94.32}
RHO={'Be':1.848,'CFRP':1.55,'Al':2.699,'Ti':4.54,'SS':7.9,'Ni':8.90,'Cu':8.96}
print("=== barrier candidates: x/X0 per 100 um of continuous foil ===")
for m in ['Be','Al','Ti','SS','Ni','Cu']:
    print("  %-4s rho=%5.2f  X0=%5.2f g/cm2  ->  %.4f %% per 100 um  (rel to Al: x%.2f)"%(
        m,RHO[m],X0[m],RHO[m]*0.01/X0[m]*100, (RHO[m]/X0[m])/(RHO['Al']/X0['Al'])))

print("\n=== P*R scaling: gas + structure both scale as P*R ===")
def rho_he3(P): return P*101325*3.016e-3/(8.314*293.15)/1000  # g/cm3
def cell(P,R,sig_allow=500.,barrier=('Al',0.005),shell='CFRP',verbose=False):
    """P bar, R cm. sig_allow MPa. barrier (mat, cm). returns dict"""
    t_shell_mm = (P*0.1)*(R*10)/sig_allow   # mm, hoop
    t_shell_mm = max(t_shell_mm, 0.30)      # manufacturing floor
    gas = rho_he3(P)*R/X0['He3']
    sh  = RHO[shell]*(t_shell_mm/10)/X0[shell]
    ba  = RHO[barrier[0]]*barrier[1]/X0[barrier[0]]
    return dict(t=t_shell_mm,gas=gas,shell=sh,bar=ba,tot=gas+sh+ba)

print("%5s %5s %7s %9s %9s %9s %9s"%("P[bar]","R[cm]","t[mm]","gas%","shell%","barrier%","total%"))
for P in [5,10,20,30,50]:
    for R in [2.0,4.0,5.0]:
        c=cell(P,R)
        print("%5d %5.1f %7.2f %9.4f %9.4f %9.4f %9.4f"%(P,R,c['t'],c['gas']*100,c['shell']*100,c['bar']*100,c['tot']*100))

print("\n=== rate ~ R^2 * P * L at fixed budget B ~ P*R  =>  rate ~ B*R*L ===")
print("  fixed budget check: P*R constant")
for P,R in [(50,2.),(20,5.),(10,10.)]:
    c=cell(P,R)
    print("   P=%2d R=%4.1f  P*R=%5.0f  budget=%.4f%%  rate index (R^2*P*L, L=40) = %.3g"%(
        P,R,P*R,c['tot']*100,R**2*P*40))

print("\n=== candidate builds, 40 cm long, radial exit budget ===")
def build(name,P,R,barrier,shell_mm,gap,win,extra=0.0):
    gas=rho_he3(P)*R/X0['He3']
    ba=RHO[barrier[0]]*barrier[1]/X0[barrier[0]] if barrier else 0.0
    sh=RHO['CFRP']*(shell_mm/10)/X0['CFRP']
    tot=gas+ba+sh+gap+win+extra
    areal=rho_he3(P)*40
    print("%-38s P=%2d R=%3.1f  gas %.4f  bar %.4f  shell %.4f  gap %.4f  win %.4f | TOT %.3f%%  th0=%.2fdeg  areal=%.3f g/cm2 (x%.2f nTOF)"%(
        name,P,R,gas*100,ba*100,sh*100,gap*100,win*100,tot*100,hl(10,tot),areal,areal/0.2508))
    return tot
GAP_AIR=1.205e-3*15/X0['Air']; GAP_HE=0.1786e-3*15/X0['He4']
WIN=1.40*0.004/X0['Mylar']+1.42*0.005/X0['Kapton']+8.96*0.0009/X0['Cu']
WIN_LO=1.40*0.0025/X0['Mylar']+1.42*0.005/X0['Kapton']+2.699*0.0015/X0['Al']
print("  [MM window as built = %.4f %% ; with Al cathode 15um + 25um mylar = %.4f %%]"%(WIN*100,WIN_LO*100))
build("nTOF as built (500 bar, R=1)",500,1.0,('Al',0.06),0.9,GAP_AIR,WIN)
build("A: 50 bar R=5 Al 100um",50,5.0,('Al',0.01),0.5,GAP_AIR,WIN)
build("B: 30 bar R=5 Al 50um",30,5.0,('Al',0.005),0.30,GAP_HE,WIN)
build("C: 30 bar R=5 Be 100um shell-free",30,5.0,('Be',0.01),0.30,GAP_HE,WIN_LO)
build("D: 10 bar R=5 Be 250um structural",10,5.0,('Be',0.025),0.0,GAP_HE,WIN_LO)
build("E: 10 bar R=4 Al 25um + CFRP 0.3",10,4.0,('Al',0.0025),0.30,GAP_HE,WIN_LO)
build("F: 5 bar R=4 Al 25um + CFRP 0.3",5,4.0,('Al',0.0025),0.30,GAP_HE,WIN_LO)

print("\n=== Be as structure: hoop stress check (sigma = P*R/t, MPa) ===")
for P,R,t in [(10,5.0,0.25),(10,5.0,0.5),(30,5.0,0.5),(30,5.0,1.0),(50,5.0,1.0)]:
    print("  P=%2d bar R=%.1f cm t=%.2f mm -> sigma=%6.1f MPa   (Be yield ~240-345, CFRP allow ~500)"%(
        P,R,t,(P*0.1)*(R*10)/t))
